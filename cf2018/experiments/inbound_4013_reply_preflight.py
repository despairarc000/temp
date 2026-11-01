"""Offline-only candidate for an incoming uncompressed TGCP 0x4013 RPC reply.

This intentionally composes the existing strict AA-framing subset with the
source-pinned 4013/DataHead shape and offline RPC64/reason validator.
No network, listener, original native execution or client-acceptance claim.
It neither exports nor persists payload, IDs, keys or sequences.
"""
from rx_envelope import Receiver, FrameError, _uint, _base
from address_response_gate import parse_response, assess_response, ResponseError

CAP=8192

def _fields(data):
    fields={}
    pos=0
    while pos < len(data):
        tag,pos=_uint(data,pos,len(data),32)
        number,kind=tag>>4,tag&15
        if number<1 or number in fields:
            raise FrameError('unsupported or duplicate field')
        if kind==1:
            if pos>=len(data):raise FrameError('truncated uint8')
            value=data[pos];pos+=1
        elif kind==5:
            if pos+4>len(data):raise FrameError('truncated nested length')
            length=int.from_bytes(data[pos:pos+4],'big');pos+=4
            if length>len(data)-pos:raise FrameError('nested length exceeds input')
            value=data[pos:pos+length];pos+=length
        elif kind==0:
            value,pos=_uint(data,pos,len(data),32)
        else:
            raise FrameError('unsupported field kind')
        fields[number]=(kind,value)
    return fields

def inspect_inbound_4013_reply(frame,pending_rpc_sequences):
    """Return only fixed labels; cannot establish original-client acceptance."""
    if type(frame) is not bytes or not 32<=len(frame)<=CAP:
        return 'NOT_COMPARABLE'
    if not isinstance(pending_rpc_sequences,(set,frozenset)) or not all(
            type(x) is int and 0<=x<2**64 for x in pending_rpc_sequences):
        raise ValueError('bounded in-memory pending RPC64 set required')
    try:
        receiver=Receiver(CAP)
        messages=receiver.feed(frame)
        receiver.finish()
        if len(messages)!=1:return 'INVALID_TGCP_FRAMING'
        header_size=messages[0].header_size
        outer=_fields(frame[5:header_size])
        if set(outer)!={1,2} or outer[1][0]!=5 or outer[2][0]!=5:
            return 'INBOUND_DATAHEAD_NOT_RECOGNIZED'
        base=_base(outer[1][1],0,len(outer[1][1]))
        # Original native TGCPBase field 6 is the inbound per-frame
        # decrypt-mode byte. Require an explicit zero for this conservative
        # cleartext-only candidate, not an unknown runtime default.
        if base.get(6)!=0:
            return 'UNSUPPORTED_ENCRYPTION_MODE'
        ext=_fields(outer[2][1])
        if set(ext)!={0x4013} or ext[0x4013][0]!=5:
            return 'INBOUND_DATAHEAD_NOT_RECOGNIZED'
        datahead=_fields(ext[0x4013][1])
        # Conservative known-variant policy, not a claim all native variants
        # require every field. Route bytes are intentionally not interpreted.
        if (set(datahead)!={1,2,3,4} or
                any(datahead[n][0]!=1 for n in (1,2,3)) or
                datahead[4][0]!=5 or not datahead[4][1]):
            return 'INBOUND_DATAHEAD_NOT_RECOGNIZED'
        if datahead[1][1]!=0:
            return 'UNSUPPORTED_COMPRESSION_MODE'
        rpc=parse_response(messages[0].body)
        return assess_response(rpc,pending_sequences=pending_rpc_sequences)
    except FrameError:
        return 'INVALID_TGCP_FRAMING'
    except ResponseError:
        return 'INVALID_RPC_RESPONSE'

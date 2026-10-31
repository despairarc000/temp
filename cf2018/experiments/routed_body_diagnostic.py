"""Fixed-label, in-memory diagnostics; no payload, route or sequence is returned.

This narrows a failed classifier at two native-grounded boundaries, not a broad
signature scan. It is not a reply generator or a phone/authentication oracle.
"""


def header_reason(body, offset):
    if len(body)-offset<4:return 'SHORT_LENGTH'
    n=int.from_bytes(body[offset:offset+4],'big')
    if n&0xffff0000==0x80010000:return 'VERSIONED_PREFIX_CANDIDATE'
    if not 1<=n<=64:return 'NAME_LENGTH_POLICY'
    pos=offset+4
    if pos+n>len(body):return 'TRUNCATED_NAME'
    name=body[pos:pos+n]
    if not (name[:1].isalpha() or name[:1]==b'_'):return 'METHOD_BYTES_POLICY'
    if any(not (65<=c<=90 or 97<=c<=122 or 48<=c<=57 or c in (95,46)) for c in name):
        return 'METHOD_BYTES_POLICY'
    pos+=n
    if pos>=len(body):return 'SHORT_TYPE'
    if body[pos] not in (1,2,3,4):return 'MESSAGE_KIND_POLICY'
    pos+=1
    if pos+8>=len(body):return 'SHORT_SEQUENCE_OR_ARGUMENT'
    pos+=8
    if body[pos] not in (0,2,3,4,6,8,10,11,12,13,14,15):return 'FIRST_FIELD_TYPE_POLICY'
    return 'LEGACY_HEADER_PLAUSIBLE'


def diagnose_body(body, sequence):
    if type(body) is not bytes or len(body)>8192:
        raise ValueError('bounded in-memory body required')
    if type(sequence) is not int or not 0<=sequence<2**32:
        raise ValueError('validated header packet sequence required')
    return {'sequence_prefix':'SHORT' if len(body)<4 else
            'MATCH' if body[:4]==sequence.to_bytes(4,'big') else 'MISMATCH',
            'legacy_at_start':header_reason(body,0),
            'legacy_after_sequence':header_reason(body,4)}


def inspect_v38_frame(frame):
    """Use the existing v38 bounded parser, exporting only fixed classifications."""
    from tgcp_wire import fields,require_field
    from routed_fingerprint_v21 import route_value_and_body
    rejected={'sequence_prefix':'NOT_COMPARABLE','legacy_at_start':'NOT_COMPARABLE',
              'legacy_after_sequence':'NOT_COMPARABLE','known_address_route':'UNKNOWN'}
    if type(frame) is not bytes or not 7<=len(frame)<=8192:return rejected
    if frame[:3]!=b'\x43\x66\xaa':return rejected
    try:
        end=2+int.from_bytes(frame[3:7],'big')
        if not 7<=end<=len(frame):return rejected
        outer=fields(frame[7:end]);base=fields(require_field(outer,1,5).value)
        if require_field(base,9,0).value!=len(frame)-end:return rejected
        sequence=require_field(base,7,0).value
        name,body=route_value_and_body(frame)
        if body is None:return rejected
        return {**diagnose_body(body,sequence),
                'known_address_route':'MATCH' if name==b'QueryAddrSvr' else
                    'OTHER' if name is not None else 'UNKNOWN'}
    except (ValueError,IndexError,TypeError,OverflowError):return rejected

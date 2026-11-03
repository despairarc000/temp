"""Scoped update lookup and read-only typed version request discriminator.

No listener or VersionUpdate reply. Only the previously tested address-response
builder is called, with an independently verified target and sequence guards.
All externally returned diagnostic values are fixed labels.
"""
VERSION_ROUTE=b'VersionUpdate'
METHOD=b'VersionUpdate:ReqUpdateVersion'

def version_context_matches(candidate,reference):
    try:
        from second_service_syn_gate import _parts
        from r056_second_service_syn import first_syn_decision
        if type(candidate) is not bytes or type(reference) is not bytes:return False
        if len(candidate)!=134 or len(reference)!=133:return False
        if first_syn_decision(candidate)[0]!='OTHER_NAMED_ROUTE' or first_syn_decision(reference)[0]!='REFERENCE_NAMED_ROUTE_CANDIDATE':return False
        a,ae,sa,ra,na=_parts(reference);b,be,sb,rb,nb=_parts(candidate)
        if na!=b'QueryAddrSvr' or nb!=VERSION_ROUTE or ra[4]!=rb[4]:return False
        if a[0][3]!=b[0][3] or [f[4] for f in a]!=[f[4] for f in b] or ae[0][4]!=be[0][4]:return False
        if [(f[0],f[1],f[4]) for f in sa]!=[(f[0],f[1],f[4]) for f in sb]:return False
        return all(x[3]==y[3] for x,y in zip(sa,sb) if x[0]!=14)
    except (ValueError,TypeError,IndexError,StopIteration,OverflowError):return False

def make_lookup_reply(frame):
    from address_query_target import classify_frame
    from r033_reply import make_candidate
    if classify_frame(frame)['address_target']!='VERSION_ADDRESS_QUERY':raise ValueError('exact complete version address query required')
    return make_candidate(frame) # Existing RPC64 correlation/loopback-only policy.

def classify_body(body,sequence):
    no={'version_request':'NOT_IDENTIFIED','version_request_reason':'SHAPE_MISMATCH','version_mode':'UNKNOWN'}
    if type(body) is not bytes or not 4<=len(body)<=4096 or type(sequence) is not int or not 0<=sequence<2**32:return no
    if body[:4]!=sequence.to_bytes(4,'big'):return {**no,'version_request_reason':'PACKET_SEQUENCE_MISMATCH'}
    header=len(METHOD).to_bytes(4,'big')+METHOD+b'\1'
    if body[4:4+len(header)]!=header:return no
    p=4+len(header)+8
    def read(count):
        nonlocal p
        if count<0 or p+count>len(body):raise ValueError('short request')
        out=body[p:p+count];p+=count;return out
    def struct(shape,required,depth=0):
        if depth>3:raise ValueError('depth budget')
        seen=set();mode=None
        for unused in range(16):
            kind=read(1)[0]
            if kind==0:
                if not required<=seen:raise ValueError('missing fields')
                return mode
            ident=int.from_bytes(read(2),'big')
            if ident in seen or ident not in shape or shape[ident][0]!=kind:raise ValueError('unexpected field')
            seen.add(ident);spec=shape[ident]
            if kind in (6,8,10):
                value=int.from_bytes(read({6:2,8:4,10:8}[kind]),'big')
                if depth==2 and ident==3:mode=value
            elif kind==11:
                length=int.from_bytes(read(4),'big')
                if length>1024:raise ValueError('string bound')
                read(length)
            elif kind==12:
                child=struct(spec[1],spec[2],depth+1)
                if child is not None:mode=child
            else:raise ValueError('unsupported type')
        raise ValueError('field budget')
    comm={**{i:(8,) for i in range(1,5)},5:(10,),6:(10,),7:(11,),8:(10,),9:(6,)}
    custom={i:(11,) for i in range(1,4)}
    request={1:(12,comm,set(range(1,8))),2:(11,),3:(12,custom,{1,2,3})}
    try:
        mode=struct({1:(12,request,{1,2})},{1})
        if p!=len(body):return no
    except (ValueError,IndexError,OverflowError):return no
    group='APPLICATION' if mode==1 else 'RESOURCES' if mode==2 else 'OTHER'
    return {'version_request':'COMPLETE_LEGACY64','version_request_reason':'EXACT_METHOD_AND_TYPED_ARGS','version_mode':group}

def classify_frame(frame):
    no={'version_request':'NOT_COMPARABLE','version_request_reason':'FRAME_INVALID','version_mode':'UNKNOWN'}
    if type(frame) is not bytes or not 7<=len(frame)<=8192 or frame[:3]!=b'\x43\x66\xaa':return no
    try:
        from tgcp_wire import fields,require_field
        from routed_fingerprint_v21 import route_value_and_body
        from gcloud_datahead_v38 import compression_from_routed_frame
        end=2+int.from_bytes(frame[3:7],'big')
        if not 7<=end<=len(frame):return no
        base=fields(require_field(fields(frame[7:end]),1,5).value)
        if require_field(base,4,0).value!=0x4013 or require_field(base,9,0).value!=len(frame)-end:return no
        if require_field(base,6,1).value!=0:return {**no,'version_request_reason':'CIPHER_NOT_CLEAR'}
        if compression_from_routed_frame(frame).get('compression_flag')!='no':return {**no,'version_request_reason':'COMPRESSION_NOT_CLEAR'}
        name,body=route_value_and_body(frame)
        if name!=VERSION_ROUTE:return {**no,'version_request_reason':'ROUTE_MISMATCH'}
        return classify_body(body,require_field(base,7,0).value)
    except (ValueError,TypeError,IndexError,OverflowError):return no

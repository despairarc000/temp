"""Read-only fixed-label address-query target discriminator. No reply generation.

Checks the original legacy64 request grammar, complete consumption, packet
sequence and route/clear transport guards. Labels refer to request content only,
not successful discovery, ownership, authentication or a version request itself.
"""
METHOD=b'QueryAddrSvr:QueryAddrInfo'

def classify_body(body,sequence):
    no={'address_target':'NOT_IDENTIFIED','address_target_reason':'SHAPE_MISMATCH'}
    if type(body) is not bytes or not 4<=len(body)<=1024 or type(sequence) is not int or not 0<=sequence<2**32:return no
    if body[:4]!=sequence.to_bytes(4,'big'):
        return {**no,'address_target_reason':'PACKET_SEQUENCE_MISMATCH'}
    head=len(METHOD).to_bytes(4,'big')+METHOD+b'\1'
    if body[4:4+len(head)]!=head:return no
    p=4+len(head)+8 # Independent RPC64 sequence, never returned.
    if body[p:p+6]!=b'\x0c\0\1\x0a\0\1':return no
    p+=6+8 # game_id is neither logged nor used as a substitute service label.
    if body[p:p+3]!=b'\x0a\0\2' or p+11>len(body):return no
    unit=int.from_bytes(body[p+3:p+11],'big');p+=11
    if body[p:p+3]!=b'\x0b\0\3' or p+7>len(body):return no
    n=int.from_bytes(body[p+3:p+7],'big');p+=7
    if n>128 or p+n+2!=len(body) or body[-2:]!=b'\0\0':return no
    service=body[p:p+n]
    label={(b'dir',3):'DIRECTORY_ADDRESS_QUERY',(b'download',1):'VERSION_ADDRESS_QUERY'}.get((service,unit),'OTHER_ADDRESS_QUERY')
    return {'address_target':label,'address_target_reason':'COMPLETE_LEGACY64'}

def classify_frame(frame):
    no={'address_target':'NOT_COMPARABLE','address_target_reason':'FRAME_INVALID'}
    if type(frame) is not bytes or not 7<=len(frame)<=8192 or frame[:3]!=b'\x43\x66\xaa':return no
    try:
        from tgcp_wire import fields,require_field
        from routed_fingerprint_v21 import route_value_and_body
        from gcloud_datahead_v38 import compression_from_routed_frame
        end=2+int.from_bytes(frame[3:7],'big')
        if not 7<=end<=len(frame):return no
        outer=fields(frame[7:end]);base=fields(require_field(outer,1,5).value)
        if require_field(base,9,0).value!=len(frame)-end:return no
        if require_field(base,4,0).value!=0x4013:return no
        if require_field(base,6,1).value!=0:return {**no,'address_target_reason':'CIPHER_NOT_CLEAR'}
        if compression_from_routed_frame(frame).get('compression_flag')!='no':return {**no,'address_target_reason':'COMPRESSION_NOT_CLEAR'}
        name,body=route_value_and_body(frame)
        if name!=b'QueryAddrSvr':return {**no,'address_target_reason':'ROUTE_MISMATCH'}
        return classify_body(body,require_field(base,7,0).value)
    except (ValueError,TypeError,IndexError,OverflowError):return no

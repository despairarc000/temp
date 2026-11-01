"""Privacy-preserving exact-qualified classifier for a validated TGCP frame.

It uses the independently verified packet-header sequence and exact routed
name before inspecting the bounded original-compatible RPC body in RAM.
Returns ONLY a fixed label, never request, route, IDs or body.
"""
from qualified_address_request import classify_known_qualified_query

def inspect_qualified_frame(frame):
    from routed_body_diagnostic import inspect_v38_frame
    from routed_fingerprint_v21 import route_value_and_body
    rejected={'qualified_address_request':'NOT_COMPARABLE'}
    if type(frame) is not bytes or not 7<=len(frame)<=8192:
        return rejected
    fixed=inspect_v38_frame(frame)
    if (fixed.get('sequence_prefix')!='MATCH' or
        fixed.get('known_address_route')!='MATCH'):
        return rejected
    _name,body=route_value_and_body(frame)
    if body is None or len(body)<4:
        return rejected
    # The equality to independent header sequence has ALREADY been verified.
    result=classify_known_qualified_query(body,int.from_bytes(body[:4],'big'))
    return {'qualified_address_request':result['qualified_address_request']}

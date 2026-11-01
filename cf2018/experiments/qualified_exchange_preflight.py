"""Offline-only correlation of an exact qualified address request and candidate reply.

Inputs are caller-supplied bounded in-memory bytes. Never logs, stores, sends
or returns sequence values, addresses, route values or payloads.
This does not check the actual Android QuerySession or live server acceptance.
"""
from qualified_address_request import (
    QUALIFIED_NAME, classify_known_qualified_query
)
from address_response_gate import parse_response, assess_response, ResponseError

MAX_SIZE = 8192
RPC_SEQUENCE_OFFSET = 4 + 4 + len(QUALIFIED_NAME) + 1


def inspect_qualified_exchange(request_body, packet_sequence, reply_rpc):
    if type(request_body) is not bytes or type(reply_rpc) is not bytes:
        raise ValueError('in-memory bytes required')
    if not 1 <= len(request_body) <= MAX_SIZE or not 1 <= len(reply_rpc) <= MAX_SIZE:
        raise ValueError('bounded input required')
    if type(packet_sequence) is not int or not 0 <= packet_sequence < 2**32:
        raise ValueError('uint32 TGCP packet sequence required')
    request = classify_known_qualified_query(request_body, packet_sequence)
    if request['qualified_address_request'] != 'COMPLETE_STRUCTURAL_CANDIDATE':
        return 'REQUEST_NOT_RECOGNIZED'
    # Separate 64-bit RPC sequence, NOT the 4-byte TGCP packet sequence.
    rpc_seq = int.from_bytes(request_body[RPC_SEQUENCE_OFFSET:RPC_SEQUENCE_OFFSET+8], 'big')
    try:
        reply = parse_response(reply_rpc)
    except ResponseError:
        return 'REPLY_NOT_STRUCTURALLY_VALID'
    return assess_response(reply, pending_sequences={rpc_seq})

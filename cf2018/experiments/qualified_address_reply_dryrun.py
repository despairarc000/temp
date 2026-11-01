"""OFFLINE ONLY: build a structurally guarded address-RPC response candidate.

No TGCP frame, socket send, client login or actual native-session acceptance.
Only a validated original request, a numeric IPv4 loopback address and port.
No logging, file writes, or global session state. Never expose live RPC values.
"""
from ipaddress import ip_address

from address_response_gate import parse_response, assess_response
from qualified_address_request import QUALIFIED_NAME, classify_known_qualified_query

RPC_SEQUENCE_OFFSET = 4 + 4 + len(QUALIFIED_NAME) + 1


def _int32(n):
    return n.to_bytes(4, 'big', signed=True)


def _field(kind, field_id):
    return bytes([kind]) + field_id.to_bytes(2, 'big')


def candidate_reply(request_body, tgcp_sequence, *, host='127.0.0.1', port=9080):
    """Produce only an in-memory Thrift RPC candidate, not a network reply."""
    if type(host) is not str or type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('bounded local target required')
    try:
        addr = ip_address(host)
    except ValueError as exc:
        raise ValueError('numeric loopback required') from exc
    if addr.version != 4 or not addr.is_loopback:
        raise ValueError('only local IPv4 loopback permitted in this dry run')
    classified = classify_known_qualified_query(request_body, tgcp_sequence)
    if classified['qualified_address_request'] != 'COMPLETE_STRUCTURAL_CANDIDATE':
        raise ValueError('native-qualified request not recognized')

    # This is the original 64-bit RPC sequence, NOT the 32-bit TGCP sequence.
    rpc_seq = request_body[RPC_SEQUENCE_OFFSET:RPC_SEQUENCE_OFFSET+8]
    hostname = host.encode('ascii')
    address_info = (
        _field(11, 1) + _int32(len(hostname)) + hostname +
        _field(8, 2) + _int32(port) + b'\x00'
    )
    result = (
        _field(8, 1) + _int32(0) + _field(11, 2) + _int32(0) +
        _field(15, 3) + b'\x0c' + _int32(1) +
        address_info + b'\x00'
    )
    rpc = (
        _int32(len(QUALIFIED_NAME)) + QUALIFIED_NAME + b'\x02' + rpc_seq +
        _field(12, 0) + result + b'\x00'
    )
    parsed = parse_response(rpc)
    status = assess_response(
        parsed, pending_sequences={int.from_bytes(rpc_seq, 'big')}
    )
    if status != 'STRUCTURAL_CANDIDATE_ONLY_NOT_GAME_ACCEPTANCE':
        raise ValueError('offline structural preflight refused candidate')
    return rpc

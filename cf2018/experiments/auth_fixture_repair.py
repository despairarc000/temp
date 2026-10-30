"""Pinned synthetic fixture repair only; not a general server serializer."""
from tgcp_body_envelope import encode_body_envelope

def corrected_v12_fixture(arm):
    """Only repair the three pinned synthetic historical fixtures, for regression.

    Byte 32 is their verified one-byte base field 9, and header size is 42.
    This is deliberately fixture-specific; a general server must encode its base
    body length from len(encode_body_envelope(union_payload)). All account/header
    assumptions in the historical fixtures remain unvalidated.
    """
    from auth_v12_fixtures import reply
    packet = reply(arm)  # validates exact historical hash before any change
    header_size = int.from_bytes(packet[1:5], 'big')
    if header_size != 42 or packet[30:32] != b'\x91\x01':
        raise ValueError('unsupported historical fixture layout')
    old_body = packet[header_size:]
    if packet[32] != len(old_body):
        raise ValueError('historical body length mismatch')
    body = encode_body_envelope(old_body)
    if len(body) >= 128:
        raise ValueError('historical one-byte length layout exceeded')
    return packet[:32] + bytes([len(body)]) + packet[33:header_size] + body

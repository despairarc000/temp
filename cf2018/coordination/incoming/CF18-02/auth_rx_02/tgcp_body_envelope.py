"""Original TGCP body-envelope encoding; no account/authentication semantics.

The TGCPBody native decoder consumes its own AA/99 + uint32 total-length
preamble, independently of the outer frame/header. This helper wraps an already
serialized union; it does not generate an account, token, key or valid session.
No listener, connector or automatic device action.
"""


def encode_body_envelope(union_payload, *, varint=True, max_size=65536):
    if not isinstance(union_payload, bytes):
        raise TypeError('serialized union must be bytes')
    if type(varint) is not bool:
        raise TypeError('varint must be bool')
    if type(max_size) is not int or not 5 <= max_size <= 65536:
        raise ValueError('body cap must be between 5 and 65536')
    total = 5 + len(union_payload)
    if total > max_size:
        raise ValueError('body envelope exceeds cap')
    return (b'\xaa' if varint else b'\x99') + total.to_bytes(4, 'big') + union_payload


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

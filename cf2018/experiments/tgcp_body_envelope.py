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

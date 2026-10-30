"""CrossFire 2018 TGCP WAIT/Bingo body-only serializer.

Based on pinned Apollo native writers; no login/session generation, socket,
listener, captured auth bytes or Android execution. Structural encoding does
NOT establish server identity validity or actual client acceptance.
"""
from dataclasses import dataclass

class BodyEncodingError(ValueError):
    pass

WAIT, BINGO, MAX_BODY = 0x3002, 0x6002, 4096

def _int(name, value, bits, signed=False):
    if type(value) is not int:
        raise BodyEncodingError(f'{name} must be integer')
    lo = -(1 << (bits - 1)) if signed else 0
    hi = (1 << (bits - 1)) - 1 if signed else (1 << bits) - 1
    if not lo <= value <= hi:
        raise BodyEncodingError(f'{name} out of {bits}-bit range')
    return value

def varuint(value, bits=64):
    _int('varuint', value, bits)
    result = bytearray()
    while value > 127:
        result.append((value & 0x7f) | 0x80)
        value >>= 7
    result.append(value)
    return bytes(result)

def varint64(value):
    """Native writeVarInt64 ZigZag encoding."""
    value = _int('session_id', value, 64, signed=True)
    return varuint(((value << 1) ^ (value >> 63)) & ((1 << 64) - 1))

def _tag(field, kind):
    return varuint((field << 4) | kind, bits=32)

def _nested(field, content):
    if not isinstance(content, bytes) or len(content) >= 1 << 32:
        raise BodyEncodingError('nested content type/size invalid')
    return _tag(field, 5) + len(content).to_bytes(4, 'big') + content

def _scalar(field, value, bits=32):
    return _tag(field, 0) + varuint(value, bits=bits)

@dataclass(frozen=True)
class WaitFields:
    position: int
    total: int
    rough_time: int

@dataclass(frozen=True)
class RelayFields:
    position: int
    identity: bytes
    server_id: int
    session_id: int

@dataclass(frozen=True)
class BingoFields:
    relay: RelayFields
    compression_method: int
    compression_limit: int

def _envelope(selector, component):
    union = _nested(selector, component)
    length = len(union) + 5
    if length > MAX_BODY:
        raise BodyEncodingError('body exceeds local cap')
    return b'\xaa' + length.to_bytes(4, 'big') + union

def wait_body(fields):
    if not isinstance(fields, WaitFields):
        raise BodyEncodingError('explicit WaitFields required')
    content = b''.join((
        _scalar(1, _int('position', fields.position, 32)),
        _scalar(2, _int('total', fields.total, 32)),
        _scalar(3, _int('rough_time', fields.rough_time, 32)),
    ))
    return _envelope(WAIT, content)

def bingo_body(fields):
    if not isinstance(fields, BingoFields) or not isinstance(fields.relay, RelayFields):
        raise BodyEncodingError('explicit BingoFields and RelayFields required')
    r = fields.relay
    if not isinstance(r.identity, bytes) or len(r.identity) != 16:
        raise BodyEncodingError('native relay writer requires exactly 16 identity bytes')
    position = _int('position', r.position, 32)
    server_id = _int('server_id', r.server_id, 64)
    method = _int('compression_method', fields.compression_method, 8)
    limit = _int('compression_limit', fields.compression_limit, 32)
    relay = (_scalar(1, position)
             + _nested(2, r.identity)
             + _scalar(3, server_id, 64)
             + _tag(4, 0) + varint64(r.session_id))
    body = _nested(1, relay) + _tag(2, 1) + bytes([method]) + _scalar(3, limit)
    return _envelope(BINGO, body)

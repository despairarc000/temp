"""Strict offline Bingo/WAIT body inspector, NOT native decoder equivalence.

Rejects mismatched header/body selector, wrong AA envelope or missing fields
by local safety policy. No network, credentials, account or session validation.
"""
class BodyStructureError(ValueError):
    pass

def _uint(buf, pos, end, max_bits=64):
    value = 0
    for index in range((max_bits + 6) // 7):
        if pos >= end: raise BodyStructureError('truncated varuint')
        byte = buf[pos]; pos += 1
        value |= (byte & 127) << (7 * index)
        if value >= 1 << max_bits: raise BodyStructureError('varuint overflow')
        if not byte & 128: return value, pos
    raise BodyStructureError('varuint overlong')

def _fields(buf, schema, *, relay=False):
    pos, end = 0, len(buf)
    seen = set()
    while pos < end:
        tag, pos = _uint(buf, pos, end, 32)
        field, kind = tag >> 4, tag & 15
        if field in seen: raise BodyStructureError('duplicate field')
        if field not in schema or schema[field] != kind:
            raise BodyStructureError('unsupported field/kind for strict mode')
        seen.add(field)
        if kind == 5:
            if pos + 4 > end: raise BodyStructureError('truncated nested length')
            size = int.from_bytes(buf[pos:pos + 4], 'big'); pos += 4
            if size > end - pos: raise BodyStructureError('nested end beyond body')
            inner = buf[pos:pos + size]; pos += size
            if relay and field == 2 and size != 16:
                raise BodyStructureError('relay identity must be 16 bytes')
            if not relay and field == 1 and schema == {1: 5, 2: 1, 3: 0}:
                _fields(inner, {1: 0, 2: 5, 3: 0, 4: 0}, relay=True)
        elif kind == 1:
            if pos >= end: raise BodyStructureError('truncated uint8')
            pos += 1
        else:
            _, pos = _uint(buf, pos, end)
    if seen != set(schema): raise BodyStructureError('required fields missing')
    return {'field_count': len(seen), 'complete': True}

def inspect_body(header_type, body, *, max_size=4096):
    if header_type not in (0x3002, 0x6002):
        raise BodyStructureError('only 0x3002 WAIT / 0x6002 Bingo supported')
    if not isinstance(body, bytes) or not 5 <= len(body) <= max_size:
        raise BodyStructureError('invalid or oversized body')
    if body[0] != 0xaa: raise BodyStructureError('AA body envelope required')
    declared = int.from_bytes(body[1:5], 'big')
    if declared != len(body): raise BodyStructureError('TGCPBody declared length mismatch')
    tag, pos = _uint(body, 5, len(body), 32)
    if tag != (header_type << 4) | 5:
        raise BodyStructureError('header/body union type mismatch')
    if pos + 4 > len(body): raise BodyStructureError('truncated component length')
    n = int.from_bytes(body[pos:pos + 4], 'big'); pos += 4
    if n != len(body) - pos: raise BodyStructureError('component declared length mismatch')
    detail = (_fields(body[pos:], {1: 0, 2: 0, 3: 0}) if header_type == 0x3002
              else _fields(body[pos:], {1: 5, 2: 1, 3: 0}))
    return {'body_type': f'0x{header_type:04x}', 'body_size': len(body),
            'component_size': n, 'field_count': detail['field_count'],
            'scope': 'STRICT_OFFLINE_STRUCTURAL_ONLY_NOT_AUTHENTICATION'}

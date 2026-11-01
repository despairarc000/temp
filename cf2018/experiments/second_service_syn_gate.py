"""Exact non-route client-SYN comparison; fixed labels, NO ACK permission.

Original reference stays private. This checks a bounded candidate against that
reference in memory; it never emits field values, route names or hashes.
"""
from r056_second_service_syn import first_syn_decision
from rx_envelope import _uint, FrameError


def _records(data):
    pos, out, seen = 0, [], set()
    while pos < len(data):
        if len(out) >= 48:
            raise ValueError('field budget')
        start = pos
        tag, pos = _uint(data, pos, len(data), 32)
        key = data[start:pos]
        number, kind = tag >> 4, tag & 15
        if number == 0 or number in seen:
            raise ValueError('duplicate or zero field')
        seen.add(number)
        if kind == 0:
            value, pos = _uint(data, pos, len(data), 32)
        elif kind == 1:
            if pos == len(data):
                raise ValueError('short byte')
            value, pos = data[pos], pos + 1
        elif kind == 5:
            if pos + 4 > len(data):
                raise ValueError('short length')
            length = int.from_bytes(data[pos:pos+4], 'big')
            pos += 4
            if pos + length > len(data):
                raise ValueError('short payload')
            value, pos = data[pos:pos+length], pos+length
        else:
            raise ValueError('unknown kind')
        out.append((number, kind, value, data[start:pos], key))
    return out


def _parts(wire):
    outer = _records(wire[7:])
    if [(f[0], f[1]) for f in outer] != [(1, 5), (2, 5)]:
        raise ValueError('outer shape')
    ext = _records(outer[1][2])
    if len(ext) != 1 or ext[0][:2] != (0x1001, 5):
        raise ValueError('extension shape')
    syn = _records(ext[0][2])
    route = next(f for f in syn if f[0] == 14)
    if route[1] != 5:
        raise ValueError('route kind')
    choices = _records(route[2])
    if len(choices) != 1 or choices[0][:2] != (4, 5) or choices[0][4] != b'\x45':
        raise ValueError('route union')
    names = _records(choices[0][2])
    if len(names) != 1 or names[0][:2] != (1, 5) or names[0][4] != b'\x15':
        raise ValueError('name shape')
    return outer, ext, syn, route, names[0][2]


def compare_security_context(candidate, reference):
    """A matching label still requires a separately authorized ACK experiment."""
    refused = 'REFUSED'
    try:
        if type(candidate) is not bytes or type(reference) is not bytes:
            return refused
        if len(reference) != 133 or len(candidate) != 131:
            return refused
        if first_syn_decision(reference)[0] != 'REFERENCE_NAMED_ROUTE_CANDIDATE':
            return refused
        if first_syn_decision(candidate)[0] != 'TEN_BYTE_NAMED_ROUTE_CANDIDATE':
            return refused
        a, ae, sa, ra, na = _parts(reference)
        b, be, sb, rb, nb = _parts(candidate)
        if len(na) != 12 or len(nb) != 10 or ra[4] != rb[4]:
            return refused
        if a[0][3] != b[0][3]:  # Entire encoded base, including all security/session inputs.
            return refused
        if [f[4] for f in a] != [f[4] for f in b] or ae[0][4] != be[0][4]:
            return refused
        if [(f[0], f[1], f[4]) for f in sa] != [(f[0], f[1], f[4]) for f in sb]:
            return refused
        if any(x[3] != y[3] for x, y in zip(sa, sb) if x[0] != 14):
            return refused
        return 'MATCH_EXCEPT_ROUTE'
    except (ValueError, FrameError, IndexError, TypeError, StopIteration, OverflowError):
        return refused

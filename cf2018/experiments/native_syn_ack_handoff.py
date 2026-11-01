"""Original SYN preparation -> ACK parse -> suppressed auth-send controls.

Only synthetic names/ACK bytes. No sockets, crypto success, real identifiers,
native auth construction or game execution. Source fingerprinted by runner.
"""
from native_control import NativeControl, CTX, BUF


def _vi(v):
    out = bytearray()
    while v >= 128:
        out.append((v & 127) | 128)
        v >>= 7
    return bytes(out) + bytes([v])


def _field(n, kind, value):
    tag = _vi(n << 4 | kind)
    if kind == 0:
        return tag + _vi(value)
    if kind == 1:
        return tag + bytes([value])
    return tag + len(value).to_bytes(4, 'big') + value


def synthetic_ack(*, magic=0x4366, key_mode=0):
    # Fixture, not a production/server response builder. Unsupported scalar
    # key-mode control omits its union to keep that negative mode effective.
    base = b''.join(_field(i, 1 if i == 6 else 0, value)
                    for i, value in enumerate([magic, 0, 1, 0x1002, 0, 0, 1, 0, 0], 1))
    ack = _field(1, 1, 0) + _field(2, 1, key_mode)
    if key_mode == 0:
        ack += _field(3, 5, b'\x01\x00')
    ack += _field(4, 1, 0) + _field(5, 0, 1024) + _field(6, 0, 0)
    h = _field(1, 5, base) + _field(2, 5, _field(0x1002, 5, ack))
    return b'\xaa' + (5 + len(h)).to_bytes(4, 'big') + h


def probe(library, *, name_size=10, variant='valid', relay=False):
    if (type(relay) is not bool or name_size not in (10, 12)
            or variant not in ('valid', 'wrong_magic', 'bad_key', 'prefixed', 'truncated')):
        raise ValueError('bounded synthetic case required')
    n = NativeControl(library)
    name = b'S' * name_size
    n.write(CTX + 4, 42)
    n.write(CTX + 0x3400, 4)
    n.write(CTX + 0x6cc, int(relay))
    n.uc.mem_write(CTX + 0x3408, name + b'\0')

    def strncpy(dest, source, count, unused):
        if count != 127:
            raise ValueError('unexpected native name-copy bound')
        data = bytes(n.uc.mem_read(source, count)).split(b'\0', 1)[0]
        n.uc.mem_write(dest, data + bytes(count - len(data)))
        return dest

    sent = n.execute(0x3aba5c, (CTX, 0), {
        0x193e48: ('bounded synthetic strncpy', strncpy),
        0x3ab430: ('outgoing pack/encrypt/send suppressed', 0)})
    if sent != 0:
        raise ValueError('SYN preparation failed')
    route_prepared = n.read(CTX + 0x2de1, 1) == 4
    name_prepared = bytes(n.uc.mem_read(CTX + 0x2de8, name_size + 1)) == name + b'\0'
    # Transfer actual prepared handle to a fresh runner at the same addresses,
    # avoiding accumulated instrumentation hooks. This is not an OS connection.
    prepared = bytes(n.uc.mem_read(CTX, 0x40000))
    rx = NativeControl(library)
    rx.uc.mem_write(CTX, prepared)
    wire = synthetic_ack(magic=0x3366 if variant == 'wrong_magic' else 0x4366,
                         key_mode=1 if variant == 'bad_key' else 0)
    if variant == 'prefixed':
        wire = b'\x43\x66' + wire
    if variant == 'truncated':
        wire = wire[:-1]
    rx.uc.mem_write(BUF, wire)
    rx.write(CTX + 0x70c, 65536)
    rx.write(CTX + 0x714, len(wire))
    code = rx.execute(0x3a9f8c, (CTX, 0), {
        0x284fcc: ('network no-new-data stub; no socket', -3),
        0x3ab964: ('auth send suppressed', -77)})
    return {'return': code, 'syn_prepared_named_route': route_prepared,
            'synthetic_name_copied': name_prepared, 'state': rx.read(CTX + 0x6c8),
            'auth_send_boundary': 'auth send suppressed' in rx.calls,
            'consumed': rx.read(CTX + 0x710), 'relay_requested': relay,
            'syn_stubs': n.calls, 'receive_stubs': rx.calls}

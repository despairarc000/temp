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


APPLICATION_FIELDS = {'none': None, 'game_id': (8, 1), 'unit_id': (0x10, 1),
                      'client_type': (0x114, 1), 'platform_101': (0x114, 101),
                      'platform_102': (0x114, 102)}


def _prepare_syn(library, name_size, relay, attribute):
    if attribute not in APPLICATION_FIELDS:
        raise ValueError('bounded synthetic application attribute required')
    n = NativeControl(library)
    name = b'S' * name_size
    n.write(CTX + 4, 42)
    n.write(CTX + 0x3400, 4)
    n.write(CTX + 0x6cc, int(relay))
    n.uc.mem_write(CTX + 0x3408, name + b'\0')
    if APPLICATION_FIELDS[attribute] is not None:
        offset, value = APPLICATION_FIELDS[attribute]
        n.write(CTX + offset, value)

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
    return n, name


def probe(library, *, name_size=10, variant='valid', relay=False, attribute='none'):
    if (type(relay) is not bool or name_size not in (10, 12)
            or variant not in ('valid', 'wrong_magic', 'bad_key', 'prefixed', 'truncated')):
        raise ValueError('bounded synthetic case required')
    n, name = _prepare_syn(library, name_size, relay, attribute)
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


def application_prefix(library, attribute='none'):
    """Original serializer fields1..7 on fixed synthetic data, then STOP.

    Returns only independently synthetic encoded fields to regression tests.
    No actual account/token values or full packets are accepted as input.
    """
    from native_control import AUX, OUT, STOP
    from second_service_syn_gate import _records
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_PC
    n, _ = _prepare_syn(library, 10, False, attribute)
    w = NativeControl(library)
    w.uc.mem_write(CTX, bytes(n.uc.mem_read(CTX, 0x40000)))
    w.write(AUX, OUT); w.write(AUX+4, 0); w.write(AUX+8, 4096)
    stopped = []
    def boundary(u, address, size, unused):
        if address == 0x3b293e:
            stopped.append(True)
            u.reg_write(UC_ARM_REG_R0, 0)
            u.reg_write(UC_ARM_REG_PC, STOP | 1)
    w.uc.hook_add(UC_HOOK_CODE, boundary)
    rc = w.execute(0x3b2826, (CTX+0x2340, AUX))
    if rc != 0 or not stopped:
        raise ValueError('original serializer prefix failed')
    data = bytes(w.uc.mem_read(OUT, w.read(AUX+4)))
    return {f[0]: f[3] for f in _records(data)}

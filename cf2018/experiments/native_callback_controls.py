"""Pinned native callback controls, with injected runtime/list/RTTI boundaries.

No protocol message, valid identity, socket, thread or UI callback is generated.
"""
from native_control import NativeControl, CTX, OUT, AUX, STOP

CLIENT, CONNECTOR, SERVICE = AUX+0x4000, AUX+0x5000, AUX+0x6000
LIST, BUFFER = AUX+0x7000, AUX+0x7100


def callback_probe(library, *, stage='transport', observer=True, result=0,
                   connector=True, cast=True, buffer_cast=True, state=5,
                   execute_bind=False):
    if stage not in ('transport', 'dispatch'):
        raise ValueError('bounded stage required')
    if any(type(v) is not bool for v in (observer, connector, cast, buffer_cast, execute_bind)):
        raise ValueError('boolean controls required')
    if result not in (0, 9) or state not in (4, 5):
        raise ValueError('unsupported status/state control')
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                                  UC_ARM_REG_R3, UC_ARM_REG_PC)
    n = NativeControl(library)
    # Existing library data/GOT and vtable bytes are read, never synthesized.
    targets = {'gcp_observer': n.read(0x4f5b60+0xf8+8),
               'connection_result': n.read(0x4f5b60+12+0x8c),
               'service_observer': n.read(0x4f4a60+8+8)}
    if targets != {'gcp_observer': 0x3c6379,
                   'connection_result': 0x3c59fb,
                   'service_observer': 0x39ca79}:
        raise ValueError('pinned vtable relationship differs')
    n.write(CONNECTOR, 0x4f5b60+12)
    n.write(CONNECTOR+0x18, 0x4f5b60+0xf8)
    n.write(SERVICE, 0x4f4a60+8)
    n.write(BUFFER, 0x4f5778+8)
    n.write(0x506a74+4, 5)  # synthetic logger level: skip formatting only
    n.write(CTX+4, 42)
    n.write(CTX+0x6c8, state)
    n.write(CTX+0x230c, 64)
    n.write(CTX+0x70c, 65536)
    n.write(CLIENT+0x58, CTX)
    n.write(CONNECTOR+0x198, CLIENT if connector else 0)
    events, scheduled = [], []
    reached_bind = False
    def observe(u, address, size, unused):
        nonlocal reached_bind
        if address in (0x3c6378, 0x3c6300, 0x3c59fa, 0x3c67ac,
                       0x39ca78, 0x39cad6, 0x39cae4, 0x3c1498):
            events.append(['native_site', address])
        if address == 0x39ca78:
            events.append(['service_result', n.read(u.reg_read(UC_ARM_REG_R1)+12)])
            events.append(['connected_info_pointer_matches',
                           u.reg_read(UC_ARM_REG_R2) == CONNECTOR+0x78])
        if address == 0x3c18ec:
            reached_bind = True
            events.append(['MSG_BUFFER_BIND' if execute_bind else 'STOP_BEFORE_MSG_BUFFER_BIND', address])
            if not execute_bind:
                u.reg_write(UC_ARM_REG_R0, (-77) & 0xffffffff)
                u.reg_write(UC_ARM_REG_PC, STOP | 1)
        if len(events) > 64:
            raise RuntimeError('callback trace limit')
    n.uc.hook_add(UC_HOOK_CODE, observe)
    def empty_string(dest, *unused):
        n.uc.mem_write(dest, bytes(36))
        return dest
    def assign_string(dest, source, *unused):
        n.uc.mem_write(dest, bytes(n.uc.mem_read(source, 36)))
        return dest
    def clock(*unused):
        n.uc.reg_write(UC_ARM_REG_R1, 0)
        return 0
    def schedule(obj, method, adjust, argument):
        scheduled.append({'object_matches': obj == CONNECTOR,
                          'method': method, 'adjust': adjust,
                          'argument': argument})
        return 0
    def copy_list(dest, source, *unused):
        n.write(dest, LIST)
        n.write(dest+4, LIST+(4 if observer else 0))
        n.write(dest+8, LIST+(4 if observer else 0))
        return dest
    def get_buffer(dest, *unused):
        n.write(dest, BUFFER)
        n.write(dest+4, 0)
        return dest
    def dynamic_cast(obj, *unused):
        return obj if (buffer_cast if obj == BUFFER else cast) else 0
    def allocate(count, *unused):
        if count != 16:
            raise ValueError('unexpected native allocation size')
        return AUX+0x7400
    stubs = {
        0x3971f0: ('AString empty storage substitute; no allocator', empty_string),
        0x39738c: ('AString assignment storage substitute', assign_string),
        0x3974c0: ('AString destructor suppressed', 0),
        0x394a3e: ('clock zero64', clock),
        0x394a78: ('tick clock zero64', clock),
        0x381cda: ('UI scheduling CAPTURE ONLY; no thread/callback', schedule),
        0x284fcc: ('net wrapper no data -3; no socket', -3),
        0x37e958: ('timer reset suppressed', 0),
        0x1a4c04: ('single-thread lock suppressed', 0),
        0x1a4c16: ('single-thread unlock suppressed', 0),
        0x3a51f4: ('OnDataOutEvent suppressed; no send', 0),
        0x397b50: ('observer vector copy injected <=1 element', copy_list),
        0x397ba4: ('injected observer vector destructor suppressed', 0),
        0x3c9b48: ('RTTI dynamic_cast supplied result, NOT runtime binding proof',
                     dynamic_cast),
        0x3c93fc: ('allocator supplied isolated 16-byte function object', allocate),
        0x33e286: ('shared-count destructor suppressed', 0),
        STOP+0x200: ('GetBuffer virtual boundary supplied synthetic buffer', get_buffer),
    }
    if stage == 'transport':
        n.write(LIST, CONNECTOR+0x18)
        n.write(CLIENT+0x5c, LIST)
        n.write(CLIENT+0x60, LIST+(4 if observer else 0))
        code = n.execute(0x3a57d0, (CLIENT, OUT+0x100), stubs)
    else:
        n.write(LIST, SERVICE)
        n.write(SERVICE+0x28, AUX+0x7200 if connector else 0)
        n.write(SERVICE+0x24, CONNECTOR+0x14 if connector else 0)
        n.write(AUX+0x7200, AUX+0x7300)
        n.write(AUX+0x7300+0xb4, (STOP+0x200)|1)
        code = n.execute(0x3c67ac, (CONNECTOR, result), stubs)
    return {'return': code, 'targets': targets, 'events': events,
            'scheduled': scheduled, 'reached_bind_boundary': reached_bind,
            'service_error_flag': n.read(SERVICE+0x60, 1),
            'client_connected': n.read(CLIENT+0x1b2, 1),
            'buffer_manager_nonzero': bool(n.read(BUFFER+0x4c)),
            'bound_connector_matches': n.read(AUX+0x7400+12) == CONNECTOR+0x14,
            'connected_info_prefix_unchanged_zero':
                bytes(n.uc.mem_read(CONNECTOR+0x78, 0xf4)) == bytes(0xf4),
            'stubs': n.calls,
            'evidence': 'INJECTED_CONTEXT_NATIVE_CALLBACK_NOT_AUTHENTICATION'}

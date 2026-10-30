"""Optional hash-pinned native v1.2 auth-response trace, with explicit stubs.

Actual frame/base/extension/receive/body/account/state/Bingo instructions execute.
Only preloaded independently synthetic bytes are accepted by the test workflow.
There is no network, credential construction, serializer or Android-runtime claim.
"""
import hashlib
from native_control import NativeControl, CTX, BUF, OUT, AUX

STAGES = {
    0x3a9ff6: 'auth_state', 0x3ac306: 'auth_receive',
    0x3abe34: 'receive_decrypt', 0x3ab5ec: 'gather',
    0x3aab44: 'header_helper', 0x3b7340: 'header_unpack',
    0x3b719c: 'header_varint', 0x3af4cc: 'base_varint',
    0x3b6a3c: 'extension', 0x3b8860: 'body_unpack',
    0x3b8488: 'body_union', 0x3b39c0: 'auth_component',
    0x3ad100: 'account_component', 0x3ac39e: 'bingo_receive',
}
BODY = CTX + 0x1288


def _signed(value):
    return value if value < 0x80000000 else value - 0x100000000


class _Trace:
    def __init__(self, native):
        from unicorn import UC_HOOK_CODE
        from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1,
            UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_LR, UC_ARM_REG_SP)
        self.events, self.pending, self.predicates = [], [], []
        n = native
        def observe(u, address, size, unused):
            for call in list(self.pending):
                if call['return_address'] == address:
                    record = {'stage': call['stage'], 'event': 'return',
                              'code': _signed(u.reg_read(UC_ARM_REG_R0))}
                    if call.get('readbuf') is not None:
                        record['consumed'] = n.read(call['readbuf'] + 4) - call['start']
                    self.events.append(record)
                    self.pending.remove(call)
            if address in STAGES:
                stage = STAGES[address]
                call = {'stage': stage, 'return_address': u.reg_read(UC_ARM_REG_LR) & ~1}
                record = {'stage': stage, 'event': 'enter', 'address': address}
                if stage in ('body_union', 'auth_component', 'account_component'):
                    readbuf = u.reg_read(UC_ARM_REG_R2 if stage == 'body_union' else UC_ARM_REG_R1)
                    call.update(readbuf=readbuf, start=n.read(readbuf+4))
                    record['declared'] = u.reg_read(UC_ARM_REG_R3 if stage == 'body_union' else UC_ARM_REG_R2)
                if stage == 'body_unpack':
                    record['input_length'] = u.reg_read(UC_ARM_REG_R3)
                self.events.append(record)
                self.pending.append(call)
            if address == 0x3b724a:
                self.predicates.append({'address': address, 'extension_selector': n.read(u.reg_read(UC_ARM_REG_SP)+8)})
            if address == 0x3b88d8:
                self.predicates.append({'address': address, 'condition': 'TGCPBody mode is neither AA nor 99',
                    'observed_byte': n.read(u.reg_read(UC_ARM_REG_SP)+7, 1), 'return': -32})
            if address == 0x3b88dc:
                self.predicates.append({'address': address, 'body_cursor': n.read(u.reg_read(UC_ARM_REG_SP)+0x10)})
            if len(self.events) > 512:
                raise RuntimeError('trace event budget exceeded')
        n.uc.hook_add(UC_HOOK_CODE, observe)


def trace_wire(library, wire, *, state_handler=True, encryption_method=0, network_result=-3):
    """Real native parse from preloaded wire; no parser/gather/Bingo success stub.

    network_result=-3 is a wrapper-level no-new-data result; -4 is an explicit
    EOF-like wrapper-status control, not an observation of a real peer.
    """
    if not isinstance(wire, bytes) or not 1 <= len(wire) <= 512:
        raise ValueError('synthetic wire must contain 1..512 bytes')
    if type(state_handler) is not bool or encryption_method not in (0, 4) or network_result not in (-3, -4):
        raise ValueError('unsupported bounded control configuration')
    n = NativeControl(library)
    for off, value in [(4, 42), (0x70c, 65536), (0x714, len(wire)),
                       (0x6c8, 3), (0x11c, encryption_method)]:
        n.write(CTX+off, value)
    n.uc.mem_write(BUF, wire)
    n.uc.mem_write(CTX+0x138, b'R' * 0x114)
    trace = _Trace(n)
    code = n.execute(0x3a9ff6 if state_handler else 0x3ac306, (CTX, 0), {
        0x284fcc: ('net_recv wrapper supplied-status stub; no socket', network_result)})
    account = bytes(n.uc.mem_read(CTX+0x138, 0x114))
    return {'return': code, 'state': n.read(CTX+0x6c8),
        'decoded_marker': n.read(CTX+0x720, 2), 'effective_type': n.read(CTX+0x726, 2),
        'header_length': n.read(CTX+0x734), 'body_length': n.read(CTX+0x738),
        'cursor': n.read(CTX+0x710), 'buffered': n.read(CTX+0x714),
        'diagnostic_type': n.read(CTX+0x33e4),
        'account_unchanged': account == b'R' * 0x114,
        'account_zero': account == bytes(0x114),
        'synthetic_uid_zero': n.read(CTX+0x138+0x108, 8) == 0,
        'account_sha256': hashlib.sha256(account).hexdigest(),
        'events': trace.events, 'predicates': trace.predicates, 'stubs': n.calls,
        'context': 'fresh synthetic initialized state 3, method 0 or 4, no key; not a phone snapshot'}


def trace_component(library, payload, *, component):
    """Isolated real component decoding, explicitly outside full-path reachability."""
    if not isinstance(payload, bytes) or len(payload) > 512 or component not in ('auth', 'account'):
        raise ValueError('unsupported bounded synthetic component')
    n = NativeControl(library)
    if payload:
        n.uc.mem_write(BUF, payload)
    for off, value in [(0, BUF), (4, 0), (8, len(payload))]:
        n.write(AUX+off, value)
    trace = _Trace(n)
    entry = 0x3b39c0 if component == 'auth' else 0x3ad100
    code = n.execute(entry, (BODY, AUX, len(payload)))
    return {'return': code, 'consumed': n.read(AUX+4), 'events': trace.events,
            'stubs': n.calls, 'isolated_component_only': True}

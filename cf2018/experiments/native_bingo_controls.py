"""Bounded hash-specific Bingo/session controls; never a valid server reply.

Wire controls deliberately mismatch header and auth-body types. Isolated decoded
branch controls explicitly substitute receive/parser outcomes. No game networking,
credential generation or implicit execution. Original new host code only.
"""
from native_control import NativeControl, CTX, BUF, OUT, AUX

STAGES = {0x3aa046: 'ready', 0x3ac39e: 'bingo_receive',
          0x3abe34: 'receive_decrypt', 0x3ab5ec: 'gather',
          0x3b8860: 'body', 0x3b8488: 'body_union',
          0x3b39c0: 'auth_component', 0x3b76a6: 'bingo_component',
          0x3b0dd2: 'relay_component', 0x3b4e20: 'wait_component'}


class _Observe:
    def __init__(self, n):
        from unicorn import UC_HOOK_CODE
        from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_LR, UC_ARM_REG_SP
        self.events, self.pending, self.selectors = [], [], []
        def observe(u, address, size, unused):
            for stage, target in list(self.pending):
                if target == address:
                    value = u.reg_read(UC_ARM_REG_R0)
                    self.events.append((stage, value if value < 0x80000000 else value-0x100000000))
                    self.pending.remove((stage, target))
            if address in STAGES:
                self.pending.append((STAGES[address], u.reg_read(UC_ARM_REG_LR) & ~1))
            if address == 0x3ac41c:
                self.selectors.append(n.read(u.reg_read(UC_ARM_REG_SP)+0x10))
            if len(self.events) > 128 or len(self.pending) > 32:
                raise RuntimeError('trace event budget exceeded')
        n.uc.hook_add(UC_HOOK_CODE, observe)


def _context(library, state=4):
    n = NativeControl(library)
    for offset, value in [(4, 42), (0x6c8, state), (0x70c, 65536),
                          (0x33f4, 7), (0x33f8, 99)]:
        n.write(CTX+offset, value)
    n.uc.mem_write(CTX+0x6d8, b'S'*44)
    return n


def _result(n, trace, code):
    return {'return': code, 'state': n.read(CTX+0x6c8),
            'header_type': n.read(CTX+0x726, 2),
            'post_body_selectors': trace.selectors, 'events': trace.events,
            'relay_unchanged': bytes(n.uc.mem_read(CTX+0x6d8, 44)) == b'S'*44,
            'relay_matches_decoded_prefix': bytes(n.uc.mem_read(CTX+0x6d8, 44)) == bytes(n.uc.mem_read(CTX+0x1288, 44)),
            'compression': [n.read(CTX+0x33f4), n.read(CTX+0x33f8)],
            'queue': [n.read(CTX+offset) for offset in (0x33b4, 0x33b8, 0x33bc, 0x33c0)],
            'diagnostic_type': n.read(CTX+0x33e4), 'stubs': n.calls}


def mismatched_auth_wire(header_type=0x6002):
    """Only a negative fixture: Bingo/WAIT header with AUTH body union 0x2002.

    No 0x6002 Bingo component or real account/session is encoded. This diagnoses
    type correlation; numeric state5 must never be called authenticated.
    """
    if header_type not in (0x3002, 0x6002):
        raise ValueError('only reviewed mismatched header controls')
    # Pinned public packet dependencies, not unpublished canonical auth drafts.
    from auth_v12_fixtures import varuint
    from auth_fixture_repair import corrected_v12_fixture
    wire = corrected_v12_fixture('V12_BODY_EMPTY')
    old, new = varuint((0x2002 << 4) | 1), varuint((header_type << 4) | 1)
    header = wire[:42]
    if header.count(old) != 1 or len(old) != len(new):
        raise ValueError('historical synthetic header layout drift')
    return header.replace(old, new) + wire[42:]


def wire_probe(library, wire=b'', *, ready=False, network_result=-3,
               state=4, initialized=True, descriptor=42):
    if not isinstance(wire, bytes) or len(wire) > 512:
        raise ValueError('independent synthetic input capped at 512 bytes')
    if type(ready) is not bool or network_result not in (-3, -4):
        raise ValueError('unsupported bounded control configuration')
    if state not in (3, 4) or type(initialized) is not bool or descriptor not in (-1, 42):
        raise ValueError('unsupported state/initialization/descriptor control')
    n = _context(library, state)
    n.write(CTX+0x124, int(initialized))
    n.write(CTX+4, descriptor & 0xffffffff)
    if wire:
        n.uc.mem_write(BUF, wire)
    n.write(CTX+0x714, len(wire))
    trace = _Observe(n)
    code = n.execute(0x3aa046 if ready else 0x3ac39e, (CTX, 0), {
        0x284fcc: ('net wrapper supplied no-data/EOF-like status; no socket', network_result)})
    r = _result(n, trace, code)
    r['evidence'] = 'REAL_NATIVE_PARSE_OF_INDEPENDENT_SYNTHETIC_NEGATIVE_INPUT'
    return r


def decoded_probe(library, *, header_type=0x6002, receive_result=0,
                  parser_result=None, decoded_selector=None, state=4):
    """Isolated branch test; receive and optional parser outcomes are STUBS.

    parser_result=None runs real body decode on malformed FC. Zero injects only
    independent decoded storage. This cannot demonstrate wire/session acceptance.
    """
    if header_type not in (0x2002, 0x3002, 0x6002):
        raise ValueError('unsupported header control')
    if receive_result not in (0, -12, -10, -31) or parser_result not in (None, 0, -32):
        raise ValueError('unsupported receive/parser branch control')
    if decoded_selector not in (None, 0x3002, 0x6002, 0x2002) or state not in (3, 4):
        raise ValueError('unsupported selector/state control')
    n = _context(library, state)
    n.write(CTX+0x726, header_type, 2)
    n.uc.mem_write(OUT, b'\xfc')
    trace = _Observe(n)
    def receive(handle, length_pointer, timeout, unused):
        if receive_result == 0:
            n.write(length_pointer, 1)
        return receive_result
    stubs = {0x3abe34: ('DECODED RECEIVE STUB; no wire parsing', receive)}
    if parser_result is not None:
        def parse(obj, selector_pointer, source, length):
            if parser_result == 0:
                n.uc.mem_write(obj, b'P'*44)
                for off, value in [(0, 17), (4, 34), (8, 51), (0x34, 4096)]:
                    n.write(obj+off, value)
                n.write(obj+0x30, 3, 1)
                if decoded_selector is not None:
                    n.write(selector_pointer, decoded_selector)
                    n.write(selector_pointer+4, 0)
            return parser_result
        stubs[0x3b8860] = ('BODY PARSER RESULT/STORAGE STUB; not protocol acceptance', parse)
    code = n.execute(0x3ac39e, (CTX, 0), stubs)
    r = _result(n, trace, code)
    r['evidence'] = 'DECODED_BOUNDARY_WITH_EXPLICIT_RECEIVE_AND_OPTIONAL_PARSER_STUBS'
    return r


def component_probe(library, payload, *, component, declared=None):
    """Actual isolated component decoder, no whole-frame/session interpretation."""
    if not isinstance(payload, bytes) or len(payload) > 512 or component not in ('bingo', 'relay'):
        raise ValueError('unsupported bounded component input')
    if declared is None:
        declared = len(payload)
    if type(declared) is not int or not 0 <= declared <= 512:
        raise ValueError('component declared bound invalid')
    n = NativeControl(library)
    if payload:
        n.uc.mem_write(BUF, payload)
    n.uc.mem_write(OUT, b'R'*64)
    for off, value in [(0, BUF), (4, 0), (8, len(payload))]:
        n.write(AUX+off, value)
    code = n.execute(0x3b76a6 if component == 'bingo' else 0x3b0dd2, (OUT, AUX, declared))
    return {'return': code, 'consumed': n.read(AUX+4),
            'relay_payload_unchanged': bytes(n.uc.mem_read(OUT, 40)) == b'R'*40,
            'presence': n.read(OUT+(0x38 if component == 'bingo' else 0x28)),
            'compression': [n.read(OUT+0x30, 1), n.read(OUT+0x34)],
            'position': n.read(OUT), 'stubs': n.calls,
            'evidence': 'ISOLATED_REAL_COMPONENT_DECODE_NOT_PHONE_AUTH'}


def relay_reuse_prefix(library):
    """Execute only the existing SYN relay-copy prefix; stop before any send.

    Surrounding registers and the chosen branch are synthetic. This establishes
    byte flow, not a server's policy for generating valid relay/session fields.
    """
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R5, UC_ARM_REG_PC
    from native_control import STOP
    n = NativeControl(library)
    n.uc.mem_write(CTX+0x6d8, b'M'*44)
    n.uc.reg_write(UC_ARM_REG_R5, CTX)
    stopped = False
    def hook(u, address, size, unused):
        nonlocal stopped
        if address == 0x3abc20:
            stopped = True
            u.reg_write(UC_ARM_REG_R0, (-77) & 0xffffffff)
            u.reg_write(UC_ARM_REG_PC, STOP | 1)
    n.uc.hook_add(UC_HOOK_CODE, hook)
    code = n.execute(0x3abc0a, (0, 0, CTX+0x2880))
    return {'stop_code': code, 'stopped_before_send': stopped,
            'copied_44_bytes': bytes(n.uc.mem_read(CTX+0x2888, 44)) == b'M'*44,
            'stubs': n.calls, 'synthetic_branch_entry': True}

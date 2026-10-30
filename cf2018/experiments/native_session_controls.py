"""Hash-pinned decoded-state/body-component controls; no ACK/auth serializer.

Uses the canonical explicit bounded native runner. No network or crypto success.
The token-construction prefix control stops before any account/token/hash work.
"""
import hashlib
from native_control import NativeControl, CTX, BUF, OUT, AUX, STOP

BODY = CTX + 0x1288


def _trace_body(n):
    from unicorn import UC_HOOK_CODE
    addresses = {0x3b49a6, 0x3b4a2c, 0x3b4a32, 0x3b39c0, 0x3ac306,
                 0x3ac32e, 0x3ac354, 0x3ac37e, 0x3ac390, 0x3aa024,
                 0x3ab808, 0x3ab80c}
    def observe(u, address, size, unused):
        if address in addresses:
            n.branches.append(address)
    n.uc.hook_add(UC_HOOK_CODE, observe)


def _component(n, fragment, declared):
    if not isinstance(fragment, bytes) or len(fragment) > 512:
        raise ValueError('synthetic component capped at 512 bytes')
    if type(declared) is not int or not 0 <= declared <= 512:
        raise ValueError('declared component outside bound')
    if fragment:
        n.uc.mem_write(BUF, fragment)
    for offset, value in [(0, BUF), (4, 0), (8, len(fragment))]:
        n.write(AUX + offset, value)


def ack_body_probe(library, fragment, *, initial_presence=0, declared_length=None):
    """Actual TGCPAckBody component decoder; no envelope/ACK wire message."""
    if declared_length is None:
        declared_length = len(fragment)
    n = NativeControl(library)
    _trace_body(n)
    _component(n, fragment, declared_length)
    n.write(BODY, initial_presence, 1)
    code = n.execute(0x3b49a6, (BODY, AUX, declared_length))
    return {'return': code, 'consumed': n.read(AUX+4),
            'presence': n.read(BODY, 1),
            'embedded_account_prefix_sha256': hashlib.sha256(bytes(n.uc.mem_read(BODY+8, 0x114))).hexdigest(),
            'calls': n.calls, 'branches': n.branches}


def ack_presence_state_probe(library, presence):
    """Actual ACK/state caller on injected presence; recv decoded boundary stub."""
    n = NativeControl(library)
    _trace_body(n)
    n.write(BODY, presence, 1)
    n.write(CTX + 0x726, 0x1002, 2)
    n.uc.mem_write(CTX+0x138, b'R' * 0x114)

    def receive(context, length_ptr, timeout, unused):
        n.write(length_ptr, 0)
        return 0
    code = n.execute(0x3a9f8c, (CTX,), {
        0x3abe34: ('recv/decrypt decoded-boundary stub; empty stage', receive),
        0x3ab964: ('auth send suppressed', -77)})
    return {'return': code, 'presence': n.read(BODY, 1),
            'state': n.read(CTX+0x6c8),
            'account_unchanged': bytes(n.uc.mem_read(CTX+0x138, 0x114)) == b'R' * 0x114,
            'calls': n.calls, 'branches': n.branches}


def auth_response_probe(library, *, header_type=0x2002, receive_result=0,
                        body=b'', parser_result=None, state_handler=False,
                        bingo_result=-12):
    """Actual auth caller/state logic; an explicit parser stub isolates copying.

    parser_result=None uses the actual body decoder. A supplied result is always
    labeled a stub; zero tests control flow only, never authenticated acceptance.
    """
    if not isinstance(body, bytes) or len(body) > 256:
        raise ValueError('synthetic body capped at 256 bytes')
    n = NativeControl(library)
    _trace_body(n)
    n.write(CTX + 0x726, header_type, 2)
    n.write(CTX + 0x6c8, 3)
    n.uc.mem_write(CTX+0x138, b'R' * 0x114)
    n.uc.mem_write(BODY, b'Q' * 0x114)
    if body:
        n.uc.mem_write(OUT, body)

    def receive(context, length_ptr, timeout, unused):
        n.write(length_ptr, len(body))
        return receive_result
    stubs = {0x3abe34: ('recv/decrypt decoded-boundary stub', receive),
             0x3ac39e: ('bingo receive suppressed', bingo_result)}
    if parser_result is not None:
        stubs[0x3b8860] = ('body parser supplied-result stub', parser_result)
    code = n.execute(0x3a9ff6 if state_handler else 0x3ac306, (CTX, 0), stubs)
    copied = bytes(n.uc.mem_read(CTX+0x138, 0x114))
    return {'return': code, 'state': n.read(CTX+0x6c8),
            'diagnostic_type': n.read(CTX+0x33e4),
            'account_copy_matches_synthetic_source': copied == b'Q' * 0x114,
            'account_unchanged': copied == b'R' * 0x114,
            'calls': n.calls, 'branches': n.branches}


def timestamp_prefix_probe(library, timestamp):
    """Run auth-request prefix, then stop before C++ account/token construction."""
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_PC
    n = NativeControl(library)
    _trace_body(n)
    n.write(CTX + 0x3490, timestamp)
    stopped = False

    def boundary(u, address, size, unused):
        nonlocal stopped
        if address == 0x3dde18:
            stopped = True
            u.reg_write(UC_ARM_REG_R0, (-77) & 0xffffffff)
            u.reg_write(UC_ARM_REG_PC, STOP | 1)
    n.uc.hook_add(UC_HOOK_CODE, boundary)
    code = n.execute(0x3ab7e8, (CTX, AUX))
    if not stopped:
        raise RuntimeError('expected pre-token construction boundary not reached')
    return {'stop_code': code, 'outgoing_timestamp': n.read(AUX+0x50c),
            'stopped_before_account_token_hash': stopped,
            'calls': n.calls, 'branches': n.branches}

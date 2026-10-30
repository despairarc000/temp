"""Bounded, optional native ACK controls; no server ACK serializer or networking.

Runs selected original functions from one externally supplied, hash-pinned ELF.
Decoded inputs and component TLV fragments are independently synthetic. Stubbed
boundaries isolate predicates, never demonstrate full receiver/phone acceptance.
"""
import hashlib
from pathlib import Path

LIBRARY_SHA256 = '4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'
CTX, BUF, OUT, AUX, STACK, STOP = (0x1000000, 0x1010000, 0x1020000,
                                  0x1030000, 0x1100000, 0x1200000)


class NativeControl:
    """Private-source runner. Every execution uses a fresh zeroed address space."""
    def __init__(self, library):
        library = Path(library)
        if library.stat().st_size != 5243704:
            raise ValueError('unexpected library size')
        if hashlib.sha256(library.read_bytes()).hexdigest() != LIBRARY_SHA256:
            raise ValueError('unexpected library fingerprint')
        from elftools.elf.elffile import ELFFile
        from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        self.uc.mem_map(0, 0x800000)
        with library.open('rb') as f:
            elf = ELFFile(f)
            if elf.elfclass != 32 or not elf.little_endian or elf['e_machine'] != 'EM_ARM':
                raise ValueError('unexpected ELF ISA')
            for segment in elf.iter_segments():
                if segment['p_type'] == 'PT_LOAD':
                    self.uc.mem_write(segment['p_vaddr'], segment.data())
        for address, size in [(CTX, 0x40000), (STACK, 0x10000), (STOP, 0x1000)]:
            self.uc.mem_map(address, size)
        self.calls, self.branches = [], []
        self.write(CTX + 0x1280, OUT)
        self.write(CTX + 0x1284, 256)
        self.write(CTX + 0x708, BUF)
        self.write(CTX + 0x124, 1)
        self.write(CTX + 0x6c8, 2)

    def write(self, address, value, size=4):
        if not isinstance(value, int) or not 0 <= value < 1 << (8 * size):
            raise ValueError('unsigned integer outside field width')
        self.uc.mem_write(address, value.to_bytes(size, 'little'))

    def read(self, address, size=4):
        return int.from_bytes(self.uc.mem_read(address, size), 'little')

    def execute(self, entry, registers, stubs=None):
        from unicorn import UC_HOOK_CODE
        from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
            UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC)
        regs = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)
        stubs = dict(stubs or {})
        for reg, value in zip(regs, registers):
            self.uc.reg_write(reg, value & 0xffffffff)
        self.uc.reg_write(UC_ARM_REG_SP, STACK + 0xf000)
        self.uc.reg_write(UC_ARM_REG_LR, STOP | 1)
        done = False
        branch_points = {0x3abe58, 0x3abeb2, 0x3abec4, 0x3abeca, 0x3abeea,
            0x3abefc, 0x3abf08, 0x3abf4e, 0x3abf74, 0x3abfde, 0x3ac032,
            0x3ac06c, 0x3ac100, 0x3ac11e, 0x3ac126, 0x3ac16e, 0x3ac1a4,
            0x3a9fca, 0x3a9fd6, 0x3ab24a, 0x3ab31e, 0x3b5bd2, 0x3b5bda}

        def hook(u, address, size, unused):
            nonlocal done
            if address == STOP:
                done = True
                u.emu_stop()
                return
            if address in branch_points:
                self.branches.append(address)
            args = [u.reg_read(r) for r in regs]
            if address in stubs:
                name, action = stubs[address]
                self.calls.append(name)
                value = action(*args) if callable(action) else action
                u.reg_write(UC_ARM_REG_R0, value & 0xffffffff)
            elif address in (0x193e60, 0x193ed8, 0x193e6c):
                dest, source, count = args[:3]
                if count > 65536:
                    raise ValueError('libc stub budget exceeded')
                data = (bytes([source & 255]) * count if address == 0x193e60
                        else bytes(u.mem_read(source, count)))
                if data:
                    u.mem_write(dest, data)
                self.calls.append('bounded libc memory operation')
                u.reg_write(UC_ARM_REG_R0, dest)
            elif address in (0x393e80, 0x1b3b1c, 0x1b3b26, 0x1c6544):
                self.calls.append({0x393e80: 'XLog no-op', 0x1b3b1c: 'last-error get=0',
                    0x1b3b26: 'last-error set no-op', 0x1c6544: 'error-string only'}[address])
                u.reg_write(UC_ARM_REG_R0, STOP + 0x100 if address == 0x1c6544 else 0)
            else:
                return
            u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))

        self.uc.hook_add(UC_HOOK_CODE, hook)
        self.uc.emu_start(entry | 1, STOP + 2, timeout=1000000, count=100000)
        if not done:
            raise RuntimeError('native instruction/time budget reached')
        code = self.uc.reg_read(UC_ARM_REG_R0)
        return code if code < 0x80000000 else code - (1 << 32)

    def snapshot(self, code):
        return {'return': code, 'method': self.read(CTX + 0x11c),
            'key_mode': self.read(CTX + 0x120), 'key_length': self.read(CTX + 0x458, 1),
            'cursor': self.read(CTX + 0x710), 'buffered': self.read(CTX + 0x714),
            'pending': self.read(CTX + 0x718), 'saved_base_word': self.read(CTX + 0x3490),
            'diagnostic_type': self.read(CTX + 0x33e4),
            'ack_scalar4': self.read(CTX + 0x33f4),
            'ack_scalar5': self.read(CTX + 0x33f8),
            'special_error_flag': self.read(CTX + 0x33d4),
            'calls': self.calls, 'branches': self.branches}


def decoded_probe(library, *, message_type=0x1002, method=0, key_mode=0,
                  key_length=0, encrypted=0, body=b'', base_word=7,
                  splitter_result=0, compute_result=-40, through_ack=False):
    """Actual recv/decrypt, injected *decoded* splitter state. No framing claim.

    DH calculation is a failure-only stub; AES primitives are never stubbed to
    succeed. through_ack retains the actual ACK caller around recv/decrypt. These controls cover mode dispatch/failures and plaintext paths.
    """
    if not isinstance(body, bytes) or len(body) > 256:
        raise ValueError('synthetic body capped at 256 bytes')
    if not isinstance(compute_result, int) or compute_result >= 0:
        raise ValueError('DH stub must return a failure')
    n = NativeControl(library)
    for offset, value, width in [(0x726, message_type, 2), (0x728, base_word, 4),
        (0x72c, encrypted, 1), (0x740, method, 1), (0x741, key_mode, 1),
        (0x744, key_length, 1), (0x734, 32, 4), (0x738, len(body), 4),
        (0x714, 32 + len(body), 4), (0x718, 32 + len(body), 4)]:
        n.write(CTX + offset, value, width)
    n.uc.mem_write(CTX + 0x745, b'Z' * 255)  # independent synthetic key storage
    if body:
        n.uc.mem_write(BUF + 32, body)
    code = n.execute(0x3ac0b8 if through_ack else 0x3abe34,
                     (CTX, 0) if through_ack else (CTX, AUX, 0), {
        0x3ab5ec: ('splitter decoded-boundary stub', splitter_result),
        0x3abd7c: ('DH compute failure-only stub', compute_result)})
    result = n.snapshot(code)
    result['output_length'] = None if through_ack else n.read(AUX)
    result['output_matches_synthetic_body'] = bytes(n.uc.mem_read(OUT, len(body))) == body
    return result


def ack_probe(library, *, message_type=0x1002, body_length=0,
              receive_result=0, scalar4=1, scalar5=7,
              error_state=0, error_detail=0, state_handler=False, state=2,
              body_result=None):
    """Actual recv_ack (optionally actual state handler), stubbed recv/decrypt.

    Nonempty bodies run the real body parser on zero synthetic bytes unless an
    explicitly supplied body_result stub tests error propagation. Auth send is
    always stubbed and recorded; no socket is created.
    """
    if not isinstance(body_length, int) or not 0 <= body_length <= 256:
        raise ValueError('synthetic body length capped at 256')
    n = NativeControl(library)
    for offset, value, width in [(0x726, message_type, 2), (0xb4c, scalar4, 1),
        (0xb50, scalar5, 4), (0x33a8, error_state, 4), (0x33ac, error_detail, 4),
        (0x6c8, state, 4)]:
        n.write(CTX + offset, value, width)

    def receive(context, length_ptr, timeout, unused):
        n.write(length_ptr, body_length)
        return receive_result
    stubs = {0x3abe34: ('recv/decrypt decoded-boundary stub', receive),
             0x3ab964: ('auth send suppressed', -77)}
    if body_result is not None:
        stubs[0x3b8860] = ('body parser result stub', body_result)
    code = n.execute(0x3a9f8c if state_handler else 0x3ac0b8, (CTX, 0), stubs)
    return n.snapshot(code)


def ack_tlv_probe(library, fragment, *, declared_length=None):
    """Actual ACK component varint decoder; not a complete TGCP frame/ACK."""
    if not isinstance(fragment, bytes) or len(fragment) > 512:
        raise ValueError('synthetic TLV component capped at 512 bytes')
    if declared_length is None:
        declared_length = len(fragment)
    if not isinstance(declared_length, int) or not 0 <= declared_length <= 512:
        raise ValueError('declared component bound invalid')
    n = NativeControl(library)
    if fragment:
        n.uc.mem_write(BUF, fragment)
    for offset, value in [(0, BUF), (4, 0), (8, len(fragment))]:
        n.write(AUX + offset, value)
    code = n.execute(0x3b5ab6, (CTX, AUX, declared_length))
    return {'return': code, 'consumed': n.read(AUX + 4),
        'method': n.read(CTX, 1), 'key_mode': n.read(CTX + 1, 1),
        'scalar4': n.read(CTX + 0x40c, 1), 'scalar5': n.read(CTX + 0x410),
        'scalar6': n.read(CTX + 0x414),
        'calls': n.calls, 'branches': n.branches}

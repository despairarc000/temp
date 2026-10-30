"""Read-only, hash-pinned native loader branch controls. No patch/decryption tool.

Synthetic entry contexts, not an Android loader, account or game execution.
"""
import hashlib
from pathlib import Path

PINS = {
    'mono': (3889708, '025e971133d24a38ddb2493cf2adee8208555bb5967247fa889a6ad7b91dac91'),
    'tprt': (153676, 'f608b142822b888f4e5b44bbb0167e8d5c02e1680ea89bab8171aeaab59b4f0a'),
}
CTX, BUF, STACK, STOP = 0x1000000, 0x1004000, 0x1100000, 0x1200000


def guarded_bytes(path, kind):
    p = Path(path)
    size, digest = PINS[kind]
    if p.stat().st_size != size:
        raise ValueError('unexpected source size')
    data = p.read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError('unexpected source hash')
    return data


class TprtControl:
    def __init__(self, library):
        guarded_bytes(library, 'tprt')
        from elftools.elf.elffile import ELFFile
        from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
        self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        self.u.mem_map(0, 0x40000)
        with open(library, 'rb') as f:
            elf = ELFFile(f)
            if elf.elfclass != 32 or not elf.little_endian or elf['e_machine'] != 'EM_ARM':
                raise ValueError('unexpected source ISA')
            for s in elf.iter_segments():
                if s['p_type'] == 'PT_LOAD':
                    self.u.mem_write(s['p_vaddr'], s.data())
        for addr in (CTX, STACK, STOP):
            self.u.mem_map(addr, 0x10000)

    def write(self, addr, value):
        self.u.mem_write(addr, (value & 0xffffffff).to_bytes(4, 'little'))

    def read(self, addr):
        return int.from_bytes(self.u.mem_read(addr, 4), 'little')

    def execute(self, entry, registers, boundary):
        from unicorn import UC_HOOK_CODE
        from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
            UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6,
            UC_ARM_REG_R7, UC_ARM_REG_SP, UC_ARM_REG_LR)
        for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3), registers):
            self.u.reg_write(reg, value & 0xffffffff)
        self.u.reg_write(UC_ARM_REG_SP, STACK+0xf000)
        self.u.reg_write(UC_ARM_REG_LR, STOP|1)
        done = False
        def hook(u, address, size, unused):
            nonlocal done
            if address == STOP or boundary(u, address):
                done = True
                u.emu_stop()
        self.u.hook_add(UC_HOOK_CODE, hook)
        self.u.emu_start(entry|1, STOP+2, timeout=1000000, count=100000)
        if not done:
            raise RuntimeError('native instruction/time budget reached')
        return self.u.reg_read(UC_ARM_REG_R0)


def classify_branch(library, prefix, length):
    """Actual signature branch, stopped before any transform or Mono call."""
    if type(prefix) is not bytes or len(prefix) != 4:
        raise ValueError('independent four-byte prefix required')
    if type(length) is not int or not 4 <= length <= 16*1024*1024:
        raise ValueError('bounded declared length required')
    from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
        UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_PC, UC_ARM_REG_LR)
    n = TprtControl(library)
    n.u.mem_write(BUF, prefix)
    n.u.reg_write(UC_ARM_REG_R4, BUF)
    n.write(STACK+0xf000+12, length)
    events, stubs = [], []
    def boundary(u, a):
        if a == 0x171dc:
            count = u.reg_read(UC_ARM_REG_R2)
            if count != 4:
                raise ValueError('unexpected signature-copy size')
            u.mem_write(u.reg_read(UC_ARM_REG_R0),
                        bytes(u.mem_read(u.reg_read(UC_ARM_REG_R1), count)))
            stubs.append('bounded four-byte memcpy')
            u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))
        if a in (0x3512, 0x351e):
            events.append({'site': a, 'transform_mode':
                           u.reg_read(UC_ARM_REG_R3) if a == 0x3512 else None,
                           'input_offset': u.reg_read(UC_ARM_REG_R0)-BUF
                           if a == 0x3512 else None})
            return True
        return False
    n.execute(0x34ca, (), boundary)
    return {'events': events, 'stubs': stubs,
            'input_unchanged': bytes(n.u.mem_read(BUF, 4)) == prefix,
            'evidence': 'INJECTED_ENABLED_BRANCH_STOP_BEFORE_TRANSFORM'}


def native_crc(library, data):
    if type(data) is not bytes or len(data) > 4096:
        raise ValueError('synthetic CRC input <=4096 bytes required')
    n = TprtControl(library)
    if data:
        n.u.mem_write(BUF, data)
    return n.execute(0xe000, (BUF, len(data)), lambda u, a: False)


def postload_comparison(library, before, looked_up):
    """Execute actual comparison with explicit supplied post-load lookup result.

Hash values are independent synthetic controls, never a real loaded image hash.
Termination is intercepted before syscall, never executed on host/device.
"""
    if any(type(v) is not int or not 0 <= v < 2**32 for v in (before, looked_up)):
        raise ValueError('unsigned synthetic checksum values required')
    from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R4, UC_ARM_REG_R5,
        UC_ARM_REG_R7, UC_ARM_REG_PC, UC_ARM_REG_LR)
    n = TprtControl(library)
    n.write(STACK+0xf000+8, before)
    n.write(STACK+0xf000+0x1c, CTX)
    n.write(CTX+12, 0x12345678)  # independent module lookup handle
    n.u.reg_write(UC_ARM_REG_R5, BUF)
    n.u.reg_write(UC_ARM_REG_R7, CTX+0x100)  # zero dynamic guard configuration
    events, stubs = [], []
    def boundary(u, a):
        if a in (0x802c, 0x824c):
            stubs.append('monitor singleton supplied' if a == 0x802c else
                         'post-load lookup CRC supplied; no module enumeration')
            u.reg_write(UC_ARM_REG_R0, CTX+0x200 if a == 0x802c else looked_up)
            u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))
        if a in (0x3612, 0x3616, 0x361a):
            events.append(['native_site', a])
        if a == 0x31ac:
            events.append(['termination_requested', u.reg_read(UC_ARM_REG_R0)])
            return True
        if a == 0x36a8:
            events.append(['normal_return_boundary', u.reg_read(UC_ARM_REG_R4)])
            return True
        return False
    n.execute(0x35fc, (), boundary)
    return {'events': events, 'stubs': stubs,
            'evidence': 'INJECTED_POSTLOAD_CHECKSUM_NOT_PHONE_CAUSE'}


def mono_handoff(mono, tprt):
    """Original ARM entry -> Thumb veneer -> actual table target, then stop.

    Only the needed GOT slot and table slot receive synthetic loader relocation;
    no libtprt initialization or image parsing executes.
    """
    guarded_bytes(mono, 'mono')
    guarded_bytes(tprt, 'tprt')
    from elftools.elf.elffile import ELFFile
    from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE
    from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
        UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR)
    u = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    u.mem_map(0, 0x400000)
    u.mem_map(0x500000, 0x40000)
    u.mem_map(STACK, 0x10000)
    for path, base in ((mono, 0), (tprt, 0x500000)):
        with open(path, 'rb') as f:
            e = ELFFile(f)
            if e.elfclass != 32 or not e.little_endian or e['e_machine'] != 'EM_ARM':
                raise ValueError('unexpected source ISA')
            for s in e.iter_segments():
                if s['p_type'] == 'PT_LOAD':
                    u.mem_write(base+s['p_vaddr'], s.data())
    target = int.from_bytes(u.mem_read(0x523e00+26*4, 4), 'little')
    if target != 0x33fd:
        raise ValueError('unexpected image-loader table target')
    u.mem_write(0x3d8f94, (0x523e00).to_bytes(4, 'little'))
    u.mem_write(0x523e00+26*4, (target+0x500000).to_bytes(4, 'little'))
    args = (0x1000, 8192, 0, 0x2000)
    regs = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)
    for r, value in zip(regs, args):
        u.reg_write(r, value)
    u.reg_write(UC_ARM_REG_SP, STACK+0xf000)
    u.reg_write(UC_ARM_REG_LR, 0x1000)
    events, done = [], False
    def hook(u, a, size, unused):
        nonlocal done
        if a in (0x196c38, 0x14da4, 0x3d5fec, 0x5033fc):
            events.append(a)
        if a == 0x5033fc:
            done = True
            u.emu_stop()
    u.hook_add(UC_HOOK_CODE, hook)
    u.emu_start(0x196c38, 0x503400, timeout=1000000, count=128)
    if not done:
        raise RuntimeError('native handoff not reached within budget')
    return {'sites': events, 'target_rva': target & ~1,
            'arguments_preserved': tuple(u.reg_read(r) for r in regs) == args,
            'relocations': ['mono GOT g_tprt_pfn_array', 'tprt function slot26'],
            'evidence': 'EXPLICIT_TWO_RELOCATION_HANDOFF_NOT_ANDROID_INIT'}

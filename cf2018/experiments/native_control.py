"""Hash-pinned optional native runner; no server serializer or networking.

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


"""Optional bounded execution controls for one private, hash-pinned ARM library.

Requires pyelftools and Unicorn. Contains no original game code or binary bytes.
Only native splitter/header decoding executes; recv and libc are explicit stubs.
No ACK/session/state-machine acceptance is inferred from a return value.
"""
import hashlib
import struct
from pathlib import Path

LIBRARY_SHA256 = '4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'


def probe(library, data):
    if not isinstance(data, bytes) or len(data) > 65536:
        raise ValueError('independent synthetic bytes capped at 64 KiB required')
    library = Path(library)
    if library.stat().st_size != 5243704:
        raise ValueError('unexpected library size')
    if hashlib.sha256(library.read_bytes()).hexdigest() != LIBRARY_SHA256:
        raise ValueError('unexpected library fingerprint')
    from elftools.elf.elffile import ELFFile
    from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
    from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1,
        UC_ARM_REG_R2, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC)
    ctx, buf, stack, stop = 0x1000000, 0x1010000, 0x1100000, 0x1200000
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(0, 0x800000)
    with library.open('rb') as f:
        elf = ELFFile(f)
        if elf.elfclass != 32 or not elf.little_endian or elf['e_machine'] != 'EM_ARM':
            raise ValueError('unexpected ELF ISA')
        for segment in elf.iter_segments():
            if segment['p_type'] == 'PT_LOAD':
                uc.mem_write(segment['p_vaddr'], segment.data())
    uc.mem_map(ctx, 0x20000)
    uc.mem_map(stack, 0x10000)
    uc.mem_map(stop, 0x1000)
    uc.mem_write(buf, data)
    for offset, value in [(0x708, buf), (0x70c, 65536), (0x710, 0),
                          (0x714, len(data)), (0x718, 0), (0x71c, 0)]:
        uc.mem_write(ctx + offset, struct.pack('<I', value))
    uc.reg_write(UC_ARM_REG_R0, ctx)
    uc.reg_write(UC_ARM_REG_R1, 0)
    uc.reg_write(UC_ARM_REG_SP, stack + 0xf000)
    uc.reg_write(UC_ARM_REG_LR, stop | 1)
    branches, stubs = [], []
    done = False

    def hook(u, address, size, unused):
        nonlocal done
        if address == stop:
            done = True
            u.emu_stop()
            return
        if address in (0x3aab44, 0x3b7340, 0x3af4cc, 0x3ab6f6, 0x3ab74a):
            branches.append(address)
        r0 = u.reg_read(UC_ARM_REG_R0)
        r1 = u.reg_read(UC_ARM_REG_R1)
        r2 = u.reg_read(UC_ARM_REG_R2)
        if address == 0x284fcc:
            u.reg_write(UC_ARM_REG_R0, 0xfffffffd)
            stubs.append('net_recv returns -3; no network')
        elif address == 0x193e60:
            if r2 > 65536:
                raise ValueError('memset stub budget exceeded')
            u.mem_write(r0, bytes([r1 & 255]) * r2)
            stubs.append('libc memset')
        elif address in (0x193ed8, 0x193e6c):
            if r2 > 65536:
                raise ValueError('copy stub budget exceeded')
            u.mem_write(r0, bytes(u.mem_read(r1, r2)))
            stubs.append('libc memcpy/memmove')
        elif address == 0x1c6544:
            u.reg_write(UC_ARM_REG_R0, stop + 0x100)
            stubs.append('error string only')
        else:
            return
        u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(0x3ab5ed, stop + 2, timeout=1000000, count=100000)
    if not done:
        raise RuntimeError('native instruction/time budget reached')
    result = uc.reg_read(UC_ARM_REG_R0)
    if result & 0x80000000:
        result -= 1 << 32
    def word(offset):
        return struct.unpack('<I', uc.mem_read(ctx + offset, 4))[0]
    return {'return': result,
            'decoded_magic': struct.unpack('<H', uc.mem_read(ctx + 0x720, 2))[0],
            'header_length': word(0x734), 'body_length': word(0x738),
            'pending_frame_length': word(0x718), 'lookahead_length': word(0x71c),
            'cursor': word(0x710), 'buffered': word(0x714),
            'branches': branches, 'stubs': stubs}

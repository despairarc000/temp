"""Bounded original RPC unit-source controls with functional string stubs.

Only fixed synthetic names/integers; no socket, original C++ runtime, real
address, account or server exchange. NativeControl requires pinned Apollo.
"""
from native_control import NativeControl, CTX, AUX, OUT, STACK, STOP


def parse_synthetic_unit(library, unit=3, malformed=False):
    if unit not in (1, 3) or type(malformed) is not bool:
        raise ValueError('bounded synthetic unit required')
    n = NativeControl(library)
    domain = b'Example' if malformed else ('Example.%d.12345.agcloudcs.com' % unit).encode()
    cursor = [AUX+0x1000]
    def cstr(address):
        return bytes(n.uc.mem_read(address, 512)).split(b'\0', 1)[0]
    def get(obj):
        return cstr(n.read(obj))
    def put(obj, data):
        if len(data) > 512 or cursor[0]+len(data)+16 > AUX+0x8000:
            raise ValueError('synthetic string budget')
        address = cursor[0]; cursor[0] += len(data)+16
        n.uc.mem_write(address, data+b'\0'); n.write(obj, address)
        return obj
    put(AUX, domain)
    def copy(dest, source, *_):
        return put(dest, get(source))
    def find(obj, pattern, offset, unused):
        pos = get(obj).find(cstr(pattern), offset)
        return pos if pos >= 0 else 0xffffffff
    def substring(dest, source, offset, count):
        value = get(source)
        return put(dest, value[offset:] if count == 0xffffffff else value[offset:offset+count])
    def atoi(address, *_):
        return int(cstr(address).decode())
    def atoll(address, *_):
        from unicorn.arm_const import UC_ARM_REG_R1
        value = int(cstr(address).decode())
        n.uc.reg_write(UC_ARM_REG_R1, value >> 32)
        return value & 0xffffffff
    code = n.execute(0x3993c8, (AUX, OUT), {
        0x3f95f4: ('functional synthetic string copy', copy),
        0x3f96c0: ('functional synthetic string assignment', copy),
        0x3f848c: ('functional synthetic string find', find),
        0x3f9834: ('functional synthetic substring', substring),
        0x3f8a20: ('synthetic string destruction suppressed', 0),
        0x193dd0: ('synthetic decimal-to-int conversion', atoi),
        0x194658: ('synthetic decimal-to-int64 conversion', atoll)})
    return {'return': code, 'unit_matches_synthetic_input': n.read(OUT+0x10, 8) == unit,
            'game_matches_synthetic_input': n.read(OUT+8, 8) == 12345,
            'stubs': n.calls}


def rpc_unit_override(library, unit):
    if unit not in (1, 3):
        raise ValueError('bounded synthetic unit required')
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R6, UC_ARM_REG_PC
    n = NativeControl(library)
    n.write(STACK+0xf000+0x20, unit)
    n.uc.reg_write(UC_ARM_REG_R6, CTX)
    reached = []
    def stop(u, address, size, unused):
        if address == 0x3c4656:
            reached.append(True); u.reg_write(UC_ARM_REG_R0, 0); u.reg_write(UC_ARM_REG_PC, STOP | 1)
    n.uc.hook_add(UC_HOOK_CODE, stop)
    n.execute(0x3c4652, ())
    return bool(reached) and n.read(CTX+0x24) == unit

"""Bounded native virtual-dispatch prefix; no connector creation or network.

Uses canonical hash-pinned emulation from the prior reviewed integration. The
CGCloud instance and surrounding state are synthetic; actual vtable bytes and
AddressService dispatch instructions execute. Stop before selected method entry.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'experiments'))
from native_control import NativeControl, CTX, AUX, OUT, STOP


def address_factory_probe(library, *, address_point_offset=12):
    """Offset 12 is native constructor provenance; 8 is a malformed-state control."""
    if address_point_offset not in (8, 12):
        raise ValueError('only reviewed address point or bounded negative control')
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R5, UC_ARM_REG_R6,
                                  UC_ARM_REG_PC)
    n = NativeControl(library)
    address_point = 0x4f5d50 + address_point_offset
    selected = n.read(address_point + 0x18) & ~1
    n.write(CTX, address_point)
    n.write(CTX+0x8018, 8080)  # independent synthetic integer, no real target
    n.write(AUX, OUT)
    n.uc.reg_write(UC_ARM_REG_R5, CTX+0x8000)
    n.uc.reg_write(UC_ARM_REG_R6, AUX)
    reached = False

    def stop_before_method(u, address, size, unused):
        nonlocal reached
        if address == selected:
            reached = True
            u.reg_write(UC_ARM_REG_R0, (-77) & 0xffffffff)
            u.reg_write(UC_ARM_REG_PC, STOP | 1)
    n.uc.hook_add(UC_HOOK_CODE, stop_before_method)
    code = n.execute(0x39d756, (), {
        0x3c82a0: ('CGCloud GetInstance synthetic-object stub', CTX)})
    if not reached:
        raise RuntimeError('selected virtual method boundary not reached')
    return {'stop_code': code, 'selected_method': selected,
            'stopped_before_method': reached, 'calls': n.calls,
            'synthetic_instance': True, 'address_point_offset': address_point_offset}

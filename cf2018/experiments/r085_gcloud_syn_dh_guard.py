"""R085: exact-original conditional GCloud SYN DH serialization static audit.

The GCloud SYN writer checks an existing DH-state pointer before invoking
tgcpapi_generate_dh. If absent, a conditional branch skips that helper.
The helper itself checks the same handle-relative DH pointer before reading it.
The static branch does not prove the phone's handle or an accepted ACK.

No network, ACK crafting, key extraction, dynamic patch, or original binary export.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

from r057_original_address_callers import (
    ORIGINAL_SHA, ORIGINAL_SIZE, parse_elf, direct_calls, containing_symbol,
)
from r058_name_service_wiring import progbits_sections, virtual_file_offset

# Thumb instruction halfwords from exact original GCloud sender/helper.
PINS = {
    0x3ABA7C: 0xF505, 0x3ABA7E: 0x534F, # handle-relative DH slot base
    0x3ABA92: 0x6A9B,                   # load DH pointer
    0x3ABA94: 0x2B00,                   # cmp r3,#0
    0x3ABA96: 0xD039,                   # BEQ: skip DH helper
    0x3ABA98: 0x2303,                   # only nonnull branch: scalar 3
    0x3ABA9C: 0x7023,                   # store branch-specific scalar
    0x3ABA9E: 0x4621,                   # buffer argument for helper
    0x3ABAA0: 0xF7FF, 0x3ABAA2: 0xFF9E, # BL DH serialization
    0x3ABB0C: 0xE9D5, 0x3ABB0E: 0x2302, # normal SYN continuation
    0x3AB9F2: 0xB1E8,                   # helper null handle guard
    0x3AB9F4: 0xB1F9,                   # helper null destination guard
    0x3AB9F6: 0xF500, 0x3AB9F8: 0x554F, # same handle-relative offset
    0x3AB9FA: 0x6AAB,                   # helper loads DH pointer
    0x3AB9FC: 0xB1F3,                   # helper null DH guard
}
FUNCTIONS = {
    0x3ABA5C: (556, "gcloud_tgcpapi_send_syn_msg"),
    0x3AB9E0: (124, "tgcpapi_generate_dh"),
}
REQUIRED_CALLS = {0x3AB9E0: {0x3ABAA0: "gcloud_tgcpapi_send_syn_msg"}}

def beq_target(insn, address):
    if (insn & 0xFF00) != 0xD000:
        raise ValueError("not original Thumb BEQ encoding")
    offset = (insn & 0xFF) << 1
    if offset & 0x100:
        offset -= 0x200
    return address + 4 + offset

def cbz_target(insn, address):
    # For 16-bit CBZ/CBNZ T1, bit 11 is 0 for CBZ.
    if (insn & 0xFD00) != 0xB100:
        raise ValueError("not Thumb CBZ T1 encoding")
    imm6 = ((insn >> 9) & 1) << 5 | ((insn >> 3) & 31)
    return address + 4 + (imm6 << 1)

def verify_guards(read16):
    for addr, expected in PINS.items():
        if read16(addr) != expected:
            raise ValueError("R085 original DH guard instruction changed")
    if beq_target(read16(0x3ABA96), 0x3ABA96) != 0x3ABB0C:
        raise ValueError("SYN no-DH branch does not skip helper")
    if cbz_target(read16(0x3AB9FC), 0x3AB9FC) != 0x3ABA3C:
        raise ValueError("helper's missing-DH guard changed")
    if cbz_target(read16(0x3AB9F2), 0x3AB9F2) != 0x3ABA30:
        raise ValueError("helper's null-handle guard changed")
    if cbz_target(read16(0x3AB9F4), 0x3AB9F4) != 0x3ABA36:
        raise ValueError("helper's null-buffer guard changed")
    return True

def verify_functions(functions):
    for addr, (size, part) in FUNCTIONS.items():
        matches = [f for f in functions
                   if f.address == addr and f.size == size and part in f.name]
        if len(matches) != 1:
            raise ValueError("R085 function identity mismatch")
    return True

def verify_calls(observed, functions):
    if set(observed) != set(REQUIRED_CALLS):
        raise ValueError("R085 wrong direct-call target set")
    for target, required in REQUIRED_CALLS.items():
        if not set(required).issubset(observed[target]):
            raise ValueError("R085 GCloud SYN DH helper edge missing")
        for site, owner in required.items():
            if owner not in (containing_symbol(functions, site) or ""):
                raise ValueError("R085 original direct-call owner mismatch")
    return True

def audit(original):
    p = Path(original)
    if p.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("R085 wrong source size")
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("R085 wrong source hash")
    sections = progbits_sections(raw)
    def read16(addr):
        return struct.unpack_from("<H", raw,
            virtual_file_offset(sections, addr, 2))[0]
    executable, functions = parse_elf(raw)
    verify_guards(read16)
    verify_functions(functions)
    verify_calls(direct_calls(raw, executable, REQUIRED_CALLS), functions)
    return {
        "evidence": "EXACT_OWNER_ORIGINAL_STATIC",
        "original_verified": True,
        "instruction_halfwords_checked": len(PINS),
        "function_identities_checked": len(FUNCTIONS),
        "direct_call_edges_checked": 1,
        "sender_omits_dh_helper_if_pointer_null": True,
        "helper_also_requires_dh_pointer": True,
        "sender_no_dh_branch_rejoins_syn": True,
        "phone_dh_state_pointer": "NOT_OBSERVED",
        "phone_ack_key_mode": "NOT_OBSERVED",
        "second_service_ack_accepted": False,
        "gameplay_verified": False,
        "network_started": False,
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-lib", required=True)
    args = p.parse_args()
    try:
        r = audit(args.original_lib)
    except (OSError, ValueError, TypeError, struct.error) as e:
        print(json.dumps({"status":"REFUSED","reason":type(e).__name__,
                          "network_started":False}))
        raise SystemExit(2) from None
    print(json.dumps(r, indent=2))

if __name__ == "__main__":
    main()

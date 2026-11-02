"""R086: original GCloud ACK modes 0/2/3, source-only branch matrix.

This bounded auditor inspects the exact original game's receive/decrypt ACK
key-mode decision. It supplies intentionally conservative label-only synthetic
branch controls: no actual packet parsing, fake ACK, key derivation, decryption,
network traffic, authentication, or login bypass.

Labels such as MODE2_SET_KEY_SOURCE_BRANCH do NOT indicate accepted ACK,
session, auth, or gameplay. The second service's key mode is unknown.
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

# Source: exact owner-original GCloud::gcloud_tgcpapi_recv_and_decrypt_pkg.
# The preceding ACK gather and effective-type check are separate predicates.
PINS = {
    0x3ABEB2: 0xF894, 0x3ABEB4: 0x7741, # load mode (handle+0x741)
    0x3ABEB6: 0x2F02,                   # mode 2?
    0x3ABEB8: 0xD007,                   # BEQ 0x3ABECA (copy key)
    0x3ABEBA: 0x2F03,                   # mode 3?
    0x3ABEBC: 0xD015,                   # BEQ 0x3ABEEA (derive key)
    0x3ABEBE: 0x2F00,                   # mode 0?
    0x3ABEC0: 0xF040, 0x3ABEC2: 0x80D4, # BNE.W: reject other modes
    0x3ABEC4: 0xF884, 0x3ABEC6: 0x7458, # mode0: zero key length
    0x3ABEC8: 0xE01E,                   # B 0x3ABF08: bypass key setup
    0x3ABECA: 0xF504, 0x3ABECC: 0x61E8, # mode2 key buffer address
    0x3ABED4: 0xF894, 0x3ABED6: 0x2744, # decoded key information
    0x3ABEE0: 0xF8C4, 0x3ABEE2: 0x7120, # write key config
    0x3ABEE8: 0xE008,                   # B 0x3ABEFC: common set_key
    0x3ABEEA: 0xF504, 0x3ABEEC: 0x61E8, # mode3 existing DH context
    0x3ABEF2: 0xF7FF, 0x3ABEF4: 0xFF43, # compute_k
    0x3ABEF6: 0x2800, 0x3ABEF8: 0xF040, # check derive result
    0x3ABEFC: 0x4620,                   # common path
    0x3ABEFE: 0xF7FF, 0x3ABF00: 0xF9A4, # set_key
    0x3ABF02: 0x2800, 0x3ABF04: 0xF040, # check set_key result
    0x3ABF08: 0xF8D4, 0x3ABF0A: 0x9738, # normal body processing
}

EXPECTED_CALLS = {
    0x3ABD7C: {0x3ABEF2: "gcloud_tgcpapi_recv_and_decrypt_pkg"},
    0x3AB24A: {0x3ABEFE: "gcloud_tgcpapi_recv_and_decrypt_pkg"},
}
EXPECTED_FUNCTIONS = {
    0x3ABE34: (644, "gcloud_tgcpapi_recv_and_decrypt_pkg"),
    0x3AB24A: (76, "tgcpapi_set_key"),
    0x3ABD7C: (184, "tgcpapi_compute_k"),
}

def thumb_cond_target(code: int, site: int, condition: int) -> int:
    """Thumb-1 conditional B, requiring one explicitly expected condition."""
    if type(code) is not int or type(site) is not int or site & 1 or not 0 <= code <= 65535:
        raise ValueError("bounded aligned instruction required")
    if (code & 0xFF00) != (0xD000 | (condition << 8)):
        raise ValueError("wrong Thumb conditional branch")
    disp = (code & 255) << 1
    if disp & 256:
        disp -= 512
    return (site + 4 + disp) & 0xFFFFFFFF

def thumb_b_target(code: int, site: int) -> int:
    """Thumb-1 unconditional B only."""
    if type(code) is not int or type(site) is not int or site & 1 or (code & 0xF800) != 0xE000:
        raise ValueError("wrong Thumb B instruction")
    disp = (code & 2047) << 1
    if disp & 2048:
        disp -= 4096
    return (site + 4 + disp) & 0xFFFFFFFF

def verify_static(read16, functions, calls):
    for addr, expected in PINS.items():
        if read16(addr) != expected:
            raise ValueError("ACK mode branch native halfword mismatch")
    branches = (
        (thumb_cond_target(read16(0x3ABEB8), 0x3ABEB8, 0), 0x3ABECA),
        (thumb_cond_target(read16(0x3ABEBC), 0x3ABEBC, 0), 0x3ABEEA),
        (thumb_b_target(read16(0x3ABEC8), 0x3ABEC8), 0x3ABF08),
        (thumb_b_target(read16(0x3ABEE8), 0x3ABEE8), 0x3ABEFC),
    )
    if any(actual != expected for actual, expected in branches):
        raise ValueError("ACK mode branch target mismatch")
    for addr, (size, name) in EXPECTED_FUNCTIONS.items():
        if not any(f.address == addr and f.size == size and name in f.name for f in functions):
            raise ValueError("ACK mode original function identity mismatch")
    if set(calls) != set(EXPECTED_CALLS):
        raise ValueError("unexpected ACK mode target set")
    for target, requirements in EXPECTED_CALLS.items():
        if not set(requirements).issubset(calls[target]):
            raise ValueError("missing original ACK mode key callsite")
        for site, owner in requirements.items():
            if owner not in (containing_symbol(functions, site) or ""):
                raise ValueError("ACK key source owner mismatch")
    return True

def classify_source_branch(mode: int, *, has_dh: bool, key_present: bool,
                           encrypted_body: bool, encryption_method: int) -> str:
    """Conservative *symbolic* branch constraints, NOT a real ACK validator.

    Boolean inputs are synthetic flags, never actual ACK/key or login data.
    The result never says the server accepted, authenticated, or supplied keys.
    """
    if (type(mode) is not int or type(has_dh) is not bool
            or type(key_present) is not bool or type(encrypted_body) is not bool
            or type(encryption_method) is not int or not 0 <= encryption_method <= 255):
        raise ValueError("typed bounded symbolic inputs required")
    if mode not in (0, 2, 3):
        return "OTHER_MODE_NATIVE_REJECT_BRANCH"
    if mode == 0:
        if encrypted_body and encryption_method != 0:
            return "NO_KEY_ENCRYPTED_BODY_LATER_FAILURE_RISK"
        return "MODE0_NO_KEY_SETUP_SOURCE_ONLY"
    if mode == 2:
        if not key_present and encryption_method != 0:
            return "MODE2_EMPTY_KEY_NONZERO_ENCRYPTION_REJECT"
        if key_present and encryption_method not in (0, 3, 4):
            return "MODE2_UNSUPPORTED_METHOD_REJECT"
        return "MODE2_SET_KEY_SOURCE_ONLY"
    if not has_dh:
        return "MODE3_ABSENT_DH_CONTEXT_REJECT_EXPECTED"
    return "MODE3_DH_COMPUTE_KEY_SOURCE_ONLY"

def audit(original):
    original = Path(original)
    if original.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("wrong owner Apollo size")
    raw = original.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("wrong owner Apollo SHA")
    sections = progbits_sections(raw)
    def read16(addr):
        return struct.unpack_from("<H", raw, virtual_file_offset(sections, addr, 2))[0]
    executable, functions = parse_elf(raw)
    verify_static(read16, functions, direct_calls(raw, executable, EXPECTED_CALLS))
    return {
        "evidence": "EXACT_ORIGINAL_NATIVE_STATIC",
        "original_verified": True,
        "instruction_halfwords_checked": len(PINS),
        "known_direct_key_callsites_checked": 2,
        "mode_0_no_key_setup_branch": True,
        "mode_2_copy_and_set_key_branch": True,
        "mode_3_compute_and_set_key_branch": True,
        "other_modes_rejected_in_native_branch": True,
        "mode_0_may_need_key_later_for_encrypted_body": True,
        "phone_second_ack_mode": "NOT_OBSERVED",
        "second_ack_accepted": False,
        "login_or_gameplay_verified": False,
        "network_started": False,
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-lib", required=True)
    args = p.parse_args()
    try:
        result = audit(args.original_lib)
    except (OSError, ValueError, TypeError, struct.error) as exc:
        print(json.dumps({"status": "REFUSED", "reason": type(exc).__name__,
                          "network_started": False}))
        raise SystemExit(2) from None
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

"""R061: original CF2018 Apollo ACK/auth body-decoder fork.

Static call and function-size pins only. Verifies *which* parser is invoked
and GCloud's AA/99 envelope selection, NOT a valid wire reply or phone stack.
No listener, credentials, game modification, binary export or packet crafting.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

from r057_original_address_callers import (
    ORIGINAL_SHA, ORIGINAL_SIZE, parse_elf, direct_calls, containing_symbol
)
from r058_name_service_wiring import progbits_sections, virtual_file_offset

# Four original ACK/auth receiver calls dispatch to TWO separate serializers.
DECODER_CALLS = {
    0x1F9F6A: {
        0x1C1B90: "tgcpapi_recv_ack_msg",
        0x1C1F1E: "tgcpapi_recv_authrsp_msg",
    },
    0x3B8860: {
        0x3AC1B6: "gcloud_tgcpapi_recv_ack_msg",
        0x3AC366: "gcloud_tgcpapi_recv_authrsp_msg",
    },
    0x1F9E78: {0x1F9F86: "TGCPBody6unpack"},
    0x1F4842: {0x3B888E: "TGCPBody9unpackTLV"},
    0x1A333E: {0x3B88A6: "TGCPBody9unpackTLV"},
    0x3B8488: {0x3B88C0: "TGCPBody9unpackTLV"},
    0x3B8674: {0x3B88C6: "TGCPBody9unpackTLV"},
}

# Check individual decoder function identities, not inferred wire compatibility.
DECODER_IDENTITIES = {
    "legacy_dispatch": (0x1F9F6A, 48, "TGCPBody6unpack"),
    "legacy_body": (0x1F9E78, 242, "TGCPBody6unpack"),
    "gcloud_dispatch": (0x3B8860, 130, "TGCPBody9unpackTLV"),
    "gcloud_varint": (0x3B8488, 492, "TGCPBody19unpackTLVWithVarint"),
    "gcloud_no_varint": (0x3B8674, 492, "TGCPBody17unpackTLVNoVarint"),
}

# Original 32-bit THUMB instructions compared as 16-bit halfwords.
# GCloud reads marker then specifically compares AA and 99.
GCLOUD_MARKER_PINS = {
    0x3B888E: 0xF63B, 0x3B8890: 0xFFD8, # BL readUInt8
    0x3B8896: 0x2BAA, # CMP r3,#0xaa
    0x3B8898: 0xD001, # BEQ
    0x3B889A: 0x2B99, # CMP r3,#0x99
    0x3B889C: 0xD11C, # BNE -> refuses other marker
    0x3B88A6: 0xF5EA, 0x3B88A8: 0xFD4A, # BL readUInt32
    0x3B88C0: 0xF7FF, 0x3B88C2: 0xFDE2, # varint decoder
    0x3B88C6: 0xF7FF, 0x3B88C8: 0xFED5, # no-varint decoder
}
LEGACY_DISPATCH_PINS = {
    0x1F9F86: 0xF7FF, 0x1F9F88: 0xFF77,
}


def validate_identifiers(funcs, identities=DECODER_IDENTITIES):
    for key, (addr, length, name) in identities.items():
        m = [f for f in funcs
             if f.address == addr and f.size == length and name in f.name]
        if len(m) != 1:
            raise ValueError("original parser identity mismatch")


def validate_calls(sets, funcs, expected=DECODER_CALLS):
    if set(sets) != set(expected):
        raise ValueError("original decoder targets mismatch")
    # Other native consumers exist; only require the grounded callsites.
    for target, callers in expected.items():
        if not set(callers).issubset(sets[target]):
            raise ValueError("required original decoder callsite absent")
        for site, needle in callers.items():
            if needle not in (containing_symbol(funcs, site) or ""):
                raise ValueError("original decoder call owner mismatch")


def native_instruction_failures(raw, sections):
    failures = []
    for address, value in {**GCLOUD_MARKER_PINS, **LEGACY_DISPATCH_PINS}.items():
        start = virtual_file_offset(sections, address, 2)
        if struct.unpack_from("<H", raw, start)[0] != value:
            failures.append("decoder_instruction")
    return failures


def audit(path):
    f = Path(path)
    if f.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("source size mismatch")
    raw = f.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("source SHA mismatch")
    executable, funcs = parse_elf(raw)
    validate_identifiers(funcs)
    validate_calls(direct_calls(raw, executable, DECODER_CALLS), funcs)
    if native_instruction_failures(raw, progbits_sections(raw)):
        raise ValueError("original native parser instruction changed")
    return {
        "evidence": "EXACT_ORIGINAL_NATIVE_STATIC_ONLY",
        "source_verified": True,
        "original_parser_functions": len(DECODER_IDENTITIES),
        "direct_calls": sum(len(x) for x in DECODER_CALLS.values()),
        "original_halfword_pins": len(GCLOUD_MARKER_PINS) + len(LEGACY_DISPATCH_PINS),
        "legacy_ack_and_auth_use_gcp_body_unpack": True,
        "gcloud_ack_and_auth_use_gcloud_body_unpack_tlv": True,
        "gcloud_body_envelope_marker": "AA_OR_99",
        "gcloud_body_reads_declared_length": True,
        "legacy_same_marker_rule": "UNPROVEN",
        "phone_second_service_receiver": "UNVERIFIED",
        "accepted_second_service_ack": False,
        "game_login_verified": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-lib", required=True)
    args = p.parse_args()
    try:
        result = audit(args.original_lib)
    except (OSError, ValueError, struct.error):
        print(json.dumps({"status": "REFUSED", "reason": "SOURCE_OR_INSTRUCTION_MISMATCH"}))
        raise SystemExit(2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

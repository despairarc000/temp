"""R059: verify exact-original GCloud name-query -> endpoint-start division.

Read-only hash-pinned Apollo static audit, no packet/server send, APK modification,
credentials, route-name output or original binary committed. A static call does
NOT confirm phone execution or an accepted second-service ACK/session.
"""
from __future__ import annotations
import argparse
import json
import hashlib
import struct
from pathlib import Path

from r057_original_address_callers import (
    ORIGINAL_SHA, ORIGINAL_SIZE, parse_elf, direct_calls, containing_symbol
)
from r058_name_service_wiring import progbits_sections, virtual_file_offset

EXPECTED_CALLERS = {
    0x3A3C74: {0x3A5DE6: "CTGcp12OnThreadProc"},
    0x39D18C: {
        0x3A6890: "CDefaultNameService5Query",
        0x3C334E: "RpcConnector15InitLbIpAddress",
    },
    0x3A9D92: {0x3A4A80: "CTGcp13OnThreadStart"},
}

# Native Thumb halfwords. Each 32-bit instruction's two halves are pinned.
# choosingNameService:
# +2e0 holds name-service object; query key at +2d8; vtable +8 Query
# then vtable +12 Update.
# OnThreadStart uses resolved endpoint +2dc, NOT the query key +2d8.
EXPECTED_HALFWORDS = {
    0x3A3C7E: 0xF8D0, 0x3A3C80: 0x02E0, # load service object +2e0
    0x3A3C94: 0x6803,                     # load service vtable
    0x3A3C96: 0xF8D4, 0x3A3C98: 0x12D8, # load query key +2d8
    0x3A3C9A: 0x689B, 0x3A3C9C: 0x4798, # vtable+8, blx (Query)
    0x3A3C9E: 0xF8D4, 0x3A3CA0: 0x02E0, # load service +2e0
    0x3A3CA2: 0x6803, 0x3A3CA4: 0x68DB, 0x3A3CA6: 0x4798, # +12 Update
    0x3A4A7C: 0xF8D4, 0x3A4A7E: 0x12DC, # endpoint +2dc
    0x3A61AE: 0xF8D4, 0x3A61B0: 0x32DC, # callback endpoint field read
}

EXPECTED_VTABLE = {
    0x4F5088: 0x3A681D, # CDefaultNameService.Query, slot+8
    0x4F508C: 0x3A66DB, # CDefaultNameService.Update, slot+12
}
QUERY_KEY_OFFSET = 0x2D8
ENDPOINT_OFFSET = 0x2DC
NAMESERVICE_OFFSET = 0x2E0


def static_pin_failures(raw, sections):
    failures = []
    for address, expected in EXPECTED_HALFWORDS.items():
        offset = virtual_file_offset(sections, address, 2)
        if struct.unpack_from("<H", raw, offset)[0] != expected:
            failures.append("instruction_mismatch")
    for address, expected in EXPECTED_VTABLE.items():
        offset = virtual_file_offset(sections, address, 4)
        if struct.unpack_from("<I", raw, offset)[0] != expected:
            failures.append("virtual_dispatch_mismatch")
    return failures


def audit(path):
    path = Path(path)
    if path.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("wrong original source size")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("wrong original source hash")
    executable, funcs = parse_elf(raw)
    actual = direct_calls(raw, executable, EXPECTED_CALLERS)
    for target, expected in EXPECTED_CALLERS.items():
        if actual[target] != set(expected):
            raise ValueError("original native callgraph changed")
        for site, symbol in expected.items():
            if symbol not in (containing_symbol(funcs, site) or ""):
                raise ValueError("original native caller changed")
    if static_pin_failures(raw, progbits_sections(raw)):
        raise ValueError("original query / endpoint instructions changed")
    return {
        "evidence": "EXACT_ORIGINAL_NATIVE_STATIC",
        "original_hash_valid": True,
        "direct_edges_checked": sum(map(len, EXPECTED_CALLERS.values())),
        "halfwords_checked": len(EXPECTED_HALFWORDS),
        "virtual_entries_checked": len(EXPECTED_VTABLE),
        "name_service_query_via_vtable_slot8": True,
        "name_service_update_via_slot12": True,
        "query_key_and_endpoint_distinct_offsets": True,
        "callback_runtime_execution": "NOT_VERIFIED",
        "actual_route_name": "UNKNOWN",
        "second_service_ack_or_login": "NOT_VERIFIED",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-lib", required=True)
    args = p.parse_args()
    try:
        result = audit(args.original_lib)
    except (OSError, ValueError, struct.error):
        print(json.dumps({"status": "REFUSED", "reason": "ORIGINAL_OR_PIN_MISMATCH"}))
        raise SystemExit(2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

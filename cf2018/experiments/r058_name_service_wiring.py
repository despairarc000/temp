"""R058: exact-original GCloud name-service to TGCP observer wiring.

Evidence is static-only. The owner-private 2018 Apollo ELF is read-only and
SHA-pinned. Outputs contain only fixed method labels and booleans, no route,
address, account, bytes, or captured protocol traffic. No listener/send.
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

# The *direct* chain includes two original constructor variants and the
# connector's run-time connect entry; do not conflate with phone execution.
EXPECTED_EDGES = {
    0x3A3374: {
        0x3C696A: "CGCloudConnector13connectTConnd",
    },
    0x3A69E0: {
        0x3C76D2: "CGCloudConnectorC2",
        0x3C78A2: "CGCloudConnectorC1",
    },
}

# Source-observed instruction halfwords: CTGcp::SetNameService
# stores INameService pointer at +0x2e0; calls vtable slot +0x10
# to register an observer with this+0x48. CDefaultNameService stores
# observer at +8; its delivery function has an indirect BLX r8.
EXPECTED_HALFW = {
    0x3A3378: 0xF8C0, 0x3A337A: 0x12E0,  # str.w r1, [r0,#0x2e0]
    0x3A3386: 0x6912, 0x3A3388: 0x4790,  # ldr r2,[r2,#0x10]; blx r2
    0x3A66A8: 0x6081, 0x3A66AA: 0x4770,  # str r1,[r0,#8]; bx lr
    0x3A6B70: 0x47C0,                    # blx r8 in address callback
}

# Original .data.rel.ro (or other PROGBITS) virtual addresses. Thumb bit 1
# applies to function pointers. Query/Update/SetObserver are adjacent slots.
EXPECTED_VTABLE = {
    0x4F5088: 0x3A681D,  # CDefaultNameService::Query
    0x4F508C: 0x3A66DB,  # CDefaultNameService::Update
    0x4F5090: 0x3A66A9,  # CDefaultNameService::SetObserver
    0x4F4F68: 0x3A60B5,  # CTGcp::OnQueryNameResult observer body
    0x4F4F84: 0x3A626D,  # adjusting observer vtable thunk
    0x4F98B0: 0x3A6A71,  # bound name-service callback member pointer
}


def progbits_sections(raw):
    if (len(raw) < 52 or raw[:6] != b"\x7fELF\x01\x01"
            or struct.unpack_from("<H", raw, 18)[0] != 40):
        raise ValueError("expected ELF32LE ARM")
    shoff = struct.unpack_from("<I", raw, 32)[0]
    shent, shnum = struct.unpack_from("<HH", raw, 46)
    if shent < 40 or not 1 <= shnum <= 512 or shoff + shent*shnum > len(raw):
        raise ValueError("invalid section bounds")
    result = []
    for i in range(shnum):
        off = shoff + shent*i
        typ, flags, vaddr, fileoff, size = struct.unpack_from("<5I", raw, off+4)
        if typ == 1:
            if fileoff > len(raw) or size > len(raw) - fileoff:
                raise ValueError("section beyond source")
            result.append((vaddr, fileoff, size, flags))
    return result


def virtual_file_offset(sections, address, size):
    if size <= 0:
        raise ValueError("invalid read")
    hits = [
        fileoff + address - vaddr
        for vaddr, fileoff, length, _ in sections
        if vaddr <= address and address - vaddr + size <= length
    ]
    if len(hits) != 1:
        raise ValueError("ambiguous/unmapped ELF address")
    return hits[0]


def pinned_data_failures(raw, sections):
    """Check exact words, never print original words or raw game payload."""
    errors = []
    for addr, expected in EXPECTED_HALFW.items():
        off = virtual_file_offset(sections, addr, 2)
        if struct.unpack_from("<H", raw, off)[0] != expected:
            errors.append("native_instruction_pin")
    for addr, expected in EXPECTED_VTABLE.items():
        off = virtual_file_offset(sections, addr, 4)
        if struct.unpack_from("<I", raw, off)[0] != expected:
            errors.append("native_callback_vtable_pin")
    return errors


def audit(original):
    source = Path(original)
    if source.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("wrong original Apollo size")
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("wrong original Apollo SHA-256")
    sections = progbits_sections(raw)
    executable, functions = parse_elf(raw)
    callers = direct_calls(raw, executable, EXPECTED_EDGES)
    for target, expected in EXPECTED_EDGES.items():
        if callers[target] != set(expected):
            raise ValueError("unexpected original native caller set")
        for site, symbol in expected.items():
            if symbol not in (containing_symbol(functions, site) or ""):
                raise ValueError("callsite owner mismatched")
    if pinned_data_failures(raw, sections):
        raise ValueError("original method/observer/vtable pin mismatch")
    return {
        "evidence": "EXACT_ORIGINAL_APOLLO_STATIC",
        "sha256_match": True,
        "direct_call_edges_checked": sum(map(len, EXPECTED_EDGES.values())),
        "halfwords_checked": len(EXPECTED_HALFW),
        "vtable_pointers_checked": len(EXPECTED_VTABLE),
        "name_service_created_by_connector": True,
        "connect_calls_ctgcp_set_name_service": True,
        "ctgcp_sets_observer_via_nameservice_vtable": True,
        "name_service_stores_observer": True,
        "deferred_address_callback_has_indirect_observer_dispatch": True,
        "on_query_name_result_vtable_entry_exists": True,
        "dynamic_runtime_callback_observed": False,
        "route_name_identified": False,
        "second_service_ack_accepted": False,
        "phone_login_observed": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-lib", required=True)
    a = p.parse_args()
    try:
        outcome = audit(a.original_lib)
    except (ValueError, OSError, struct.error):
        print(json.dumps({"status": "REFUSED", "reason": "ORIGINAL_OR_PIN_MISMATCH"}))
        raise SystemExit(2)
    print(json.dumps(outcome, indent=2))


if __name__ == "__main__":
    main()

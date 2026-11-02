"""R075: original CTDir route-literal length and RPC caller discrimination.

Read-only static audit on SHA-pinned original Apollo. Proves that CTDir
passes a different integer argument to RpcConnector::Init than the two other
direct callers, owns a ten-byte printable route literal, and does not
directly call RpcConnector::Update in the original ELF.

Does NOT prove a live Android connector, route name, received unit value,
accepted ACK, account, session, or bot match. No raw strings emitted.
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


EXPECTED_CALLS = {
    0x3C4530: {  # RpcConnector::Init
        0x32FC74: "gcloud_version_action_imp3run",
        0x36175E: "CPufferInitAction24MakeSureGetUrlFromServer",
        0x36F0E0: "CTDir10Initialize",
    },
    0x3C5248: {  # RpcConnector::Update: only version and puffer direct calls
        0x32FDF8: "gcloud_version_action_imp3run",
        0x3619A4: "CPufferInitAction24MakeSureGetUrlFromServer",
    },
    0x36CE4C: {  # directory service RPC client constructor
        0x36F13C: "CTDir10Initialize",
    },
    0x36F034: {},  # no direct Thumb BL to CTDir::Initialize
}

# Parameter r3 is the first `int` after this, route/domain, ConnectCfg.
# Do NOT infer it is the client type, unit number, or authenticated role.
PARAM_R3 = {0x32FC72: 0x2308, 0x36175C: 0x2308, 0x36F0DE: 0x230F}
OTHER_PINS = {
    0x36F096: 0x4939,  # LDR r1,[PC,#0xe4] -> original literal 0x36f17c
    0x36F09E: 0x4479,  # ADD r1,pc
    0x36F0AC: 0x2301,  # MOVS r3,#1 (directory local config)
    0x36F0AE: 0xF845,  # beginning of pre-indexed STR instruction
    0x36F0B0: 0x3D10,  # stores 1 in temporary ConnectCfg unit
}
ROUTE_LITERAL_LOAD = 0x36F096
ROUTE_PC_ADD = 0x36F09E
ROUTE_LITERAL_LEN = 10


def verify_calls(actual, funcs, expected=EXPECTED_CALLS):
    if set(actual) != set(expected):
        raise ValueError("watched native caller target set changed")
    for target, sites in expected.items():
        if actual[target] != set(sites):
            raise ValueError("direct caller set mismatch")
        for site, owner in sites.items():
            if owner not in (containing_symbol(funcs, site) or ""):
                raise ValueError("direct call owning method mismatch")


def verify_instruction_pins(raw, sections, pins=None):
    pins = {**PARAM_R3, **OTHER_PINS} if pins is None else pins
    for addr, expected in pins.items():
        off = virtual_file_offset(sections, addr, 2)
        if struct.unpack_from("<H", raw, off)[0] != expected:
            raise ValueError("original Thumb instruction mismatch")


def route_literal_shape(raw, sections):
    """Resolve CTDir's LDR-literal + ADD-PC. Return only shape, NEVER string."""
    ldr = ROUTE_LITERAL_LOAD
    add = ROUTE_PC_ADD
    ldr_h = struct.unpack_from(
        "<H", raw, virtual_file_offset(sections, ldr, 2))[0]
    add_h = struct.unpack_from(
        "<H", raw, virtual_file_offset(sections, add, 2))[0]
    if ldr_h != OTHER_PINS[ldr] or add_h != OTHER_PINS[add]:
        raise ValueError("original PC-relative instruction changed")
    # Thumb 16-bit LDR literal: Align(PC,4) + imm8*4.
    target = ((ldr + 4) & ~3) + (ldr_h & 255) * 4
    displacement = struct.unpack_from(
        "<I", raw, virtual_file_offset(sections, target, 4))[0]
    # Thumb ADD (high register, PC): PC = add instruction address +4.
    string_address = (displacement + add + 4) & 0xFFFFFFFF
    candidate = raw[virtual_file_offset(sections, string_address, 32):
                    virtual_file_offset(sections, string_address, 32) + 32]
    length = candidate.find(b"\0")
    if length != ROUTE_LITERAL_LEN:
        raise ValueError("expected ten-byte route literal no longer present")
    if not all(32 <= ch <= 126 for ch in candidate[:length]):
        raise ValueError("original route literal not printable ASCII")
    return {"route_literal_ascii_length": length, "route_bytes_exported": False}


def audit(path):
    path = Path(path)
    if path.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("original libapollo size mismatch")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("original libapollo digest mismatch")
    sections, functions = parse_elf(raw)
    verify_calls(direct_calls(raw, sections, EXPECTED_CALLS), functions)
    mem_sections = progbits_sections(raw)
    verify_instruction_pins(raw, mem_sections)
    shape = route_literal_shape(raw, mem_sections)
    return {
        "evidence": "EXACT_ORIGINAL_NATIVE_STATIC_ONLY",
        "original_source_sha256_match": True,
        "watched_native_direct_edges": sum(map(len, EXPECTED_CALLS.values())),
        "parameter_halfwords_checked": len(PARAM_R3),
        "total_instruction_halfwords_checked": len(PARAM_R3) + len(OTHER_PINS),
        "directory_rpc_init_r3": 15,
        "version_and_puffer_rpc_init_r3": 8,
        "directory_local_cfg_unit_before_parser": 1,
        "directory_direct_rpc_update": False,
        "version_puffer_direct_rpc_update": True,
        **shape,
        "phone_route_same_as_ctdir": "UNKNOWN",
        "phone_unit_value": "UNKNOWN",
        "runtime_connector_selected": "UNKNOWN",
        "second_service_ack_accepted": False,
        "login_or_gameplay_verified": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-lib", required=True)
    args = p.parse_args()
    try:
        result = audit(args.original_lib)
    except (ValueError, OSError, struct.error):
        print(json.dumps({"status": "REFUSED", "reason": "ORIGINAL_OR_CALLGRAPH_PIN_MISMATCH"}))
        raise SystemExit(2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

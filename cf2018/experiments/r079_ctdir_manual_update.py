"""R079: exact-original CTDir tail branches missed by the prior BL-only scan.

Three 10-byte CTDir wrappers use a Thumb B.W (tail branch), NOT BL. In
particular CTDir::UpdateByManual branches to RpcConnector::Update, whose
original BL sites enter CreateConnection; that method constructs a GCloud
named-route object and retrieves the GCloud singleton.

This is ORIGINAL STATIC control-flow evidence, not proof that Android invoked
CTDir::UpdateByManual, which connector object was selected, valid ACK or login.
No packet output, listener, key, service-name or binary export.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from r057_original_address_callers import (
    ORIGINAL_SIZE, ORIGINAL_SHA, parse_elf, direct_calls, containing_symbol,
)
from r058_name_service_wiring import progbits_sections, virtual_file_offset

# wrapper: (address, exact 10-byte shape, destination, source/target name)
WRAPPERS = {
    "is_connected": (0x36F016, (0x6880, 0xB108, 0xF053, 0xBBDF, 0x4770),
                     0x3C27DC, "CTDir11IsConnected", "RpcConnector11IsConnected"),
    "enable_manual_update": (0x36F020, (0x6880, 0xB108, 0xF053, 0xBAAC, 0x4770),
                             0x3C2580, "CTDir18EnableManualUpdate",
                             "RpcConnector18EnableManualUpdate"),
    "update_by_manual": (0x36F02A, (0x6880, 0xB108, 0xF056, 0xB90B, 0x4770),
                         0x3C5248, "CTDir14UpdateByManual", "RpcConnector6Update"),
}

# The last two edges provide concrete NEW original proof that RPC CreateConnection
# constructs a GCloud name route and retrieves a GCloud instance. No claim
# is made about the indirect connector creation call that follows.
EXPECTED_CALLS = {
    0x3C4F78: {0x3C52B4: "RpcConnector6Update",
               0x3C5372: "RpcConnector6Update"},
    0x398CB4: {0x3C500A: "RpcConnector16CreateConnection"},
    0x3C82A0: {0x3C5088: "RpcConnector16CreateConnection"},
}


def decode_thumb_b_w(h1, h2, instruction_address):
    """Decode Thumb-2 unconditional B.W T4 only; no BL/BLX or arbitrary data."""
    if (type(h1) is not int or type(h2) is not int or
            type(instruction_address) is not int or
            not 0 <= h1 <= 0xffff or not 0 <= h2 <= 0xffff or
            not 0 <= instruction_address < 2**32 or instruction_address & 1):
        raise ValueError("bounded aligned Thumb B.W input required")
    if h1 & 0xf800 != 0xf000 or h2 & 0xd000 != 0x9000:
        raise ValueError("not an unconditional Thumb B.W")
    sign = (h1 >> 10) & 1
    i1 = 1 ^ ((h2 >> 13) & 1) ^ sign
    i2 = 1 ^ ((h2 >> 11) & 1) ^ sign
    displacement = (sign << 24 | i1 << 23 | i2 << 22 |
                    (h1 & 0x3ff) << 12 | (h2 & 0x7ff) << 1)
    if sign:
        displacement -= 1 << 25
    return (instruction_address + 4 + displacement) & 0xffffffff


def verify_wrappers(read_halfwords, symbols):
    """read_halfwords(address, 10) -> tuple of five uint16, no raw bytes output."""
    if not isinstance(symbols, dict):
        raise ValueError("original symbol map required")
    results = {}
    for label, (address, expected, dest, source_id, target_id) in WRAPPERS.items():
        halfwords = read_halfwords(address, 10)
        if type(halfwords) not in (tuple, list) or tuple(halfwords) != expected:
            raise ValueError("original CTDir wrapper instruction pin changed")
        actual = decode_thumb_b_w(halfwords[2], halfwords[3], address + 4)
        if actual != dest:
            raise ValueError("CTDir direct tail target mismatch")
        if source_id not in symbols.get(address, ""):
            raise ValueError("CTDir wrapper symbol identity mismatch")
        if target_id not in symbols.get(dest, ""):
            raise ValueError("RPC destination symbol identity mismatch")
        results[label] = dest
    return results


def verify_call_edges(observed, functions):
    if set(observed) != set(EXPECTED_CALLS):
        raise ValueError("native watched target set mismatch")
    for target, sites in EXPECTED_CALLS.items():
        actual = set(observed[target])
        if target == 0x3C4F78 and actual != set(sites):
            raise ValueError("RPC Update direct callset mismatch")
        if not set(sites).issubset(actual):
            raise ValueError("missing required route/create native edge")
        for site, owner in sites.items():
            if owner not in (containing_symbol(functions, site) or ""):
                raise ValueError("RPC route/create call owner mismatch")
    return True


def audit(apollo):
    path = Path(apollo)
    if path.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("wrong Apollo source size")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("wrong Apollo source hash")
    from struct import unpack_from
    sec = progbits_sections(raw)
    _, functions = parse_elf(raw)
    symbols = {}
    for f in functions:
        symbols.setdefault(f.address, f.name)
    def read_halfwords(address, size):
        offset = virtual_file_offset(sec, address, size)
        return tuple(unpack_from("<5H", raw, offset))
    verify_wrappers(read_halfwords, symbols)
    executable, _ = parse_elf(raw)
    verify_call_edges(direct_calls(raw, executable, EXPECTED_CALLS), functions)
    return {
        "evidence": "EXACT_ORIGINAL_APOLLO_STATIC_SHA_PINNED",
        "original_apollo_verified": True,
        "ctdir_wrappers_verified": len(WRAPPERS),
        "ctdir_update_by_manual_tail_branches_to_rpc_update": True,
        "rpc_update_direct_create_connection_sites": 2,
        "create_connection_constructs_gcloud_name_route": True,
        "create_connection_obtains_gcloud_instance": True,
        "ctdir_update_method_invoked_on_phone": "NOT_PROVEN",
        "gcloud_connector_created_for_ctdir_at_runtime": "NOT_PROVEN",
        "second_service_ack_accepted": False,
        "login_or_gameplay_verified": False,
        "network_started": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-lib", required=True)
    arg = p.parse_args()
    try:
        result = audit(arg.original_lib)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "REFUSED", "reason": type(exc).__name__,
                          "network_started": False}))
        raise SystemExit(2) from None
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

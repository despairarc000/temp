"""R073: exact original Apollo ordering of RPC domain-unit parsing and lookup.

Static-only. Verify direct ARM Thumb calls in the same Init method: domain
check/parse occurs before InitLbIpAddress, which requests AddressService.
The later CreateConnection is called from Update and selects an LB endpoint.
This DOES NOT link the CTDir route to the actual R037 Android reconnect.
No socket, ACK, private strings, app edits, or original binary exported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from r057_original_address_callers import (
    ORIGINAL_SHA, ORIGINAL_SIZE, parse_elf, direct_calls, containing_symbol
)

# Full exact native CALLER sets, not only plausible textual matches.
# Site-ordered within RpcConnector::Init:
# 0x3c4622 check domain; 0x3c464c parse domain; 0x3c474c LB lookup.
EDGES = {
    0x3C4530: {
        0x32FC74: "gcloud_version_action_imp3run",
        0x36175E: "CPufferInitAction24MakeSureGetUrlFromServer",
        0x36F0E0: "CTDir10Initialize",
    },
    0x399214: {
        0x39BBEE: "AddressService15ProcessResponse",
        0x39D200: "AddressService17GetServiceAddress",
        0x3C4622: "RpcConnector4Init",
    },
    0x3993C8: {
        0x39ADFE: "AddressService14ProcessRequest",
        0x3C464C: "RpcConnector4Init",
    },
    0x3C32CC: {
        0x3C474C: "RpcConnector4Init",
    },
    0x39D18C: {
        0x3A6890: "CDefaultNameService5Query",
        0x3C334E: "RpcConnector15InitLbIpAddress",
    },
    0x3C4F78: {
        0x3C52B4: "RpcConnector6Update",
        0x3C5372: "RpcConnector6Update",
    },
    0x3C4B04: {
        0x3C505A: "RpcConnector16CreateConnection",
    },
}

INIT_STEPS = (0x3C4622, 0x3C464C, 0x3C474C)
INIT_START, INIT_SIZE = 0x3C4530, 892


def validate_edges(actual, functions, expected=EDGES):
    if set(actual) != set(expected):
        raise ValueError("missing or extra watched target")
    for target, callsites in expected.items():
        if actual[target] != set(callsites):
            raise ValueError("unexpected direct callsite set")
        for site, owner_substring in callsites.items():
            if owner_substring not in (containing_symbol(functions, site) or ""):
                raise ValueError("unexpected source method of original call")


def verify_init_order(functions, calls=INIT_STEPS):
    if len(calls) != 3 or len(set(calls)) != 3:
        raise ValueError("wrong bounded original order")
    if not (INIT_START <= calls[0] < calls[1] < calls[2] <
            INIT_START + INIT_SIZE):
        raise ValueError("domain parse not proven earlier than address lookup")
    for site in calls:
        if "RpcConnector4Init" not in (containing_symbol(functions, site) or ""):
            raise ValueError("callsite not owned by original Init")


def audit(path):
    file = Path(path)
    if file.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("original Apollo size mismatch")
    raw = file.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("original Apollo SHA mismatch")
    exec_sections, functions = parse_elf(raw)
    validate_edges(direct_calls(raw, exec_sections, EDGES), functions)
    verify_init_order(functions)
    return {
        "evidence": "EXACT_ORIGINAL_STATIC_CALL_ORDER",
        "original_source_sha_match": True,
        "native_direct_calls_verified": sum(map(len, EDGES.values())),
        "rpc_init_domain_check_then_parser_then_lookup": True,
        "directory_init_calls_rpc_init": True,
        "rpc_update_calls_later_create_connection": True,
        "lb_selection_occurs_in_create_connection": True,
        "address_reply_itself_changed_unit": "NOT_ESTABLISHED",
        "directory_route_is_actual_phone_route": "NOT_ESTABLISHED",
        "on_phone_changed_field": "NOT_OBSERVED",
        "next_service_ack_accepted": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-lib", required=True)
    options = parser.parse_args()
    try:
        result = audit(options.original_lib)
    except (ValueError, OSError):
        print(json.dumps({"status": "REFUSED", "reason": "UNPINNED_SOURCE_OR_EDGE"}))
        raise SystemExit(2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

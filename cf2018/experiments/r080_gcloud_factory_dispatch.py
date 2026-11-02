"""R080: original CGCloud factory virtual-slot audit on the RPC connection path.

Exact static vtable and Thumb instruction pins only: RpcConnector::CreateConnection
retrieves CGCloud singleton and performs a virtual call through vptr+0x18.
Original CGCloud primary vtable slot +0x18 is CreateApolloConnection, whose
original direct BL constructs CGCloudConnector. Conditional *source* path,
NOT proof the original phone took this branch, connected or accepted an ACK.

No traffic, original bytes, route strings, accounts, keys, or phone data exported.
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

# Actual original site: ldr r3,[r0]; ldr r5,[r3,#0x18]; blx r5.
FACTORY_DISPATCH_PINS = {
    0x3C508C: 0x6803,
    0x3C5092: 0x699D,
    0x3C5096: 0x47A8,
}
CGCLOUD_VTABLE_PRIMARY_POINT = 0x4F5D5C
CGCLOUD_VTABLE_OBJECT_START = 0x4F5D50
CGCLOUD_SLOT = 0x18
CGCLOUD_VTABLE_RTTI = 0x4F5D18
EXPECTED_THUMB_CREATE_APOLLO = 0x3C7E39
EXPECTED_VTABLE_WORDS = {
    0x4F5D54: 0,                       # primary offset-to-top
    0x4F5D58: CGCLOUD_VTABLE_RTTI,     # typeinfo
    0x4F5D5C: 0x3C8081,              # CGCloud destructor Thumb entry
    CGCLOUD_VTABLE_PRIMARY_POINT + CGCLOUD_SLOT: EXPECTED_THUMB_CREATE_APOLLO,
}

REQUIRED_CALLS = {
    0x3C8204: {0x3C82B2: "CGCloud11GetInstance"},
    0x3C7784: {0x3C7EE6: "CGCloud22CreateApolloConnection"},
    0x3A69E0: {0x3C78A2: "CGCloudConnectorC1"},
    0x3A33A0: {0x3C6C4A: "CGCloudConnector13connectTConnd"},
    0x3A369C: {0x3C6C86: "CGCloudConnector13connectTConnd"},
    0x3AC0B8: {0x3A845A: "gcloud_tgcpapi_start_connection",
               0x3A9FB0: "OnStateKeySyning"},
    0x3B8860: {0x3AC1B6: "gcloud_tgcpapi_recv_ack_msg"},
}


def verify_virtual_dispatch(read16, read32):
    """Validate the original vptr+0x18 dispatch with strict source pins."""
    for address, opcode in FACTORY_DISPATCH_PINS.items():
        if read16(address) != opcode:
            raise ValueError("CGCloud factory virtual dispatch instruction changed")
    if (CGCLOUD_VTABLE_PRIMARY_POINT != CGCLOUD_VTABLE_OBJECT_START + 12
            or CGCLOUD_VTABLE_PRIMARY_POINT + CGCLOUD_SLOT != 0x4F5D74):
        raise ValueError("GCloud vtable address-point boundary changed")
    for address, expected in EXPECTED_VTABLE_WORDS.items():
        if read32(address) != expected:
            raise ValueError("CGCloud factory vtable pointer changed")
    return "CGCLOUD_CREATE_APOLLO_CONNECTION_STATIC_VTABLE_MATCH"


def verify_direct_edges(observed, functions):
    if set(observed) != set(REQUIRED_CALLS):
        raise ValueError("wrong watched original target set")
    for dest, required in REQUIRED_CALLS.items():
        if not set(required).issubset(observed[dest]):
            raise ValueError("missing original GCloud factory or receiver edge")
        for site, method in required.items():
            if method not in (containing_symbol(functions, site) or ""):
                raise ValueError("unexpected GCloud factory/receiver owner")
    return True


def audit(original):
    original=Path(original)
    if original.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("unexpected Apollo size")
    raw=original.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ORIGINAL_SHA:
        raise ValueError("unexpected Apollo SHA")
    sections=progbits_sections(raw)
    def read16(address):
        return struct.unpack_from("<H", raw, virtual_file_offset(sections, address, 2))[0]
    def read32(address):
        return struct.unpack_from("<I", raw, virtual_file_offset(sections, address, 4))[0]
    verify_virtual_dispatch(read16, read32)
    executable, funcs=parse_elf(raw)
    verify_direct_edges(direct_calls(raw, executable, REQUIRED_CALLS), funcs)
    return {
        "evidence": "SHA_PINNED_ORIGINAL_NATIVE_STATIC",
        "original_apollo_verified": True,
        "virtual_dispatch_instructions_checked": len(FACTORY_DISPATCH_PINS),
        "vtable_words_checked": len(EXPECTED_VTABLE_WORDS),
        "known_direct_calls_checked": sum(map(len, REQUIRED_CALLS.values())),
        "rpc_create_connection_calls_cgcloud_factory_virtual": True,
        "virtual_slot_resolves_create_apollo_connection": True,
        "factory_constructs_gcloud_connector": True,
        "gcloud_connector_has_default_name_service": True,
        "gcloud_transport_ack_body_decoder_conditional": "GCLOUD_TGCP_TLV",
        "phone_ran_cgcloud_factory": "NOT_PROVEN",
        "new_connector_used_r077_route": "NOT_PROVEN",
        "second_service_ack_accepted": False,
        "game_login_verified": False,
        "listener_started": False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-lib",required=True)
    args=p.parse_args()
    try:
        result=audit(args.original_lib)
    except (OSError, ValueError, TypeError, struct.error) as exc:
        print(json.dumps({"status":"REFUSED","reason":type(exc).__name__,
                          "listener_started":False}))
        raise SystemExit(2) from None
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()

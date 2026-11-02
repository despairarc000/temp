"""R082: exact-original RpcConnector::CreateConnection IConnector Connect dispatch.

R081 had identified the secondary IConnector vtable slots but left the later
indirect call unresolved. R082 pins the factory's +0x14 IConnector subobject
return adjustment, CreateConnection's Initialize/observer/manual-update/Connect
virtual callsites, the secondary vtable target, and Connect's native transport
continuation. This is conditional source control flow only, not proof Android
executed it or that a second-service ACK/session was accepted.

No sockets, ACK generation, packet bytes, original binary export or credentials.
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

# CGCloud::CreateApolloConnection constructs the concrete object, then returns
# the IConnector subobject pointer (complete-object address + 0x14).
FACTORY_RETURN_ADJUST = {
    0x3C7F50: 0xF105,  # ADD.W r0, r5, #0x14
    0x3C7F52: 0x0014,
}

# CreateConnection: Initialize (+0x10), service observer (+0x08),
# EnableManualUpdate (+0x34), then Connect (+0x18).
DISPATCH_PINS = {
    0x3C5114: 0x682B,  # load IConnector subobject vptr
    0x3C5120: 0x691B,  # load vtable +0x10
    0x3C5122: 0x4798,  # BLX r3 -> Initialize thunk
    0x3C5136: 0x689B,  # load observer slot after interface/base adjustment
    0x3C5138: 0x4798,  # BLX r3 -> AddObserver virtual thunk
    0x3C5142: 0x6B5B,  # load vtable +0x34
    0x3C5144: 0x4798,  # BLX r3 -> EnableManualUpdate thunk
    0x3C5146: 0x682B,  # reload IConnector subobject vptr
    0x3C5152: 0x699B,  # load vtable +0x18
    0x3C5154: 0x4798,  # BLX r3 -> Connect thunk
}

# The secondary IConnector vtable address point is 0x4f5c14. Values are
# Thumb function pointers; slot offsets are relative to that address point.
VTABLE_PINS = {
    0x4F5C00: 0xFFFFFFEC,  # -0x14 virtual-base adjustment entry
    0x4F5C14: 0x003C7C8D,  # secondary destructor thunk
    0x4F5C1C: 0x003C5919,  # AddObserver virtual thunk
    0x4F5C24: 0x003C61B5,  # Initialize adjusting thunk (+0x10)
    0x4F5C2C: 0x003C7055,  # Connect adjusting thunk (+0x18)
    0x4F5C48: 0x003C59E7,  # EnableManualUpdate adjusting thunk (+0x34)
}

# Required direct BL continuation, with exact caller ownership. Additional
# legitimate callers are allowed; only these grounded edges are required.
REQUIRED_CALLS = {
    0x3C7784: {0x3C7EE6: "CGCloud7CGCloud22CreateApolloConnection"},
    0x3C68E0: {
        0x3C6F4A: "CGCloudConnector7Connect",
        0x3C6FC2: "CGCloudConnector7Connect",
    },
    0x3A33A0: {0x3C6C4A: "CGCloudConnector13connectTConnd"},
    0x3A369C: {0x3C6C86: "CGCloudConnector13connectTConnd"},
}


def verify_virtual_dispatch(read16, read32):
    for address, expected in FACTORY_RETURN_ADJUST.items():
        if read16(address) != expected:
            raise ValueError("factory IConnector return adjustment changed")
    for address, expected in DISPATCH_PINS.items():
        if read16(address) != expected:
            raise ValueError("CreateConnection virtual dispatch changed")
    for address, expected in VTABLE_PINS.items():
        if read32(address) != expected:
            raise ValueError("CGCloudConnector secondary vtable changed")
    return "ICONNECTOR_CONNECT_CALLSITE_AND_VTABLE_MATCH"


def verify_direct_calls(observed, functions):
    if set(observed) != set(REQUIRED_CALLS):
        raise ValueError("wrong original Connect continuation target set")
    for target, required in REQUIRED_CALLS.items():
        if not set(required).issubset(observed[target]):
            raise ValueError("required original Connect continuation absent")
        for site, owner in required.items():
            if owner not in (containing_symbol(functions, site) or ""):
                raise ValueError("original Connect continuation owner mismatch")
    return True


def audit(original):
    path = Path(original)
    if path.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("wrong Apollo source size")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("wrong Apollo source SHA")
    sections = progbits_sections(raw)

    def read16(address):
        return struct.unpack_from(
            "<H", raw, virtual_file_offset(sections, address, 2)
        )[0]

    def read32(address):
        return struct.unpack_from(
            "<I", raw, virtual_file_offset(sections, address, 4)
        )[0]

    verify_virtual_dispatch(read16, read32)
    executable, functions = parse_elf(raw)
    verify_direct_calls(
        direct_calls(raw, executable, REQUIRED_CALLS), functions
    )
    return {
        "evidence": "EXACT_ORIGINAL_SHA_PINNED_STATIC",
        "original_apollo_verified": True,
        "factory_return_adjustment_checked": True,
        "create_connection_dispatch_halfwords_checked": len(DISPATCH_PINS),
        "secondary_vtable_words_checked": len(VTABLE_PINS),
        "required_direct_continuation_edges": sum(map(len, REQUIRED_CALLS.values())),
        "factory_returns_iconnector_subobject_plus_0x14": True,
        "create_connection_calls_initialize": True,
        "create_connection_registers_service_observer": True,
        "create_connection_calls_enable_manual_update": True,
        "create_connection_calls_connect_slot_plus_0x18": True,
        "connect_slot_resolves_to_cgcloudconnector_connect_thunk": True,
        "connect_directly_calls_connect_tconnd": True,
        "connect_tconnd_calls_route_setter_and_transport_start": True,
        "phone_executed_create_connection": "NOT_PROVEN",
        "phone_executed_connect": "NOT_PROVEN",
        "second_service_ack_accepted": False,
        "login_or_gameplay_verified": False,
        "network_started": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-lib", required=True)
    args = parser.parse_args()
    try:
        result = audit(args.original_lib)
    except (OSError, ValueError, TypeError, struct.error) as exc:
        print(json.dumps({
            "status": "REFUSED",
            "reason": type(exc).__name__,
            "network_started": False,
        }))
        raise SystemExit(2) from None
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

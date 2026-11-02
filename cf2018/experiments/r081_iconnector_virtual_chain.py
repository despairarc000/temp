"""R081: bounded, original source-only IConnector init/connect virtual boundary.

R080 resolves CGCloud::CreateApolloConnection to CGCloudConnector construction.
This audit checks the original follow-on IConnector interface vtable: secondary
CGCloudConnector vptr, Initialize & Connect adjusting thunks, and direct
Connect -> connectTConnd -> route & Start calls. Runtime vptr/object identity,
whether phone executed these calls and ACK acceptance are still NOT established.
No listener, ACK serializer, account values or packet construction.
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

# Indirect initialization call after the CGCloud factory returns. These
# halfwords were independently reviewed in the SHA-matching 2018 ELF.
PINNED_DISPATCH = {
    0x3C509A: 0x4605,  # mov r5, r0: preserve new connector pointer
    0x3C5114: 0x682B,  # ldr r3, [r5]: connector vptr
    0x3C5120: 0x691B,  # ldr r3, [r3, #0x10]
    0x3C5122: 0x4798,  # blx r3
    0x3C512A: 0x682B,  # later connection virtual path
    0x3C5138: 0x4798,  # later blx r3, not proven which vtable in runtime
}
SECONDARY_ICONNECTOR_VPTR = 0x4F5C14
VTABLE_WORDS = {
    0x4F5C10: 0x4F5B0C,  # RTTI for CGCloudConnector
    0x4F5C14: 0x3C7C8D,  # adjusting destructor Thumb pointer
    0x4F5C24: 0x3C61B5,  # vptr + 0x10: Initialize adjusting thunk
    0x4F5C2C: 0x3C7055,  # vptr + 0x18: Connect adjusting thunk
    0x4F5C48: 0x3C59E7,  # secondary manual-update adjusting thunk
    0x4F5C4C: 0x3C59F3,
}

REQUIRED_DIRECT = {
    0x3C68E0: {0x3C6F4A: "CGCloudConnector7Connect",
               0x3C6FC2: "CGCloudConnector7Connect"},
    0x3A33A0: {0x3C6C4A: "CGCloudConnector13connectTConnd"},
    0x3A369C: {0x3C6C86: "CGCloudConnector13connectTConnd"},
    0x3AC0B8: {0x3A845A: "gcloud_tgcpapi_start_connection",
               0x3A9FB0: "OnStateKeySyning"},
}


def verify_dispatch(read16, read32):
    if SECONDARY_ICONNECTOR_VPTR + 0x10 != 0x4F5C24:
        raise ValueError("IConnector virtual slot offset mismatch")
    for site,expected in PINNED_DISPATCH.items():
        if read16(site) != expected:
            raise ValueError("RPC connector virtual instruction changed")
    for address,expected in VTABLE_WORDS.items():
        if read32(address) != expected:
            raise ValueError("CGCloudConnector IConnector vtable pointer changed")
    return "ICONNECTOR_INIT_VIRTUAL_SLOT_MATCH"


def verify_direct_calls(got, functions):
    if set(got) != set(REQUIRED_DIRECT):
        raise ValueError("GCloud receiver/transport targets changed")
    for target, required in REQUIRED_DIRECT.items():
        if not set(required).issubset(got[target]):
            raise ValueError("required GCloud connector call absent")
        for site,owner in required.items():
            if owner not in (containing_symbol(functions,site) or ""):
                raise ValueError("GCloud connector call owner mismatch")
    return True


def audit(original):
    path=Path(original)
    if path.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("original source size required")
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ORIGINAL_SHA:
        raise ValueError("original source SHA required")
    sec=progbits_sections(raw)
    def read16(x):
        return struct.unpack_from("<H",raw,virtual_file_offset(sec,x,2))[0]
    def read32(x):
        return struct.unpack_from("<I",raw,virtual_file_offset(sec,x,4))[0]
    verify_dispatch(read16,read32)
    executable,functions=parse_elf(raw)
    verify_direct_calls(direct_calls(raw,executable,REQUIRED_DIRECT),functions)
    return {
        "evidence":"SHA_PINNED_ORIGINAL_SOURCE_ONLY",
        "original_apollo_verified":True,
        "indirect_dispatch_halfwords_checked":len(PINNED_DISPATCH),
        "gcloud_iconnector_vtable_words_checked":len(VTABLE_WORDS),
        "required_direct_transport_edges":sum(map(len,REQUIRED_DIRECT.values())),
        "secondary_iconnector_initialize_thunk_identified":True,
        "secondary_iconnector_connect_thunk_identified":True,
        "gcloud_connect_calls_connect_tconnd":True,
        "connect_tconnd_sets_route_and_starts_transport":True,
        "phone_selected_this_subobject_vptr":"NOT_PROVEN",
        "phone_second_ack_receiver_execution":"NOT_PROVEN",
        "second_service_ack_accepted":False,
        "login_or_gameplay_verified":False,
        "network_started":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-lib",required=True)
    a=p.parse_args()
    try:
        outcome=audit(a.original_lib)
    except (ValueError,OSError,TypeError,struct.error) as exc:
        print(json.dumps({"status":"REFUSED","reason":type(exc).__name__,
                          "network_started":False}))
        raise SystemExit(2) from None
    print(json.dumps(outcome,indent=2))


if __name__=="__main__":
    main()

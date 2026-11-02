"""R084: bounded original RPC -> GCloud DH-parameter configuration source audit.

Identifies the default-constructed AString in the RPC ConnectorInitInfo and
tracks its copy into CGCloudConnector, then the c_str argument carried through
the two CTGcp::Initialize call branches and GCloud DH wrapper.

A default-constructed string is empty, but this STATIC audit cannot prove
that the exact phone object took this path, that no runtime mutation occurred,
or which ACK key mode an actual server would use. In particular, this is NOT
a license to replay the reference first-service ACK on the second route.

No client/game binary exported, no real route/account/key bytes, no sockets,
no packet crafting, no credentials and no phone activity.
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

# Instruction *halfwords* from the exact owner Apollo. These tie object
# offsets, call ordering and the argument passed to each nested initializer.
# A single BL reference or string symbol is NOT sufficient for this claim.
PINS = {
    # RpcConnector::CreateConnection inlines ConnectorInitInfo construction.
    0x3C5018: 0x4630,  # r0 = local init-info base
    0x3C501A: 0xF7AA, 0x3C501C: 0xFA95,  # buffer-base constructor
    0x3C5020: 0xF106, 0x3C5022: 0x0010,  # r0 = init-info +0x10
    0x3C5032: 0xF7D2, 0x3C5034: 0xF8DD,  # AString default ctor
    0x3C511C: 0x4632,  # r2 = init-info for virtual Initialize
    0x3C5120: 0x691B, 0x3C5122: 0x4798,  # Initialize virtual dispatch

    # CGCloudConnector::Initialize copies init-info string into owned string.
    0x3C6134: 0xF105, 0x3C6136: 0x0110,  # source init-info +0x10
    0x3C6142: 0xF104, 0x3C6144: 0x003C,  # destination connector +0x3c
    0x3C6148: 0xF7D1, 0x3C614A: 0xF920,  # AString operator=(AString const&)

    # Both alternative connection branches read that owned string and pass
    # the resulting c_str as stacked argument #6 to CTGcp::Initialize.
    0x3C6A4A: 0xF106, 0x3C6A4C: 0x003C,
    0x3C6A52: 0xF7D0, 0x3C6A54: 0xFC4F,
    0x3C6A5C: 0x9005,  # [sp+#0x14] = AString::c_str result
    0x3C6A70: 0xF7DD, 0x3C6A72: 0xF952,
    0x3C6BAE: 0xF106, 0x3C6BB0: 0x003C,
    0x3C6BB6: 0xF7D0, 0x3C6BB8: 0xFB9D,
    0x3C6BC0: 0x9005,
    0x3C6BD4: 0xF7DD, 0x3C6BD6: 0xF8A0,

    # CTGcp::Initialize -> gcloud_tgcpapi_init -> conditional DH setter.
    0x3A3EF6: 0xF003, 0x3A3EF8: 0xFFA3,
    0x3A7FC8: 0x9912,  # load the DH argument from stack
    0x3A7FCA: 0xF7FF, 0x3A7FCC: 0xFF2E,
}
FUNCTIONS = {
    0x3C4F78: (720, "RpcConnector16CreateConnection"),
    0x3C60B8: (252, "CGCloudConnector10Initialize"),
    0x3C68E0: (1204, "CGCloudConnector13connectTConnd"),
    0x3A3D18: (624, "CTGcp10Initialize"),
    0x3A7E40: (684, "gcloud_tgcpapi_init"),
    0x3A7E2A: (22, "gcloud_tgcpapi_set_dh"),
}
REQUIRED_CALLS = {
    0x36F548: {0x3C501A: "RpcConnector16CreateConnection"},
    0x3971F0: {0x3C5032: "RpcConnector16CreateConnection"},
    0x39738C: {0x3C6148: "CGCloudConnector10Initialize"},
    0x3972F4: {
        0x3C6A52: "CGCloudConnector13connectTConnd",
        0x3C6BB6: "CGCloudConnector13connectTConnd",
    },
    0x3A3D18: {
        0x3C6A70: "CGCloudConnector13connectTConnd",
        0x3C6BD4: "CGCloudConnector13connectTConnd",
    },
    0x3A7E40: {0x3A3EF6: "CTGcp10Initialize"},
    0x3A7E2A: {0x3A7FCA: "gcloud_tgcpapi_init"},
}


def verify_pins(read16):
    for addr, expected in PINS.items():
        if read16(addr) != expected:
            raise ValueError("R084 original instruction/offset mismatch")
    return True


def verify_functions(functions):
    for addr, (size, part) in FUNCTIONS.items():
        matches = [f for f in functions
                   if f.address == addr and f.size == size and part in f.name]
        if len(matches) != 1:
            raise ValueError("R084 original function identity mismatch")
    return True


def verify_calls(observed, functions):
    if set(observed) != set(REQUIRED_CALLS):
        raise ValueError("R084 unexpected source-call target collection")
    for target, required in REQUIRED_CALLS.items():
        if not set(required).issubset(observed[target]):
            raise ValueError("R084 original source-call edge missing")
        for site, owner in required.items():
            if owner not in (containing_symbol(functions, site) or ""):
                raise ValueError("R084 source-call owner mismatch")
    return True


def audit(original):
    path = Path(original)
    if path.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("R084 wrong original size")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("R084 wrong original SHA")
    sections = progbits_sections(raw)
    def read16(addr):
        return struct.unpack_from("<H", raw,
            virtual_file_offset(sections, addr, 2))[0]
    executable, functions = parse_elf(raw)
    verify_pins(read16)
    verify_functions(functions)
    verify_calls(direct_calls(raw, executable, REQUIRED_CALLS), functions)
    return {
        "evidence": "EXACT_ORIGINAL_SHA_PINNED_STATIC",
        "original_source_verified": True,
        "native_halfwords_checked": len(PINS),
        "native_function_identities_checked": len(FUNCTIONS),
        "required_direct_call_edges": sum(map(len, REQUIRED_CALLS.values())),
        "rpc_init_info_string_default_constructed": True,
        "rpc_init_info_string_source_offset": "+0x10",
        "connector_owned_string_destination_offset": "+0x3c",
        "both_connect_branches_pass_owned_string": True,
        "source_reaches_conditional_dh_setter": True,
        "static_rpc_constructor_default_string": "EMPTY",
        "phone_runtime_string": "NOT_OBSERVED",
        "second_service_ack_key_mode": "NOT_OBSERVED",
        "second_service_ack_accepted": False,
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

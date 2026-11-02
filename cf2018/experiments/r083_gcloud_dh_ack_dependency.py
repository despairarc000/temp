"""R083: exact-original GCloud per-handle DH / ACK-key dependency audit.

R082 pins the IConnector Connect call. This audit follows that source path into
CTGcp construction/initialization, conditional DH setup, SYN public-value
serialization, ACK key-mode dispatch and the key-synchronization state.

The crucial condition is explicit: gcloud_tgcpapi_set_dh only tail-branches to
set_dh_info for a nonempty DH-parameter string; that routine generates a DH
keypair. The SYN helper serializes the local DH public component. On ACK mode 3,
receive/decrypt computes a shared key from the ACK's RawDHRsp using the current
handle's DH context, then sets the transport key. Actual phone DH string,
key mode and runtime object path remain unproven.

No ACK generation, keys, credentials, packet bytes, sockets or original binary
export. This is static control-flow evidence, not a successful handshake.
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
from r079_ctdir_manual_update import decode_thumb_b_w

# The DH wrapper checks its input before its only tail branch. Its B.W target
# is set_dh_info; the destination performs the actual DH_generate_key call.
DH_WRAPPER_PINS = {
    0x3A7E2C: 0xB109,  # null/pointer guard
    0x3A7E2E: 0x780A,  # inspect first byte
    0x3A7E30: 0xB922,  # empty/nonempty branch
    0x3A7E3C: 0xF004,  # Thumb-2 B.W
    0x3A7E3E: 0xBB38,
}
DH_WRAPPER_TARGET = 0x3AC4B0

# Original direct BL edges across Connect -> CTGcp -> DH -> SYN -> ACK.
REQUIRED_CALLS = {
    0x3C93FC: {0x3C6950: "CGCloudConnector13connectTConnd"},
    0x3A62A0: {0x3C6956: "CGCloudConnector13connectTConnd"},
    0x3A3D18: {
        0x3C6A70: "CGCloudConnector13connectTConnd",
        0x3C6BD4: "CGCloudConnector13connectTConnd",
    },
    0x3A7D0C: {0x3A3D7A: "CTGcp10Initialize"},
    0x3A7E40: {0x3A3EF6: "CTGcp10Initialize"},
    0x3A7E2A: {0x3A7FCA: "gcloud_tgcpapi_init"},
    0x27E9DE: {0x3AC5E6: "gcloud_tgcpapi_set_dh_info"},
    0x3AB9E0: {0x3ABAA0: "gcloud_tgcpapi_send_syn_msg"},
    0x3ABD7C: {0x3ABEF2: "gcloud_tgcpapi_recv_and_decrypt_pkg"},
    0x3AB24A: {0x3ABEFE: "gcloud_tgcpapi_recv_and_decrypt_pkg"},
    0x27E9E8: {0x3ABDC8: "tgcpapi_compute_k"},
    0x27FC64: {0x3ABDF4: "tgcpapi_compute_k"},
    0x3AC0B8: {0x3A9FB0: "OnStateKeySyning"},
    0x3AB964: {0x3A9FD8: "OnStateKeySyning"},
    0x3C68E0: {
        0x3C6F4A: "CGCloudConnector7Connect",
        0x3C6FC2: "CGCloudConnector7Connect",
    },
    0x3A33A0: {0x3C6C4A: "CGCloudConnector13connectTConnd"},
    0x3A369C: {0x3C6C86: "CGCloudConnector13connectTConnd"},
}

# Symbol start/size identity pins: this prevents a similar-named or legacy
# receiver from being substituted into the GCloud source chain.
FUNCTIONS = {
    0x3C68E0: (1204, "CGCloudConnector13connectTConnd"),
    0x3A3D18: (624, "CTGcp10Initialize"),
    0x3A7E40: (684, "gcloud_tgcpapi_init"),
    0x3A7E2A: (22, "gcloud_tgcpapi_set_dh"),
    0x3AC4B0: (436, "gcloud_tgcpapi_set_dh_info"),
    0x3AB9E0: (124, "tgcpapi_generate_dh"),
    0x3ABA5C: (556, "gcloud_tgcpapi_send_syn_msg"),
    0x3ABD7C: (184, "tgcpapi_compute_k"),
    0x3ABE34: (644, "gcloud_tgcpapi_recv_and_decrypt_pkg"),
    0x3AC0B8: (316, "gcloud_tgcpapi_recv_ack_msg"),
    0x3A9F8C: (106, "OnStateKeySyning"),
}


def verify_wrapper(read16, symbols):
    for address, expected in DH_WRAPPER_PINS.items():
        if read16(address) != expected:
            raise ValueError("conditional DH wrapper instruction changed")
    destination = decode_thumb_b_w(
        read16(0x3A7E3C), read16(0x3A7E3E), 0x3A7E3C
    )
    if destination != DH_WRAPPER_TARGET:
        raise ValueError("DH wrapper tail target changed")
    if "gcloud_tgcpapi_set_dh" not in symbols.get(0x3A7E2A, ""):
        raise ValueError("DH wrapper symbol mismatch")
    if "gcloud_tgcpapi_set_dh_info" not in symbols.get(DH_WRAPPER_TARGET, ""):
        raise ValueError("DH setup target symbol mismatch")
    return True


def verify_functions(functions):
    for address, (size, name_part) in FUNCTIONS.items():
        hits = [f for f in functions
                if f.address == address and f.size == size and name_part in f.name]
        if len(hits) != 1:
            raise ValueError("original GCloud function identity mismatch")
    return True


def verify_calls(observed, functions):
    if set(observed) != set(REQUIRED_CALLS):
        raise ValueError("wrong GCloud DH/ACK callgraph target set")
    for target, sites in REQUIRED_CALLS.items():
        if not set(sites).issubset(observed[target]):
            raise ValueError("required GCloud DH/ACK edge missing")
        for site, owner in sites.items():
            if owner not in (containing_symbol(functions, site) or ""):
                raise ValueError("GCloud DH/ACK edge owner mismatch")
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

    executable, functions = parse_elf(raw)
    symbols = {}
    for function in functions:
        symbols.setdefault(function.address, function.name)
    verify_wrapper(read16, symbols)
    verify_functions(functions)
    verify_calls(direct_calls(raw, executable, REQUIRED_CALLS), functions)
    return {
        "evidence": "EXACT_ORIGINAL_SHA_PINNED_STATIC",
        "original_apollo_verified": True,
        "gcloud_connect_to_ctgcp_initialize_edges": 2,
        "dh_wrapper_tail_branch_verified": True,
        "dh_generate_key_call_verified": True,
        "syn_serializes_local_dh_public_component": True,
        "ack_mode3_compute_k_and_set_key_edges_verified": True,
        "compute_k_uses_dh_compute_key_and_md5": True,
        "key_sync_ack_then_auth_request_edges_verified": True,
        "phone_dh_parameter_string": "NOT_PROVEN",
        "phone_ack_key_mode": "NOT_PROVEN",
        "second_service_key_response_accepted": False,
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

"""R060: source-pinned dual ACK/auth receive pipeline audit in CF2018 Apollo.

The original transport contains *legacy* tgcpapi_* and *GCloud*
gcloud_tgcpapi_* pipelines with different state handlers and packet gatherers.
This file validates direct-call ownership only. No ACK generation, sockets,
credential handling, original library copying or game patching.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from r057_original_address_callers import (
    ORIGINAL_SHA, ORIGINAL_SIZE, parse_elf, direct_calls, containing_symbol
)

# Exact original ARM Thumb BL locations, independently observed on the native ELF.
# Named source owners are checked, not merely the destination address.
RECEIVER_CALLS = {
    0x1C195C: {
        0x1BAD08: "tgcpapi_start_connection",
        0x1BEB6A: "OnStateKeySyning",
    },
    0x3AC0B8: {
        0x3A845A: "gcloud_tgcpapi_start_connection",
        0x3A9FB0: "OnStateKeySyning",
    },
    0x1C1E34: {
        0x1BADF0: "tgcpapi_start_connection",
        0x1BB47E: "tgcpapi_relay_connection",
        0x1BEC68: "OnStateAuthing",
    },
    0x3AC306: {
        0x3A850A: "gcloud_tgcpapi_start_connection",
        0x3A8A5E: "gcloud_tgcpapi_relay_connection",
        0x3AA012: "OnStateAuthing",
    },
    0x1C0C50: {
        0x1BEF10: "OnStateDone",
        0x1C17CA: "tgcpapi_recv_and_decrypt_pkg",
    },
    0x3AB5EC: {
        0x3AA14C: "OnStateDone",
        0x3ABE4C: "gcloud_tgcpapi_recv_and_decrypt_pkg",
    },
}


# Matching original SYN transmission lanes (three callsites per sender).
# Pin both directions before selecting a second-service ACK implementation.
SYN_CALLS = {
    0x1C1544: {
        0x1BAC32: "tgcpapi_start_connection",
        0x1BB276: "tgcpapi_relay_connection",
        0x1BEAFA: "OnStateTcpSyning",
    },
    0x3ABA5C: {
        0x3A83C6: "gcloud_tgcpapi_start_connection",
        0x3A8936: "gcloud_tgcpapi_relay_connection",
        0x3A9F52: "OnStateTcpSyning",
    },
}

# Full receiving-function identities, NOT payload compatibility assertions.
# Exact original symbol starts/sizes were verified in the 2018 ELF.
RECEIVERS = {
    "legacy_ack": (0x1C195C, 788, "tgcpapi_recv_ack_msg"),
    "gcloud_ack": (0x3AC0B8, 316, "gcloud_tgcpapi_recv_ack_msg"),
    "legacy_auth": (0x1C1E34, 540, "tgcpapi_recv_authrsp_msg"),
    "gcloud_auth": (0x3AC306, 152, "gcloud_tgcpapi_recv_authrsp_msg"),
}


def validate_function_identities(funcs, identities=RECEIVERS):
    for key, (start, length, needle) in identities.items():
        matching = [f for f in funcs if f.address == start
                    and f.size == length and needle in f.name]
        if len(matching) != 1:
            raise ValueError("original receive function identity differs")


def validate_edges(callsets, funcs, requirements=RECEIVER_CALLS):
    if set(callsets) != set(requirements):
        raise ValueError("missing/extra tracked receiver")
    for target, expected in requirements.items():
        if callsets[target] != set(expected):
            raise ValueError("unexpected direct callers for receiver")
        for site, owner_part in expected.items():
            owner = containing_symbol(funcs, site) or ""
            if owner_part not in owner:
                raise ValueError("receiver call owned by unexpected function")


def audit(path):
    path = Path(path)
    if path.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("original source size mismatch")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("original source SHA mismatch")
    executable, funcs = parse_elf(raw)
    validate_function_identities(funcs)
    callsets = direct_calls(raw, executable, RECEIVER_CALLS)
    validate_edges(callsets, funcs)
    syn_calls = direct_calls(raw, executable, SYN_CALLS)
    validate_edges(syn_calls, funcs, SYN_CALLS)
    return {
        "evidence": "ORIGINAL_APOLLO_DIRECT_CALL_STATIC",
        "original_sha_valid": True,
        "original_receiver_identities_checked": len(RECEIVERS),
        "direct_receiver_calls_checked": sum(len(c) for c in RECEIVER_CALLS.values()),
        "direct_syn_sender_calls_checked": sum(len(c) for c in SYN_CALLS.values()),
        "legacy_and_gcloud_syn_senders_differ": True,
        "legacy_and_gcloud_ack_receiver_differ": True,
        "legacy_and_gcloud_auth_receiver_differ": True,
        "legacy_and_gcloud_gather_receiver_differ": True,
        "second_service_stack_on_phone": "NOT_VERIFIED",
        "same_ack_bytes_valid_across_stacks": "NOT_VERIFIED",
        "second_service_handshake_accepted": False,
        "game_login_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-lib", required=True)
    args = parser.parse_args()
    try:
        result = audit(args.original_lib)
    except (ValueError, OSError):
        print(json.dumps({"status": "REFUSED", "reason": "SOURCE_OR_CALLGRAPH_MISMATCH"}))
        raise SystemExit(2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

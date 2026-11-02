"""R078: CTDir-to-GCloud ACK lineage, static provenance only.

This is a *conditional* path audit. It proves selected original direct BL
edges on a supplied SHA-pinned private Apollo; it does not prove that Android
called CTDir::Update, selected this connector, accepted an ACK, or logged in.

This module neither sends packets nor constructs an ACK. No route values,
account fields or native bytes are exported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from r057_original_address_callers import (
    ORIGINAL_SHA, ORIGINAL_SIZE, EXPECTED as R057_EDGES,
    containing_symbol, direct_calls, parse_elf,
)
from r060_dual_ack_receivers import (
    RECEIVER_CALLS, validate_function_identities as validate_receiver_identities,
)
from r061_ack_body_decoder_fork import (
    DECODER_CALLS, validate_identifiers as validate_decoder_identities,
)
from r073_rpc_initialization_order import EDGES as RPC_EDGES

# Only prior independently grounded Apollo callsites. Targets for which other
# callers could exist are checked as required subsets, never asserted exclusive.
REQUIRED_CALLS = {
    0x3C4530: RPC_EDGES[0x3C4530],       # CTDir::Initialize -> RpcConnector::Init
    0x3C4F78: RPC_EDGES[0x3C4F78],       # RpcConnector::Update -> CreateConnection
    0x3A62A0: {0x3C6956: "CGCloudConnector"},  # GCloud TGCP constructor
    0x3A33A0: R057_EDGES[0x3A33A0],     # CGCloudConnector applies route
    0x3A369C: {0x3C6C86: "CGCloudConnector"},  # GCloud start
    0x3AC0B8: RECEIVER_CALLS[0x3AC0B8], # GCloud start/key state -> ACK receiver
    0x3B8860: DECODER_CALLS[0x3B8860],   # GCloud ACK/auth -> TLV decoder
}
EXACT_CALLSETS = frozenset({
    0x3C4530, 0x3C4F78, 0x3A33A0, 0x3AC0B8,
})
EXPECTED_CHAIN = (
    "CTDIR_INITIALIZE_TO_RPC_INIT",
    "RPC_UPDATE_TO_CREATE_CONNECTION",
    "GCLOUD_CONSTRUCTOR",
    "GCLOUD_ROUTE_SETTER",
    "GCLOUD_TRANSPORT_START",
    "GCLOUD_ACK_RECEIVER",
    "GCLOUD_ACK_BODY_TLV_DECODER",
)
GAPS = (
    "CTDIR_RUNTIME_UPDATE_SCHEDULING",
    "RPC_TO_GCLOUD_OBJECT_SELECTION_AT_RUNTIME",
    "PHONE_SECOND_SERVICE_RECEIVER_EXECUTION",
    "SECOND_SERVICE_ACK_KEY_AND_SESSION_VALIDATION",
)


def verify_edges(observed, functions, required=REQUIRED_CALLS):
    """Fail on missing/wrong pinned edge or caller. No synthetic packet input."""
    if set(observed) != set(required):
        raise ValueError("watched target set mismatch")
    for target, expected in required.items():
        sites = set(observed[target])
        if target in EXACT_CALLSETS and sites != set(expected):
            raise ValueError("exact original caller set mismatch")
        if not set(expected).issubset(sites):
            raise ValueError("original direct call missing")
        for site, owner in expected.items():
            if owner not in (containing_symbol(functions, site) or ""):
                raise ValueError("callsite owner differs from pinned original")
    return True


def audit(original):
    path = Path(original)
    if path.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("private Apollo size mismatch")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("private Apollo SHA mismatch")
    executable, functions = parse_elf(raw)
    verify_edges(direct_calls(raw, executable, REQUIRED_CALLS), functions)
    validate_receiver_identities(functions)
    validate_decoder_identities(functions)
    return {
        "evidence": "EXACT_ORIGINAL_STATIC_DIRECT_CALLS_ONLY",
        "original_apollo_verified": True,
        "required_direct_edges": sum(map(len, REQUIRED_CALLS.values())),
        "verified_chain_components": EXPECTED_CHAIN,
        "unproven_dynamic_handoffs": GAPS,
        "conditional_receiver_if_gcloud_path": "GCLOUD_TGCP_ACK_THEN_TLV_BODY",
        "legacy_receiver_interchangeable": False,
        "phone_ctdir_runtime_execution": "NOT_PROVEN",
        "second_service_ack_accepted": False,
        "game_login_verified": False,
        "network_started": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-lib", required=True)
    args = parser.parse_args()
    try:
        result = audit(args.original_lib)
    except (ValueError, OSError) as exc:
        print(json.dumps({
            "status": "REFUSED", "reason": type(exc).__name__,
            "network_started": False,
        }))
        raise SystemExit(2) from None
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

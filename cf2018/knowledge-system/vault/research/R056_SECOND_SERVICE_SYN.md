# R056 — Fail-closed second-service SYN dispatch for the fake-server lane

Date: 2026-11-02. Scope: **original CF2018 client-server protocol restoration**. Evidence: previously confirmed R037/R039 phone A/B behavior + R037 original-native route-serialization pins + new SOURCE-ONLY implementation and PUBLIC CI tests. No APK editing, standalone map research, new original-binary emulation or phone experiment.

## Problem this code actually solves

The owner's real CF2018 2018 client first sends a **133-byte** `QueryAddrSvr` named-route `0x1001` SYN. A correctly RPC64-correlated candidate address-service `0x4013` reply in R037 was associated with later **131-byte** SYNs carrying a distinct 10-byte route name; R039's wrong-RPC64 control kept all reference SYNs. This is a real protocol transition but not authentication.

The existing 63-byte synthetic first-service ACK is qualified against one exact reference SYN. R042 original TGCP ACK-head has *no route field14* but that does not prove that session, timestamp, key response, server service identity or other checks remain equivalent. Automatically ACKing the 131-byte SYN would be an ungrounded live experiment.

## Added server-side module

[`experiments/r056_second_service_syn.py`](../../../experiments/r056_second_service_syn.py) accepts one bounded **complete** first TCP frame in memory (original two-byte `43 66` + AA-framed TGCP data), reuses the strict local `Receiver` and TLV parsing tools, and checks:

- Exactly one complete frame, size 32–1,024, no trailing data or premature EOF;
- Valid AA framing, outer nested base and extension, SYN extension type `0x1001`;
- SYN field14 kind5 → named-route variant4 kind5 → field1 kind5 route name;
- Existing first-service reference name `QueryAddrSvr` versus a **different** name of exactly ten bytes;
- Invalid/unsupported variants, duplicate fields, lengths, malformed input and non-SYN types fail closed.

It emits **only** two fixed public labels per candidate: `REFERENCE_NAMED_ROUTE_CANDIDATE/DEFER_TO_PINNED_REFERENCE_GATE`, `TEN_BYTE_NAMED_ROUTE_CANDIDATE/HOLD_NO_ACK`, `OTHER_NAMED_ROUTE/HOLD_NO_ACK`, or `UNRECOGNIZED_OR_INCOMPLETE_SYN/NO_ACK`. It never emits name, RPC64, frame, address, token or secret. For the original QueryAddrSvr it still defers to the *existing byte-identical reference gate*; the parser does not authorize the old ACK by itself. For second-service SYN it explicitly holds, with no invented ACK/session bytes. No networking or auto-run.

Test file [`tests/test_r056_second_service_syn.py`](../../../tests/test_r056_second_service_syn.py): **10 synthetic unit methods** with positive reference and ten-byte named-route classification, other names, non-SYN type, alternate variants, duplicate fields, truncated/coalesced input, wrong preamble, body/trailing bytes, size/type checks and sanitized output. Synthetic fixture is a **minimal structural TLV**, not an extracted original SYN. [GitHub Actions 41341222988](https://github.com/despairarc000/temp/actions/runs/41341222988) completed **SUCCESS**, including knowledge doctor and unit tests. This does not prove native parser equivalence, that exact real 131-byte SYN is accepted by this strict subset, or game login.

## Integration status / next falsifiable work

**NOT YET integrated into the owner's currently running Termux v3.8/v3.8.1 fake-server script**: that exact private ZIP's runtime first-frame handler was not reopened/verified in this run, and blind string replacement into the server would be unsafe. Existing source-only tests run from the public repository; they are not a phone/tested-server deployment.

For an actual next server step, use the original pinned private v3.8 source and locate **its actual first-frame dispatch hook**. Integrate only the fixed-label classifier before the strict reference-SYN check, preserving all old ACK/auth/Bingo bytes, run IDs, per-connection timeouts, SOCKS5 selected IP/port routing and non-target passthrough. Add a synthetic **two-connection** test: reference 133-byte first SYN gets only the existing reference stage; distinct valid 131-byte named-route is recognized but gets **NO** speculative ACK; negative malformed/unknown routes receive no response. Exact source/fixture hashes and A/B lifecycle must be pinned. A real phone test is not justified until the second-service ACK/session requirement is supported by original code.

In parallel the outstanding native question remains: identify the source of the 10-byte route and the route-specific `0x1002` ACK/session security (R046–R050/R042), without assuming that GCloud and NApollo are the same connector path.

**Outcome:** Server-side next-route classification and safe dispatch policy are implemented, CI-verified and bounded. No second-service handshake or login acceptance achieved.

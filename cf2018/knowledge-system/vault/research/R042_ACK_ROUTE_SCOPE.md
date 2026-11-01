# R042 — Original TGCP ACK structure and downstream service evidence

Date: 2026-11-01. **Evidence:** exact original Apollo read-only static code plus source-free tests; R037/R039 live phone A/B results from previous runs; read-only previous XAPK comparison report. **No R042 phone test. No real authenticated login, lobby, TDM or bots.**

## Status of the "big blocker"

The old question "can a correctly correlated incoming 0x4013 reply influence the original client" has a **strong positive behavioral signal**: correct 64-bit RPC sequence in four separately tested active runs led to shorter SYNs; the wrong-sequence R039 phone test, close-only R038 and passive R034 instead retained the original 133-byte QueryAddrSvr SYNs. The user's R039 report explicitly verified the reply had a deliberately wrong RPC64, with all other reply bytes the same, and showed **four exact reference SYNs**. This is strong evidence of a response-driven next-service transition, but not a native callback trace or verified acceptance of every reply field.

The subsequent 131-byte SYNs retain the named-route variant4, and the name field is exactly 2 bytes shorter than reference QueryAddrSvr (12 -> 10). The actual 10-byte route value is deliberately not retained. We are **past a key first-service question, still inside the larger login/next-service blocker**.

## New original-native result: ACK head has no service route

Read-only SHA256-pinned libapollo.so (5,243,704 bytes; SHA256 4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8). Original `gcloud_gcp::TGCPAckHead::packTLVWithVarint` at 0x3b58d0 emits exactly the six field tags `0x11,0x21,0x35,0x41,0x50,0x60` (fields1..6). Field3 is a nested `TGCPKeyRsp` serialized at 0x3b5926 through 0x3afefa. It has **no field14 route element and does not call the TGCPRouteInfo serializer** in this function. The constructor at 0x3b589a gives window field5 default0x400, not a full guarantee of all server runtime defaults. Original `gcloud_tgcpapi_recv_ack_msg` checks response packet type `0x1002` at 0x3ac106–0x3ac11c and then handles further body/state (0x3ac1b6). `0x1001` is the SYN family.

The current synthetic ACK builder was **deliberately limited in research code to an exact 133-byte QueryAddrSvr SYN and refuses any other service**. This is a restriction of our test harness, not proof that the original packet format requires the old name. The original ACK **head** itself is route-independent, but the client's **whole-packet state, session key and key-response checks may still vary**. Reusing the exact 63-byte ACK for an unknown 131-byte route is **NOT justified** without native end-to-end acceptance tests.

Hash-pinned original-static audit [native_ack_route_scope_audit.py](../../../experiments/native_ack_route_scope_audit.py) has **12/12 Thumb instruction pins PASS**, and [7 focused tests](../../../tests/test_native_ack_route_scope_audit.py) all PASS against the original private library, including missing/mutated pin negatives. No original .so, original game files, or route-name values are committed.

## Application-side evidence availability

Local private workspace has `CF2018_libapollo.so` (generic Apollo transport) and source-only harnesses. GitHub research repository contains source-only metadata/scripts, **not** the original Unity game client DLL or APK. Connected Google Drive search found the user's previously investigated **unpacked OBB folder**, but no directly accessible `Assembly-CSharp.dll` or `Original.xapk`. The preexisting owner's `CF2018_XAPK_Comparison_Report.txt` identifies the **original XAPK stored on Termux as `~/storage/downloads/Original.xapk`** at that time and containing `com.tencent.tmgp.cfmnac.apk` -> `assets/bin/Data/Managed/Assembly-CSharp.dll`. This is an *older report*, not a claim the phone still has the file today. It identified the original DLL SHA256 as `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9`. The original managed game DLL is a much better candidate than generic Apollo for finding the **caller-supplied 10-byte downstream service name** and result callback consumer.

## Next priority

1. **Read-only acquire** original game's `Assembly-CSharp.dll` from the locally retained original XAPK if available. Never commit proprietary DLL or raw account/game data to GitHub. Validate SHA256 before deeper disassembly. Inspect managed methods that call `GetServiceAddress`/GCloud connector, and service configuration to identify downstream 10-byte named route.
2. Independently trace ACK **outer framing, per-connection session/key-response processing** in original Apollo and construct a narrowly-scoped synthetic 131-byte SYN reply only after original-native preflight. ACK head route-independent is useful but **not** proof a generic ACK will be accepted.
3. Do not repeat R039 or send guessed service ACK. No new phone experiment until a protocol-specific, one-variable question remains unresolved.

**Milestones:** first-stage reply-induced route transition: observed; pending RPC64 dependency: strongly supported by A/B control; second-service name: unknown; second-service handshake: unverified; authenticated game/lobby/bots: not achieved.

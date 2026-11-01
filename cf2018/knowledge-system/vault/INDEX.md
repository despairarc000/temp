# Vault — evidence and operating memory
- [CHECKPOINT](CHECKPOINT.md) — latest verified project status.
- [EVIDENCE](EVIDENCE.md) — evidence IDs and limitations.
- [OPEN_QUESTIONS](OPEN_QUESTIONS.md) — exact unknowns and next tests.
- [WORKLOG](WORKLOG.md) — historical handoff.
- [ACK_RECEIVER](research/ACK_RECEIVER.md) — hash-scoped receiver trace and remaining session gate.
- [TGCP](research/TGCP.md) — native handshake/ACK research.
- [RELAY](research/RELAY.md) — tested passive transport core and EOF evidence limits.
- [STARTUP](research/STARTUP.md) — APK editing failure and controls.
- [ACCEPTANCE](specs/ACCEPTANCE.md) — milestone gates.
- [ADR-0001](decisions/ADR-0001-LOCAL-BRIDGE.md) — local bridge architecture.
- [ADR-0002](decisions/ADR-0002-HASH-SCOPED-NATIVE.md) — hash-scoped native evidence and offline framing.

Every new claim requires date, status, source, what was observed, what is inferred, and a falsifying test. Statuses: CONFIRMED_ON_PHONE, CONFIRMED_NATIVE_STATIC, LOCAL_TEST_ONLY, HYPOTHESIS, UNKNOWN, DISPROVEN, SUPERSEDED. Never silently promote a hypothesis to measured behavior.

- [AUTH_RECEIVER](research/AUTH_RECEIVER.md) — exact v1.2 earliest native failure, correction and remaining Bingo/relay gate.

- [BINGO_SESSION](research/BINGO_SESSION.md) — actual negative correlation, WAIT semantics and received relay-field reuse.

- [CONNECTION_CALLBACKS](research/CONNECTION_CALLBACKS.md) — actual local success notification and AddressService buffer boundary, not authentication.

- [INTEGRITY_NATIVE](research/INTEGRITY_NATIVE.md) — protected on-disk assembly, Mono provider detour and bounded termination predicate; historical phone cause still unknown.

- [SERVER_PATH](research/SERVER_PATH.md) — latest phone progression, server-vs-integrity priority and actual routed TX boundary.

- [V38_BLOCKER](research/V38_BLOCKER.md) — latest uploaded report, classifier/source gap and native compression/encryption distinction.

[V38_SOURCE_AUDIT — native stage/serializer differential and metadata diagnostic](research/V38_SOURCE_AUDIT.md).

**All task routes now include [CURRENT_HANDOFF](../../coordination/CURRENT_HANDOFF.md)**: actual PCAPdroid/Termux workflow and next diagnostic; old task summaries do not reset progress.

- [ADDRESS_APPLICATION](research/ADDRESS_APPLICATION.md) — actual native arguments, required reason field, strict preflight correction and remaining runtime evidence.

- [PHONE_V381](research/PHONE_V381.md) — latest actual phone evidence and next producer target.

- [REPOSITORY_SOURCE_AUDIT](research/REPOSITORY_SOURCE_AUDIT.md) — exact local source availability, repository reconciliation and upstream queue trace.

- [UPSTREAM_REQUEST_CHAIN](research/UPSTREAM_REQUEST_CHAIN.md) — source-verified AddressService/MsgBuffer/connector/routed-TGCP send chain and on-phone limits.

- [R024_PROTOCOL_CALLS](research/RPC_PROTOCOL_CALLSITE_R024.md) — original RpcConnector direct initialization caller audit; three use binary type 0x20.
- [R025_QUALIFIED_ADDRESS](research/QUALIFIED_ADDRESS_ROUTE_R025.md) — original colon-qualified RPC and route setter, explaining diagnostic false negatives; supersedes bare-name exclusion.

- [R027_PHONE_QUALIFIED_RPC](research/PHONE_R027_QUALIFIED_RPC.md) — live-phone structural match for both routed 0x4013 requests, original RX pending-session constraints and offline correlation tests.

- [R028_ADDRESS_RECEIVER](research/ADDRESS_RX_BRANCH_R028.md) — original pending-session and typed response control-flow audit plus loopback-only offline reply construction.

- [R029_INBOUND_CHAIN](research/ADDRESS_INGRESS_R029.md) — original TGCP receive/unpack, queue, connector and address RPC session-dispatch path (static only).

- [R030_4013_INBOUND](research/INBOUND_4013_R030.md) — original native incoming 0x4013 handling, uncompressed/LZ4 branch, and reply-prefix negative controls.

- [R031_INBOUND_PAYLOAD](research/INBOUND_BOUNDARY_R031.md) — 45 original-native instruction pins identifying clear-payload boundaries and offline AA/4013 reply preflight.

- [R032_PER_FRAME_SECURITY](research/INBOUND_BASE_SECURITY_R032.md) — native TGCP base field6 controls per-frame inbound decrypt branch; clear-mode offline validation.

- [R033_ONE_REPLY](research/R033_ONE_REPLY_TEST.md) — source-only, opt-in one-response phone experiment with 113 original and 8 synthetic offline tests; no phone response yet.

- [R034_PHONE_OUTCOME](research/R034_PHONE_REPLY_OUTCOME.md) — one 169-byte send on phone, no observed follow-up, three 131-byte first frames and zero-reply passive diagnostic kit.

- [R035_FIRSTFRAME_CONTROL](research/R035_REPLY_FIRSTFRAME_CONTROL.md) — R034 real-phone four 133-byte reference first frames and source-only R035 active one-reply structural diagnostic, not phone-tested.

- [R036_SYN_LENGTH](research/R036_SYN_LENGTH_INVESTIGATION.md) — real 131-byte 0x1001 SYNs retain base-field shape; source-only nested-length diagnostic, not phone tested.

- [R037_SYN_ROUTE_FIELD14](research/R037_ROUTE_FIELD14.md) — actual R036 131-byte phone SYNs differ only in route field14; exact native route encoder verified; route-shape diagnostic ready.

- [R038_CLOSE_CONTROL](research/R038_CLOSE_CONTROL.md) — real R037 shorter named-route reconnects; source-only early-close-without-4013-reply causal control, phone result pending.

- [R039_RPC64_NEGATIVE](research/R039_RPC64_NEGATIVE_CONTROL.md) — real R038 no-reply close control restored 4/4 original SYNs; R039 wrong RPC64 one-bit A/B phone diagnostic, offline tested.

- [R040_RPC64_PHONE](research/R040_RPC64_PHONE_CONTROL.md) — real R039 wrong-RPC64 phone result: 4 original SYNs, no route transition; original 0x5001 stop-session native attribution and audit.

- [R041_ADDRESS_CALLBACK](research/R041_ADDRESS_CALLBACK_TRACE.md) — original-native 34-pin QueryAddrInfo parse/result0/queued DNS/callback trace; downstream 10-byte route still unknown.

- [R042_ACK_ROUTE_SCOPE](research/R042_ACK_ROUTE_SCOPE.md) — original 12-pin ACK head six-field route-independent serialization; 7 tests, client 0x1002 gate and missing original managed game DLL.

- [R043_MANAGED_ROUTE](research/R043_MANAGED_SERVICE_ROUTE.md) — build-hash-pinned offline Unity managed service-name scanner; source-only kit 16 synthetic tests, real game DLL scan pending.
- [R044_DRIVE_MANAGED](research/R044_DRIVE_MANAGED_CALLGRAPH.md) — original CF2018 Unity application DLL located in Drive, hash verified, real login/lobby Apollo client callgraph, ten-byte named route still unknown.

- [R045_MANAGED_NATIVE](research/R045_MANAGED_NATIVE_ROUTE_ORIGIN.md) — original game managed lobby connector traced into hash-pinned native type4 named-route selection; 17 native pins verified, 9 local tests PASS; next route still unknown.

- [R046_GCLOUD_ROUTE](research/R046_GCLOUD_ROUTE_INTO_SYN.md) — 26 original GCloud static pins trace route type4 setter -> transport handle -> SYN writer, with separate endpoint/ACK gates; phone route value unknown.

- [R047_CONNECTOR_SOURCE](research/R047_CONNECTOR_ROUTE_SOURCE.md) — native GCloud connector clones the route into +0x19c, conditionally applies it to TGCP, then starts; 14 original pins/7 tests passed, upstream caller unknown.

- [R048_INIT_ROUTE](research/R048_CONNECTOR_INIT_ROUTE.md) — GCloud serialized route discriminator +0x44, optional route object +0x48, verified virtual SetRouteInfo slot +0x20, and downstream named-route SYN chain; 23 original pins, 8 tests.

- [R049_MANAGED_ROUTE_BOUNDARY](research/R049_MANAGED_ROUTE_BOUNDARY.md) — original managed CIL has just wrapper->NApollo P/Invoke direct setter call; native GCloud init route is distinct and its runtime source remains unknown.
- [R051_STANDALONE](research/R051_STANDALONE_MATCH_ENTRY_AUDIT.md) — original CIL startup sequencing, menu latency-vs-offline gate, data-driven builder and AI-spawn prerequisites; 36 exact pins, nine offline tests.
- [R052_TRAINING_SPAWN](research/R052_TRAINING_PLAYER_SPAWN_INHERITANCE.md) — AITrainGame inherits PVE StartMatch, which calls actual controller and initial pawn spawn; seven inherited TypeDef pins and 14 CIL method pins, seven offline tests.

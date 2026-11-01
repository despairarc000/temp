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

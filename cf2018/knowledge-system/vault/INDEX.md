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

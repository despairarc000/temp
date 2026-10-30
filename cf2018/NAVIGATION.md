# NAVIGATION — CF2018 ICM entrypoint

| Task | Read first | Then |
|---|---|---|
| Mission/scope | [IDEA_PLAN](IDEA_PLAN.md) | [ACCEPTANCE](knowledge-system/vault/specs/ACCEPTANCE.md) |
| Current work and blockers | [CHECKPOINT](knowledge-system/vault/CHECKPOINT.md) | [WORKLOG](knowledge-system/vault/WORKLOG.md) |
| TGCP, ACK, framing, Apollo | [Reviewed receiver](knowledge-system/vault/research/ACK_RECEIVER.md), [body/session continuation](knowledge-system/vault/research/ACK_SESSION.md), [TGCP](knowledge-system/vault/research/TGCP.md) | [EVIDENCE](knowledge-system/vault/EVIDENCE.md), [OPEN_QUESTIONS](knowledge-system/vault/OPEN_QUESTIONS.md) |
| Authentication, 0x2001/0x2002, Bingo | [AUTH_RECEIVER](knowledge-system/vault/research/AUTH_RECEIVER.md), [Bingo/session](knowledge-system/vault/research/BINGO_SESSION.md) | [Phone v1.2](coordination/incoming/CF18-05/PHONE_V12_RESULT.md), [assignments](coordination/assignments.json) |
| SOCKS5, PCAPdroid, Termux | [TECHNICAL_PLAN](TECHNICAL_PLAN.md) | [ACCEPTANCE](knowledge-system/vault/specs/ACCEPTANCE.md) |
| Worker ownership / next task | [Assignments](coordination/assignments.json) | [Integration](coordination/INTEGRATION.md) |
| Passive relay diagnostics | [RELAY](knowledge-system/vault/research/RELAY.md) | [Integration](coordination/INTEGRATION.md) |
| Source binaries and assets | [Source provenance](sources/SOURCE_PROVENANCE.md), [DRIVE_MANIFEST](sources/DRIVE_MANIFEST.md) | [EVIDENCE](knowledge-system/vault/EVIDENCE.md) |
| Startup / patch integrity | [STARTUP research](knowledge-system/vault/research/STARTUP.md) | [OPEN_QUESTIONS](knowledge-system/vault/OPEN_QUESTIONS.md) |
| Offline bot/game features | [IDEA_PLAN](IDEA_PLAN.md) | [IMPLEMENTATION_PLAN](IMPLEMENTATION_PLAN.md), [ACCEPTANCE](knowledge-system/vault/specs/ACCEPTANCE.md) |
| Decisions | [ADR-0001](knowledge-system/vault/decisions/ADR-0001-LOCAL-BRIDGE.md) | [OPEN_QUESTIONS](knowledge-system/vault/OPEN_QUESTIONS.md) |
| Knowledge tooling | [ICM](knowledge-system/icm/ICM.md) | [Graphify](knowledge-system/graphify/GRAPHIFY.md), [Vault index](knowledge-system/vault/INDEX.md) |

Cold start: AGENTS → NAVIGATION → IDEA_PLAN → CHECKPOINT → task route `python tools/knowledge.py route tgcp ack` → linked source/test evidence → implement or research → doctor/tests → update vault.

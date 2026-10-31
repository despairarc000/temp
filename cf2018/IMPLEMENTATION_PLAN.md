# IMPLEMENTATION PLAN — phase gates

| Gate | Work | Exit evidence |
|---|---|---|
| G0 | Source inventory, permission, APK/XAPK/OBB identity, build controls | hashes, original asset manifest, original-code baseline |
| G1 | Stable no-root local bridge | on-device capture of real client bytes and correct passthrough — **PASS for known TCP targets** |
| G2 | TGCP ACK / auth | post-ACK 0x2001 CONFIRMED ON PHONE; verified auth/session still **BLOCKED** |
| G3 | Address discovery | client requests address service and accepts locally issued service address |
| G4 | Update/config/resources | proceeds past Checking for update packages with original assets |
| G5 | Offline identity / lobby | can enter/offline navigate actual game interface without remote dependency |
| G6 | TDM bots | full match, bot AI, damage, scoring, end & replay |
| G7 | Bomb/S&D bots | objectives, bombs, rounds, AI, end & replay |
| G8 | packaging and recovery | repeatable launch, reboot/reinstall controls, no proprietary distribution |

**Immediate queue:** [server path review and native routed TX](knowledge-system/vault/research/SERVER_PATH.md).
Phone v1.4 corrected auth removes immediate EOF; v1.5/v1.6 synthetic Bingo elicits
authentic0x4013 in3/4 trials. Identify inner application RPC and reciprocal routed
receiver before issuing a reply. Auth/account and G3 service acceptance remain
unverified. This is beyond first transport hop, still early in the playable-game
mission. Park managed editing: no decoded round trip and no verified safe patch.
Do not discard its findings. No new phone experiment or schedule automatically.

## Current source and implementation boundary

Current operational handoff and patch kit: [CURRENT_HANDOFF](coordination/CURRENT_HANDOFF.md). Exact v38 bridge source was supplied and audited; no blanket deployed-source blocker remains. The ready v3.8.1 diagnostic preserves replies and uses the existing PCAPdroid/Termux path, owner manual opt-in only. Older component-boundary paragraphs below are historical.

[Recovered mirror provenance](sources/SOURCE_PROVENANCE.md) supports hash-specific
native/managed analysis: package/version, library ISA/hashes and internal signature
are checked. Historical phone embedded APK hash parity is reported; G0 remains partial on current installed/full-XAPK/OBB equality.
No blanket missing-library blocker applies to this verified mirror on the current
runner, but every activation must check actual private source access.

Canonical offline framing and source verification are integrated with explicit
subset/identity limits. Relay core and SOCKS5 handoff are bounded local stages;
full bridge wiring awaits the historical/deployed passthrough interface. An envelope-only A/B/C comparison is justified in principle but not ready to run. [Assignments](coordination/assignments.json)
reserve non-overlapping tasks; [ADR-0002](knowledge-system/vault/decisions/ADR-0002-HASH-SCOPED-NATIVE.md)
records the evidence boundary.

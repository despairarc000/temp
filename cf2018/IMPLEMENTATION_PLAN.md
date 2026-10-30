# IMPLEMENTATION PLAN — phase gates

| Gate | Work | Exit evidence |
|---|---|---|
| G0 | Source inventory, permission, APK/XAPK/OBB identity, build controls | hashes, original asset manifest, original-code baseline |
| G1 | Stable no-root local bridge | on-device capture of real client bytes and correct passthrough — **PASS for known TCP targets** |
| G2 | TGCP ACK / auth | authentic client emits a new post-ACK packet, then verified session state — **BLOCKED** |
| G3 | Address discovery | client requests address service and accepts locally issued service address |
| G4 | Update/config/resources | proceeds past Checking for update packages with original assets |
| G5 | Offline identity / lobby | can enter/offline navigate actual game interface without remote dependency |
| G6 | TDM bots | full match, bot AI, damage, scoring, end & replay |
| G7 | Bomb/S&D bots | objectives, bombs, rounds, AI, end & replay |
| G8 | packaging and recovery | repeatable launch, reboot/reinstall controls, no proprietary distribution |

**Immediate queue:** continue [CF18-G2-ACK-01](knowledge-system/vault/research/ACK_RECEIVER.md)
on downstream copied-account/Bingo/session validation after the reviewed
[body continuation](knowledge-system/vault/research/ACK_SESSION.md); separately finish native framing
boundaries and recover actual runtime/relay evidence. G2 requires an authentic
later client protocol packet, never parser/emulation success. Bot implementation
remains deferred.

## Current source and implementation boundary

[Recovered mirror provenance](sources/SOURCE_PROVENANCE.md) supports hash-specific
native/managed analysis: package/version, library ISA/hashes and internal signature
are checked. G0 remains partial on historical phone/full-XAPK/OBB equality.
No blanket missing-library blocker applies to this verified mirror on the current
runner, but every activation must check actual private source access.

Canonical offline framing and source verification are integrated with explicit
subset/identity limits. Relay core and SOCKS5 handoff are bounded local stages;
full bridge wiring awaits the historical/deployed passthrough interface. No
on-device A/B/C proposal is ready. [Assignments](coordination/assignments.json)
reserve non-overlapping tasks; [ADR-0002](knowledge-system/vault/decisions/ADR-0002-HASH-SCOPED-NATIVE.md)
records the evidence boundary.

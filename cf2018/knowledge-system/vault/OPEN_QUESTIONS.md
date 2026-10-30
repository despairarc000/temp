# OPEN QUESTIONS — bounded P0 queue

| ID | Remaining question | Current evidence / next falsifiable action | State |
|---|---|---|---|
| Q-01 | Which incoming envelope is used by the actual phone runtime? | Pinned mirror GCloud path decodes AA/99 then compares decoded 0x4366; both raw prefix orders fail. Compare phone hash/path; framing lane owns remaining 99/bounds/lookahead trace. | MIRROR_PATH_RECONCILED / PHONE_UNVERIFIED |
| Q-02 | What originated historical early EOF? | Original v0.1-v0.8 relay/captures or verified deployed post-method interface still needed; local core/handoff tests do not attribute that EOF. | UNKNOWN / BLOCKED_SOURCE |
| Q-03 | Which server base/session fields are generated, echoed or zeroed? | Bounded mirror ACK functions contain no observed SYN-base equality check; no server policy follows. Received timestamp feeds auth-request +0x50c; source/echo policy unknown. Continue copied-account/Bingo/session checks. | PARTIAL_NATIVE / READY_RESEARCH |
| Q-04 | Is key mode 0 compatible with actual negotiation and later messages? | Mirror empty-body branch skips key setup, but later encrypted body can return -31. Optional body/copy branches reviewed, downstream session/crypto use unfinished; verify actual SYN/phone context; no successful DH/cipher negotiation yet. | PARTIAL_NATIVE / PHONE_UNVERIFIED |
| Q-05 | What does actual client send after ACK? | Mirror reaches suppressed auth-send; timestamp feeds its buildup. Separate 0x2002 receiver copies account only after parser zero; copy success controls stub that parser. Need authentic later phone packet after justified ACK; state-handler zero can mean waiting. | STATIC_BOUNDARY_ONLY |
| Q-06 | How to resolve discontinued config DNS safely? | Narrow DNS/local HTTP/TLS research after G2. | BLOCKED_ON_G2 |
| Q-07 | How do recovered source, connected Drive and phone originals relate? | Mirror APK/native/managed hashes and internal signature verified; Drive target-native availability, phone equality and OBB match remain unverified. Await new precise source/hash evidence; no repeated capped scans. | MIRROR_VERIFIED / PHONE_OBB_PARTIAL |
| Q-08 | Which original bot modes/scripts/assets are usable? | No bot implementation before G2; later source-grounded non-overlapping research only. | DEFERRED |

[Receiver trace](research/ACK_RECEIVER.md), [body/session review](research/ACK_SESSION.md), [provenance](../../sources/SOURCE_PROVENANCE.md),
[evidence](EVIDENCE.md), [assignments](../../coordination/assignments.json).
No prefix-only phone retry plan is ready; no repeated 1000-connection retries.

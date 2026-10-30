# OPEN QUESTIONS — current auth receive gate

| ID | Remaining question | Current evidence / next falsifiable action | State |
|---|---|---|---|
| Q-01 | Actual runtime path and framing boundary behavior? | AA_DIRECT advances real phone; pinned GCloud decodes AA/99 then marker4366. CF18-01 boundary0019 submitted; path-selection/wrapper draft unfinished. Review separately; no raw-prefix retry. | PHONE_HOP_CONFIRMED / PATH_PARTIAL |
| Q-02 | Who initiated early EOF? | v1.2 local read_eof is not FIN/RST attribution. Retrieve actual deployed v1.2 bridge source and directional lifecycle; historical0.1–0.8 scripts remain missing. Native body failure does not itself identify socket closer. | UNKNOWN / BLOCKED_SOURCE |
| Q-03 | Generated/echoed base/account/session fields? | Timestamp feeds auth buildup; no general echo rule. Full-wire auth correction reaches copy/state4 under synthetic context; 3002 WAIT and relay-field copy/reuse reviewed; body selector replaces header and mismatched input can reach state5. Meaningful identity/session/application consumers remain open. | PARTIAL_NATIVE / READY_BINGO_RESEARCH |
| Q-04 | Actual keys/encryption/correlation? | Unencrypted exact fixtures pass receive; encryptedflag1/method4/no-key control fails-31 before body. No real key negotiation or arbitrary identifier validity established. | PARTIAL_NATIVE / PHONE_UNVERIFIED |
| Q-05 | Why do v1.2 0x2002 replies fail? | All pass frame/effective2002; missing TGCPBody preamble makes A5 failAA/99, body-32 -> auth-18, before account. Corrected native path waitsBingo/state4. Real phone0x2001 confirmed; auth/session still unverified. | EARLIEST_NATIVE_FAILURE_LOCALIZED / DEPLOYMENT_BLOCKED |
| Q-06 | Safe config/update progression? | Narrow config/DNS work after auth/session evidence. | BLOCKED_ON_G2 |
| Q-07 | Source/phone/OBB relation? | Mirror pins/internal signature verified. CF18-05 reports historical embedded APK/DLL hash parity; original report not newly retrieved here. Current installed APK/runtime/fullXAPK/OBB equality unverified. Await precise new locator. | HISTORICAL_PARITY_REPORTED / OBB_PARTIAL |
| Q-08 | Original bot functionality? | No bot implementation before G2; later separately grounded research only. | DEFERRED |

[Bingo/session](research/BINGO_SESSION.md), [Auth trace](research/AUTH_RECEIVER.md), [ACK trace](research/ACK_RECEIVER.md),
[session](research/ACK_SESSION.md), [source](../../sources/SOURCE_PROVENANCE.md),
[evidence](EVIDENCE.md), [assignments](../../coordination/assignments.json).
V1.4 wrapper-only comparison justified in principle; not ready without deployed
bridge source and directional controls. No automatic phone/network experiment.

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

## Current callback/recovery refinement

Q-03: [connection callbacks](research/CONNECTION_CALLBACKS.md) locally create zero
notification and bind/open buffer without examining connected-info account content
in the examined handler. Still unknown: meaningful subsequent request/response and
account/session validity. Next bounded native target Send_QueryAddrInfo0x3998d4 /
Recv_QueryAddrInfo0x399a98. Never count callback/open as authentication.
Q-02: CF05 c9b1d355 reports actual bridge recovery and prepared v1.4; private package
not independently reopened here, phone directional outcome still absent. No new
payload sweep. All schedules paused by user; assignments are dormant work scopes.

## Q-09 — reliable managed editing / startup exit

[Integrity native investigation](research/INTEGRITY_NATIVE.md): actual stored
Assembly-CSharp/firstpass are non-PE; Mono image loading is detoured to libtprt.
An enabled post-load first4096-byte CRC mismatch can request termination. Which
predicate failed in historical edited build remains UNKNOWN: actual edited file,
precise diff and matched startup/termination logs are absent. Next offline work:
provider context initialization, name-dependent transform selection and exact
round-trip feasibility, before any changed assembly or bypass. Headers alone do
not establish valid IL/Mono loadability. Safe modified build NOT_ESTABLISHED.

Q-09 refinement: original Unity reads through virtual/file paths before Mono. Reproduce that exact buffer and provider initialization; do not assume ciphertext from APK is directly passed unchanged, or that a plain PE replacement is safe. Actual caller diagnostic branch is now controlled separately from protection termination.

## Current priority supersedes earlier ACK/body blockers — 2026-10-31

[Latest reviewed evidence](research/SERVER_PATH.md): v1.4 body fix tested on phone;
v1.5/v1.6 real post-Bingo0x4013 in3/4. Q-05 earliest body issue now fixed in tested
lab path. Q-03/Q-04 remain account/key/identity unknown, not inferred from state5.
New immediate Q-10: which application request/envelope is in the real routed
traffic, and which reciprocal RX path accepts a correlated service response?
TX adds BE packet-sequence32 before application bytes, prior to encryption; not a length.
Kind-filter observer defect explains why absence of hint is inconclusive.
DLL Q-09 remains unresolved and parked; no source round trip or safe edit.

Q-10 latest: [v3.8 report](research/V38_BLOCKER.md) confirms kind5 observed and compression off, but operation remains unidentified. Require actual v3.8 source to verify DataHead mapping/slicing/recognizer policy before another experiment. Compression is independent of encryption. No reply was attempted, so no response rejection diagnosed.

Q-10 source gap resolved by [exact v38 audit](research/V38_SOURCE_AUDIT.md). The native four-byte prefix is packet sequence; earlier UID interpretation corrected. Exact lab stages select method0 and native legacy header passes observer. Actual phone operation still unknown. Prepared fixed-label boundary diagnostic; no new reply until producer/reciprocal receiver evidence.

Current operational refinement: [CURRENT_HANDOFF](../../coordination/CURRENT_HANDOFF.md) supersedes old deployed-source/first-hop blockers for v38. v3.8.1 patch kit is prepared and locally validated through actual SOCKS5 redirector -> fake server, no new phone result. Await fixed-label sequence/header/route result; continue producer/reciprocal receiver offline. Do not request broad raw capture or restart ACK guesses.

Q-10 native refinement: [ADDRESS_APPLICATION](research/ADDRESS_APPLICATION.md) verifies full generated QueryAddrInfo arguments and native-required response reason STRING. Both simple native-produced legacy/strict complete requests are recognized by existing v38 observer. Real unknown packet therefore needs boundary/producer/runtime evidence; another format toggle is not justified. Canonical preflight rejects missing reason, while actual pending-map/accepted endpoint integration remains open.

Q-10 measured refinement: [v381 phone result](research/PHONE_V381.md) supports sequence boundary and identifies exact QueryAddrSvr route. App operation remains unknown; offset4 fails lexical method-name policy. Next trace CTGcp::onDataOutEvent queue producer and reciprocal handler. No repeat boundary test or guessed reply.

Q-07 availability clarification: [re-audit](research/REPOSITORY_SOURCE_AUDIT.md) verifies private extracted APK/Apollo/storedDLLs, not full XAPK/OBB. Q-10 producer continuation now targets upstream callers of CTGcp Write0x3a45bc/0x3a4708 after queue/data/size handoff trace; no repeat phone boundary test.

Q-10 original-native continuation (2026-11-01): [UPSTREAM_REQUEST_CHAIN](research/UPSTREAM_REQUEST_CHAIN.md) statically ties generated AddressService send/arguments and MsgBuffer callback to a concrete connector/routed TGCP queue, with 11/11 instruction pins. The **remaining question** is which concrete runtime producer/transform made the phone's 80/85 bytes fail method-name recognition after the four-byte sequence. Next positive control: execute a bounded synthetic QueryAddrInfo through MsgBuffer::writeEnd and its connector callback, intercept before network, compare with existing v38 observer. Then trace reciprocal RX. No repeated V3.8.1 observer, guessed reply, or inferred auth success.


Q-10 producer check R010 (2026-11-01): [UPSTREAM_REQUEST_CHAIN](research/UPSTREAM_REQUEST_CHAIN.md) now includes a runnable 24-pin original static verifier with six tests. Validates exact callsite and conditional gates, NOT a memory-to-memory native message run. Required next evidence remains the actual full `Send_QueryAddrInfo` message through `MsgBuffer` and its callback, or a grounded proof of why it cannot execute under bounded synthetic context. No live reply is justified.

Q-10 R011 (2026-11-01): Two original-native direct MsgBuffer::bind callsites verified in AddressService::OnConnectProc and RpcConnector::OnConnectProc, 26/26 pinned audit PASS. This adds a concrete alternative bound producer; do not equate the observed QueryAddrSvr route with one bound MsgBuffer without proving ownership. [UPSTREAM_REQUEST_CHAIN](research/UPSTREAM_REQUEST_CHAIN.md). Next: connector/receiver ownership and bounded full-message differential, no phone replay or guessed response.

Q-10 R012 (2026-11-01): Source-pinned native reciprocal RX differentiates AddressService's ProcessResponse/QuerySession lookup from RpcConnector's ProcessMessage/typed response dispatch. 33/33 static checks PASS; this remains non-executed source evidence. Determine actual runtime connector ownership plus pending correlation before any 4013 reply. [UPSTREAM_REQUEST_CHAIN](research/UPSTREAM_REQUEST_CHAIN.md).

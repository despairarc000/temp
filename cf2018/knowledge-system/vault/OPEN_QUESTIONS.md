# OPEN QUESTIONS — current auth receive gate

R073 (2026-11-02): [Original RPC initialization order](research/R073_RPC_INITIALIZATION_ORDER.md) fixes sequence: parse unit-domain during `RpcConnector::Init` before its `AddressService` lookup, with separate `Update → CreateConnection`. This challenges interpretation that R037 reply **contains and sets** next SYN unit; static causal link is unverified. 14 exact original direct BL callsites source-checked; 11 public synthetic tests PASS/one original gate SKIP. Falsify field5 hypothesis with existing value-free `CF2018_SYN_DIFFERENCE_Result.txt`, not new ACK or unpinned phone kit.

R072 (2026-11-02), ORIGINAL NATIVE SOURCE/BOUNDED EMULATION: examined RPC CreateConnection explicitly keeps client-type override selector0, so R071 selector2 is not supplied by this caller. Its differing flag enables SetNameService, not demonstrated security/account change. RPC Init can replace configured unit with a numeric service-domain component; actual parser flow with functional synthetic string/number stubs, original override store and serializer unit1→3 controls pass. Unit1→3 changes only same-length SYN5 and still reaches suppressed auth-send; bad key remains blocked. CTDir is one verified Init caller and configures a10-byte route literal, a compatible candidate not phone attribution.4 native-gated methods PASS. Next use the existing field-number diagnostic to discriminate unit-field explanation from other paths; no new ACK attempt. [Evidence](research/RPC_DOMAIN_UNIT_SOURCE.md).

R071 (2026-11-01 UTC), ORIGINAL NATIVE STATIC/BOUNDED EMULATION: AddressService fixes unit1; connector initialization transfers caller unit to CTGcp. CTGcp starts client type101; connector selector2 overrides102, selector3 overrides0, selector1 sets101. Pinned reference agrees with discovery unit1/type101. Actual serializer:101→102 changes field6 at same length;101→0 shortens it by1, which does not fit R069 if field6 is its sole extra change. GameID comes from shared common state in both inspected branches.5 private-source tests PASS, previous handoff3 PASS. Compatible candidate is not phone identification. No gate relaxation or new phone test. Next trace actual downstream init-info suppliers. [Evidence](research/SYN_ATTRIBUTE_SUPPLIERS.md).

R070 (2026-11-01 UTC), ORIGINAL NATIVE STATIC/EMULATION WITH STUBS: mapped SYN4/5/6 to llGameID/iUnitID/iClientType via original writer and visualize names. Actual SYN preparation and serializer prefix show each synthetic application-attribute change yields exactly one same-length field difference, with key/encryption fields unchanged. All3 changes still reach suppressed auth-send on the same synthetic63-byte ACK.2 new methods/six mutation cases PASS;3 existing native handoff methods/seven cases PASS. This supplies concrete non-security alternatives to R069's extra field change, not that phone field's identity. Gate unchanged; no new phone test requested. Next trace attribute suppliers for address discovery versus next connector. [Evidence](research/NATIVE_SYN_APPLICATION_FIELDS.md).

R069 PHONE RESULT (2026-11-01 UTC): owner one-ACK report shows first-service address reply written, then3 reconnects with131-byte named-route SYNs; all SYN_CONTEXT REFUSED, ACK0. Each has route14 length-2 AND syn_same_length_modified_count1: at least one other SYN field differs, identity unknown. No second ACK attempt occurred; cannot call this ACK rejection or auth progress. New standalone diagnostic copy patch reports changed field numbers/types only and hard-disables next ACK.4 label tests +1 loopback integration +113 original regressions PASS. Next identify that field before native interpretation or weakening any condition. [Evidence](research/SECOND_SERVICE_ACK_PHONE_RESULT.md).

R068 (2026-11-01 UTC), OPTIONAL ONE-ACK EXPERIMENT PREPARED / PHONE NOT RUN: separately opted-in extra ACK requires exact SYN-context match, prior R037 address-reply write and a locked one-attempt budget. It reuses the working63-byte ACK, observes one next-service frame, then closes without sending next-service auth/Bingo. 113 original regressions +5 loopback lifecycle +2 refusal tests PASS. Default remains HOLD_NO_ACK. Separate report/run paths preserve old results. Next owner-controlled Termux/PCAPdroid experiment can test for AUTH_REQUEST_OBSERVED; this is transport progress, not account login. [Procedure](research/SECOND_SERVICE_ACK_EXPERIMENT.md).

R067 (2026-11-01 UTC), SOURCE/LOOPBACK ONLY: new exact non-route SYN comparison requires identical encoded base and every SYN field except the bounded12→10-byte named route. R037 now exports fixed SYN_CONTEXT labels while preserving HOLD_NO_ACK. Five gate tests, updated two-connection lifecycle and113 original prepared-copy regressions PASS. Historical redacted phone summaries cannot retroactively establish this exact match. No new ACK/phone/session acceptance. Next combine a successful runtime comparison with the source-backed ACK predicates in a separately bounded manual experiment. [Proof](research/SECOND_SERVICE_DISPATCH_PATCH.md).

R066 (2026-11-01 UTC), ORIGINAL NATIVE EMULATION WITH STUBS: actual GCloud SYN preparation with synthetic named routes then original ACK parsing reaches suppressed auth-send for both10/12-byte names. 3 methods/7 cases PASS, including malformed magic, unsupported mode1, TX prefix, truncation and relay-route negatives. SYN pack/send and auth send suppressed; prepared handle transferred between fresh emulator contexts. This narrows route-length-alone exclusion, not actual phone security/session acceptance. R065 unknown-route HOLD_NO_ACK remains. Next compare actual non-route SYN/security fields to working reference before any bounded manual ACK test. [Evidence](research/NATIVE_SYN_ACK_HANDOFF.md).

R065 (2026-11-01 UTC): owner-supplied R037 ZIP matches recorded 35,193-byte/SHA receipt; exact preparer chain and generated handler now pinned. R056 corrected dispatch integrated into active-reply R037 copy without changing original reply code, one-shot guard, redirector or live opt-in. 113 original regression +30 R037 focused +1 new two-connection loopback tests PASS; 2 source-refusal tests PASS. This supersedes R064's missing-active-source integration blocker. Changed route still HOLD_NO_ACK; no phone or login proof. Next establish second-service ACK/session predicates before another live experiment. [Details](research/SECOND_SERVICE_DISPATCH_PATCH.md).

2026-11-01 UTC — Guarded Termux dispatch patch: corrected R056's use of inbound reply grammar on client SYNs (client base kind0 except field6 kind1). Exact private baseline and redirector fingerprints verified; copy-only preparer verifies 60 files. 11 classifier tests + 6 patch controls PASS with private source; 113 original prepared-copy regression tests PASS. No new ACK, phone run or login; actual R037 active-reply source integration remains outstanding. [Details](research/SECOND_SERVICE_DISPATCH_PATCH.md).

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

Q-10 R015: Original source verifies normal AddressService protocol initialization as non-strict binary (factory type0x20, flag+0x21=0). [Trace](research/UPSTREAM_REQUEST_CHAIN.md). Next distinguish later strict flag mutation or another producer with bounded original-code evidence, then run an isolated full-message writer. Do not assume this initializes the observed phone 4013 payload.

Q-10 R016/R017 source-free refinement (2026-11-01): V3.8.1 `METHOD_BYTES_POLICY` at offsets0/4 are dependent once the matched sequence-prefix and bounded name-length label are combined; do not count two independently malformed RPC headers. Five new local source-free tests PASS in [test_routed_label_implications.py](../../tests/test_routed_label_implications.py), contrasting candidate complete unmodified native legacy and strict headers: both produce different offset4 classifications from the actual report, conditional on observer boundaries. No app operation, crypto state, connector owner or authentic session identified. Next original-private isolated whole-message writer/callback capture, then concrete runtime owner and RX correlation. Do not run duplicate phone diagnostics or send a guessed reply.


Q-11 R057 (2026-11-02): [Original native direct caller audit](research/R057_ADDRESS_LOOKUP_CALLERS.md) newly verifies two exact direct `AddressService::GetServiceAddress` producers: `GCloud::CDefaultNameService::Query` and `pebble::rpc::RpcConnector::InitLbIpAddress`, itself called by `RpcConnector::Init`. The former has callback/observer symbol candidates (`OnGetServiceAddress`, `CTGcp::OnQueryNameResult`); none is a confirmed phone runtime edge. Must determine which producer supplies the 10-byte post-R037 named route and whether name-result notification invokes route setting before second-connection `0x1002` ACK/session handling. Same first-service ACK cannot be assumed valid. Evidence: owner Drive Apollo SHA256 separately MATCH, six direct original BL edges; 10 source-only synthetic tests PASS; one private-original gate SKIPPED in CI. No server integration/phone auth claim.

Q-11 R058 (2026-11-02): [GCloud name-service observer wiring](research/R058_NAME_SERVICE_OBSERVER_WIRING.md) now verified from the original native file: GCloud connector construction creates CDefaultNameService, connectTConnd calls CTGcp::SetNameService, and the concrete vtable routes SetObserver registration to the name service. Original AddressService init and callback/member-function pointers also grounded. Source-only auditor has 3 direct edges, 7 instruction pins, 6 function pointers; 9 public synthetic tests PASS, 1 private original test SKIPPED in CI. This is STATIC wiring only. Still determine if GCloud or RpcConnector owns the R037 alternate route; endpoint lookup is not route-name identification. Next resolve real ACK/key/session handling, not another guessed wire response.

Q-11 R059 (2026-11-02): [Original GCloud name-query vs endpoint trace](research/R059_SERVICE_QUERY_ENDPOINT.md). CTGcp::OnThreadProc directly calls choosingNameService; original method dispatches a query key from CTGcp+0x2d8 through INameService vtable Query+8 and Update+12; original address callback path uses a separate resolved endpoint CTGcp+0x2dc on transport start. RouteInfo remains another separate configuration mechanism. Four exact original native callsites / 16 halfwords / 2 vtable pointers checked privately, 10 synthetic CI tests PASS and one private test SKIP. This does not identify runtime route name or GCloud-vs-RpcConnector ownership and does not make second service ACK valid. Next examine original route-specific ACK/security and runtime choice instead of another guessed route or first-service ACK replay.

Q-11 R060 (2026-11-02): [Distinct original ACK receivers](research/R060_DUAL_ACK_RECEIVERS.md) show separate legacy tgcpapi and GCloud tgcpapi native ACK, auth-response and packet-gather functions, with 14 original receiver and six SYN-sender direct callsites (20 total). This is no proof of incompatible ACK bytes; R037 alternate-route real-phone stack remains unidentified. Public 13 synthetic tests PASS, original-only one SKIP in CI. Next compare both original ACK session/key predicates and identify which concrete connector generated the alternate SYN before another server response.

Q-11 R061 (2026-11-02): [Exact original ACK/auth decoder fork](research/R061_ACK_BODY_DECODER_FORK.md): legacy receiver uses `gcp::TGCPBody::unpack` while GCloud receiver uses `gcloud_gcp::TGCPBody::unpackTLV`. Original GCloud decoder checks AA/99 and declared length; legacy complete envelope/key/session predicates not yet compared. Owner-private original 9/9 body-decoder direct BL sites and 14/14 native instruction halfwords matched; 12 public synthetic tests PASS and 1 private-original test SKIPPED in corrected [CI 41350373758](https://github.com/despairarc000/temp/actions/runs/41350373758). Need determine actual R037 alternate connection stack, compare both ACK contracts, and then design source-grounded second-service response; no new phone ACK sent.

# Evidence registry — initial historical import (2026-10-30)

Historical results described here come from the user's Termux runs and TXT reports, plus native static review described in the conversation. Reports/hashes and original binaries are **not** checked into this public repo; verify them before stronger claims.

| ID | Class | Evidence | Supports / limits |
|---|---|---|---|
| E-01 | ON_PHONE | PCAPdroid older connection capture | Failed TCP to 45.113.69.32, 211.159.211.105, 119.28.34.12 on 8080/8085; `cfm-na-conf.cfmna-tencent.com` NXDOMAIN |
| E-02 | ON_PHONE | `CF2018_Redirect_Test_Report.txt` | 53 observed TCP connections, 32 diverted, each 133 client bytes |
| E-03 | ON_PHONE + ANALYSIS | `CF2018_Real_Request_Bytes.txt` | 32 payloads have single SHA-256 `3b91f9be6acde7e6f0be56970bc2c7f6d6d4ba8d5fd8392d4536fa0edb85f9dd`; route `QueryAddrSvr` |
| E-04 | ON_PHONE | `CF2018_TGCP_v03_Report.txt` | 33 SYNs, 17 on 8085/16 on 8080, 0 replies |
| E-05 | ON_PHONE | `CF2018_TGCP_v04_ACK_Result.txt` | Synthetic 65-byte ACK sent; peer closes; report accumulates older sessions and reuses port-local IDs, counts unreliable |
| E-06 | ON_PHONE | `CF2018_TGCP_v05_AB_Report.txt` | 8 passive/8 ACK controlled; passive median ~7003 ms, ACK median ~11 ms, no client follow-up |
| E-07 | ON_PHONE LOGCAT | `CF2018_TGCP_v06_Native_Log_Report.txt` | Apollo initialization + traffic; no reliable TGCP reject diagnosis; too-broad log filter matched unrelated touch `0x1002` |
| E-08 | HISTORICAL_NATIVE_STATIC + REPORTED_LOCAL_TEST | `CF2018_TGCP_v07_Audit.txt` | Client TX 43 66 prefix, syntactic candidate ACK fields, no verified server handshake |
| E-09 | HISTORICAL_NATIVE_STATIC + REPORTED_LOCAL_TEST | v0.8 FrameGate package | Imported raw 66 43 inference; superseded for the pinned mirror path by E-16; no phone acceptance |
| E-10 | ON_PHONE | signed-only vs edited DLL controls and `CF2018_XAPK_Comparison_Report.txt` | identical original payload except modified managed DLL; modified DLL early-exits, cause such as integrity not yet proven |

## Coordinator-reviewed evidence — 2026-10-30

| ID | Class | Evidence | Supports / limits |
|---|---|---|---|
| E-11 | SOURCE_AUDIT + LOCAL_TEST_ONLY | [CF18-01 result](../../coordination/incoming/CF18-01/RESULT.md); eight audit tests rerun | The Python helper accepts only the modeled prefix and ignores suffix/size/stream state. Does not verify native RX or ACK acceptance. |
| E-12 | CONNECTED_DRIVE_METADATA + DIRECTORY_LISTING | [CF18-04 result](../../coordination/incoming/CF18-04/RESULT.md) | Known folder hierarchy accessible; Data sample capped at 100. Search failed a known-file control, so absence claims are unsupported. No target hash/version/native library verified in that Drive inventory; see separate mirror E-15. |
| E-13 | ORIGINAL_CODE + LOCAL_TEST_ONLY | [Passive relay research](research/RELAY.md), original core and 19 relay tests | Both observed EOF directions, half-close, byte preservation, error/timeout/local-stop attribution and bounds tested locally. No historical source audit, SOCKS5/device compatibility or Q-02 resolution. |

E-08/E-09 are imported historical native-review summaries without an independently
verified library fingerprint/address trace in the historical import. E-16/E-17
are independently sourced mirror evidence, not retrospective validation of those
reports. Do not treat serializer syntax as receiver acceptance.

## Grounded known strings
TGCP variants: client SYN 0x1001, ACK 0x1002. Route name `QueryAddrSvr`. Related native symbols: `tgcpapi_encrypt_and_send_pkg`, `tgcpapi_gather_and_split_entire_pkg`, `gcloud_tgcpapi_recv_ack_msg`, `TGCPHead::packTLV`, `TGCPAckHead::packTLVWithVarint`. Native address service `QueryAddrSvrClient::QueryAddrInfo` is **later** than the current handshake; no authenticated session established.

## Provenance & limits
Source locations to re-open with authorized Drive access: [Drive manifest](../../sources/DRIVE_MANIFEST.md). Do not treat static symbol names, a parser's own unit tests, or locally synthesized replies as official-server capture. The v0.8 raw-prefix premise is retired for the E-16 mirror path; phone equality
and runtime selection remain unverified.

## E-14 — bounded SOCKS5 handoff, 2026-10-30

Class: ORIGINAL_CODE + LOCAL_TEST_ONLY. Source:
[CF18-03 result](../../coordination/incoming/CF18-03/RESULT.md), submitted in
`9f77b2cbf9f0249b566c75e8a4e42666cb44c292`; canonical
[implementation](../../experiments/socks5_handoff.py) and
[tests](../../tests/test_socks5_handoff.py).

Twenty-three canonical handoff tests passed, including a real localhost
fragmentation/pipelining handoff and a synthetic canonical-core attachment.
The full canonical suite passed 52 tests. This establishes the bounded stage's
parsing, scope, ownership, limits and metadata behavior only. No actual upstream
connection, deployed passthrough interface, device compatibility, historical EOF
cause, TGCP ACK acceptance or original native validation was demonstrated.
Q-02 remains UNKNOWN and G2 BLOCKED.


## E-15 to E-18 — coordinator-reviewed recovered mirror

Reviewed at c52243228e8d2d38dd6b4c1d85f464d9f94461f8. Source receipt:
[canonical provenance](../../sources/SOURCE_PROVENANCE.md) and
[MIRROR_RECEIPT](../../sources/MIRROR_RECEIPT.json).

| ID | Class | Actual source / conclusion / limit |
|---|---|---|
| E-15 | MIRROR_SOURCE_PROVENANCE + INTERNAL_V1_SIGNATURE_VERIFICATION | [CF18-04](../../coordination/incoming/CF18-04/SOURCE_RESULT.md), c52243228e8d2d38dd6b4c1d85f464d9f94461f8. Exact v1.0.11.11 package, native/managed member hashes, ARM ELF identity and 1212 signed-entry digests rechecked. External certificate trust, full XAPK/OBB and phone equality unverified. |
| E-16 | ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS | [CF18-01](../../coordination/incoming/CF18-01/NATIVE_RX_RESULT.md), fefd0dc224851fefc2b74a51fc95e0fa0090e9a2. Pinned GCloud RX compares decoded marker 0x4366 after AA/99 TLV; raw prefix orders fail. TX prepends 43 66 independently. 32 lane tests rerun; nine execute native splitter/decoder controls with explicit stubs. No phone runtime/path claim. |
| E-17 | ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS | [CF18-02](../../coordination/incoming/CF18-02/RESULT.md), 56db53d81326810d5bea342b11ea4e07dc351e01. ACK selector/type, key-mode/body branches, error side effects and state/auth boundary traced; 25 controls rerun. Mode-0 empty-stage return does not establish later crypto/session; server field generation remains unknown. No accepted server ACK. |
| E-18 | ORIGINAL_CODE + LOCAL_SYNTHETIC / PRIVATE_SOURCE_VERIFICATION | Canonical [framing](../../experiments/rx_envelope.py), [17 tests](../../tests/test_rx_envelope.py), [source verifier](../../tools/verify_private_source.py), [14 controls](../../tests/test_verify_private_source.py). 83 canonical tests passed with private APK selected. Strict subset policies and signature checks do not establish full native receiver parity or G2. |

[CF18-G2-ACK-01](research/ACK_RECEIVER.md) combines the ordered receiver trace,
explicit emulation boundaries and remaining body/session/runtime/relay gates.
No original binary, capture, game key or raw disassembly is published. No new
phone packet or device experiment was obtained; Q-02 and G2 remain blocked.

## E-19 — optional ACK body and later session uses

Class: ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS + ORIGINAL_CODE /
INDEPENDENT_SYNTHETIC. Reviewed main 37b808d095641c90e80a707209f656e9bf29c53f.
[Integration provenance](../../coordination/INTEGRATION.md) records actual hashes
of the completed unpublished local CF18-02 continuation; no source commit invented.
[Canonical trace](research/ACK_SESSION.md), [runner](../../experiments/native_control.py),
[controls](../../experiments/native_session_controls.py),
[18 tests](../../tests/test_native_session_controls.py).

Received base timestamp is copied into the next auth-request field. Optional
embedded-body component presence is not an observed fast-auth path in examined
callers. Separate type-0x2002 receiver parses then copies account/state; successful
copy controls explicitly stub parser zero. Waiting zero does not call Bingo.
Server timestamp generation, account/auth semantics, later Bingo/session/crypto and
phone equivalence remain unknown. State 4 is never counted as authentication.

All 40 affected lane tests reproduced. Canonical 101 PASS with private sources
selected; default 82 PASS and 19 explicit private-source SKIP. Knowledge doctor
PASS. Actual pinned source hash/ISA and bounded branches were checked. Native
functions run in isolated emulation with labeled decoded-boundary/parser/send
stubs, not Android sockets. No complete wire reply, phone run, new authentic
packet or G2 advancement. No original/raw native code or sensitive bytes published.

## E-20 — phone progression supersedes ACK-first checkpoint

Class: USER_CONFIRMED_PHONE_OBSERVATION + SANITIZED_PHONE_REPORTS. Reviewed from
CF18-05 at main9a0d6ef09c6b62a4543c8c9aadef15f1946df470:
[v0.9](../../coordination/incoming/CF18-05/PHONE_V09_RESULT.md),
[v1.0](../../coordination/incoming/CF18-05/PHONE_V10_RESULT.md),
[v1.1](../../coordination/incoming/CF18-05/PHONE_V11_RESULT.md),
[v1.2](../../coordination/incoming/CF18-05/PHONE_V12_RESULT.md).
Real SYN133 -> AA_DIRECT ACK63 -> authentic0x2001/117 is confirmed. v1.0's empty
ext_type output was a kind-filter bug; observed pair[8193,1] identifies0x2001.
v1.2 has8 sessions,2 per arm: all250 clientbytes/twoframes; silence about7s;
synthetic66/49/79 replies produce read_eof at8–11ms. No third packet or valid
session. Local EOF does not identify FIN/RST origin. Historical earlier no-post-
ACK statements remain accurate only for their earlier runs, not current status.
No fresh phone run was performed by the coordinator.

## E-21 — reported historical source parity

Class: HISTORICAL_ON_PHONE_REPORT + INDEPENDENT_MIRROR_HASH_VERIFICATION.
[CF18-05 summary](../../coordination/incoming/CF18-05/RESULT.md), source commit
b26007d73b5d6d781c8c8e8e1681c18f55cb18ce, reports Original.xapk embedded APK
SHA33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9,
matching the independently verified mirror; managed DLL hash also matches.
It reports0 differing non-signature entries among1212 for the re-signed control.
Original comparison report bytes/precise private locator were not newly retrieved
in this activation. Supports reported historical parity, not installed APK,
current runtime context, entire XAPK/OBB or connected Drive equality.

## E-22 — earliest exact v1.2 native failure and body correction

Class: ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS + ORIGINAL_CODE /
INDEPENDENT_SYNTHETIC. Submitted [CF18-02](../../coordination/incoming/CF18-02/auth_rx_02/RESULT.md)
in9a0d6ef09c6b62a4543c8c9aadef15f1946df470, using exact [CF18-05 fixtures](../../coordination/incoming/CF18-05/V13_NATIVE_TEST_PACKET.md)
from14a49c610826e6a08f6bc7d9bb06ad0e5ad30b75. Coordinator independently reran25
incoming tests and regenerated the [native matrix](../../coordination/incoming/CF18-02/auth_rx_02/NATIVE_MATRIX.json) exactly.
[Canonical trace](research/AUTH_RECEIVER.md) includes addresses, all stubs and limits.

All exact originals pass frame/header/effective2002/receive. TGCPBody mode A5
fails AA/99 at0x3b8896–9c, returns-32 at0x3b88d8 after1byte; auth maps-18 at
0x3ac378. Auth/account/Bingo not reached; prior account unchanged/state3.
Verified correction adds AA+BE total length before existing body union and
recomputes outer length. Corrected71/54/84-byte paths parse real components,
copy/state4, then real Bingo-12/wait; no parser-success stub. Dummy UID/account
and waiting are not session acceptance. Native incompatibility is independent
of actual phone EOF cause. Deployed bridge source/wiring still unavailable.

Original canonical [encoder](../../experiments/tgcp_body_envelope.py), separate
[fixture repair](../../experiments/auth_fixture_repair.py), [native controls](../../experiments/native_auth_rx.py),
[19 auth tests](../../tests/test_native_auth_rx.py) and seven pin tests integrated.
Full canonical128 PASS private-selected; default95 PASS/33 private-sourceSKIP.
DoctorPASS; source verifierPASS including1212 signed entries/trust-chain not
validated. Conditional six-connection v1.4 envelope comparison is justified in
principle, not ready without reviewed deployed bridge/directional instrumentation.
No actual phone test, generated credential/key/Bingo, auth session or gameplay.

## E-23 — Bingo correlation and received relay-data uses

Class: ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS + INDEPENDENT_SYNTHETIC.
Coordinator reviewed completed LOCAL CF02 bingo_01 draft against ccdd219f9ed121e77fc06ad20b50b77614079cbf.
No source packet commit exists; exact six input hashes are in [integration](../../coordination/INTEGRATION.md).
[Canonical trace](research/BINGO_SESSION.md), [controls](../../experiments/native_bingo_controls.py),
[21 tests](../../tests/test_native_bingo_controls.py), [actual23-control matrix](../../coordination/CF18-G2-AUTH-RX-02/BINGO_MATRIX.json).

3002 dispatches TGCPWaitBody/position-total-roughTime, correcting prior stop wording.
Header checks3002/6002 before body, but real union parsing overwrites selector.
Actual deliberately mismatched header6002 or3002/body2002 decodes auth component,
never Bingo component, yet reaches state5/copy. No parser-success stub in those
wire controls. Numeric state5 cannot establish valid correlation/authentication.
Separate decoded parser-zero controls explicitly stub results/storage. Relay44-byte
fields and compression copy traced; later SYN prefix reuses relay block, stopped
before send. Generation/account binding remain unknown; no valid Bingo built.

Incoming21, auth25 and CF01 path8 controls independently reproduced. Canonical149
PASS/private-selected; default97 PASS/52 private-sourceSKIP; doctorPASS; both
native matrices reproduce exactly. Original-source verifier/CMS/all1212 entries
PASS, external trust not validated. No Android/device/network run or auth success.

## E-24 — reviewed bounded factory/wrapper continuation

Class: ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS. Source
[CF18-01 path result](../../coordination/incoming/CF18-01/PATH_RESULT.md), commit
ccdd219f9ed121e77fc06ad20b50b77614079cbf. Coordinator reran8 controls. Actual
examined native receive wrapper preserves raw prefixes; synthetic AddressService
virtual prefix selects GCloud factory using constructor vtable address point.
No actual phone runtime selection or EOF source is proven. Strict99/bounds parser
proposal from0019 remains a separate pending integration, not silently promoted.

## E-25 — local connection callback is not authenticated session

Class: ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_EXPLICIT_STUBS. Base
c9b1d3555f8dd4036d64d1d34cb47a440b881c4c. [Trace](research/CONNECTION_CALLBACKS.md),
[original controls](../../experiments/native_callback_controls.py),
[actual ten-case matrix](../../coordination/CF18-G2-CALLBACK-01/NATIVE_MATRIX.json).
Actual observer thunk/connector locally constructs result0 and schedules notify
with unchanged zero account prefix. Independently invoked notify, explicit vector/
RTTI/GetBuffer substitutes, original AddressService result9 error vs0 bind branch.
Real local bind installs callable; real open is no-op. No account validation or
request send in examined handler; no whole-client absence claim. All11 new tests
PASS; canonical160 PASS/private-selected; sourcefree98 PASS/62 SKIP; local CF02
13 PASS. Every stub and independent-stage limit recorded; no valid session/phone.

## E-26 — private bridge recovery handoff, reported separately

Class: CF18-05_REPORTED_PRIVATE_SOURCE_REVIEW_AND_LOCAL_TESTS. Commit
c9b1d3555f8dd4036d64d1d34cb47a440b881c4c,
[handoff](../../coordination/incoming/CF18-05/V14_DEPLOYED_BRIDGE_HANDOFF.md).
Reports recovered actualv1.2 scripts and user-only v1.4 envelope comparison,21 local
tests. Private ZIP not independently re-opened by coordinator this activation;
no new phone result or historical EOF attribution. Supersedes blanket unavailable
source claim for preparing that probe; does not resolve Q-02.

## E-27 — protected stored DLL and native image-loader/termination boundary

Classes: ORIGINAL_FILE_FORMAT_OBSERVATION + ORIGINAL_NATIVE_STATIC +
NATIVE_EMULATION_WITH_EXPLICIT_SUBSTITUTIONS. Base6a0ecc16877adbdc4eed03cefebb5b4144f7bd6f.
[Native trace](research/INTEGRITY_NATIVE.md), [source/control matrix](../../coordination/CF18-INTEGRITY-01/NATIVE_MATRIX.json),
[controls](../../experiments/native_integrity_controls.py),
[read-only preflight](../../tools/managed_image_preflight.py).
Exact original APK has15 managed members:13 bounded PE/CLI headers, game and
firstpass non-PE. Original Mono0x196c38 -> veneer -> provider slot26/0x33fc handoff
reproduced with two explicit relocations. Signature controls stop before transform.
Actual CRC matches independent zlib vectors. Injected pre/post lookup nonzero
mismatch requests termination18; equal/zero controls avoid mismatch path. Monitor
lookup is explicitly supplied, runtime flag/context injected, syscall never run.
This does not prove historical phone cause, key/init/format round trip or safe
managed modification.176 canonical PASS private-selected;106 PASS/70 SKIP default;
source verifier in suite PASS with prior trust-chain limitation. No original edit.

## E-28 — Unity caller versus provider initialization

Original native static + bounded emulation with injected results. [Integrity continuation](research/INTEGRITY_NATIVE.md): Unity JUMP_SLOT0xaa924c/PLT0x55f60 called at0x20f87c. Actual return-check controls distinguish nonnull/status0 from null or nonzero-status diagnostics. Four tests PASS; caller input/Android initialization not reproduced; no decode/round trip/phone exit cause claimed.

## E-29 — reconciled phone14–16 and chosen server continuation

Reviewed at5d76e82696984717e394552cc6fb9c076e77e01f. CF05 user-uploaded redacted
report summaries: v1.4 correction removes immediate EOF2/2; synthetic Bingo causes
real0x4013 in3/4 trials across v1.5/v1.6. Original raw report not newly fetched;
no coordinator phone run. [Server path](research/SERVER_PATH.md) links precise
reports, outcomes and observer-kind defect. No authenticated account/RPC identified.
Canonical stale no-post-Bingo/deployment-unavailable statements superseded.

## E-30 — actual original routed TX pre-encryption dataflow

Original-native static + isolated synthetic native execution. [Trace](research/SERVER_PATH.md),
[seven-case matrix](../../coordination/ROUTED_TX_MATRIX.json), [original controls](../../experiments/native_routed_tx.py).
Actual send_with_route builds4013 header and copies BE packet-sequence32 before application
payload; header routing/compression fields separate. State5, initialization, length,
timeout and route-pointer guards tested. Stops before encrypt/send; no final wire,
real identity/session or RPC inferred. Seven new methods PASS; canonical187 PASS private,
108 PASS/79 SKIP default. Incoming Bingo13/address14 tests rerun as synthetic only.

## E-31 — actual uploaded v3.8 DataHead report

[Review](research/V38_BLOCKER.md), source5383 bytes SHA256031dcb5bf33eb979cd95b161708c454006fd938f50ff08893db923fa81614cb3. User-supplied phone report:2/4 routed frames, kind5, body80/85; report classifiers do not identify application. No4013 reply sent. Route/crypto claims limited to available metadata; v38 probe code absent. Independent pinned-native helper controls (four methods) distinguish mode0 copy vs encrypted no-key-31 with either compression setting; not a measurement of phone crypto.

## E-32 — exact v38 source audit and native differential

[Actual results, native addresses, stubs and limits](research/V38_SOURCE_AUDIT.md). User ZIP hash e3bbc31f7b93e738aff0d4205dd0d1418c7abd55b7c17b332ca5d426eb619df2. Source gap in E-31 resolved. Exact synthetic lab stages select method0 and states2/4/5 with state3 supplied. Original legacy header serializer agrees with v38 classifier on independent synthetic input. Correction to E-30: body prefix is native `dwSequence`, not UID; original counter increment verified before suppressed send. Added metadata-only observer copy; original/prepared focused suites9 PASS each, canonical205 private PASS /117 PASS+88 SKIP default. No native failing predicate identified for actual redacted phone body; no phone run/account acceptance.

## E-33 — actual phone workflow consolidated and diagnostic made portable

[Current handoff](../../coordination/CURRENT_HANDOFF.md) directly reviews exact v38 README/starter/redirector/probe. PCAPdroid CrossFire-only, Termux excluded, SOCKS5 localhost1080 -> Termux local8080/8085. Added patch-only v3.8.1 kit (no private fixtures/game files), exact original ZIP/all60 hash guard, separate report/run IDs, unchanged protocol-handler AST and actual-stage byte comparisons. Four Linux synthetic game sessions traverse actual NO-AUTH/CONNECT redirector -> server; non-target binary passthrough also verified. Four patch-kit tests PASS; canonical209 private PASS /120 PASS+89 SKIP default; doctorPASS. Owner manual phone run has not occurred; latest real report remains v38.

## E-34 — actual generated address request and required response fields

[Native trace/matrix/controls](research/ADDRESS_APPLICATION.md). Original args writer emits34+N; native full legacy/strict controls both recognized by existing v38 parser.80/85 legacy size model first differs61; actual report64plus does not fit that simple model. Original generated result decoder requires I32 result AND reason STRING; missing result0x39eaae, missing reason0x39ead8 (stopped before exception allocation; no native error code invented). Empty reason accepted structurally. Corrected canonical offline preflight integrated from CF05 original code, incoming unchanged.12 native/bounds/differential +15 preflight PASS;236 private canonical PASS /137 PASS+99 SKIP default; doctorPASS. No actual phone producer, accepted response/session or new device result established.

## E-35 — actual user v3.8.1 phone result

[Report review](research/PHONE_V381.md),5777 bytes SHA2568b4e60eb97f08c81cf6b904c674dd201652deead588c5f30d4e0a4393c298919. Two routed samples both match header packet sequence and exact allowlisted QueryAddrSvr route. Both fail METHOD_BYTES_POLICY at offsets0/4; full operation unidentified. No4013 reply sent. New native-static direct caller candidate0x3a5476 in CTGcp::onDataOutEvent; next trace upstream queue/body producer. No new phone run requested or native rejection inferred. Default236 total137 PASS/99 SKIP, doctorPASS; prior private236 not rerun.

## E-36 — fresh source/repository audit and upstream queue trace

[Descriptive audit](research/REPOSITORY_SOURCE_AUDIT.md): actual4 source file hashes recalculated; full XAPK/OBB not present in workspace/attachments, receipt whole_archive_downloaded false. Live complete181-file tree and23 incoming reports reviewed; stale receipt progress distinguished from v381. Original-static CTGcp Write -> queue -> PopOneSendBuffer -> onDataOutEvent pointer/size handoff traced; upstream Write callers/constructors next. No queue runtime/phone acceptance. Default236 total137 PASS/99 SKIP, doctorPASS.

## E-37 — pinned native upstream producer and connector path, 2026-11-01

[Original-source static investigation](research/UPSTREAM_REQUEST_CHAIN.md). Re-hashed original Apollo5,243,704 bytes/SHA2564812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8; 11/11 direct callsite/field instruction pins PASS with LLVM Thumb disassembly and ELF symbols. New evidence connects AddressService::ProcessRequest -> Send_QueryAddrInfo -> pargs writer, plus MsgBuffer::bind callback, MsgBuffer::writeEnd dispatch, concrete CGCloudConnector::Write -> CTGcp routed queue -> onDataOutEvent send. Dynamic concrete dispatch and full phone producer **not proven**; no new phone data/4013 response/auth/login progress. Next bounded memory-only original-code differential between MsgBuffer and connector; no raw original code or account bytes committed.

## E-38 — source-pinned producer and reciprocal receive ownership, 2026-11-01

[Native trace and audit](research/UPSTREAM_REQUEST_CHAIN.md). Exact privately provided original Apollo (5,243,704 bytes, SHA256 4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8) checked; read-only LLVM Thumb instruction audit: **33/33 static pins PASS** in 13 bounded regions. Two direct MsgBuffer::bind callsites belong to AddressService and RpcConnector connection callbacks. AddressService::OnDataRecvedProc calls ProcessResponse, whose processing includes QuerySession lookup. RpcConnector::OnDataRecvedProc calls ProcessMessage and its own typed response dispatcher. Six Python tests PASS with original private source; source-free five PASS/one explicit SKIP. No original-native whole-message execution, owner phone run, new 0x4013 reply, authenticated account, lobby or gameplay. Runtime connector ownership of the phone's two 80/85-byte requests remains UNKNOWN.

## E-39 — verified native pointer/length copy boundary, 2026-11-01

[Evidence](research/UPSTREAM_REQUEST_CHAIN.md): 10 added instruction pins prove MsgBuffer's original buffer pointer/count reach the conditional CGCloudConnector/AString/AData copy call, ending at PLT `memcpy` in the original Apollo. Expanded static verifier 43/43 PASS and 6/6 Python tests with hash-pinned original. Earlier canonical 24-pin test regression repaired. Connector selection on the actual phone and final wire encoding are NOT established.

## E-40 — default AddressService binary protocol is non-strict, 2026-11-01

[Original source trace](research/UPSTREAM_REQUEST_CHAIN.md): 8/8 new original-native static pins PASS: InitProtocol factory type0x20, binary branch, strict flag+0x21 initialized 0, message writer's legacy branch. Expanded verifier declares51 pins, GitHub Actions source-free suite and knowledge doctor PASS. Real phone producer, later flag mutation, accepted reply remain UNKNOWN.

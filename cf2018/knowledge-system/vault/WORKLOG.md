# WORKLOG — initial handoff (2026-10-30)

- Earlier: signed-only original-code client reached update checking. DLL patch and one-byte DLL control exited early; APK/OBB editing frozen.
- v0.1–v0.3: local PCAPdroid SOCKS5 and Termux bridge captured real 133-byte TGCP SYN for `QueryAddrSvr`. Framing/decoder prototyped.
- v0.4: synthesized 65-byte ACK; massive retries, immediate socket closes, no new client frame; diagnostic IDs/log accumulation defective.
- v0.5: 8 passive/8 ACK bounded comparison; median SYN-to-end ~7003ms passive vs ~11ms ACK, zero next client frames.
- v0.6: ADB native-log attempt; Apollo initialization observed; TGCP reject logs unavailable in Android logcat. Filter had false positives from touch `0x1002`.
- v0.7: static native audit of sender/receiver, identified unverified mirrored fields and framing.
- v0.8: static candidate correcting first two server bytes `43 66`→`66 43`; local tests only, no verified real client acceptance.
- 2026-10-30: setup of isolated public `temp/cf2018` knowledge workspace and Drive reference, not a replacement for authorized original binary store.

Next: [CHECKPOINT](CHECKPOINT.md) and [TGCP](research/TGCP.md).

## 2026-10-30 — coordinator integration

Reviewed live main ec0d55fd338df6cc6f7d1e7aad59c7885fa88f06 and incoming CF18-01/04
packets; no remote CF18-02/03 packet existed. Integrated prefix-model limitations
and source-search coverage limits into canonical knowledge; corrected helper
text that presented an unverified native premise as known. Reviewed the preserved
local CF18-03 original draft, integrated a passive loopback core and 19 transport
tests (16 adapted plus three coordinator controls). Canonical suite: 29 PASS;
CF18-01 audit suite: eight PASS; knowledge doctor PASS. No native/client/device
acceptance evidence was added. Historical Q-02 and G2 remain unresolved.
[Integration record](../../coordination/INTEGRATION.md) identifies actual inputs,
local draft hashes and scope. Assignments are maintained by the coordinator only.

Canonical code/evidence integration: `15be6fc1401a164f00c2d3c9623ba29d6ac7ac53`.
[Assignments](../../coordination/assignments.json) record exact source/integration commits, one scoped task per lane and honest prerequisite states. CF18-03 has one READY bounded SOCKS5-adapter proposal; native/source tasks await their missing prerequisites.

## 2026-10-30 — bounded SOCKS5 packet integration

Reviewed packet 9f77b2cbf9f0249b566c75e8a4e42666cb44c292; integrated its original
negotiation/handoff stage into canonical experiments/tests. Kept the disabled
entrypoint, strict exact-IP-and-port route selection and normal-dispatch handoff.
Added reset-message privacy and declared-domain truncation controls: 52 canonical
tests plus eight framing-audit tests PASS; knowledge doctor PASS. No actual target
connection, installed proxy, historical bridge hook or device/native evidence.
CF18-03 deployment wiring awaits bridge source; Q-02 and G2 unchanged.

Canonical handoff integration: `f70a874ed903b030fd51a94a36dff0ca43dcfff4`.
Assignments close CF18-G1-SOCKS5-01 only as a bounded stage and reserve
CF18-G1-BRIDGE-HOOK-01 for CF18-03, blocked on real historical bridge source.
All remaining lanes await new source evidence or review input; no fresh READY
task is invented from unchanged missing prerequisites.


## 2026-10-30 — recovered mirror receiver/source integration

Reviewed c52243228e8d2d38dd6b4c1d85f464d9f94461f8 and all four lanes.
Independently reran framing 32, ACK 25 and source 14 controls against the private
pinned originals. Integrated original offline framing (17 canonical tests,
including base_type/terminal-EOF coordinator controls), private-source verifier
(14 controls) and descriptive source receipt. Canonical suite 83 PASS with
private APK selected; source-free run has two private-source skips; doctor PASS.

Updated current knowledge around the actual decoded marker, effective extension
type, ACK/key/body ordering and side effects. The old v0.8 raw-prefix premise is
retired for this mirror path. Source identity now supports bounded native work;
phone/OBB equality, runtime selection and historical relay evidence remain gaps.
No original/lane packet is modified or uploaded, no valid ACK is constructed,
and no phone/network experiment or bot work runs. G2 remains BLOCKED.
[Integration record](../../coordination/INTEGRATION.md) describes review and code
adaptations. Substantive integration: `88c439b7938642076f721c0ec9319fd45d008420`.
The queue handoff records this exact SHA, gives framing/ACK-body research one
ready task each, and leaves relay/phone-identity tasks waiting on real evidence.

## 2026-10-30 — CF18-00 body/session integration

Reviewed main 37b808d095641c90e80a707209f656e9bf29c53f and all four lanes. No active
worker; preserved unfinished CF18-01 boundary draft and unpublished CF18-02 inputs.
The latter's actual hashes, not an invented source commit, identify this review.
[Acceptance](../../coordination/ACK_BODY_INTEGRATION_ACCEPTANCE.md) preceded edits.
Rechecked actual pinned Apollo hash/ISA and bounded native branch sites; 40 lane
methods reproduced. Integrated original canonical opt-in native controls and
18 tests, plus [timestamp/body/session trace](research/ACK_SESSION.md). Three
coordinator controls cover source pin, fresh state and error-before-copy/Bingo.
101 canonical tests PASS with private sources/dependencies selected; default
82 PASS, 19 private-source SKIP; knowledge doctor PASS. Only canonical CF2018
files changed; incoming edits, originals and root app untouched. No phone/network
experiment, valid ACK/auth reply, token construction or gameplay claimed.
G2 BLOCKED, A/B/C false. Next: downstream account/Bingo/session predicates; exact
phone/OBB/historical bridge evidence still missing. Queue handoff will identify
the substantive integration commit once created.

Body/session integration commit: `40c4aafe6665e671d08df6badb378121ec4ff213`. Updated assignments record that
actual SHA and the downstream bounded continuation; earlier integration refs
are preserved. No new phone/source claim or completed framing packet.

## 2026-10-30 — exact auth receive failure integrated

Reviewed9a0d6ef09c6b62a4543c8c9aadef15f1946df470; source packets9a0/14a49 and phone
reports09–12. ACK63 -> authentic0x2001/117 is confirmed; auth/session still blocked.
All three exact v1.2 replies fail bodyAA/99 mode with A5/-32, auth maps-18, before
account parsing. Independently regenerated native matrix and reran25 incoming
controls. Integrated bounded encoder, separate fixture adapter, full-native trace
and regressions; preserved original hashes/headers/accounts and explicit stubs.
Canonical128 PASS private-selected; default95 PASS/33 SKIP; doctor/source verifier
PASS. No phone/network run; corrected parser reaches state4/Bingo wait only.

Updated stale checkpoint/queue/ICM/graph and reported historical APK parity limits.
Preserved incoming/unfinished path drafts. Deployed v1.2 source/directional EOF
still missing; no direct local-server deployment is claimed. Next offline work:
Bingo/session/application predicates; separate submitted99 boundary review.
[Integration](../../coordination/INTEGRATION.md) and [auth trace](research/AUTH_RECEIVER.md).

## 2026-10-30 — coordinator resumed and completed auth/Bingo integration

Resume main ccdd219f9ed121e77fc06ad20b50b77614079cbf; preserved prior interrupted
canonical draft and all incoming files. Auth25, local Bingo21 and submitted
path8 tests reproduced; actual original-source integrity/CMS/1212 entries PASS.
Integrated the body encoder/fixture regressions and original Bingo negative
controls with exact local-input provenance, no invented source packet commit.
Both matrices reproduced exactly. Canonical149 PASS/private-selected; default
97 PASS/52 SKIP; doctorPASS. Current phone ACK->0x2001 evidence reconciled.
3002 corrected to WAIT; malformed header/body can reach native5, never counted
as authentication. No valid Bingo/credentials, deployed bridge wiring, phone run
or playable state. Updated canonical knowledge/graph/ICM and bounded lane queue.

## 2026-10-30 — direct user-requested offline callback investigation

Schedules stayed paused. Refreshed c9b1d355 and its new CF05 bridge handoff;
rechecked pinned original Apollo and actual environment. Reviewed/reran completed
local CF02 application13 controls without editing incoming paths. Added actual
observer thunk/connector/local-result/UI-boundary and separate AddressService
branch controls. Local connected/result0/bind/open are not account validation.
Eleven new tests; canonical160 PASS private-selected, sourcefree98 PASS/62 SKIP;
ten-case matrix reproduced exactly; doctor PASS. Original binaries untouched.
[Trace and limits](research/CONNECTION_CALLBACKS.md). No phone experiment run.

## 2026-10-30 — direct user DLL startup investigation

Base6a0ecc16 refreshed, actual original APK/DLL/native hashes/ISA checked. Found
stored game DLL/firstpass are non-PE, unlike13 other assemblies. Original Mono
detour to libtprt reproduced; actual signature branches, CRC routine and injected
post-load checksum mismatch termination path tested. Historical edited bytes/logs
not present, so no causal phone failure or safe patch claimed. Added read-only
header/diff preflight and bounded native controls;176 canonical PASS/private,
106 PASS/70 SKIP sourcefree, doctorPASS. [Trace](research/INTEGRITY_NATIVE.md).
All originals untouched; scheduled workers and session track stayed paused.

## Integrity-02 continuation

Pinned Unity caller/import and seven provider constructors traced statically. Four actual caller-result controls PASS, injected results explicitly distinct from a DLL load. No unchanged round trip yet.180 canonical PASS private;107 PASS/73 SKIP default; doctorPASS. Originals untouched/schedules paused.

## 2026-10-31 — user requested route comparison and continued best-supported path

Reviewed latest main/phone14–16/incoming server findings. Chose local-server
continuation on actual client progression; integrity parked, no halfway/gameplay
claim. Native routed TX copies BE packet-sequence32+application payload; seven actual-native
controls stop before encryption/send and verify guards. Incoming Bingo13 and
address14 synthetic tests rerun. Canonical187 PASS private;108 PASS/79 SKIP default;
doctorPASS. [Decision and evidence](research/SERVER_PATH.md). No original edits,
phone test or scheduled worker restart. Incoming remote files hydrated read-only;
no incoming paths included in coordinator commit.

## 2026-10-31 — v3.8 attachment supersedes older observer context

Read/hash actual5383-byte user report. Reconciled2/4 laterframes and no4013reply. Added four native crypto-boundary tests proving compression context does not determine key/copy branch.191 canonical PASS private;109 PASS/82 SKIP default; doctorPASS. [Review and limits](research/V38_BLOCKER.md). No private capture or credentials published, no schedule/phone run.

## 2026-10-31 — exact v38 source/native differential

User requested active investigation. Opened exact ZIP privately; source audits PASS. Original receiver replay selects mode0 through exact lab stages with stated stubs/state3 injection. Actual native header writer agrees with v38 legacy classifier. Corrected earlier UID interpretation to native packet sequence and verified real counter increment. Prepared private metadata-only observer copy preserving all outgoing replies; original/prepared9 focused tests PASS each.205 canonical private PASS;117 PASS/88 SKIP default; doctorPASS. [Full evidence/integration](research/V38_SOURCE_AUDIT.md). No native rejection of actual phone payload localized, no guessed response or phone test. Schedules paused.

## 2026-10-31 — owner requested proactive handoff and existing workflow continuity

Read actual v38 PCAPdroid/Termux package before preparing portable patch-only kit. Added CURRENT_HANDOFF to mandatory entrypoints and every ICM route; consolidated checkpoint/cold-start so historical missing-source/no-first-hop blocks cannot replace current facts. Kit consumes existing owner ZIP, preserves replies/handler, adds fixed diagnostics and versioned report/IDs. Four synthetic sessions through actual SOCKS5 redirector/server and unrelated binary passthrough PASS.209 canonical private PASS;120 PASS/89 SKIP default; doctorPASS. No phone run, original edit or schedule restart.

## 2026-10-31 — continued real native application investigation

User asked for concrete blocker/action. Executed generated QueryAddrInfo args/result instructions with explicit memory/string-runtime substitutions. Native args34+N and full legacy/strict positive controls show observer can recognize those complete forms; real request still unknown. Native result requires reason STRING; missing field reaches0x39ead8. Integrated corrected original CF05 preflight canonically; incoming files unchanged.12 native controls and15 preflight methods PASS;236 canonical private PASS /137 PASS+99 SKIP default; doctorPASS. No new phone response/run or kit change.

## 2026-10-31 — reviewed actual v381 phone upload

[New evidence](research/PHONE_V381.md): sequence and exact QueryAddrSvr route MATCH in both routed samples; lexical method-name policy failure at offsets0/4, not truncation/length. Next native producer candidate CTGcp::onDataOutEvent direct send edge3a5476. Preserved4 outcomes/EOF limits. No repeat phone request; latest result nowv381, no accepted operation/response. Default236 total137 PASS/99 SKIP, doctorPASS.

## 2026-10-31 — owner requested full source and repository context check

[Audit](research/REPOSITORY_SOURCE_AUDIT.md): no full XAPK/OBB downloaded; verified APK/Apollo/storedDLLs rehashed. Complete live tree and23 incoming reports reviewed; historical missing-source/no-post-ACK summaries superseded. Continued original-static producer trace to CTGcp Write overloads/queue; next upstream caller buffer construction. Default236 total137 PASS/99 SKIP, doctorPASS. Originals unchanged, no repeated phone test or source download.

## 2026-11-01 — upstream original-native request construction traced

Pinned local original Apollo SHA2564812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8, size5243704, ELF32 LE ARM. LLVM Thumb disassembly/readelf used for 11 explicit source instruction checks; 11/11 PASS. Traced ProcessRequest -> Send_QueryAddrInfo / generated args writer and MsgBuffer bind/writeEnd bound IConnector callback -> CGCloudConnector::Write -> CTGcp route queue -> send event. The bridge between the virtual endpoint and the phone's actual concrete invocation is **not** measured. [Finding](research/UPSTREAM_REQUEST_CHAIN.md); no new service operation, reply, phone test, decoder fix, binaries or credentials. DLL work and schedules remain parked.


## 2026-11-01 — static source-pinned producer verifier, no new phone data

Added original-code read-only `producer_boundary_audit.py` plus synthetic and private-source-gated tests. Exact original Apollo SHA-256 pinned; 24/24 instruction checks PASS across seven Thumb regions, five source-free tests PASS and one original-source test PASS when provided (otherwise SKIP). Confirmed original virtual calls/message callback/size and connection guards. No whole-message native execution or matched runtime producer/response; all schedule and client modification freezes unchanged. See [UPSTREAM_REQUEST_CHAIN](research/UPSTREAM_REQUEST_CHAIN.md).

## 2026-11-01 — source-pinned reciprocal RX ownership audit

Read exact original Apollo and added seven new pinned checks across AddressService::OnDataRecvedProc, its session-lookup response processor, RpcConnector::OnDataRecvedProc and its typed message dispatcher. Auditor now 33/33 native **static** instruction pins PASS; six Python tests PASS with original private source (source-free 5 PASS/1 SKIP). No original-native whole-message execution, phone observation, response generated, network/server modification or gameplay progress. [UPSTREAM_REQUEST_CHAIN](research/UPSTREAM_REQUEST_CHAIN.md).

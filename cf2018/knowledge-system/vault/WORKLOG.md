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

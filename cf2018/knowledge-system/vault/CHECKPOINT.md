# CHECKPOINT — 2026-10-30, body/session integration

**Goal:** real offline TDM and Bomb/S&D in CrossFire: Legends 2018 v1.0.11.11
`com.tencent.tmgp.cfmnac`, Mono. **NOT PLAYABLE. G2 BLOCKED.**

## Current reviewed evidence

- [Mirror source](../../sources/SOURCE_PROVENANCE.md) is privately available on
  this runner and internally verified: exact package/version, APK/member hashes,
  ELF32 little-endian ARM EABI5, Mono assemblies and all 1212 signed APK entries.
  It was recovered after the user's explicit internet-search instruction.
  Phone-build equality, matching OBB and full XAPK identity remain unverified.
- [Receiver trace](research/ACK_RECEIVER.md): GCloud ACK calls receive/decrypt and
  its GCloud splitter. The 0x4366 check is on a decoded base field after TLV;
  both raw 43 66 and 66 43 fail in that mirror path. The v0.8 raw-prefix premise
  is retired for this hash/path; actual phone runtime selection is not proven.
- ACK extension selector supplies effective type. Key mode 0 can reach the empty
  stage; later encrypted data can still fail. Native return zero does not prove
  a complete accepted ACK or negotiated session. No server field echo/generation
  policy is justified. The [body/session continuation](research/ACK_SESSION.md) identifies received
  timestamp use in the next auth request and a separate auth-response account
  copy/state-4 branch. Parser-zero copy controls are explicitly stubbed; no
  authenticated session is demonstrated. Downstream Bingo/session uses remain open.
- Canonical [offline parser](../../experiments/rx_envelope.py) and
  [source verifier](../../tools/verify_private_source.py) are integrated original
  code. Parser extensions are opaque, base_type is not an effective ACK type,
  and finish is terminal. No reply builder/listener or device runner was added.
- [Relay/handoff](research/RELAY.md) remains locally validated diagnostic stages.
  Historical v0.1-v0.8 bridge sources, original reports and deployed post-method
  passthrough interface are still missing. Q-02 EOF cause remains UNKNOWN.

## Historical phone observations — originals not revalidated

Signed-only original-code startup reached update checking; edited managed DLL
exited early. PCAPdroid SOCKS5/Termux captured 133-byte QueryAddrSvr SYNs. v0.5
reported passive median 7003.04 ms versus synthetic-ACK median 10.99 ms,
ACK-to-EOF 8.44 ms and zero later client packets. v0.6 logcat did not identify a
reliable native reject. No new phone run, accepted ACK, auth, AddressService,
updater/config progression, offline lobby or bot match was obtained here.

## Prior coordinator checks

Reviewed base `c52243228e8d2d38dd6b4c1d85f464d9f94461f8` and all 55 tracked CF2018
blob hashes. The local snapshot is not a git checkout; git status exited 128.
Knowledge doctor PASS. Canonical suite: 83 tests PASS with private APK selected
(52 previous, 17 framing, 14 source controls). Source-free run: 83 total,
81 PASS and two private-source SKIP. Separately CF18-01 32, CF18-02 25 and
CF18-04 14 lane tests PASS, no skips, with actual private source selected.
Native emulation has explicit stubs and does not count as Android/phone proof.
[Integration record](../../coordination/INTEGRATION.md) records the review.

## Current body/session checks

Reviewed live main `37b808d095641c90e80a707209f656e9bf29c53f`; 64 tracked blobs
checked, only the preserved local CF18-02 RESULT continuation link differs.
No git checkout or active worker process. Completed local CF18-02 continuation
has no remote source commit; actual draft hashes are recorded in integration.
Reran 40 lane methods and checked bounded native branch/data-flow sites against
actual pinned ARM source. Canonical original native runner/session controls and
18 tests integrated, including three coordinator controls. Full suite: 101 PASS
with private APK/library selected; default: 101 total, 82 PASS, 19 private-source
SKIP. Knowledge doctor PASS. Incoming drafts and original binaries stay private
or unchanged, respectively; no phone/network experiment was run.

## Next exact task and prerequisites

[Assignments](../../coordination/assignments.json) retain exclusive paths and
one task per lane. CF18-02 continues CF18-G2-ACK-01 on downstream copied-account,
Bingo and session predicates. CF18-01 owns remaining 99/bounds/lookahead behavior. Both require the
pinned source available and verified in that activation; schedules do not imply
a shared disk. CF18-03 awaits actual historical/deployed bridge interface.
CF18-04 awaits new phone/OBB/historical-source evidence; no repeated asset scans.

G0 remains partial on phone/OBB identity. No A/B/C candidates or device plan are
ready: runtime context, justified session candidate and relay prerequisites are
missing. A later authentic post-ACK client protocol packet is still mandatory
for G2 advancement. See [EVIDENCE](EVIDENCE.md), [questions](OPEN_QUESTIONS.md).

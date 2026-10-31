# CF18-00 integration record — 2026-10-30

Reviewed base main `ec0d55fd338df6cc6f7d1e7aad59c7885fa88f06`. Sole coordinator
owns canonical code/tests, assignments and knowledge. Lane packets stay immutable
unless their owner revises them. Local drafts are not assumed to exist on later
runners; the integrated canonical files are the durable handoff.

| Lane | Actual input | Coordinator disposition |
|---|---|---|
| CF18-01 | [Framing audit](incoming/CF18-01/RESULT.md), commit 0a5cf7496471f25809bb62242c3365670ce006db | Eight audit tests rerun successfully. Integrated model limitations and corrected historical-premise wording. No native RX finding accepted. |
| CF18-02 | No remote packet at reviewed base; preceding activation explicitly reported no native evidence or code | Q-03/Q-04 remain blocked on exact original-library provenance and branch trace. No validator or accepted-ACK claim integrated. |
| CF18-03 | Preserved local original draft from the interrupted transport activation; no submitted remote packet | Read/reviewed the actual source and 16 tests, copied to canonical paths, adapted imports and added three directional/resource controls. Nineteen relay tests passed. No historical EOF attribution accepted. |
| CF18-04 | [Bounded source inventory](incoming/CF18-04/RESULT.md), commit ec0d55fd338df6cc6f7d1e7aad59c7885fa88f06 | Integrated accessible-folder metadata, partial-listing limits and known-file search-control failure. No target binary/version/hash verified. |

Local draft SHA-256 provenance, calculated from actual files before copying:

- passive_relay.py: `a8e2c5367fd74bbbcef2ba6cdeef4fbad1069b3b984c78ab2852255a6fef0a99`
- test_passive_relay.py: `33fc54685541ac1c339fb11c1b96486d16576546178221c3ea73589874435e2b`
- ACCEPTANCE.md: `2a77828fdc8367e60a46fb749ec0026f7281d1fcb07e6b7844951ec4f9b54ff0`

These identify original new diagnostic text, not game binaries. The local draft
has no fabricated packet commit SHA. Canonical paths are experiments/passive_relay.py
and tests/test_passive_relay.py; [relay research](../knowledge-system/vault/research/RELAY.md)
records interface, limits and actual checks. Only the coordinator writes those
canonical paths; future CF18-03 proposals belong under its incoming directory.

Actual validation: knowledge doctor passed; `python -m unittest discover -s tests -v`
passed 29 tests; CF18-01 explicit lane command passed eight additional audit tests;
direct passive_relay.py invocation printed its disabled message. Tests use only
synthetic data/localhost, with no game source, live endpoint, device or ACK test.

Earliest unmet prerequisite is G0 source provenance; G2 stays BLOCKED. No native
receiver-state trace or device A/B/C implementation is warranted yet. Code/evidence integration commit is
`15be6fc1401a164f00c2d3c9623ba29d6ac7ac53`. The coordinator recorded this exact
commit in [assignments](assignments.json), making the bounded SOCKS5-adapter
proposal ready for CF18-03.
Native lanes and source retrieval remain explicitly blocked until new evidence
or a verified private locator is supplied. Do not manufacture ready work or repeat
unchanged source searches/status reports.

## CF18-G1-SOCKS5-01 review — 2026-10-30

Reviewed source packet commit `9f77b2cbf9f0249b566c75e8a4e42666cb44c292` at that
exact live base. CF18-01/02 native prerequisites and CF18-04 source receipt were
unchanged. No new source search was justified. Local snapshot matched all 38
tracked CF2018 blobs; it is not a git checkout.

Accepted only the bounded original NO-AUTH/CONNECT negotiation and route-handoff
stage into experiments/socks5_handoff.py and tests/test_socks5_handoff.py. Adapted
imports; added two coordinator checks for reset-message privacy and declared
variable-length truncation. Canonical suite: 52 PASS; CF18-01 audit: eight PASS;
knowledge doctor PASS; direct invocation remained disabled. Incoming lane files
were not changed and no listener/connector was installed.

This does not integrate a complete deployed SOCKS5 bridge: the handoff has sent
METHOD=00 but leaves target connection, correctly bound CONNECT reply and normal
passthrough dispatch to the caller. The real historical hook is unavailable, so
CF18-03's next deployment-wiring task is blocked on that source/interface. Q-02
and G2 are unchanged. Canonical integration commit is
`f70a874ed903b030fd51a94a36dff0ca43dcfff4`, recorded in [assignments](assignments.json)
as INTEGRATED_BOUNDED_STAGE. The completed proposal is not assigned as READY;
the next bridge-wiring task is BLOCKED_SOURCE.


## Recovered mirror native/source review — 2026-10-30

Reviewed live main c52243228e8d2d38dd6b4c1d85f464d9f94461f8. All 55 tracked
CF2018 snapshot blobs matched; git status returned 128 (not a checkout). No
active lane claim was overwritten. [Acceptance](NATIVE_INTEGRATION_ACCEPTANCE.md)
was defined before canonical code edits. Incoming lane packets remain unchanged.

| Lane / actual source commit | Reviewed disposition |
|---|---|
| CF18-01 fefd0dc224851fefc2b74a51fc95e0fa0090e9a2 | Reran 32 tests including nine native controls. Accepted decoded-marker interpretation for pinned GCloud path and original AA/varint offline subset; no phone runtime claim. |
| CF18-02 56db53d81326810d5bea342b11ea4e07dc351e01 | Reran 25 controls. Accepted bounded type/key/body/error/state predicates and their stub limits. Optional body/embedded-auth/session consumers still unfinished; no server field-generation or accepted-ACK policy. |
| CF18-03 9f77b2cbf9f0249b566c75e8a4e42666cb44c292 | No new packet; existing core/handoff remain integrated. Canonical 19 relay/23 handoff controls rerun in full suite. Historical/deployed bridge source still missing; no EOF conclusion. |
| CF18-04 c52243228e8d2d38dd6b4c1d85f464d9f94461f8 | Reran 14 controls including actual CMS/all 1212 signed-entry checks. Accepted mirror source receipt/pins and original local verifier. Phone/OBB/Drive-target equality remains unverified. |

Integrated canonical experiments/rx_envelope.py and tests/test_rx_envelope.py
from CF18-01 original code. Coordinator adaptations: rename message_type to
base_type to prevent a base field implying effective extension type; finish is
terminal. Two additional independent controls cover those boundaries (17 total).
It is an offline strict subset with opaque extensions, not a server ACK or full
native parser. 99, duplicate/unknown acceptance and gather/lookahead timing remain
outside parity claims.

Integrated original tools/verify_private_source.py and
[14 controls](../tests/test_verify_private_source.py) from CF18-04, with adapted
canonical imports/document pointer, plus descriptive sources/MIRROR_RECEIPT.json.
No original file is published. No download/listener/game execution is introduced.
Default CLI is inactive; selected private paths are pinned before interpretation.

[Canonical receiver trace](../knowledge-system/vault/research/ACK_RECEIVER.md)
now focuses CF18-G2-ACK-01. Corrected E-09/Q-01/current startup docs, source
manifest, source provenance, navigation, ICM/Graphify and ADR-0002; preserved
historical phone/report limits in EVIDENCE and WORKLOG. frame_gate.py behavior
is unchanged and explicitly retired as a raw-prefix hypothesis model.

Actual checks: knowledge doctor PASS; 83 canonical tests PASS with private APK
selected; source-free suite 83 total with two private-source skips. Lane suites
32/25/14 PASS without skips. These are local/synthetic/private-source and bounded
native emulation with explicit stubs. G2 BLOCKED; no A/B/C candidates or device
plan is ready. Substantive integration commit is
`88c439b7938642076f721c0ec9319fd45d008420`; the compact [assignments](assignments.json)
handoff records that exact SHA and one bounded task per lane. CF18-01/02 are
ready only with actual pinned-source access; CF18-03/04 retain missing-evidence
prerequisites. No self-referential commit hash is invented.

## ACK body/session continuation review — 2026-10-30

Reviewed main `37b808d095641c90e80a707209f656e9bf29c53f`. The completed local
CF18-02 body/session continuation was interrupted before remote publication;
there is **no source packet commit** for it. No worker process was active. This
coordinator review integrates actual local original code/findings without editing
incoming files or inventing a submitted commit. CF18-01's unfinished boundary draft
is preserved and not integrated. CF18-03/04 have no new bridge/phone/OBB evidence;
their existing blockers remain unchanged. G0 phone/OBB identity is still the earliest
unmet prerequisite; useful independent native G2 research can continue locally.

[Acceptance](ACK_BODY_INTEGRATION_ACCEPTANCE.md) preceded canonical changes.
All 64 tracked blobs were checked; only the existing local CF18-02 RESULT link
addition differed from remote. Git status returned 128, not a checkout.
Exact SHA-256 provenance of actual CF18-02 local input text:

| Local original file | SHA-256 |
|---|---|
| BODY_ACCEPTANCE.md | afd7adb120999560ec9eace95df6afa41d51562f09be5004fa3cf649ec715480 |
| BODY_RESULT.md | b5e66948d76a7008bae0919bc09f63f5be4342206903ea97f2c7104f2413477f |
| native_body_controls.py | 09eaf2bb1a6c11a44b947715e713a469db5de1bfa772d05d60239577b36ee190 |
| test_native_body_controls.py | 8b697a6c68ced1080dc4344ec4eea5d0fd03c3e7f346441e49f5e34b6ffdf429 |
| native_ack_controls.py (previously published base runner) | 186f3a1653289897f60c8a9b3aae62e36ff89af5ace40426c98c047c96e6f317 |

Recalculated pinned library hash/ARM ISA; independently inspected actual bounded
Thumb data-flow/branch sites for auth timestamp, ACK nested component, separate
auth receiver and state handler. Reran all 40 CF18-02 lane methods, no skips.
Accepted received timestamp -> next auth field, optional-body storage and examined
immediate caller, and separate auth-response copy/state branches. Exact trace,
addresses, evidence classes, stubs and limitations: [ACK_SESSION](../knowledge-system/vault/research/ACK_SESSION.md).
No server timestamp/echo policy, valid ACK/auth response, cipher negotiation,
phone-path identity, login or authentic later client packet is inferred.

Canonical original experiments/native_control.py extracts only the existing
hash-pinned runner class (unused snapshot/probe entrypoints omitted).
experiments/native_session_controls.py adapts the local continuation import.
tests/test_native_session_controls.py adapts 15 local methods and adds two native
controls for fresh context and state receive failure, plus a dependency-free
fingerprint guard. Optional imports remain lazy; no network, download, listener,
serializer or CLI action. Fresh mappings, source pin, ISA and execution budgets
are retained. Parser-zero controls explicitly label their stub; timestamp probes
stop before account/token/hash construction.

Actual canonical private-selected run: 101 PASS, zero skips. Default run: 101
methods, 82 PASS, 19 SKIP (17 native methods and two private APK controls).
Knowledge doctor PASS. Source selection/dependency commands and limits are in
ACK_SESSION. Updated receiver/current knowledge, E-19, questions, ADR-0002, navigation
and Graphify; incoming/root app files unchanged. The queue handoff records the
exact substantive integration commit after it exists, with one bounded task per
lane. Next native task is downstream copied-account/Bingo/session validation;
phone/OBB/relay prerequisites remain. G2 BLOCKED and A/B/C readiness false.

Substantive body/session integration commit: `40c4aafe6665e671d08df6badb378121ec4ff213`. The queue handoff
records that exact reference and moves CF18-02 only to downstream account/Bingo
predicates. The incoming continuation remains unchanged and has no invented
remote packet SHA; CF18-01 still must finish its own boundary draft.

## CF18-G2-AUTH-RX-02 coordinator integration — 2026-10-30

Reviewed live main9a0d6ef09c6b62a4543c8c9aadef15f1946df470. All tracked blob hashes
checked: existing CF18-01 native_boundary_controls.py and CF18-02 RESULT.md local
changes preserved. Existing coordinator assignments/integration/worklog handoff
edits retained and reconciled; prior substantive body integration is40c4aafe6665e671d08df6badb378121ec4ff213.
Ten missing tracked CF18-05 snapshot files restored from exact connector reads;
not new remote changes. No git checkout, no active worker process.

[Acceptance](AUTH_RX_INTEGRATION_ACCEPTANCE.md) preceded code changes.
Reviewed four lanes: CF01 boundary0019dfb52700dd74c9563ea970afcdcb544b8355 submitted,
held for separate strict99 integration; its unfinished path draft preserved.
CF02 auth9a0 packet independently reproduced and accepted. CF03 still lacks actual
deployed v1.2 source/directional closure proof; older core/handoff remains bounded.
CF04 source receipt unchanged; CF05 historical APK parity and phone09–12 reports
reconciled with explicit reported-evidence limits. Source pins/ISA/CMS/all1212
entries rechecked, no downloads or original modifications.

Earliest native defect is missing TGCPBody preamble on all three exact v1.2
responses: body modeA5 -> -32 -> auth-18 before account parsing. Existing framing,
extension2002 and receive pass. Correction adds5bytes and recomputes outer length;
real corrected path reaches state4/Bingo waiting, not authentication. Native
matrix exactly regenerated. [Canonical review](../knowledge-system/vault/research/AUTH_RECEIVER.md)
contains every stage, predicate, stub and remaining unknown.

Canonical original code adapted ONLY from the public CF02 auth_rx_02 packet:
- experiments/auth_v12_fixtures.py unchanged from public fixture source.
- tgcp_body_envelope.py contains reusable bounded body encoder; pinned fixture
  offset repair moved to auth_fixture_repair.py so no arbitrary server patch API.
- native_auth_rx.py removes lane-specific sys.path; reuses canonical pinned runner.
- auth_native_matrix.py adapts imports and remains inactive without --library.
- tests/test_native_auth_rx.py adapts18 controls and adds exact cap/one-over test;
  test_auth_fixture_pins.py retains all7 public fixture regressions.
- knowledge route gains tested auth/Bingo/2001/2002/session context.
Older local canonical auth drafts backed up privately, not published as new input.

Actual incoming25 PASS; canonical128 PASS/no skips with private APK/library/deps;
default128 total95 PASS/33 SKIP; doctorPASS. Canonical matrix equals submitted JSON.
No parser/gather/decrypt/Bingo success stub, no socket/game/device test. Updated
Vault/E20–22/ICM/Graphify/navigation/source limits and assignments. Incoming lane
files and root app untouched. No live bridge wiring claim: actual v1.2 source is
missing. V1.4 justified in principle only after directional integration, six
connections with silence/old49/corrected54 and unchanged successful ACK. No
credential/key/account sweep, valid Bingo or automatic phone experiment.

This entry and queue are included with the substantive code/evidence change;
its commit SHA is discoverable in Git history, not invented as a self-reference.

## Coordinator resume: downstream Bingo review

Resume main ccdd219f9ed121e77fc06ad20b50b77614079cbf. The local CF02 bingo_01
draft was interrupted by lane reassignment and has NO remote packet commit.
Exact SHA-256 of actual local inputs reviewed:

| Local CF02 bingo_01 input | SHA-256 |
|---|---|
| ACCEPTANCE.md | 7e90e03ef0cb06857593dfe3f46936fc57cf81e772bfa3939c2b245a2c39795c |
| RESULT.md | d512d6a5b6850c6b252d3f76333dc6605c7ac2a9b5d8a63415b9f7b1a31b8c7d |
| bingo_controls.py | cabf1483b0130c6a3680604d8c82d44983d53f593cbce62bb712379d65978af0 |
| test_bingo_controls.py | 5b90d0359c3c7efdd1921eafc858740d374f3a67e82a1cee46f3bc8c11b17aeb |
| run_bingo_matrix.py | c540b9f3ed1f180d20d5fbc6f667f8c3fc677958e754807ad54c50d58aebf9d5 |
| NATIVE_MATRIX.json | 655b1d511408c1d34c7953989b89211965d79ccaa80fa456069897c0e4889663 |

Coordinator reran incoming auth25, local Bingo21 and submitted path8 controls.
Canonical149 PASS with explicit private APK/library/dependencies; default149
with97 PASS/52 SKIP. Source verifier PASS/CMS/1212 entries; trust-chain not
validated. Both actual native matrices reproduce exactly after canonical imports.
Bingo canonical code changes imports only; tests adapt source paths; no original
Bingo/session data is introduced. The deliberate malformed type-correlation
controls reach native5 without Bingo component; this is not protocol acceptance.

Integrated canonical native_bingo_controls.py/test_native_bingo_controls.py and
bingo_native_matrix.py, actual BINGO_MATRIX.json and BINGO_SESSION research.
Corrected3002 WAIT terminology and current acceptance boundaries. Reviewed CF01
factory/wrapper evidence as bounded only; its strict99 proposal remains pending.
No incoming file edited, no root app change, no deployed relay source recovered.
Current exact auth failure remains body preamble; v1.4 wrapper-only comparison
is conditional on source/instrumentation. No automatic phone test or positive
Bingo serializer. This substantive change includes shared code/knowledge and
queue together; commit identity follows from Git history, not a self-reference.

## Direct callback investigation at c9b1d355

Completed LOCAL CF18-02 session_app_01 packet reviewed,13 native controls rerun; no source packet commit exists and no incoming file changes. Input SHA-256 pins:

```json
{
  "ACCEPTANCE.md": "c7219a0cc0ea8d29ae8066f65c398c627454e14e8593cfdcf11660cc2e47b253",
  "NATIVE_MATRIX.json": "d32673221c3f4435f2df79b9f9e36067f0e24542d7e04c734105f5b89e6d32ac",
  "RESULT.md": "d8a0d8d3e616f523d7de526f8ff9df98ba50104e1eb979c3d237be49a87e57e5",
  "native_app_controls.py": "2adfdb0259230df2ad9565b26ffb7cdc7b6dba1cfffe42440ceaa7decf6ceeda",
  "run_native_matrix.py": "b1b1200c8f8d45cfe0e59dbe070e717b1d03145f634858a38c13fb3424125f87",
  "test_native_app_controls.py": "1177758e02d14d4882a8c4742b6a10b6c946bcce05cd07e2f6409ccd18b67c54"
}
```

New canonical callback controls use only canonical NativeControl; they do not import unpublished lane code. [Trace](../knowledge-system/vault/research/CONNECTION_CALLBACKS.md) and [acceptance](CF18-G2-CALLBACK-01/ACCEPTANCE.md) identify independent-stage/stub boundaries. Eleven new tests/ten cases;160 canonical PASS private-selected,98 PASS/62 SKIP sourcefree. CF05 c9b1d355 private bridge recovery is reported evidence, not independent coordinator source review. No schedule restarted or phone experiment performed.

## CF18-INTEGRITY-01 direct user investigation

Base6a0ecc16877adbdc4eed03cefebb5b4144f7bd6f, original main. User explicitly
requested reliable DLL modification investigation; session assignments unchanged,
schedules paused. [Acceptance](CF18-INTEGRITY-01/ACCEPTANCE.md), [report](../knowledge-system/vault/research/INTEGRITY_NATIVE.md),
[actual matrix](CF18-INTEGRITY-01/NATIVE_MATRIX.json). New independently original
host controls and read-only preflight, no incoming lane writes. Source pins in
report/matrix are actual hashes of members from pinned private APK. No original
binary/decrypted image/raw disassembly/key uploaded. Native provider handoff and
injected CRC-mismatch termination branch verified; historical phone cause and
safe modification remain unknown.176 canonical PASS private-selected; default
106 PASS/70 SKIP; all16 affected methods PASS; source matrix reproduced exactly.
No patch, original modification, installation, game execution or phone request.

## Server-priority reconciliation and routed TX

Base5d76e82696984717e394552cc6fb9c076e77e01f. Reviewed CF05 published phone14,
15,16 summaries, Bingo/Address static reports; reran Bingo13/address14 synthetic
controls. Incoming files downloaded for read-only local context, never modified
or included in this commit. No newly retrieved raw phone capture. Canonical
latest checkpoint supersedes historical no-post-Bingo statements. Integrity parked
by user-directed priority comparison; schedules remain paused. New original
native routed-TX runner, seven controls and metadata matrix verify pre-encryption
BE UID32 + application bytes, guards and4013 header; intercept encrypt/send.
187 canonical PASS private-selected;108 PASS/79 SKIP default; doctorPASS.
[Full decision, addresses, stubs and limits](../knowledge-system/vault/research/SERVER_PATH.md).
No generated server reply/valid identity, original modification or phone run.

## Latest v3.8 report review

Base d04cfe9a1e54f8c5e01e5839476e84beb834468a. Read original attached metadata text, actual SHA/size recorded in [review](../knowledge-system/vault/research/V38_BLOCKER.md). Only rights-safe summary published, no private payload. Four native helper methods PASS;191 canonical PASS private,109 PASS/82 SKIP default, doctorPASS. Probe source absent; no invented decoder/reply or phone rerun.

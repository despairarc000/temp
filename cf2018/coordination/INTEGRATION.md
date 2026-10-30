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
plan is ready. The exact substantive integration commit will be recorded in the
next compact assignments handoff after it exists, without inventing its own SHA.

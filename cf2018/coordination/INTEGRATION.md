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

# CF18-00 — auth receive integration acceptance

2026-10-30. Reviewed main 9a0d6ef09c6b62a4543c8c9aadef15f1946df470.
Integrate the submitted CF18-02/auth_rx_02 packet, not older local drafts.
Preserve incoming files and existing unfinished CF18-01 path work.

Before editing: required live documents, assignments, Graphify dependencies and
CF18-05 phone/fixture receipts read; no active native worker; snapshot is not a
git checkout. Default baseline: 101 total, 82 PASS, 19 private-source SKIP.

Acceptance: recompute source pins/ISA and full APK integrity; independently
reproduce all three original native failures and corrected paths, including
exact fixture pins and negative controls. No parser/gather/Bingo-success stub.
Promote only the body-envelope encoder and offline controls; no listener,
credential generation, live deployment or authentication-success assertion.
Separate reusable envelope encoding from fixture-specific byte-offset repair.
Add a coordinator control for the exact maximum body budget and one byte over.

Reconcile verified phone SYN133 -> ACK63 -> auth117 with current knowledge.
Preserve earliest native body failure (-32 mapped to -18), waiting for Bingo,
and the separate unknown EOF origin. Historical reported APK hash parity does
not establish installed APK or OBB equality. Update Vault, ICM, graph and one
scoped task per lane; track previous actual integration SHAs without inventing
this commit's self-reference. Check links and all canonical/affected tests.

Failure modes: fixture drift, source mismatch, altered stub behavior, changed
account/header bytes beyond wrapper/length, incorrect lengths, malformed input,
wrong type, encryption-without-key, wait mistaken for session success, missing
deployed bridge source, or publication outside the canonical allowlist.
Any one blocks the corresponding claim. No automatic phone experiment.

## Resume and downstream review acceptance — 2026-10-30

Resume base ccdd219f9ed121e77fc06ad20b50b77614079cbf. The prior canonical draft
was interrupted by exclusive lane reassignments; it is not a previous published
integration. Preserve all incoming drafts. Independently reproduce the local
CF02 bingo_01 continuation, record actual input hashes rather than invent a
packet commit, and integrate only supported negative controls/data flow.
Correct3002 WAIT terminology; state5 is insufficient if actual mismatched wire
can reach it. Keep decoded parser-zero stubs separate from real full-wire tests.
Review submitted CF01 path controls without claiming device runtime selection.
Publish one substantive canonical code/knowledge update after actual checks.

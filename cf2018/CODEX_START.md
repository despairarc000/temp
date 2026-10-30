# CODEX START — CF2018
This is the first task packet; do not assume the server is working.

## Required cold start
1. Open [AGENTS](AGENTS.md), [NAVIGATION](NAVIGATION.md), [IDEA_PLAN](IDEA_PLAN.md), and [CHECKPOINT](knowledge-system/vault/CHECKPOINT.md).
2. Run `python tools/knowledge.py route tgcp ack`, `python tools/knowledge.py doctor`, `python -m unittest discover -s tests -v`.
3. Open [TGCP](knowledge-system/vault/research/TGCP.md), [evidence](knowledge-system/vault/EVIDENCE.md), [questions](knowledge-system/vault/OPEN_QUESTIONS.md), and the [Drive locator](sources/DRIVE_MANIFEST.md).

## Next engineering packet: CF18-G2-ACK-01
**Problem:** 65-byte synthetic ACK closes the client's socket quickly; no post-ACK packet. v0.8 predicts a first-frame prefix error but acceptance is not proven.

**Research:** Obtain the exact 2018 `libapollo.so`, verify its provenance/hash/ISA and establish actual incoming-splitter and ACK-receiver addresses. Current Vault summaries do not supply a reproducible native branch trace. Prove the exact 2-byte magic comparison, byte ordering, cursor/length handling, session correlation, key-mode constraints, and whether the previous SOCKS5 relay could independently cause EOF.

**Deliverables:** a receiver-state trace with exact branch tests, confidence labels, minimal standalone safe implementation, tests for truncation/reordered bytes/size mismatch, and one explicitly gated on-phone A/B/C design. Keep default passive; do not run an unbounded live experiment.

**Acceptance:** static validation and tests are separate from game proof. Only a later real client packet after ACK counts as protocol advancement.

## Artifacts and access
The actual v0.1–v0.8 experimental packages and phone reports were exchanged in the earlier ChatGPT workflow; this public GitHub repository currently contains the consolidated knowledge and a safe standalone [frame-gate hypothesis test](experiments/frame_gate.py), **not a wholesale import of those packages**. To run the historical full v0.8 probe, the original source package is needed from the prior experiment; do not claim the small `frame_gate.py` is the full replacement.

[DespairArc Drive](sources/DRIVE_MANIFEST.md) has the unpacked OBB. Codex needs authorized Drive access to read it; a URL is not a download or a mount. The APK/OBB native libraries must never be committed to this public repository.

Keep future implementation files under `cf2018/`. No changes to the unrelated root Android WebView app.

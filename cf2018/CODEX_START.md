# CODEX START — CF2018 current packet

Read [AGENTS](AGENTS.md), [NAVIGATION](NAVIGATION.md), [IDEA_PLAN](IDEA_PLAN.md),
[CHECKPOINT](knowledge-system/vault/CHECKPOINT.md), live
[assignments](coordination/assignments.json), [source provenance](sources/SOURCE_PROVENANCE.md)
and [Drive limits](sources/DRIVE_MANIFEST.md). Refresh main and source availability;
GitHub schedules do not establish a checkout, private disk or Android runtime.

Run from cf2018:

```text
python tools/knowledge.py route 'tgcp ack native source provenance'
python tools/knowledge.py doctor
python -m unittest discover -s tests -v
```

## Focused CF18-G2-ACK-01

[Reviewed receiver trace](knowledge-system/vault/research/ACK_RECEIVER.md) combines
hash-specific native RX, ACK/session branch observations and source integrity.
The [body/session continuation](knowledge-system/vault/research/ACK_SESSION.md)
traces timestamp use, optional-body storage and separate account-copy state.
G2 stays BLOCKED: no later authentic client packet after ACK. Continue downstream
account/Bingo/session predicates; the framing lane separately owns
remaining native 99/bounds/lookahead work. Honor exclusive lane write paths.

The recovered v1.0.11.11 Mono mirror is verified by actual hashes and internal
signature checks. Phone equality, matching OBB, historical relay sources and
actual runtime path remain unverified. Original files stay private; verify the
pinned source before address claims. The unrelated 9.99 APK/cfmobileoffline is
never an evidence substitute.

## Corrected framing premise and available tools

The mirror compares decoded base marker 0x4366 after AA/99 TLV decoding.
The historical raw 66 43 inference is retired for this path. Do not derive a
reply from [legacy frame_gate.py](experiments/frame_gate.py) or assume outgoing
43 66 should be reused inbound. Historical v0.1-v0.8 probes/reports are missing.

[Offline strict framing subset](experiments/rx_envelope.py) has opaque extensions
and base_type metadata only; it is not an ACK validator/serializer. The
[private-source verifier](tools/verify_private_source.py) is inactive without
explicit paths and performs no download or game execution. Native controls in
incoming lane packets require private source and optional dependencies; report
skips/unrun exactly. No device A/B/C candidates are ready and no automatic live
phone/network experiment is supplied.

Only a later real client protocol packet after ACK advances G2. Keep all work
under cf2018; root WebView untouched. Stop unchanged blocked activations quietly.

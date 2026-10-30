# CODEX START — CF2018 auth receive gate

Read [AGENTS](AGENTS.md), [NAVIGATION](NAVIGATION.md), [IDEA_PLAN](IDEA_PLAN.md),
[CHECKPOINT](knowledge-system/vault/CHECKPOINT.md), live [assignments](coordination/assignments.json),
[source provenance](sources/SOURCE_PROVENANCE.md) and [Drive limits](sources/DRIVE_MANIFEST.md).
Refresh main and actual source/dependencies; schedules do not establish runtime.

```text
python tools/knowledge.py route 'authentication 0x2002 Bingo native source'
python tools/knowledge.py doctor
python -m unittest discover -s tests -v
```

[CF18-G2-AUTH-RX-02](knowledge-system/vault/research/AUTH_RECEIVER.md) supersedes
stale ACK-first checkpoints. Real phone SYN133 -> AA_DIRECT ACK63 -> authentic
0x2001/117 is confirmed. All three v1.2 auth replies omit TGCPBody preamble;
actual native body mode A5 fails -32, maps -18 before account parsing. Integrate
AA + BE total length around the existing union and recompute outer body length.
Canonical helper and full-native regression matrix are offline only; deployed
v1.2 source/wiring remains unavailable. Corrected controls reach state4 then
Bingo wait, not a valid account/session. G2 auth/session BLOCKED; NOT PLAYABLE.

Continue bounded Bingo/session predicates and deployed relay EOF attribution.
Do not restart handshake guesses, invent credentials/keys or request another
random phone sweep. V1.4 envelope-only comparison is justified in principle but
blocked on reviewed bridge/directional instrumentation. No automatic device run.

Private original source pins and internal signature are verified; historical
reported APK equality is separate from current installed APK/OBB identity.
Originals stay private. Old frame_gate.py raw-prefix behavior is a retired
hypothesis, not native acceptance. Preserve incoming lane ownership and pending
local edits. Default tests explicitly skip private-native checks; report actual
counts. Stop unchanged blocked activations quietly.

[Downstream Bingo review](knowledge-system/vault/research/BINGO_SESSION.md)
corrects3002 to WAIT/queue and shows invalid header/body correlation can still
reach numeric state5. Never use state5 alone as an authentication oracle.
Next native lane task is application/account/session consumers, without guessing
valid relay identity or Bingo. Reviewed path packet is bounded synthetic evidence.

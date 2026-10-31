# CF2018 cold start — current handoff first

Read [CURRENT_HANDOFF](coordination/CURRENT_HANDOFF.md), [AGENTS](AGENTS.md),
[NAVIGATION](NAVIGATION.md), [CHECKPOINT](knowledge-system/vault/CHECKPOINT.md),
[assignments](coordination/assignments.json) and [source provenance](sources/SOURCE_PROVENANCE.md).
The owner uses PCAPdroid CrossFire-only VPN -> SOCKS5 127.0.0.1:1080 in Termux ->
local fake TGCP server127.0.0.1:8080/8085. Termux EXCLUDED. No root/adb/new VPN path.

Latest actual phone test is v3.8: real routed4013 in2/4 trials; no identified
application request and no4013 reply. Exact v38 source is now available privately
and audited; APK/Apollo were recovered and hash verified. Recheck local availability.
Never restart handshake research or call missing-source from old task summaries.

Exact lab-stage native replay selects method0 with explicit emulation premises.
Four-byte prefix is packet sequence, NOT UID. Native legacy serializer agrees
with observer on synthetic input. No native rejection predicate for actual phone
body has been localized. No validated login/account, service response or gameplay.

Prepared [v3.8.1 patch kit](deliverables/CF2018_v381_Patch_Kit.zip) applies locally
to the owner's unchanged v38 ZIP. [Exact Termux steps](coordination/V381_TERMUX_STEPS.txt).
Default offline tests only. Phone opt-in is manual; all schedules remain paused.
Preserve known-working ACK63/auth54/Bingo91 bytes and ordering. Do not guess replies.

```text
python tools/knowledge.py route 'pcapdroid termux socks5 v38 handoff source test'
python tools/knowledge.py doctor
python -m unittest discover -s tests -v
```

Evidence/history: [v38 source/native audit](knowledge-system/vault/research/V38_SOURCE_AUDIT.md),
[report](knowledge-system/vault/research/V38_BLOCKER.md), [auth failure/correction](knowledge-system/vault/research/AUTH_RECEIVER.md),
[Bingo limits](knowledge-system/vault/research/BINGO_SESSION.md), [integrity parked](knowledge-system/vault/research/INTEGRITY_NATIVE.md),
[registry](knowledge-system/vault/EVIDENCE.md), [historical log](knowledge-system/vault/WORKLOG.md).

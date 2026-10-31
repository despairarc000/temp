# Current state

Migrated knowledge baseline: main79dd8892042c7dc871fca279c22c6082194f9079. Migration adds no phone/gameplay progress.

Goal: original CF2018 v1.0.11.11 Mono, functional offline TDM/Bomb bots. NOT PLAYABLE. No accepted service response, validated account/session, lobby or match.

Latest actual phone run: V3.8.1. Four auth requests; two routed4013 frames161/166 bytes, bodies80/85. Both match packet-sequence prefix AND exact QueryAddrSvr route. Offset4 fails method-name lexical policy; operation/encoding unknown. No4013 response sent. EOF is not proof of auth rejection.

Next task: trace upstream callers of CTGcp::Write at0x3a45bc/0x3a4708 and their AString construction/wrapper/transform, then reciprocal receive. Known chain: Write -> send queue -> PopOneSendBuffer0x3a43ac -> onDataOutEvent -> routed send0x3a5476. Native static, not phone runtime producer identification. No repeat of the same boundary test needed.

Preserve working SYN133/ACK63/auth117 -> synthetic auth54/Bingo91 sequence. Earlier missing-body-preamble failure was corrected. Four-byte prefix is packet sequence, not UID. Native result reader requires result AND reason STRING; empty reason allowed. Canonical preflight corrected. Native parser success/state5 does not establish authentication.

Evidence: [latest phone](../../cf2018/knowledge-system/vault/research/PHONE_V381.md), [native application fields](../../cf2018/knowledge-system/vault/research/ADDRESS_APPLICATION.md), [queue/source audit](../../cf2018/knowledge-system/vault/research/REPOSITORY_SOURCE_AUDIT.md).
Previous verification:236 private tests PASS; default137 PASS/99 SKIP. Historical results, not a new v2 implementation test. Schedules paused. DLL integrity track parked; no safe edited build/decoded round trip.

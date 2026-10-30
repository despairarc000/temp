# CF18-05 v1.2 auth-body A/B/C/D: offline controls and phone-test plan

2026-10-30. Evidence: NATIVE_STATIC_SERIALIZER + LOCAL_SYNTHETIC_TEST. No v1.2 real-phone results yet. Baseline [v1.1 phone result](PHONE_V11_RESULT.md).

## Why
v1.1 user phone report observed 4/4 genuine 0x2001 requests. On 2 SILENCE arms, socket remained until 7-second deadline; on 2 synthetic 66-byte 0x2002 replies with *empty* nested account, socket read EOF within ~32ms of session start, with zero third frames. Root cause is unassigned. The receiver separately requires effective type 0x2002 and parses TGCPAuthRspBody/TSF4GAccount. The old reply sent an empty account structure; its semantic validity was never established.

Static native re-review against pinned `libapollo.so` SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`:
- `TGCPAuthRspBody::packTLVWithVarint` `0x3b374e`: field tags 0x15 (nested TSF4GAccount), 0x20 (varuint16 status), 0x35/0x45 (strings).
- `TSF4GAccount::packTLVWithVarint` `0x3acf72`: fields 0x10 varuint16, 0x21 uint8, 0x35 nested IDValue, 0x40 varuint64 UID.
- `TSF4GIDValue::packTLVWithVarint` `0x3aca42`: for zero ID-type, nested union writes tag 0x01 followed by one uint8. The generic parser's zero-field restriction does not prove native rejection of this union.

## Four first-order comparison arms, two trials each
1. `SILENCE`: no 0x2002 response after observed authentic 0x2001; 7-second control.
2. `V11_EMPTY_ACCOUNT`: identical original 66-byte v1.1 response; reproduce old failure.
3. `V12_BODY_EMPTY`: 49-byte 0x2002 reply with no AuthRspBody fields; negative control for nested body processing.
4. `V12_FULL_ZERO_ACCOUNT`: 79-byte 0x2002 reply with structurally complete zeroed TSF4GAccount field tags, nested zero IDValue, and zero numeric/status/strings.

All other header/body wrapping stays as in v1.1. Every value remains synthetic zero/empty; no real user credentials or account are obtained. No server authenticity, valid account identity, accepted auth or lobby is implied. Control outcomes distinguish behavior after body *shape*, not native error codes; local `read_eof` does not establish FIN origin.

The user-facing v1.2 Termux zip resides as a conversation artifact, NOT in this public repository (it contains the historical 133-byte authentic request fixture). Preflight: 15 tests passed (unit, loopback TCP, full SOCKS5 handoff). Archive CRC passed. The report should save under `~/storage/downloads/CF2018_v12_Auth_Body_Result.txt`. Results are **PENDING ON PHONE**, so do not mark G2 completed or change canonical auth state yet.

## Coordinator and worker next action
- Review v1.1 observed data and this planned body-structure comparison. Update canonical checkpoint/EVIDENCE, replacing outdated 'no post-ACK packet' wording with 0x2001 client request confirmed, while G2 auth remains blocked.
- Await v1.2 on-phone TXT. If all synthetics close, next priority is native 0x2002 parser and relay EOF attribution, not random accounts/keys. If an arm triggers new client message, parse metadata only and trace its expected native state. Preserve strict pass/fail distinction.
- No live Tencent connections, proprietary APK/OBB edits, raw auth payloads or public original binary assets.

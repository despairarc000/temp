# R088 — Exact-original GCloud ACK post-mode gates

**2026-11-02 | CONFIRMED_NATIVE_STATIC + LOCAL_TEST_ONLY.** Read-only original `app/lib/armeabi-v7a/libapollo.so`, 5,243,704 bytes, SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`. The owner-original ELF was materialized privately from connected Drive and Thumb-disassembled; no original binary or payload is committed, no ACK or phone experiment performed.

## New verified evidence after R086

R086 enumerated GCloud key modes 0/2/3; **those are not a complete ACK acceptance contract**. Original `gcloud_tgcpapi_recv_and_decrypt_pkg` (`0x3abe34`) separately:

- Reads body length at handle `+0x738` (`0x3abf08`); nonzero goes to `0x3abf4e`, zero has an independent branch.
- Reads per-packet decrypt flag `+0x72c` (`0x3abf4e`); flag zero bypasses `tgcpapi_decrypt` to a copy path (`0x3abf60` → `0x3abfb2`); nonzero calls `tgcpapi_decrypt` (`0x3abf74` → `0x3ab31e`) and checks the result. Decrypt selection is **independent of key-mode selection**.
- Compares type `0x5002` (`0x3abff2`); matching type calls `tgcpapi_on_sstop_session` (`0x3ac02c` → `0x3aafe0`). This is **not** an ACK or session-success event.

Original `gcloud_tgcpapi_recv_ack_msg` (`0x3ac0b8`):

- Calls the gather/decrypt routine (`0x3ac0d2` → `0x3abe34`) and checks its result.
- Requires effective message type `0x1002` from handle `+0x726` (`0x3ac100`–`0x3ac11c`).
- If body length is zero (`0x3ac16e`–`0x3ac174`), skips TLV body decode. An early zero return does not prove an authenticated session.
- For positive body length calls `gcloud_gcp::TGCPBody::unpackTLV` (`0x3ac1b6` → `0x3b8860`), with error branch at `0x3ac1ba`–`0x3ac1c6`. A parsed TLV is **not** proof of login.

## Local regression and limits

Created a bounded local source-only auditor and 7 unittest cases: **39/39 original instruction halfwords, 6/6 conditional branch targets, 4/4 native direct calls verified** against the exact original. Mutation of every pinned halfword refuses. Synthetic classification reports independent type/length/decryption/TLV gates, never a successful network session. Source/test bundle was produced locally as `CF2018_R088_Source_And_Research.zip`; not committed here because that artifact remains local.

This is **static source evidence**, not an owner-phone receiver identification. The last phone result remains **R077**: 3/3 CTDir route-value matches; all second ACKs deliberately withheld; no accepted second ACK, login, lobby, or bots.

**Next offline study:** trace the producers and state updates for `+0x72c` (decrypt flag), `+0x726` (effective type), `+0x738` (body length), and determine which receiver owns the observed R077 second-service SYN; then study the native post-`unpackTLV` authentication/session transition. Do **not** send a reused or guessed first-service ACK.

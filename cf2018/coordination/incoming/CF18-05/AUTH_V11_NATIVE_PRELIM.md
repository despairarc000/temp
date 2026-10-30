# v1.1 — synthetic 0x2002 response research / controlled experiment

**Date:** 2026-10-30. Evidence class NATIVE_STATIC + LOCAL_SYNTHETIC_TEST only. Real phone response **NOT YET TESTED**. Reviewer: CF18-00.

Following [actual phone v1.0 0x2001 follow-up](PHONE_V10_RESULT.md), native `libapollo.so` fingerprint `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8` was inspected using ARM Thumb disassembly:

| Native function and address | Exact observed encoding |
|---|---|
| `TGCPExtHead::packTLVWithVarint` 0x3b673e–0x3b679e | For type `0x2002`, writes varuint tag **0x20021** (field 0x2002/kind1) plus an uint8 |
| `TGCPBody::packTLVWithVarint` 0x3b7fda–0x3b7ffc | Writes varuint tag **0x20025** (field 0x2002/kind5) and length-delimited nested response |
| `TGCPAuthRspBody::packTLVWithVarint` 0x3b374e–0x3b3844 | Writes field1 kind5 nested TSF4GAccount, field2 kind0 varuint16, fields3+4 kind5 length-delimited strings |
| `TSF4GAccount::packTLVWithVarint` 0x3acf72–0x3acff2 | Writes field1 kind0 varuint16, field2 kind1 uint8, field3 kind5 TSF4GIDValue, field4 kind0 uint64; no valid value policy established |

v1.0 report bug: `ext_type=[]` is due to Python's `extension_types = [f for f in ext if f.kind == 5]` filtering out **real `0x2001` kind1**. New v1.1 reader reports kind1 as expected; independently synthetic kind1 regression test included.

An **offline** synthetic `0x2002` response was constructed using the above syntax, with deliberately empty account and zero numeric/string fields. It is a *negative/structural-only test*; it does not demonstrate a valid account, server session, login, game unlock or cryptographic negotiation. The nested account content is deliberately not equivalent to a native serialized legitimate account. A structural `0x2002` packet alone is not a legal or operational successful server response.

v1.1 opt-in on-phone diagnostic consists of 4 connections alternating SILENCE after verified 0x2001 request versus AUTH_ZERO_STUB after the same first-stage AA_DIRECT reply. Logs report frame types/sizes/timing/digests only, not raw 73-byte auth contents. It is loopback-only and unchanged APK/OBB, plus historical per-IP/port SOCKS5 redirector; does not contact live Tencent auth. It is downloadable as a ChatGPT conversation ZIP, **not** committed here because bundled historical golden client fixture/ACK bytes are not approved for public repo.

Local verification: **7 tests PASS**, including 2-arm synthetic in-process loopback and 2-arm SOCKS5 end-to-end integration. ZIP integrity verified; no real game test, native full-account parser-run, or authentication success verified. Do not promote G2 above `CLIENT_SENT_0x2001` until a genuine later client frame is recorded and interpreted.

**Next actions:** CF18-02 should analyze auth-response body semantics and actual username/UID/session correlation rather than simply treating a decoded empty body as valid. CF18-03 should attribute end-of-stream source if v1.1 shows early EOF. CF18-00 should incorporate the user-supplied v1.0 metadata and v1.1 phone result only when actual report exists.

# R032 — TGCP Base field 6 is the per-frame inbound decryption selector

**Date:** 2026-11-01. Evidence type **CONFIRMED_NATIVE_STATIC** on exact owner-provided Apollo 5,243,704-byte ELF, SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`. No original native execution, phone reply, session acceptance, credentials or payload export.

## Corrected origin of the 0x72c selector

The earlier R030 wording called `handle+0x72c` a *connection-state flag*. That is misleading: **it resides within the decoded per-frame TGCP header**, starting at `handle+0x720`, rather than being an independently proven session-wide setting.

- The incoming packet gathering function passes `handle+0x720` to the original `TGCPHead` decoder.
- `TGCPHead::unpackTLVWithVarint` calls `TGCPBase::unpackTLVWithVarint` for base field1.
- That base decoder shifts the wire field key right four and dispatches through a nine-entry Thumb TBB table. Hash-verified table **index 5** (field6) is offset `0x36`, targeting original instruction `0x3af57c`; at `0x3af580` the decoder passes `TGCPBase+0xc` to `readUInt8` (`0x3af58e`).
- `gcloud_tgcpapi_recv_and_decrypt_pkg` then reads the same `TGCPHead+0xc` byte at `handle+0x72c` (`0x3abf4e`), compares it with zero (`0x3abf5c`) and branches to the byte-preserving clear-copy path (`0x3abf60`). Nonzero enters the separate decryption branch.
- For comparison, `tgcpapi_build_frame_base` explicitly stores zero to the **outgoing** base header's offset `+0xc` (`0x3aabec`). This is not proof that a server response has already used that value on the phone.

Therefore **Base field6=0** is an original-code-grounded condition to select the clear-copy path for one incoming response candidate. It is not enough to prove all header fields, route values, or game session state are valid. The real client's last inbound base field6 value was **not logged**, and no actual 0x4013 reply has been sent.

[Private-original static verifier](../../../experiments/native_base_security_field_audit.py) checks ten exact instructions **plus the TBB table entry: 11/11 PASS locally**; six original-gated/source-free [tests](../../../tests/test_native_base_security_field_audit.py) PASS.

## New conservative offline preflight constraint

The earlier source-only [AA-framed incoming reply preflight](../../../experiments/inbound_4013_reply_preflight.py) now parses `TGCPBase` with the existing bounded decoder and **requires explicit Base field6=0**, rather than silently assuming a session decrypt mode. It also requires a recognized 0x4013 DataHead variant with compression0 and structurally complete unprefixed type2 RPC reply correlated to the pending RPC64 sequence. The corresponding [synthetic tests](../../../tests/test_inbound_4013_reply_preflight.py) additionally reject field6=1 and missing field6; no network operation is performed.

The offline framing subset and stricter field-presence policies are not a complete replacement for the original native TGCP decoder. A model-positive result is **structural only**. No client response, login, address resolution, lobby, match or bot gameplay is demonstrated.

## Next single high-value experiment

Use the now-evidence-grounded `Base.field6=0` and `DataHead.compression=0` selectors in a bounded offline frame candidate, validate its full parsed boundaries and pending RPC64 response structure, then run one explicitly enabled phone response-acceptance test **only after** the remaining outer-frame fields, route and native receiver acceptance predicates are verified. Do not rerun the already successful R027 request identification test or mirror the outgoing client's application prefix.

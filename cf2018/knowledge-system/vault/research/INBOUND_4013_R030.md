# R030 — native incoming 0x4013, compression switch and application-buffer boundary

**Date:** 2026-11-01. **Evidence:** Original owner-supplied Apollo ELF, 5,243,704 bytes, SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`. Read-only original Thumb disassembly: **26/26 exact instruction checks PASS**. Seven local tests passed (six source-free checks and one private-original audit). No original-native dynamic execution, return packet sent, or phone response accepted.

## Narrower ingress requirements — confirmed static

- `tgcpapi_gather_and_split_entire_pkg` checks a 32-byte fixed header threshold (`0x3ab6a0`), compares packet magic against `0x4366` (`0x3ab6f6–0x3ab6fe`), then invokes its native TGCP header TLV parser (`0x3ab722`). These are **necessary checks**, not a complete server-frame specification.
- `gcloud_tgcpapi_recv_and_decrypt_pkg` invokes the gather/split handler first (`0x3abe4c`). Whether native decryption is used depends on the connection state flag at `+0x72c` (`0x3abf4e`); the enabled branch calls `tgcpapi_decrypt` (`0x3abf74`), while the disabled path copies the received bytes (`0x3abfe6`). The actual phone's inbound decryption flag and keys are unknown.
- `gcloud_tgcpapi_peek` requires connection state5 (`0x3a8d1a`) and calls that receiver (`0x3a8d6e`), then **explicitly selects incoming type `0x4013`** (`0x3a8de4–0x3a8de8`). For this type it reads the DataHead compression flag at `+0x740`. If the flag is zero, the branch at `0x3a8df2` jumps over LZ4 to output the payload pointer and length at `0x3a8edc–0x3a8ee2`. Nonzero has additional guards and potentially invokes `LZ4_decompress_safe` (`0x3a8e7c`). The observed *client-origin* 0x4013 frames from R027 had compression=no, but **server-origin compression state has not been measured**.
- `CTGcp::onDataInEvent` queues the pointer/length given by peek, `CTGcp::Read` dequeues then assigns them to `AString`, and `AddressService::ProcessResponse` passes its incoming bytes to `MsgBuffer::setMessage` before virtual `readMessageBegin` and RPC64 session lookup. These direct source pins do not establish whether native receive processing has stripped any transport prefix before the application buffer was produced.

## Negative control: do not mirror the request's four-byte prefix blindly

R027 demonstrated the original client **outgoing** 0x4013 application body contains a four-byte prefix matching its packet sequence. That does **not** establish that a **server reply** should deliver the same prefix to the AddressService RPC reader. The native AddressService parser expects a Thrift RPC message at the start of its application buffer. An independently synthetic complete type2 reply parses successfully starting at offset0; prepending four TGCP-sequence bytes makes both the original V3.8 `apollo_wire._parse_rpc_at(...,0)` and the strict offline `address_response_gate.parse_response` reject it. This is a parser-boundary *negative control*, not proof of a full server-origin TGCP frame. It cannot distinguish where a real native receive pipeline may insert/remove framing bytes before the application boundary.

## Source-only verification

- [26-pin read-only native audit](../../../experiments/native_inbound_4013_audit.py), [7 focused tests](../../../tests/test_native_inbound_4013_audit.py) (private-native test skipped in public CI)
- [RPC prefix negative controls](../../../tests/test_4013_response_prefix_boundary.py): standalone source-free checks plus private V3.8 parser cross-check when available.
- Test failure controls detect any missing or mutated native pin. Original game files and disassembly stay private.

## Next step

1. Derive and certify the server-to-client **TGCP extension `0x4013` / DataHead route/base/sequence** packet envelope from the receive-side unpacker and available native server-role traces, not from a copied client frame.
2. Verify whether an uncompressed response can reach the application buffer with **unprefixed** type2 `QueryAddrSvr:QueryAddrInfo` (or the original server reply's exact method name), with the correct RPC64 pending session and mandatory result and reason fields.
3. Only after those offline gates pass, run a single bounded real-phone **reply acceptance** test. No test packet was sent in R030. Existing login/lobby/gameplay still unverified.

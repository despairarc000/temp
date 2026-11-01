# R031 — 45-pin native inbound payload preservation and bounded AA/4013 reply preflight

**Date:** 2026-11-01. **Source scope:** privately retained original `CF2018_libapollo.so`, SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`; exact original 5,243,704-byte ARM ELF. No original game binary, payload or identifiers are committed. Native instruction evidence is static, not original execution or phone acceptance.

## Confirmed original-native static facts

A new [bounded native audit](../../../experiments/native_rx_payload_boundary_audit.py) verified **45/45 exact Thumb instruction pins** locally on the original Apollo. Seven focused regression tests passed, including the private-original audit and per-pin mutation/deletion checks. It expands R030 in two ways.

**Extension-to-DataHead path:** `TGCPHead::unpackTLVWithVarint` passes header extension field 2 to `TGCPExtHead::unpackTLVWithVarint`. The latter explicitly compares extension type `0x4013` and dispatches to `TGCPDataHead::unpackTLVWithVarint`. That handler reads field numbers 1–4, including uint8-valued fields and a length-delimited nested `TGCPRouteInfo`. This proves the original **incoming** decoder supports the same inner header *family* as the real outgoing client `0x4013` in R027. It does **not** prove every field must be present or select a specific server-origin route, outer header, cryptographic state or session ID.

**Clear/uncompressed payload boundary:** `gcloud_tgcpapi_recv_and_decrypt_pkg` reads application payload length from handle offset `+0x738`; it computes a source pointer using input base `+0x708`, current stream cursor `+0x710` and parsed header length `+0x734`. When inbound decryption flag `+0x72c` is zero, it passes **that exact pointer and declared length** to the original `memcpy` call. The unpacked buffer length is forwarded unchanged. `gcloud_tgcpapi_peek` branches directly to the output buffer when `0x4013` compression flag `+0x740` is zero. The queue/connector passes the application bytes to `AddressService::ProcessResponse`, where `MsgBuffer::setMessage` constructs a `TMemoryBuffer` from the received pointer/count and the binary RPC reader starts at the beginning.

**Implication — conditional, not live proof:** the examined original clear/uncompressed chain does **not** strip a first four-byte TGCP packet-sequence word from its application payload. A server response on **this** path must already contain a valid Thrift RPC at application offset0; blindly copying the client-origin sequence prefix into server-origin application data would give the RPC reader the wrong beginning. If native decryption or a different path is used in the real phone's session, this conclusion does not establish its input layout.

## New entirely offline compound test

The source-free [inbound response preflight](../../../experiments/inbound_4013_reply_preflight.py) composes the existing conservative [AA-prefixed stream frame subset](../../../experiments/rx_envelope.py), a strict known-variant `0x4013` extension/DataHead parser with compression0, and the existing [RPC64 response preflight](../../../experiments/address_response_gate.py). It processes **only caller-supplied in-memory bytes** and returns fixed labels. It does not generate or send TGCP packets, inspect account data, retain RPC sequences or claim a real accepted service reply.

[Synthetic tests](../../../tests/test_inbound_4013_reply_preflight.py) include a positive **offline structural candidate**, wrong pending RPC64 sequence (distinct from TGCP32), accidentally prepended four-byte word, unsupported compression, unknown extension, missing route field, malformed/truncated frame and invalid pending metadata. These deliberately apply stricter conservative policies than what the full native decoder may accept; passing them is **not proof** of native session/connection success. No phone or original client was exercised by these tests.

## Further route-parser distinction (source inspection)

The original nested `TGCPRouteInfo::unpackTLVWithVarint` at `0x3b2422` dispatches among different route variants: field1 to `SpecifyZoneRouteInfo` (`0x3b246e`), field2 to `SpecifyServerRouteInfo` (`0x3b2488`), field3 to a standalone UInt8 (`0x3b2492`), and field4 to `SpecifyNameRouteInfo` (`0x3b24ac`). The latter's own name decoder at `0x3b1ba2` handles a field1 byte string capped at 127 bytes (`0x3b1bfe`), then reads the supplied length. These are original **static** branches, not proof of the route variant sent by a server.

Thus the offline `inbound_4013_reply_preflight.py` restriction requiring a name-route nested field4 is a **deliberately narrow fixture**, not a native universal requirement. Do not conclude that all alternative server-origin route types are invalid from that model. No live return route is identified.

## Remaining uncertainties and next checkpoint

- The live client session's **inbound** decrypt flag/mode has not been observed; historical synthetic ACK behavior is not enough to assert it.
- Server-to-client base/extension values, route semantics and native replay/session checks are not certified by an original server capture.
- The native method-name matching policy for a server reply and real pending QuerySession are still not confirmed dynamically.
- The user has **not** received a `0x4013` reply yet. Real authentication, usable downstream service, lobby and gameplay remain unavailable.

**Next discriminating step:** source-pin how the inbound decrypt mode is set following the actual synthetic ACK/Bingo; then, if a clear incoming `0x4013` frame is supported, prepare one capped opt-in phone reply experiment with on-device category-only results. Do not recycle the old R027 request-identity test or mirror request bytes directly.

# R029 — original TGCP-to-AddressService RX chain (source-pinned)

**Date:** 2026-11-01. **Evidence status:** confirmed native STATIC, not packet replay, live response or authentication. Original private Apollo 5,243,704 bytes / SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`.

## New direct proof: end-to-end receive delivery

A bounded read-only disassembly audit checks **16/16 original Thumb instruction pins** covering this conditional connected path:

1. `gcloud_tgcpapi_peek` at `0x3a8d6e` calls `gcloud_tgcpapi_recv_and_decrypt_pkg` (`0x3abe34`). That native function name describes its role; the phone's active encryption mode is **not established by this name**.
2. `CTGcp::onDataInEvent` at `0x3a4f4c` calls `gcloud_tgcpapi_peek` to obtain a pointer and byte count. On success it invokes `CBufQueue::Enqueue` at `0x3a4ffe`.
3. `CTGcp::Read` calls `CBufQueue::Dequeue` at `0x3a4018`, then `AString::assign` at `0x3a403c` to transfer bytes.
4. `CGCloudConnector::Read` at `0x3c5bf0` delegates to `CTGcp::Read`. Separately, `CGCloudConnector::OnGcpDataRecved` at `0x3c5e86` posts a main-thread notification, and `notifyDataRecvedOnMainThread` at `0x3c651e` invokes an observer callback.
5. `AddressService::OnDataRecvedProc` at `0x39d4d4` reads via connector virtual call, obtains `AString` data/size at `0x39d546/0x39d54e`, and hands the bytes to `ProcessResponse` at `0x39d558`.
6. `AddressService::ProcessResponse` then reads an RPC header (`0x39b9d4`), looks up its pending **64-bit RPC QuerySession sequence** (`0x39b9f2`), checks reply kind 2 (`0x39baa0`), and calls typed `Recv_QueryAddrInfo` (`0x39bb08`).

**What this narrows:** a server reply must reach `gcloud_tgcpapi_peek` successfully and be enqueued/dequeued before application-Thrift decoding is even reached. A byte array that passes the synthetic Thrift decoder and RPC64 equality check is **insufficient** to demonstrate native client acceptance.

**Not established:** the server-to-client TGCP extension variant, necessary server-side route envelope, exact server response message-name convention, live TLS/crypto state, native pending map contents, effective game login, lobby or bots. Do not assume the client-origin 0x4013 layout can simply be mirrored for a server response. No new phone test, raw capture or speculative server response was sent.

**Verification:** [read-only auditor](../../../experiments/native_address_ingress_audit.py), [regression tests](../../../tests/test_native_address_ingress_audit.py). Full local private-original test suite **6/6 PASS**, 16/16 original native pins. Source-free CI skips private-original verification. Every changed or missing instruction is rejected by negative controls. Output contains labels only; game library is not published.

**Next:** verify the native inbound TGCP routed-data grammar and expected response-path framing from the original receive-side packet decoder, then build an OFFLINE frame classifier/preflight. Only if that passes attempt a bounded opt-in phone response experiment; keep the true 64-bit RPC sequence in memory rather than outputting it.

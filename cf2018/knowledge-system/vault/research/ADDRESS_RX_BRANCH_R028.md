# R028 — original native address-response branches and offline reply candidate

Date: 2026-11-01. STATUS: **CONFIRMED_NATIVE_STATIC** for hash-pinned Apollo instructions; **OFFLINE_SYNTHETIC_ONLY** for reply construction. No actual 0x4013 reply or phone advance.

## Source verification

User-provided original `libapollo.so` (5,243,704 bytes; SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`) was inspected read-only with LLVM Thumb disassembly. [Auditor](../../../experiments/native_address_rx_branch_audit.py) verifies **15/15 fixed instruction pins** across bounded original regions, with synthetic positive/negative controls and a private-source gated original test ([tests](../../../tests/test_native_address_rx_branch_audit.py)). Local six-test focused suite PASS with original. Public CI skips private-original test.

## Original response control flow

- Original `AddressService::ProcessResponse` invokes virtual `readMessageBegin` at `0x39b9d4` and finds a `QuerySession` keyed by **64-bit RPC sequence** at `0x39b9f2`.
- With a found session, it tests RPC response type 2 at `0x39baa0`, branches to typed processing and invokes `Recv_QueryAddrInfo` at `0x39bb08`.
- `Recv_QueryAddrInfo` invokes the generated `QueryAddrSvr_QueryAddrInfo_presult::read` at `0x399ac8`; prior original-native decoder controls proved both result and reason STRING are required (empty reason allowed).
- After transforming/filtering address information, a begin/end comparison at `0x39bd5e` separates two paths. The **empty processed-address** branch invokes a session callback at `0x39bd7e`, erases the pending session at `0x39bd90`, then caches addresses at `0x39bd96`. The **nonempty processed-address** branch prepares and queues a `ResponseInfo` item using `0x39bda2` and `0x39bdea`. This is a static control-flow distinction and does not establish which branch a real response would take, or what callback output implies for game state.
- The received method-name string is read, but this audit **does not claim** a verified matching rule for the server reply's method name, nor the correct return route/GCloud/TGCP envelope. Neither is established by the offline allowlist.

## New offline-only reply candidate

[Qualified candidate writer](../../../experiments/qualified_address_reply_dryrun.py) builds **only unframed Thrift RPC message bytes in memory**, using the full 64-bit RPC sequence from a recognized qualified request, type 2, required result and reason, one well-formed address list entry, and strictly numeric **IPv4 loopback** endpoint. It checks its own output using the existing strict offline `address_response_gate` and refuses external IPs, malformed requests and wrong sequences. No sockets, network, file output, authentication, sender or APK modifications.

[Tests](../../../tests/test_qualified_address_reply_dryrun.py) cover 64-bit request correlation (distinct from TGCP 32-bit packet sequence), field presence, bound input, external endpoint refusal and local-only addresses.

**This is not proof that the original client will accept the generated message**. The native receiver's possible session, method and routing gates, plus the correct TGCP/GCloud framing, require separate proof.

## Next decision

Do **not** repeat the already successful request-identity phone test. The next offline task is to verify the TGCP response envelope and native route/method handling for the address service. If verified, attempt one bounded, explicitly opt-in local response test with correlation kept in memory and a non-production loopback target; observe whether client acknowledges, re-queries or advances. This work does not yet imply offline lobby, match or bots.

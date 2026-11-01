# QueryAddrInfo upstream request-chain trace — 2026-11-01

Status: **CONFIRMED_NATIVE_STATIC for direct instructions**, **INFERRED for continuous end-to-end dispatch**, **UNKNOWN for the real phone's operation/encoding**. This is a source-pinned static investigation, not a client/network test or an accepted server response.

## Original source and reproducibility

Read-only original `libapollo.so`, **5,243,704 bytes**, SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`. ELF32 little-endian ARM EABI5. Actual native instruction inspection used `readelf -Ws` (demangled with `c++filt`) and LLVM 17 `llvm-objdump --triple=thumbv7a-linux-gnueabihf --disassemble` with bounded address ranges; hash checked before inspection. **11/11 explicit callsite/field pins passed** against the private original. The original library and raw disassembly are not committed.

Sample reproduction on an authorized local source (use matching source fingerprint):

```sh
sha256sum /private/path/libapollo.so
readelf -Ws /private/path/libapollo.so | c++filt | grep -E 'AddressService::ProcessRequest|Send_QueryAddrInfo|MsgBuffer::(bind|writeEnd)|CGCloudConnector::Write|CTGcp::Write'
llvm-objdump --triple=thumbv7a-linux-gnueabihf --start-address=0x3c5fd0 --stop-address=0x3c6068 --disassemble /private/path/libapollo.so
```

## Actual source-pinned instruction checkpoints

| Stage | Instruction location | Checked native observation |
|---|---|---|
| Address-service request | `0x39ae3c` | `AddressService::ProcessRequest` directly calls `Send_QueryAddrInfo` at `0x3998d4`, after `ParseDomainName` in the examined branch |
| Generated arguments | `0x39991c` | `Send_QueryAddrInfo` directly invokes generated `QueryAddrInfo_pargs::write` at `0x39ed4c` |
| Connector binding | `0x3c191e` | `MsgBuffer::bind` stores the supplied `IConnector*` in a callback binding |
| Callback installation | `0x3c193e` | `MsgBuffer::bind` installs a function target at object offset `+0x50` |
| Outgoing buffer dispatch | `0x3c1f46` | `MsgBuffer::writeEnd` invokes the callback loaded from `+0x50`, using current buffer pointer/length and route info; the callback result is handled, not a silent unconditional send |
| Callback dispatch implementation | `0x3c1508` | Bound `std::tr1` invocation calls the `IConnector::Write` member target indirectly; the concrete runtime object is not proven |
| Concrete connector buffer copy | `0x3c601e` | `CGCloudConnector::Write` passes supplied pointer/length to `AString::assign` at `0x397316` |
| Concrete connector routed submission | `0x3c6046` | `CGCloudConnector::Write` directly calls `GCloud::CTGcp::Write(AString,route)` at `0x3a4708` |
| TGCP enqueue | `0x3a47dc` | Routed `CTGcp::Write` calls send-data vector `push_back` at `0x3a4594` |
| TGCP dequeue | `0x3a53e0` | `CTGcp::onDataOutEvent` calls `PopOneSendBuffer` at `0x3a43ac` |
| Actual routed TX call | `0x3a5476` | `CTGcp::onDataOutEvent` directly invokes `gcloud_tgcpapi_send_with_route` at `0x3a91ec` |

**Interpretation:** A generated AddressService writer, an output-memory buffer, a bound connector callback and the TGCP send queue are all present with source-level links. At the connector boundary, the examined `CGCloudConnector::Write` directly assigns the supplied bytes to `AString` before invoking routed `CTGcp::Write`. This does **not** prove complete byte preservation through every upstream layer, the actual `IConnector` implementation used on-device, or the phone request's identity. An unexamined runtime callback, protocol framing, or another producer may still account for the 80/85-byte phone bodies.

## Consequences for the existing blocker

[V3.8.1 phone evidence](PHONE_V381.md) still records two later `0x4013` frames with exact `QueryAddrSvr` route and four-byte packet-sequence prefix. At offset four, the existing observer reports `METHOD_BYTES_POLICY`; it does not identify `QueryAddrInfo` or a valid account. No `0x4013` response was sent. Today's work does not change these facts.

The result **narrows the remaining producer question to a testable boundary**: distinguish (A) original generated `QueryAddrInfo` bytes in `MsgBuffer::writeEnd`; (B) bytes handed to `CGCloudConnector::Write`; (C) bytes handed to routed `CTGcp::Write`; and compare the modeled result to the existing V3.8 observer's strict and legacy controls. Do this first with original-code, independently synthetic and bounded data, intercepted before network send; compare only structure/length, never credentials or live packet contents. A single correct native-generated sample that the observer fails to recognize would falsify its modeled grammar. If all positively identify, an alternate runtime producer/transform remains likely; don't declare a concrete service operation until observed.

## Controls and limitations

- **Positive:** 11 pinned instruction/target/field checks executed against original source and passed.
- **Negative:** a wrong-size or wrong-hash library is not equivalent to this evidence; a synthetic source-independent match cannot establish original execution.
- **Not done:** whole-application Unity/Android runtime execution; a full virtual dispatch to the on-phone concrete connector; full `MsgBuffer` synthetic callback execution; controlled real-phone plaintext observation; recipient response acceptance.
- No new XAPK/OBB, managed DLL modification, fake reply, or scheduled phone experiment. No raw proprietary disassembly, binaries, captures, keys, or account data published.

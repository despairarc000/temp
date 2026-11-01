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

## CF18 producer boundary audit — 2026-11-01 continuation (R010)

Added [read-only audit](../../../experiments/producer_boundary_audit.py) and [tests](../../../tests/test_producer_boundary_audit.py) verifying 24 explicit original-native callsite/branch pins against the exact hash-pinned Apollo ELF (7 bounded Thumb ranges). The native source was **not emulated**, and no synthetic packet was sent. On the authorized private source: **24/24 PASS**, six tests PASS including five source-free tests. Without private source: five PASS, one explicit SKIP. Deliberately refuses wrong-sized/wrong-hash/incorrect-ISA inputs and never prints disassembly, payloads, routes or private paths.

New confirmed static details beyond R009: generated `Send_QueryAddrInfo` calls multiple virtual protocol operations before end-of-message; `MsgBuffer::writeEnd` uses a virtual check and a bound callback (and has a distinct alternate path); `CGCloudConnector::Write` checks size/connection and calls `AString::assign` before routed TGCP submission. **These native instructions do not establish that the real phone's 80/85-byte 0x4013 bodies came from that code path.** This rules out simplistic arguments-only byte equivalence as proven and reduces the next task to testing a whole bounded protocol-message-write through the callback, then reciprocal RX. If native emulation dependencies or initialized objects are unavailable, the blocker is explicit rather than silently substituting a synthetic response.

Reproduction with an independently authorized local original: `CF18_APOLLO_LIBRARY=/private/path/libapollo.so python -m unittest discover -s tests -p 'test_producer_boundary_audit.py' -v`; `python experiments/producer_boundary_audit.py --lib /private/path/libapollo.so`. Requires `llvm-objdump` for original-source control. This is a **static source verifier**, not a functioning in-memory execution harness or a phone experiment.

## R011 — Two independently bound connector owners (2026-11-01)

A **read-only whole-text instruction scan** of the exact pinned Apollo source located two direct `bl MsgBuffer::bind` callers, with enclosing named native functions verified through the original ELF symbols:

- `AddressService::OnConnectProc`: call at `0x39cb68`, passes connector pointer loaded from object field at `0x39cb66`.
- `RpcConnector::OnConnectProc`: call at `0x3c2934`, passes connector pointer loaded from its corresponding field at `0x3c2932`.

These are two **direct** bindings seen in the original source, not proof all indirect callers are enumerated or that either was used for the phone's routed 0x4013 request. They make a single global MsgBuffer/AddressService producer assumption unsafe. The source-pinned read-only verifier now covers **26/26** static pins (nine bounded ranges); six local tests PASS with exact original library, five PASS/one explicit SKIP without it. The original code was **not natively emulated** and no client/network test was performed.

**Next discriminating investigation:** trace which connector instance and buffer owns the phone's `QueryAddrSvr` route and where the corresponding response receiver dispatch is registered. Do not generate a reply based only on these static bind sites. The earlier virtual-callback/serialization comparison remains unexecuted.

## R012 — Reciprocal native receive ownership traced (2026-11-01)

Source-pinned original Thumb instruction inspection established two separately named **receiving** chains:

| Owner | Original-source direct callsites | Limit |
|---|---|---|
| AddressService | `OnDataRecvedProc` reads via connector virtual function at `0x39d4d4`, calls `AddressService::ProcessResponse(unsigned char const*,int)` at `0x39d558`; the no-argument response processing path finds a `QuerySession` at `0x39c1b4` | Static call graph; input identity and on-phone session membership unknown |
| RpcConnector | `OnDataRecvedProc` reads via connector virtual function at `0x3c4f14`, invokes `RpcConnector::ProcessMessage` at `0x3c4f2e`; its message parser invokes `MsgBuffer::setMessage` at `0x3c3ab8` and a typed response dispatcher at `0x3c3ba0` | Static calls; not proof the actual response has been sent or accepted |

**Why it matters:** AddressService receipt/QuerySession matching is structurally distinct from the general RpcConnector message dispatcher. A valid-looking RPC response might still be ignored without matching the correct owner, pending sequence/session and route. No server response can be justified from caller names or a synthetic decoder result alone.

The verifier now includes **33/33** source-pinned original-native instruction checks (13 bounded regions) and six Python test cases (six PASS with exact private Apollo; five PASS and one explicit SKIP without). The fuller send/receive chain remains static; no native whole-message execution, Android acceptance, network reply, or gameplay was observed. The previous R010/R011 counts remain as historical checkpoints.

**Next discriminating action:** establish whether the real on-phone 0x4013 frame was emitted by AddressService or RpcConnector, then verify response callback registration and pending sequence/session matching in the source. Only then build a bounded original decoder-positive test for a potential reply, keeping it offline until accepted predicates are known.

## R014 — conditional buffer-to-memcpy boundary, original-native static verification (2026-11-01)

**CONFIRMED_NATIVE_STATIC** (original Apollo SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, ELF32 LE ARM): `MsgBuffer::writeEnd` loads buffer start/end (`0x3c1ee0/0x3c1ee4`), computes byte count `end-start` (`0x3c1eec`), and passes original pointer/count to callback (`0x3c1f42–0x3c1f46`). The examined `CGCloudConnector::Write` branch forwards pointer and count (`0x3c601a–0x3c601e`) into `AString::assign` (`0x397318`), which delegates to `AData::Assign` (`0x396088`, `0x39609c`) and `AData::Append` (`0x395ff4–0x395ffa`), whose PLT target `0x193ed8` was independently verified as **memcpy** using its ELF PLT relocation and dynamic symbol entry. No additional application envelope is inserted during **this conditional copy path**.

**Limits:** the real phone's dynamic connector, plaintext/encryption status and request identity remain unknown. This static observation does NOT prove byte-for-byte phone wire equality or service acceptance. New discriminating test: execute a bounded native whole-message writer and intercept the callback in memory, before socket submission, then compare its synthetic structure with existing observer positive controls.

**Validation:** added 10 instruction checks in 3 disassembly windows; read-only pinned native audit **43/43 PASS**; 6/6 Python tests with privately available original library PASS. Repaired canonical test assertions incorrectly fixed to 24 after prior 33-pin implementation. No original-game modification, network/phone test, fake response, or native full-message execution.

## R015 — Initial non-strict binary protocol, original native source (2026-11-01)

**CONFIRMED_NATIVE_STATIC**, not proof of runtime phone mode: on original, hash-checked Apollo, `AddressService::InitProtocol` sends factory type `0x20` (`0x39a078`) to `ProtocolFactory::getProtocol` (`0x39a07e`) and stores the resulting protocol in its `+0x28` field (`0x39a086`). The factory selects its binary branch (`0x399daa`), sets strict-write byte `+0x21` to zero (`0x399e4e–0x399e54`). The binary protocol message writer reads that byte (`0x39c3c2`) and branches to the non-strict/legacy header when zero (`0x39c3ce`). Its original vtable method slot resolves to the binary message writer. This is evidence against guessing strict/versioned format merely because its length model can be made to fit the V3.8 report.

**Verification:** original `libapollo.so` SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, length 5243704, ELF32LE ARM. All **8 new native instruction pins PASS** with bounded LLVM disassembly. Committed verifier now defines 51 total pins and updates source-free test expectations; GitHub Actions default knowledge validation PASS at `c2913c8`. CI skips the private-source-dependent test; no 51/51 private-source rerun is claimed.

**Remaining unknown:** whether AddressService is actually the phone's producer or whether strict flag changes after initialization, and whether another transport transformation occurs. Next bounded original-code investigation: track writes to the live protocol flag or execute a synthetic whole message and capture before `MsgBuffer::writeEnd`. No fake reply, network replay or game modification.

## R017 — Source-free observer negative controls (2026-11-01)

The exact bounded diagnostic's two `METHOD_BYTES_POLICY` labels at offsets 0 and 4 on the V3.8.1 phone report are **dependent**, not two independent parser failures. Given the validated 4-byte packet-sequence prefix, the offset-4 label requires its apparent BE32 method length to fall within 1..64. This makes byte 4 zero, so offset 0 necessarily treats that zero as the first character of a purported method name and fails lexical policy (provided the reported sequence itself is 1..64, as implied by the offset-0 label).

Source-free regression tests (`../../../tests/test_routed_label_implications.py`) ran **5 PASS** locally, including 18 synthetic 80/85-byte combinations of name-length/sequence settings. Independent test fixtures of the already source-verified native formats classify unmodified complete legacy `QueryAddrInfo` as `LEGACY_HEADER_PLAUSIBLE` at offset 4, and strict/versioned as `VERSIONED_PREFIX_CANDIDATE`; neither yields the actual reported `METHOD_BYTES_POLICY` label. This is conditional on the observer's real boundary/representation; it does not independently verify the phone bytes or imply encryption. The header-only predicate is also not complete RPC or session validation (corrupted trailing fields can retain the same positive label).

**Next discriminating test:** execute the exact hash-pinned original whole-message writer with bounded synthetic fields, intercept `MsgBuffer::writeEnd`/connector before socket emission, compare only grammar/length/fixed classifications, and establish which concrete runtime owner supplies `QueryAddrSvr`. No private native library, phone capture, authenticated account, real response, or game acceptance was exercised by R017. GitHub CI/full suite has not been verified for the newly added test.

# R057 — Original native address-lookup caller provenance (fake-server lane)

Date: 2026-11-02. **Evidence classes: EXACT_ORIGINAL_APOLLO_STATIC**, verified owner Drive binary, symbol/Thumb callsite walk; plus **PUBLIC CI SYNTHETIC/NEGATIVE** checks. No Android run, no second-service ACK, login, lobby, game patch or bot match.

## Why this is the right question

R037/R039 PHONE_A_B: correct-correlated candidate `0x4013` address reply was associated with a subsequent **131-byte `0x1001` SYN with a different 10-byte name route**; deliberately wrong RPC64 retained the usual 133-byte `QueryAddrSvr` SYNs. R041 proves original `AddressService::GetServiceAddress(serviceName, callback)` accepts caller-supplied service name and correlates pending RPC64; R042 ACK-head analysis does NOT prove the prior 63-byte ACK is valid for a later connection. Thus R056's classifier is a useful guard, not the blocking capability. Actual caller/route origin and session contract are the next evidence target.

## Fresh private original verification, performed in this turn

Connected owner Drive APK-unpacked original `app/lib/armeabi-v7a/libapollo.so`: [original private file](https://drive.google.com/file/d/14Rd_IZ501GlbIE2sZIeXevK-MgsnvHIo/view), **5,243,704 bytes**. Private in-memory base64 decode and independent SHA-256 calculation returned **`4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8` MATCH**, not merely a reported historical hash. ELF32LE ARM E_MACHINE 40 and executable section bounds checked. No original bytes committed, sent to a server, or modified.

A full aligned executable-section scan of direct Thumb-2 `BL` targets (approximately **88,059 candidate BL instruction encodings**; syntactic candidates, not all necessarily reachable) found these **specific direct call sites** on the original:

| Native caller (actual original symbol owner) | BL at | Actual callee |
|---|---|---|
| `GCloud::CDefaultNameService::Query(char const*)` | `0x3a6890` | `pebble::rpc::AddressService::GetServiceAddress` `0x39d18c` |
| `pebble::rpc::RpcConnector::InitLbIpAddress(...)` | `0x3c334e` | Same `GetServiceAddress` `0x39d18c` |
| `pebble::rpc::RpcConnector::Init(...)` | `0x3c474c` | `InitLbIpAddress` `0x3c32cc` |

The exact target `GetServiceAddress` appeared at **two** direct Thumb BL sites in this executable-section scan. It does not rule out virtual/indirect callers, other shared libraries, code data pointers or runtime/inlined caller paths. The code follows ELF Thumb-symbol bit clearing before attributing callsites to their enclosing named functions.

**Independent decoder controls:** the same original direct-BL scan rediscovered R047's `GCloud::CGCloudConnector::connectTConnd` → `GCloud::CTGcp::SetRouteInfo` at `0x3c6c4a`, and the two R042/R045 ACK receiver callsites at `0x3a845a` and `0x3a9fb0`. This checks the search method against unrelated original-known edges.

## Additional original callback *symbol* evidence, not executed call chain

Original ELF symbols include:
- `GCloud::CDefaultNameService::OnGetServiceAddress(int, vector<string>*)` at `0x3a6a70`;
- `GCloud::CTGcp::OnQueryNameResult(...)` at `0x3a60b4`;
- a `std::tr1::_Function_handler` binding involving `CDefaultNameService`, which is compatible with a deferred callback design.

These support a **concrete next trace**: `CDefaultNameService::Query` registering a callback, `OnGetServiceAddress` notifying a `CTGcp` name-service observer, and then endpoint storage/startup. **That virtual callback edge has not been verified through actual instruction/vtable dispatch or a real phone trace.** The separate RPC load-balancing branch must not be conflated with the name-service branch.

## Reproducible, bounded, public source-only verifier

- [R057 native auditor](../../../experiments/r057_original_address_callers.py): Python stdlib only; exact private original SHA and size required; ELF32LE ARM section/symbol bounds, Thumb BL target decode, caller enclosing-symbol checks, six original BL call-edge pins plus callback-symbol presence. Reports only fixed function labels and status—not service strings, credentials, route names or raw disassembly. No network and read-only.
- [R057 tests](../../../tests/test_r057_original_address_callers.py): **10 source-free synthetic/negative tests PASS, and one private-original gate SKIPPED in public CI**, including forward/backward Thumb BL, BLX rejection, ELF/function-symbol fixture, altered-header/size rejection, six-edge uniqueness, and independent callback-symbol absence negatives; optional private-original test SKIPPED in public CI.
- [GitHub Actions run 41343787854](https://github.com/despairarc000/temp/actions/runs/41343787854) **SUCCESS**. This is public CI source-only. Exact-original xrefs were separately verified in-memory in this conversation; CI does not have the private Apollo binary.

## Decision and next gate

1. **Prioritize original `CDefaultNameService::Query` / `OnGetServiceAddress` → `CTGcp::OnQueryNameResult` observer-dispatch ownership**, with specific native sites or vtable links. Test against the alternative `RpcConnector::Init → InitLbIpAddress` route-producer hypothesis. Do not invent or publish the actual ten-byte name.
2. Only after the *actual subsequent connection type* and source are pinned should the fake server implement **route-specific `0x1002` ACK/session/key behavior**. The original 63-byte first-service ACK must not be blindly replayed.
3. Preserve the original V3.8/V3.8.1 Termux server ACK/auth/Bingo behaviors and SOCKS5 IP+port scope. Do not patch the game or auto-run a phone listener. R056 remains source-only and is NOT integrated into private Termux runtime.
4. Correct terminology: **“post-address-response alternate named route”** is supported; calling it definitively the “lobby service” or a confirmed different upstream service is not.

**Result:** two original native address-lookup producer branches and a concrete upstream RPC init chain have been established, and independent original-version fingerprint verification passed. No accepted second-service reply, live login, lobby or bots.

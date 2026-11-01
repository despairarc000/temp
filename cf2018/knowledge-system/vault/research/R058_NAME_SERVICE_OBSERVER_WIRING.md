# R058 — GCloud name-service callback wiring (original CF2018)

**Date:** 2026-11-02. **Evidence:** read-only original 2018 `libapollo.so`, native static calls and vtables. No runtime game, phone or ACK success.

## Newly established source links

Original pinned Apollo: 5,243,704 bytes; R057 independently verified SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`. [Owner Drive source](https://drive.google.com/file/d/14Rd_IZ501GlbIE2sZIeXevK-MgsnvHIo/view), privately read only.

- Both original `CGCloudConnector` constructors at calls `0x3c76d2` and `0x3c78a2` construct `CDefaultNameService` (`0x3a69e0`).
- `CDefaultNameService` constructor calls `AddressService` construction (`0x3a6a02`) and initialization (`0x3a6a10`).
- **New direct call:** `CGCloudConnector::connectTConnd` at `0x3c696a` invokes `CTGcp::SetNameService` at `0x3a3374`.
- `CTGcp::SetNameService` stores its name-service pointer at offset `+0x2e0` and calls virtual slot `+0x10` using an observer at `CTGcp+0x48` (`0x3a3386`/`0x3a3388`).
- Concrete `CDefaultNameService` vtable address point `0x4f5080`: `Query` at `+0x08`, `Update` at `+0x0c`, **`SetObserver` at `+0x10`** (target `0x3a66a8`). `SetObserver` stores observer to `this+8`.
- Original `CTGcp::OnQueryNameResult` observer pointers are in its vtable; `CDefaultNameService::OnGetServiceAddress` has a bound callback pointer and indirect delivery instruction. The **actual asynchronous callback invocation on Android remains unverified**.

This closes the source-level **name-service observer-registration** link that was unknown after R057. It is not a proof of the actual ten-byte named route, a specific downstream service, or accepted second-connection ACK.

## Source-only verification

[Auditor](../../../experiments/r058_name_service_wiring.py) validates 3 direct-call sites, 7 instruction halfwords and 6 original virtual/function pointers behind an exact original-file hash gate. [Nine public synthetic tests plus one optional private-source test](../../../tests/test_r058_name_service_wiring.py) plus optional private-only original gate; public [GitHub Actions 41345156313](https://github.com/despairarc000/temp/actions/runs/41345156313) **SUCCESS**. The optional original-binary test is **SKIPPED** on public CI; original byte observations above were separately checked privately.

## Next

Original `CTGcp::OnQueryNameResult` → stored endpoint → transport start needs to be distinguished from the separate named-route selector. R057 also found `RpcConnector::InitLbIpAddress`, an alternative AddressService caller; do **not** collapse these two into one. Then trace the appropriate `0x1002` ACK key/session conditions before considering a fake-server response. No APK patch or speculative phone experiment.

**State:** Better original-code grounding for fake-server route research; authenticated session, lobby and playable bots still unverified.

# R081 — Original IConnector Initialize/Connect virtual boundary

**2026-11-02. Exact original static review + source-free CI controls, NO PHONE ACK.** Continues the R079/R080 source-level CTDir→RPC→CGCloud factory→CGCloudConnector construction path. The source is the user's connected Drive SHA-verified original `libapollo.so` (5,243,704 bytes, SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`). Original bytes, names of private routes, tokens and packets are never written to GitHub.

## IConnector vtable is not the primary connector vtable

The exact original C++ `CGCloudConnector` multi-inheritance vtable `_ZTVN6GCloud16CGCloudConnectorE` starts at `0x4f5b60`, with a **primary address point** at `0x4f5b6c` and a **secondary IConnector address point** at **`0x4f5c14`**. The secondary vtable contains original adjusting-thunk pointers:

| Secondary IConnector slot | Absolute original vtable word | Exact native method |
|---|---|---|
| `+0x10` | `0x4f5c24` → **`0x3c61b5`** | `CGCloudConnector::Initialize` adjustment thunk |
| `+0x18` | `0x4f5c2c` → **`0x3c7055`** | `CGCloudConnector::Connect` adjustment thunk |
| `+0x34` | `0x4f5c48` → `0x3c59e7` | `EnableManualUpdate` adjustment thunk |
| `+0x38` | `0x4f5c4c` → `0x3c59f3` | `UpdateByManual` adjustment thunk |

These values were checked from the owner-original in memory, not guessed from exported symbols alone. The **subobject offset and vptr are critical**; adding `+0x10` to the unrelated primary vtable would identify the wrong method.

## Original callsites and what they establish

In `RpcConnector::CreateConnection`, the original code immediately following the R080 factory virtual call includes:
- `0x3c509a`: save the returned connector pointer;
- `0x3c5114`: load an interface vptr from the saved connector;
- `0x3c5120`: load the virtual entry at **vptr +0x10**;
- `0x3c5122`: **BLX r3** into that virtual entry.

For an original `CGCloudConnector` secondary IConnector vptr, **this slot resolves to its `Initialize` adjustment thunk**. The later `BLX r3` at `0x3c5138` is also visible, but its full vbase adjustment and runtime target have **not been independently proved**; label it a later indirect call, not a confirmed Connect invocation.

Separately, the original concrete **`CGCloudConnector::Connect`** directly calls **`connectTConnd`** at `0x3c6f4a` and `0x3c6fc2` (target `0x3c68e0`). That method directly calls `CTGcp::SetRouteInfo` (`0x3c6c4a` → `0x3a33a0`) and `CTGcp::Start` (`0x3c6c86` → `0x3a369c`). The GCloud start path conditionally enters the separate GCloud ACK/TLV body decoder per R060–R061. No real second-service ACK has been sent or accepted by R077.

## Validation / limits

The new [R081 auditor](../../../experiments/r081_iconnector_virtual_chain.py) is source-only, exact-size/SHA gated, checks six instruction halfwords, six vtable words and six required direct-call sites. It refuses changed pins or wrong source and creates no sockets. [R081 tests](../../../tests/test_r081_iconnector_virtual_chain.py) cover each pin mutation, missing transport call, missing route setter/Start, changed caller owner and invalid ELF. The public CI combined run [41387077303](https://github.com/despairarc000/temp/actions/runs/41387077303) is **SUCCESS: 657 tests / 152 skipped**; R081 exact-private Python test is among the skips, with original source independently inspected in memory this turn.

The user's real R077 result remains **3/3 CTDir static route equality** with second SYN field5 changed and **HOLD_NO_ACK**. The static route/connector/transport branch is now much better supported, but it **does not establish that Android invoked these methods, selected the same vtable, passed ACK/key checks, authenticated, or loaded a match**.

**Next task (offline):** distinguish the later `0x3c5138` indirect dispatch and the specific CGCloudConnector/CTGcp ACK key and session validation on the same created connection, ideally using bounded original-native synthetic emulation. A separately owner-approved phone ACK experiment should wait until that evidence is available. Do not redo the R077 route test.

## R082 correction/continuation — actual Connect dispatch identified
R081's later indirect call at `0x3c5138` is the `AddObserver` virtual thunk, not Connect. [R082](R082_ICONNECTOR_CONNECT_DISPATCH.md) verified the factory's `+0x14` IConnector return adjustment and the actual Connect virtual call at **`0x3c5154`**, loading secondary IConnector vtable slot `+0x18` → `0x3c7055` (`CGCloudConnector::Connect` adjusting thunk). The Connect method directly calls `connectTConnd` at `0x3c6f4a` / `0x3c6fc2`. The source path is now static-code verified, not phone-runtime verified.

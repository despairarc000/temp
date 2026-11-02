# R082 — Exact original IConnector Connect dispatch in RpcConnector::CreateConnection

**2026-11-02. OWNER-ORIGINAL STATIC CONTROL FLOW + PUBLIC TESTS.** This resolves the open indirect-call question left in R081. It does not claim Android executed the path.

## Exact original factory return

The original `CGCloud::CreateApolloConnection` constructs `CGCloudConnector` at direct BL site **`0x3c7ee6` → `0x3c7784`**. At **`0x3c7f50`**, the factory executes `ADD.W r0, r5, #0x14` (halfwords `0xf105 0x0014`) before returning. The secondary `IConnector` vptr is at object offset **`+0x14`**, address point **`0x4f5c14`**. Therefore the factory returns the IConnector subobject pointer, not an unadjusted complete-object pointer.

## CreateConnection's actual virtual sequence

Using that returned IConnector pointer, the original `RpcConnector::CreateConnection` has these indirect callsites:

| Site | Interface slot | Original vtable pointer | Resolved method |
|---|---:|---:|---|
| `0x3c5122` | `+0x10` | `0x4f5c24 → 0x3c61b5` | `CGCloudConnector::Initialize` adjusting thunk |
| `0x3c5138` | `+0x08` | `0x4f5c1c → 0x3c5919` | `AddObserver` virtual thunk |
| `0x3c5144` | `+0x34` | `0x4f5c48 → 0x3c59e7` | `EnableManualUpdate` adjusting thunk |
| **`0x3c5154`** | **`+0x18`** | **`0x4f5c2c → 0x3c7055`** | **`CGCloudConnector::Connect` adjusting thunk** |

The important correction: **`0x3c5138` is not Connect**; it is the observer-registration call. The actual Connect dispatch is at **`0x3c5154`** after the manual-update setup.

The `Connect` implementation directly calls `CGCloudConnector::connectTConnd` at **`0x3c6f4a`** and **`0x3c6fc2`**. That method applies the CTGcp route at **`0x3c6c4a` → `CTGcp::SetRouteInfo`** and starts transport at **`0x3c6c86` → `CTGcp::Start`**.

Combined with R079/R080, the original static path now reaches the concrete GCloud connector's Connect method and its TGCP route/start continuation. This is stronger than a factory-only link.

## Verification

- [R082 original-binary auditor](../../../experiments/r082_iconnector_connect_dispatch.py) requires the exact original Apollo SHA/size, factory return adjustment, ten dispatch halfwords, six secondary-vtable words and four direct-call target groups.
- [R082 regression tests](../../../tests/test_r082_iconnector_connect_dispatch.py) cover instruction/vtable mutation, missing constructor/Connect/route/Start edges, wrong owner and no-network controls.
- CI [41389299841](https://github.com/despairarc000/temp/actions/runs/41389299841): **SUCCESS — 673 tests, 153 skipped**. The private-original Python audit is skipped in public CI; the owner-connected original ELF was independently SHA-pinned and inspected in memory.

## Limits and next step

This proves original source callsites and vtable targets **conditional on this object/path**. It does not prove the phone constructed this connector, ran Connect, sent the second SYN through this code, or accepted an ACK.

Next: follow the newly confirmed Connect path into CTGcp initialization and determine whether the active configuration supplies a nonempty DH parameter string and which ACK key mode is selected. Do not replay the first service's ACK based on route equality alone.

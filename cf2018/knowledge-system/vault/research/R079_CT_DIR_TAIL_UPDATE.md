# R079 — CTDir uses a Thumb B.W tail branch to RpcConnector::Update

**2026-11-02. NEW ORIGINAL-NATIVE STATIC RESULT + SOURCE-FREE TESTS.** No Android runtime, second-service ACK, gameplay, APK patch or live fake-server send.

## Original evidence acquired this turn

The owner's connected Google Drive contains the 2018 unpacked APK's `app/lib/armeabi-v7a/libapollo.so` (5,243,704 bytes). This turn the file was read privately through the connected source and its **SHA-256 independently recomputed as** `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8` — matches the exact R057 original fingerprint. The ELF32 little-endian ARM section/symbol tables were parsed; a separate bounded read of three ten-byte functions decoded their exact Thumb-2 instructions. Only results below are recorded; **no original binary, route, account or packet bytes are committed**.

### What R075's BL-only scan missed

Three `GCloud::CTDir` methods are ten-byte forwarding wrappers: load the held RPC connector pointer, guard against null and execute a **Thumb-2 B.W tail branch**, then return if null. Prior R075 direct Thumb `BL` scanning correctly found no *BL*, but that negative result never excluded B.W. The original-source check now identifies three precise tail calls:

| Original CTDir method | B.W site | Exact original target |
|---|---|---|
| `CTDir::IsConnected` | `0x36f01a` | `RpcConnector::IsConnected` `0x3c27dc` |
| `CTDir::EnableManualUpdate` | `0x36f024` | `RpcConnector::EnableManualUpdate` `0x3c2580` |
| **`CTDir::UpdateByManual`** | **`0x36f02e`** | **`RpcConnector::Update` `0x3c5248`** |

Thus a **static, conditional** CTDir→RpcConnector Update edge **does exist**. This does not mean it was called on the user's phone. The wrapper has a null-guard, and the origin/timing of `CTDir::UpdateByManual` on Android remains unproven.

### Stronger original-source continuation

Original `RpcConnector::Update` has **two** verified direct calls to `RpcConnector::CreateConnection` (sites `0x3c52b4` and `0x3c5372`, target `0x3c4f78`), previously documented at R073 and rechecked this turn.

**Additional original native evidence this turn:** `RpcConnector::CreateConnection` has direct BL sites for:
- `GCloud::_tagNameRouteInfo` construction: `0x3c500a` → `0x398cb4`.
- `GCloud::CGCloud::GetInstance`: `0x3c5088` → `0x3c82a0`.

These establish a **source-level bridge from RPC connection construction to GCloud route data and the GCloud singleton**. They do **not** yet prove a particular GCloud connector instance is constructed/initialized at runtime, the exact virtual dispatch, or which TGCP ACK receiver handled the phone's next-service SYN.

## New verification

[Original-binary R079 auditor](../../../experiments/r079_ctdir_manual_update.py): requires exact original Apollo SHA/size, maps all wrapper instructions via ELF PROGBITS, rejects wrong instruction shape, decodes only Thumb **B.W** (not BL), pins all three method source/target symbol identities, and verifies four direct BL continuation edges. No network APIs, binary export or ACK logic.

[R079 tests](../../../tests/test_r079_ctdir_manual_update.py): public synthetic negative and positive controls cover wrapper shape, null guard, return instruction, tail target mutation, symbol owner, branch opcode, missing RPC→CreateConnection, missing GCloud route constructor/singleton, and wrong original file. Optional exact-owner-original audit is skipped in public CI because no private `.so` is committed. In this turn, the private original was independently read and SHA-pinned, all three B.W targets and all four continuation BL sites verified by a separate in-memory JavaScript ELF/Thumb reader. This is **private original static evidence**, not full Python native audit in CI.

## What changed and what remains

**Advanced:** R075's “no CTDir direct Update BL” remains technically true, but now **cannot be used as an argument against a CTDir→RPC Update path**. That path exists via **B.W** and leads to CreateConnection, where GCloud route info and the GCloud singleton are referenced.

**Still unresolved:** who schedules CTDir::UpdateByManual in the owner's actual Android lifecycle; how `RpcConnector::CreateConnection` selects/creates the specific GCloud connector and its ACK receiver through indirect dispatch; the valid second-service nonce/key/session and ACK; login/lobby/bot gameplay. R077 route literal equality 3/3 remains the newest phone result. No R080 Android experiment yet warranted; pursue **offline conditional native connector/vtable dispatch** next rather than sending a guessed second ACK.

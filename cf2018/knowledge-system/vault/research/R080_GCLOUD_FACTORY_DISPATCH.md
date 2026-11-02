# R080 — Verified original CGCloud virtual factory creates the GCloud connector

**2026-11-02. EXACT OWNER ORIGINAL SHA/ELF STATIC INVESTIGATION + PUBLIC SYNTHETIC TESTS.** No live phone experiment, login, second-service ACK, game patch or private binary committed.

## Why this closes R078/R079's indirect factory gap

The owner-connected extracted Android CF2018 game's `app/lib/armeabi-v7a/libapollo.so` was read privately, and its SHA-256 independently recomputed this turn: **`4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`** (5,243,704 bytes). This is the same exact original artifact used by R057–R079. ELF32 ARM function symbols, original code halfwords and vtable bytes were examined **in memory only**.

The original `RpcConnector::CreateConnection` calls `GCloud::CGCloud::GetInstance` at site **`0x3c5088`** (target `0x3c82a0`), then uses these consecutive known Thumb instructions:

| Original instruction site | Meaning |
|---|---|
| `0x3c508c` (`0x6803`) | Load virtual table pointer from returned instance |
| `0x3c5092` (`0x699d`) | Load function pointer from vptr **+0x18** |
| `0x3c5096` (`0x47a8`) | **BLX r5** — indirect virtual call |

The original primary `CGCloud` vtable's address point is **`0x4f5d5c`** (within `_ZTVN6GCloud7CGCloudE` at `0x4f5d50`). The original word at **`0x4f5d74`** (address point +0x18) is **`0x3c7e39`**, Thumb pointer to exact symbol **`GCloud::CGCloud::CreateApolloConnection`** (function start `0x3c7e38`). Original RTTI and destructor slots were also verified.

**The factory's next original direct calls:**
- `CGCloud::GetInstance` constructs `CGCloud` at **`0x3c82b2` → `0x3c8204`**.
- `CGCloud::CreateApolloConnection` directly constructs a **`GCloud::CGCloudConnector`** at **`0x3c7ee6` → `0x3c7784`**.
- `CGCloudConnector` constructor directly constructs `GCloud::CDefaultNameService` at **`0x3c78a2` → `0x3a69e0`**.
- Existing R047/R060/R061 source audits trace `CGCloudConnector::connectTConnd` to CTGcp route setter/start and to a separate GCloud ACK/TLV receiver. The original paths exist, but **not all successive virtual method invocations in `RpcConnector::CreateConnection` have been proven yet**.

Combined with R079's previously missed **`CTDir::UpdateByManual` B.W → `RpcConnector::Update`**, and two known `RpcConnector::Update → CreateConnection` BL sites, there is now a substantial *source-level* CTDir → RPC → **GCloud factory** → connector construction bridge, not merely two unrelated native subsystems.

## Proof scope and explicit limits

- `CGCloud` vtable slot selection resolves exactly to the named method in the owner's original build; this is a **static dispatch target**, conditional on the vptr being the original CGCloud primary vtable at runtime.
- The private native read also observed the method constructor/symbol provenance. **No captured Android call stack**, object identity, virtual connector Initialize/Connect invocation, ACK decryption/key check or authenticated account was observed.
- R077's three next-service named route values equaled the original CTDir static ten-byte literal (**3/3**), and each changed SYN field5 (unit ID) compared with the initial address SYN. This materially supports but does not prove that the actual phone took the above factory chain.
- **Never substitute field5 wire kind `0` for a numeric unit ID.** The local `REFUSED` label is diagnostic comparison policy, not an observed phone auth rejection.
- **No new real-phone test is justified yet.** Do not send the original 63-byte first-service ACK to a different service on the basis of route equality.

## Regression and follow-up

[R080 exact-original auditor](../../../experiments/r080_gcloud_factory_dispatch.py) checks three instruction halfwords, four original vtable entries, and eight required direct callsites across seven targets. It requires exact original SHA and size, emits only fixed booleans and counts, never copies the source or starts network. [R080 tests](../../../tests/test_r080_gcloud_factory_dispatch.py) exercise instruction and vtable mutations, missing ctor/name-service/receiver edges, unexpected ownership, safe extra caller tolerance, and refusal of wrong source. Private-original Python gated test remains **SKIPPED in public CI**; the original in-memory JS ELF reader independently verified the concrete instructions and vtable this turn.

**Next offline discriminator:** decode the original connector-returned *virtual* `Initialize` and `Connect` callsites in `RpcConnector::CreateConnection` (e.g., around `0x3c5122` and `0x3c5138`) using the exact GCloud connector vtable, then build bounded negative controls. Resolve this before any ACK/key/session phone test.

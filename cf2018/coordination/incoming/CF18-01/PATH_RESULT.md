# CF18-G2-RX-03 — bounded path selection and native receive wrapper

CF18-01, 2026-10-30. Completed against live main
`9a0d6ef09c6b62a4543c8c9aadef15f1946df470`; draft began at
`b26007d73b5d6d781c8c8e8e1681c18f55cb18ce`. SUBMITTED, no active claim remains.
Only this lane's files are submitted. [Acceptance](PATH_ACCEPTANCE.md) preceded
the original draft; resume addendum preceded completion. Classes:
ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS + INDEPENDENT_SYNTHETIC.

**Result:** the examined native net-recv wrapper preserves raw prefix bytes;
it does not strip 43 66 or 66 43 before the GCloud gather. Separately, the
examined AddressService virtual dispatch selects the GCloud Apollo factory
using the constructor's vtable address point. Neither result establishes the
current phone runtime path or a complete authenticated session.

## Current evidence preserved and source rechecked

The [phone v1.2 report](../CF18-05/PHONE_V12_RESULT.md) and explicit user
confirmation establish SYN133 -> AA_DIRECT ACK63 -> authentic0x2001/117.
The [submitted CF02 auth trace](../CF18-02/auth_rx_02/RESULT.md) already localizes
the exact three v1.2 replies' first native failure to missing TGCPBody preamble,
before account parsing. This packet does not duplicate that auth investigation
or revert to older no-post-ACK assertions. G2 auth/session remains BLOCKED.
Deployed relay source and actual directional EOF origin remain unknown.

[Source provenance](../../../sources/SOURCE_PROVENANCE.md): actual private
Apollo5243704 bytes, SHA-256
`4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`,
ELF32 little-endian ARM EABI5; addresses below are virtual/Thumb bit cleared.
Source pin checked for every probe. Bounded static reread used actual ELF symbols,
PT_LOAD bytes, relocation metadata and Capstone5.0.9. No original/raw disassembly
or library is published. Originals are private under the previously authorized
mirror receipt; no new download, Drive inventory, source modification or game run.

## Static caller relationships: GCloud and legacy are distinct

| Relationship actually reviewed | Evidence and limit |
|---|---|
| AddressService::CreateConnection entry0x39d654 | At0x39d756 calls CGCloud::GetInstance0x3c82a0, then0x39d760 loads virtual slot+0x18;0x39d764 calls it indirectly. It is not a direct factory call. |
| CGCloud singleton/constructor | GetInstance calls constructor0x3c8204 at0x3c82b2. Constructor0x3c823e–42 supplies vtable address point+0xc. CGCloud vtable0x4f5d50 slot(address point+0x18) resolves to CreateApolloConnection0x3c7e38. |
| Factory to connector | Full344-byte factory symbol includes direct constructor call0x3c7ee6 -> CGCloudConnector0x3c7784. Earlier account-factory calls are separate; symbol proximity alone was not used. |
| Connector to GCloud TGCP | connectTConnd entry0x3c68e0 includes call sites0x3c6a70/0x3c6bd4 -> GCloud::CTGcp::Initialize0x3a3d18; Initialize calls GCloud create0x3a7d0c at0x3a3d7a. |
| GCloud thread startup | OnThreadStart entry0x3a4a04 contains call site0x3a4a80 -> GCloud start0x3a9d92. 0x3a4a80 is a call site, not the function entry. |
| Legacy comparison | NApollo::CTGcp::Initialize entry0x37bfe4 contains0x37c096 -> legacy create0x1ba16c. Legacy OnThreadStart entry0x37afac contains0x37b036 -> legacy start0x1be812. These call sites are not function entry addresses. Legacy C# exports0x1e0440/0x1e048a do not prove GCloud selection. |

These bounded relationships make an AddressService GCloud route source-supported,
but do not prove actual Android caller reachability, live object/vtable, installed
runtime state or whole-library absence of other routes. Static factory linkage
is separate from the dynamic prefix control below; no connector is instantiated.

## Executed virtual-dispatch prefix controls

[native_path_controls.py](native_path_controls.py) uses the already integrated
canonical NativeControl from40c4aafe6665e671d08df6badb378121ec4ff213. It executes
actual instructions beginning0x39d756, supplies a synthetic CGCloud instance
from GetInstance, synthetic r5/r6 argument storage and actual ELF vtable bytes.
It stops before the selected method entry, returning probe sentinel-77.

| Control | Actual selected method | Meaning |
|---|---|---|
| Constructor address point vtable+12, slot+24 | 0x3c7e38 | Reaches GCloud Apollo factory boundary |
| Malformed address point vtable+8, same slot | 0x3c84b0 | Selects different method, not connector factory |

The second control is malformed synthetic state, not an observed fallback.
The only application stub is GetInstance0x3c82a0 -> synthetic object pointer;
the selected method is stopped before execution. -77 is a probe stop sentinel,
not a native protocol result. No constructor/network/account operation runs.

## Actual native wrapper plus imported-recv substitution

The [boundary runner](native_boundary_controls.py) gains optional socket_payload.
Existing default controls still substitute the entire net wrapper result.
With socket_payload supplied, actual tgcpapi_net_recv0x284fcc runs with timeout0
and calls imported recv at0x285056 -> PLT0x1940e8. Only that imported recv
is substituted with independent bytes or zero; there is no real socket.

ELF .plt starts0x193d5c; its20-byte header and12-byte slots were cross-checked
against .rel.plt/.dynsym. Relevant relocation indices and addresses:
memset20 ->0x193e60, memmove21 ->0x193e6c, memcpy30 ->0x193ed8,
__errno61 ->0x19404c, recv74 ->0x1940e8, select75 ->0x1940f4.
Timeout0 controls do not execute select. Negative recv errors requiring errno
were not exercised; injected zero is the EOF-like control, not peer evidence.

| Independent control | Actual native result |
|---|---|
| AA or99 envelope delivered through wrapper/imported recv | gather0, decoded marker0x4366, complete bytes retained |
| Raw43 66 + envelope or raw66 43 + envelope | gather-18, cursor0; remaining-byte SHA equals complete injected input: prefix preserved |
| Seven-byte partial99 header, remainder supplied by recv | gather0, full frame buffered/pending; byte hash preserved |
| Partial frame plus imported recv returning0 | actual wrapper maps zero to-4; gather reports remembered-10 |
| Complete buffered frame plus imported recv returning0 | first gather0; after explicitly HOST-simulated consumption, second gather-10 without a second recv |
| Complete frame at full buffer capacity | gather0; wrapper/imported recv not called |

Consequently upstream prefix stripping is not supported by this examined wrapper
path. This is bounded to the pinned wrapper and control configuration; an external
proxy or other route could behave differently. No phone closure is attributed.

## Stubs and budgets

Wrapper controls use fresh ELF PT_LOAD mappings, <=64KiB synthetic input/buffer,
100000 instructions and one second per native gather call. Imported recv copies
only if the supplied bytes fit the actual requested capacity; otherwise refuses.
Libc memset/memcpy/memmove are bounded to64KiB; error-string0x1c6544 supplies inert
storage only. No protocol decoder, positive native return or marker rewrite is
stubbed. Optional second call simulates caller consumption in HOST code, not
native receive/decrypt; it is explicitly labeled in results.

Factory controls reuse canonical size/hash/ISA guards and fresh memory, same
instruction/time bounds, with synthetic instance/arguments and stop-before-method.
Android globals/GOT/loader/runtime are incomplete. A selected factory or gather0
is never authentication, login, playable state or proof of on-phone path selection.

## Actual checks and concurrent-work boundary

Live head and nine startup documents/assignments/Graphify dependencies refreshed.
No active previous native worker was present; git status returned128 because the
local connector snapshot is not a checkout. Shared coordinator auth integration
drafts were already present and preserved. They are not published by this lane.
Existing CF02 and CF01 auth drafts are not resubmitted as independent research.

```text
python tools/knowledge.py route 'framing native AddressService virtual factory receive wrapper prefix preservation'
  Routes: sources1, tgcp1
python tools/knowledge.py doctor
  PASS
python -m unittest discover -s tests -v
  Ran128;95 PASS/33 private-source SKIP
CF18_APOLLO_LIBRARY=<pinned Apollo> PYTHONPATH=<private deps> \
  python -m unittest discover -s coordination/incoming/CF18-01 -p test_native_path_controls.py -v
  Ran8; all PASS
python -m unittest discover -s coordination/incoming/CF18-01 -p test_native_path_controls.py -v
  Ran8; all8 explicitly SKIP without selected private source
CF18_APOLLO_LIBRARY=<pinned Apollo> PYTHONPATH=<private deps> \
  python -m unittest discover -s coordination/incoming/CF18-01 -v
  Ran74; all PASS/no skips
python -m unittest discover -s coordination/incoming/CF18-01 -v
  Ran74;37 PASS/37 explicit private-source SKIP
```

Canonical128 counts include the preserved unpublished coordinator integration;
live main before this packet has101 canonical tests. The framing packet changes
no canonical tests/code/knowledge. All20 prior boundary and14 strict-parser
controls still pass as part of74. No phone or live-game network experiment.

## Coordinator recipe and remaining gate

Review this bounded packet and its added wrapper mode; rerun all74 framing tests
with pinned source. Keep current strict parser policies; do not add prefix stripping
based on outgoing TX, reproduce native overflow/duplicates, or treat method selection
as phone runtime proof. The separate submitted [boundary result](BOUNDARY_RESULT.md)
contains99/bounds evidence; it is not replaced by this continuation.

Integrate descriptive Q-01 factory/wrapper relationships only after review, and
retain each emulation substitution and original source pin. Canonical auth9a0
integration/ICM/checkpoint changes remain the coordinator's task; no duplication
of CF02 auth/account/Bingo ownership. Actual installed context, later session/Bingo
and deployed v1.2 relay/directional EOF remain open. The proven phone ACK-to-auth
hop is preserved; no new phone test is requested by this framing packet.

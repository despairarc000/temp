# Connection callbacks: local notification versus validated session

CF18-G2-CALLBACK-01, coordinator, 2026-10-30. Base main
`c9b1d3555f8dd4036d64d1d34cb47a440b881c4c`. Schedules remain paused.
Classes: ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_EXPLICIT_STUBS.
**No authenticated session, accepted Bingo or playable game is demonstrated.**

Source: [provenance](../../../sources/SOURCE_PROVENANCE.md), actual private
5243704-byte Apollo SHA-256
`4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`,
ELF32 little-endian ARM/Thumb, rechecked before execution. Addresses are virtual,
Thumb bit cleared. Original APK/OBB remain untouched; no network/phone run.
[Acceptance](../../../coordination/CF18-G2-CALLBACK-01/ACCEPTANCE.md),
[original controls](../../../experiments/native_callback_controls.py),
[tests](../../../tests/test_native_callback_controls.py),
[actual matrix](../../../coordination/CF18-G2-CALLBACK-01/NATIVE_MATRIX.json).

## What this advances

The exact v1.2 [earliest failure](AUTH_RECEIVER.md) remains missing TGCPBody
preamble, native -32 mapped to -18, before account parsing. The correction reaches
Bingo wait only. [Bingo research](BINGO_SESSION.md) already shows numeric state5
is insufficient. This investigation follows the next application callback instead
of constructing another reply or guessing a valid relay identity.

Completed local CF18-02 session_app_01 controls were reviewed and all13 rerun.
Their injected state5/free-buffer context yields writable event8; real CTGcp::Update
0x3a57d0 sets connected byte+0x1b2 at0x3a5ae2. Getter0x3a37e4 reads that byte.
Zero account/relay storage does not prevent this transport notification.
That local packet has no public source commit; exact input hashes are recorded
in [integration](../../../coordination/INTEGRATION.md). Incoming edits are untouched.

## Actual callback trace and evidence boundary

| Stage | Verified instruction path / consequence |
|---|---|
| CTGcp observer call0x3a5b0c | Native vector+0x5c/+0x60, slot+8. One injected observer uses original constructor-selected vtable address point0x4f5c58; stored target0x3c6379. Actual thunk0x3c6378 subtracts0x18 and enters CGCloudConnector::OnGcpConnected0x3c6300. No RTTI stub on this transport path. |
| Local result0x3c6308–0e | Sets argument0 and calls real _tagResult constructor0x36f564; constructor writes result code+0xc. No received auth/account predicate is consulted in this examined callback. String storage alone is substituted. |
| Route / statistics0x3c6310–36 | Existing CTGcp pointer optionally obtains route server ID, stores connector+0x178. Real main vtable slot+0x8c (address0x4f5bf8) targets onConnResultStatic0x3c59fa: tick/time accounting, not account validation. Tick clock supplied zero64. |
| UI boundary0x3c6352 | Actual call carries member pointer0x3c67ad, adjustment0, argument0. PerformSelectorOnUIThread is capture-only; no thread or UI execution. Connected-info account prefix remains zero. |
| Separate notify entry0x3c67ac | Explicitly injected status0 or9; real result construction/copy. Observer vector copy and RTTI outcomes substituted. Original AddressService vtable slot+8 at0x4f4a70 targets0x39ca79; actual service instructions execute. This is not end-to-end runtime observer registration proof. |
| AddressService0x39cad6–e2 | Reads result+0xc. Nonzero sets service error byte+0x60=1 and returns before buffer lookup. Status9 control verifies this earliest service error branch. |
| Zero-result service0x39cae4–0x39cb18 | Requires service connector+0x28, virtual GetBuffer+0xb4, nonnull RTTI-cast buffer. Missing connector / supplied failed buffer cast prevent binding. The connected-info pointer is passed to this function but no account-content read occurs in this examined handler. |
| Binding0x39cb64–72 | Calls real MsgBuffer::bind0x3c18ec with service IConnector+0x24, then original MsgBuffer vtable slot+0x10 resolves open0x3c1498. One control stops before bind with sentinel-77; a second executes bind with bounded16-byte allocation. |
| MsgBuffer local open | Bind installs a local callable containing supplied connector pointer. open0x3c1498 is a two-byte return. isOpen0x3c1480 statically checks function-manager+0x4c nonzero. These operations do not receive or authenticate anything. No application request is sent by this handler in these controls. |

The constructed success result is **local notification status**, not a verified
server decision or valid identity. Neither IsConnected nor reaching this callback,
AddressService callback, local buffer binding or open() is an authentication oracle.
This conclusion is bounded to these functions; later RPC/managed consumers may
apply meaningful account/session checks. No whole-client absence is claimed.

## Actual controls

Ten-case matrix regenerated identically. Transport observer: actual thunk and
connector callback execute and capture UI argument0. State4 waiting: no callback.
Empty transport list: connected flag sets but no connector callback. Separate
dispatch with injected observer/RTTI: zero result reaches bind boundary with zero
connected-info account prefix; result9 sets error flag first. Missing connector,
failed observer RTTI, failed buffer RTTI and empty dispatch list stop their later
paths. Actual local bind/open installs callable and returns without a send.
Void callback return-register leftovers are not interpreted as result codes.

Transport and dispatch controls are separate fresh contexts. State5 is injected,
not obtained by accepting a valid Bingo. UI scheduling is intercepted, then notify
is invoked independently. Do not combine these stages into a claim of an accepted
server session or actual Android callback chain.

## All substitutions and execution limits

Fresh original PT_LOAD memory via NativeControl, original GOT/vtable bytes, synthetic
FD42, state4/5, free send capacity64, zero account/relay/connected-info prefix.
Main connector+0x0 and observer+0x18 vtable address points follow actual constructor
0x3c77de–fa. No constructor/Android loader/thread completeness claim.
Synthetic log level5 at0x506a78 suppresses formatting branches only. One observer
maximum; trace64; 100000 instructions/one second per execution. No wire input.

| Boundary | Explicit substitute, only if reached |
|---|---|
| 0x3971f0 /0x39738c /0x3974c0 | Empty36-byte AString storage, bounded assignment, suppressed destructor; result-code writes remain original |
| 0x394a3e /0x394a78 | Zero64 clock/tick |
| 0x381cda | UI scheduling capture only; no callback execution |
| 0x284fcc | No-data-3, no socket |
| 0x37e958 /0x1a4c04 /0x1a4c16 | Timer reset and single-thread lock/unlock no-ops |
| 0x3a51f4 | OnDataOutEvent suppressed; no application send |
| 0x397b50 /0x397ba4 | Explicit observer-vector copy with0/1 supplied element and suppressed destructor |
| 0x3c9b48 | Supplied observer/buffer dynamic_cast outcomes; not actual RTTI/registration proof |
| Synthetic virtual GetBuffer target | Supplies synthetic buffer/shared-count storage; not a real connector implementation |
| 0x33e286 | Shared-count destructor suppressed |
| 0x3c93fc | One isolated16-byte allocation for actual bind; any other size fails |
| Canonical memory/log/error boundaries | bounded libc memory <=64KiB; XLog no-op; last-error get0/set no-op; inert error-string if reached; actual per-case use recorded in matrix |

No TGCP parser, transport state-handler, connector callback, result constructor or
AddressService branch success is stubbed. Supplied RTTI, vector and GetBuffer
boundaries are intentionally excluded from runtime acceptance claims.

## Verification and next useful boundary

Actual commands, current environment:

```text
python tools/knowledge.py route 'authentication session application connection callback account consumers'
python tools/knowledge.py doctor
  PASS
CF18_APOLLO_LIBRARY=<pinned Apollo> CF18_APK_SOURCE=<pinned APK> PYTHONPATH=<private deps> python -m unittest discover -s tests -v
  160 PASS, zero skips
python -m unittest discover -s tests -v
  160 total:98 PASS/62 explicit private-source SKIP
CF18_APOLLO_LIBRARY=<pinned Apollo> PYTHONPATH=<private deps> python -m unittest discover -s coordination/incoming/CF18-02/session_app_01 -v
  13 PASS, zero skips
PYTHONPATH=<private deps> python experiments/callback_native_matrix.py --library <pinned Apollo>
  ten cases; exact JSON reproduction verified
python experiments/callback_native_matrix.py
  inactive without explicit private source
```

Next offline target: actual QueryAddrInfo request submission/response consumer
(AddressService Send_QueryAddrInfo0x3998d4 / Recv_QueryAddrInfo0x399a98), bounded
before socket submission; find an application-level response predicate. Static
symbols locate these functions; their request/response behavior is not executed
or claimed here. Current phone EOF cause and valid Bingo/account semantics remain
unknown. No additional payload sweep or phone test is justified by these callbacks.

Separately, [CF18-05 handoff](../../../coordination/incoming/CF18-05/V14_DEPLOYED_BRIDGE_HANDOFF.md)
at c9b1d355 reports recovery/review of the private v1.2 bridge and preparation of
user-only v1.4 with21 local tests. This supersedes blanket source-unavailable
claims for that author, not the unknown EOF origin. Private package not independently
reopened in this activation; no v1.4 phone result has been supplied here.

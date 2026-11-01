# R048 — GCloud connector initialization supplies the named-route object

2026-11-01. Evidence **exact original Apollo ELF STATIC**, not a phone call stack. This extends R047's unresolved upstream route setter. Original ELF private SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, 5,243,704 bytes. **23/23 original Thumb instruction pins PASS; 8/8 local focused controls PASS** including original gated audit and source-free mutation controls. No new network test. No verified login, lobby or bots.

## Newly identified initialization route origin

1. `GCloud::_tagConnectorInitInfo::ReadFrom` (Thumb 0x398d90) reads a route-kind integer at object offset **+0x44** (`0x398dda–0x398dde`). It calls `GCloud::CreateRouteInfo` at **0x398de0**, stores its pointer at **+0x48** (`0x398de6`), and when non-null decodes its route body at **0x398dec**. `WriteTo` (`0x398b2a`) serializes the route kind at `0x398b72` and optional route payload at `0x398b7c`. **This proves the object supports a serialized route field; it does not show the runtime bytes or origin of serialized input.**
2. `GCloud::CreateRouteInfo(int)` at **0x398d24** branches on type **4** (`0x398d2a`) and constructs `GCloud::_tagNameRouteInfo` at `0x398d6e`; name type4 is an explicitly implemented variant, not a guessed one.
3. `GCloud::CGCloudConnector::Initialize(_tagConnectorInitInfoBase const*)` at **0x3c60b8** dynamic-casts to the concrete init info (`0x3c6106`), reads optional route pointer **+0x48** (`0x3c6164`), skips null (`0x3c6168`), and dispatches through connector virtual slot **+0x20** at `0x3c6172–0x3c6174`.
4. The **actual original vtable** for `GCloud::CGCloudConnector` is at ELF address `0x004f5b60`; its primary address point `0x004f5b6c`, plus **0x20**, contains `0x003c5b19` (Thumb pointer to `CGCloudConnector::SetRouteInfo` at 0x3c5b18). Verified direct vtable bytes and surrounding RTTI/destructor entries: this is the concrete dispatch target, **not** a guessed interpretation of an indirect call.
5. R047 already proved `SetRouteInfo` clones that object into connector+0x19c. `connectTConnd` passes it to `GCloud::CTGcp::SetRouteInfo` at 0x3c6c4a. R046 proved GCloud setter -> handle route buffer -> `gcloud_tgcpapi_send_syn_msg` type4/name emission. Thus the **static serialized-init-object-to-GCloud-SYN route chain is verified across native functions**. This does **not** prove that the owner's exact 131-byte SYN took this initialization path.

## Why R047's earlier direct-call search missed it

R047 found no immediate direct `BL CGCloudConnector::SetRouteInfo`. The caller in `CGCloudConnector::Initialize` instead uses a **virtual function pointer** from `this->vptr + 0x20`. The vtable target now confirms the callee. C++ hidden result-pointer calling convention means `r0` is a result buffer, `r1` is `this`, and `r2` is the route argument; do not mistake r0 for the connector object.

## Verified test scope and limits

The local source-only R048 audit hashes the original library, checks the 23 individual Thumb pins in bounded instruction windows, verifies original vtable RTTI and slot +0x20 against 0x003c5b19, and explicitly marks phone execution and authenticated login as unproven. 8/8 unit tests PASS, including per-pin omission and mutation negatives, synthetic virtual slot mutation, wrong ELF rejection, and original gated audit. Original ELF and raw strings remain private.

**Still unknown:** who populates the serialized initialization data at runtime; which concrete source/config/IPC sets the name; the exact ten-byte value after R037's correct-RPC64 reply; and the accepted second-service ACK/security state. `ReadFrom` existing does not prove that its path executed on the phone; route may also be assigned by exported `apollo_connector_setRouteInfo` or another caller. R039 wrong-RPC64 and R038 no-reply controls still strongly support response-dependent rerouting but do not establish login.

**Next research:** trace who creates/sends `_tagConnectorInitInfo`, link managed `ApolloConnector.Initialize` and native `apollo_connector_Initialize`, and determine whether post-address callback creates a different connector or changes route on an existing connector. Do not use another blind ACK or broad phone capture.
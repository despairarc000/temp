# R049 — Distinguish Unity's NApollo route setter from native GCloud initialization

Date: 2026-11-01. **Exact-original managed + native static research; no phone test or game authentication.** This follows R048 (23/23 native pins, exact virtual slot, eight offline controls), which is already committed.

## Original source integrity

- Original managed `Assembly-CSharp.dll`, 13,423,104 bytes, SHA256 `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9`, obtained from owner's connected Drive and examined read-only.
- Native `libapollo.so`, 5,243,704 bytes, SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, privately inspected with LLVM Thumb disassembly.

## New complete managed CIL call-reference check

The hash-checked protected original C# assembly has 75,087 MethodDefs. **72,428 methods could be decoded completely in the local R043/v3.8 CIL call walker**, yielding **383,258 call/newobj/ldftn references**. Across those decoded references, the only exact method-target match containing `SetRouteInfo`, `CreateApolloRouteInfo` or `apollo_connector_setRouteInfo` is:

- Caller `Apollo.ApolloConnector.SetRouteInfo` (MethodDef token `0x060097b3`, RVA `0x34d758`, method body 67 bytes), at CIL offset `+0x38`, calls `Apollo.ApolloConnector.apollo_connector_setRouteInfo` (P/Invoke method token `0x060097d1`, no managed CIL body). The wrapper also invokes `Apollo.ApolloBufferBase.Encode` at +0x10 and reads `Apollo.ApolloObject.get_ObjectId` at +0x2f before native dispatch.

There are **no other directly decoded CIL callsite references** to those three method names in this original assembly. This is a bounded one-assembly static result, **not** proof nobody uses the API: interface or reflection dispatch, other assemblies, and native-only paths remain possible. The direct wrapper call is expected and does not prove the game invokes that wrapper.

## Native exported setter is NApollo, not the GCloud init route setter

Original export `apollo_connector_setRouteInfo` at Thumb address `0x38cac0` resolves an instance using `NApollo::IApolloObjectManager::GetReqInstance` at `0x38cace`, validates the connector through `__dynamic_cast` at `0x38caee`, constructs a route object with `NApollo::ApolloRouteFactory::Create` at `0x38cb70`, then invokes the connector's **virtual setter** at `0x38cbb0`. That establishes the native P/Invoke wrapper goes through NApollo routing and an explicit route-factory operation. It does NOT establish a direct call to GCloud::CGCloudConnector::SetRouteInfo.

Separately, R048's **GCloud** path: `_tagConnectorInitInfo::ReadFrom` supports a serialized route kind (+0x44) and optional pointer (+0x48); CGCloudConnector::Initialize reads that object and virtual slot +0x20 resolves to GCloud::CGCloudConnector::SetRouteInfo, which clones into +0x19c; connectTConnd passes it to CTGcp before GCloud SYN serialization. This is a **different, independently verified native route pipeline**.

## Why this matters

Prior R037 phone tests with correct RPC64 candidate response showed shorter 131-byte SYNs with ten-byte named route; R039 wrong RPC64 and R038 close-only did not. The route's actual string and runtime producer remain unobserved. Conflating managed `ApolloConnector.SetRouteInfo`/NApollo exports with native GCloud initialization could lead to implementing the wrong handshake. The original library contains both stacks.

**Next:** identify which stack produces the observed phone SYN by tracing the **runtime caller that produces GCloud connector initialization data** (or an alternative dynamic route source) and inspecting ACK/session handling. Do not infer a ten-byte name from a literal-length search or run another generic phone experiment. If static provenance remains unresolved, a narrowly bounded route-name attribution check with no credentials may eventually be more decisive than further non-specific pin tests.

No original game files, raw packet content, phone identifiers or private route literal committed.
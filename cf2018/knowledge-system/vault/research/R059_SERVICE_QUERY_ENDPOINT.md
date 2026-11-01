# R059 — GCloud name query vs resolved endpoint (original 2018 client)

Date: 2026-11-02. Target: original CF2018 fake server, original unmodified Apollo. Evidence **EXACT ORIGINAL-NATIVE STATIC** plus public source-only unit tests. No Android test, no server ACK or account/session, and no client modifications.

## Why this matters

R037/R039 **actual phone A/B** showed a response-correlated transition from a 133-byte QueryAddrSvr SYN to a distinct 131-byte SYN with a ten-byte named route. R057 proved two original callers of AddressService::GetServiceAddress; R058 found the original GCloud connector-to-name-service observer registration. R059 identifies what the original GCloud TGCP name-service path does with a query **before** its network connection, and how the startup endpoint is held **separately** from the query key. This distinguishes server-address resolution from route-name selection.

## New, read-only original native trace

Owner-connected Drive original 5,243,704-byte libapollo.so, previously SHA256-verified at R057: `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`. Original executable Thumb BL scan in this turn, plus bounded exact instruction and vtable byte observations:

1. `GCloud::CTGcp::OnThreadProc` calls `GCloud::CTGcp::choosingNameService` at **0x3a5de6**, target **0x3a3c74**. Original direct BL target has **one** caller in the scanned executable sections.
2. `choosingNameService` loads its name-service pointer from `CTGcp+0x2e0` at **0x3a3c7e**. It loads a separate query string/pointer from **+0x2d8** at **0x3a3c96**, then calls the service's **virtual slot +8** at `0x3a3c9a`–`0x3a3c9c`. The concrete default name-service vtable at **0x4f5088** maps that slot to `CDefaultNameService::Query` (Thumb pointer 0x3a681d).
3. The same method then loads the service object again from `+0x2e0`, and dispatches **virtual slot +12** at `0x3a3ca4`–`0x3a3ca6`. The original vtable at **0x4f508c** maps that slot to `CDefaultNameService::Update` (0x3a66db).
4. R057's native direct caller scan confirmed `CDefaultNameService::Query` calls `AddressService::GetServiceAddress` at **0x3a6890**. Separately `RpcConnector::InitLbIpAddress` calls the same API at **0x3c334e**. Neither is evidence of which ran on the phone.
5. In the **returned-name endpoint lane**, `CTGcp::OnQueryNameResult` uses its own endpoint field **+0x2dc** (read at 0x3a61ae; R046 separately located selected endpoint assignment at 0x3a6194), and `CTGcp::OnThreadStart` loads `+0x2dc` at **0x3a4a7c** before calling `gcloud_tgcpapi_start` at **0x3a4a80**. This is a second distinct value, **not** the name-service query key at +0x2d8.
6. R046's separate native work identified `CTGcp::SetRouteInfo → gcloud_tgcpapi_set_route_info` storing named-route info on its transport handle, and its use by the outgoing SYN serializer. **The name-lookup key, resolved endpoint, and SYN route are separate concepts in this original implementation.** They might still share a string under specific runtime configuration; no such runtime equality or service identity has been proven.

All **16 new halfword pins**, **2 vtable pointers** and **4 direct BL sites** in this report were **compared in memory against the owner-connected original** this turn with zero mismatches. No published original bytes or private session data. This original-file read is separate from public CI.

## Reproducibility

- [R059 source-only original auditor](../../../experiments/r059_service_query_endpoint.py): verifies exact original file size/SHA, 4 direct callsites with original owning symbols, 16 instruction halfwords and 2 vtable pointers; emits only fixed evidence summaries, no payloads.
- [R059 tests](../../../tests/test_r059_service_query_endpoint.py): **10 synthetic public unit methods**, and **1 optional original-private source test** that is **SKIPPED** without the original private library.
- [GitHub Actions run 41347572660](https://github.com/despairarc000/temp/actions/runs/41347572660): **SUCCESS**, including source-only tests/knowledge validation. This does NOT mean an actual original-native function executed, let alone phone login.

## Decision and next falsifiable evidence

The immediate original GCloud address-name plumbing is now much more precisely understood: connector registers name service → thread process chooses/query/updates it → callback supplies endpoint used by transport startup. **Do not infer the ten-byte alternate named route from an endpoint or a guessed name length.** In particular, the original route configuration was applied separately through SetRouteInfo; it is not yet linked to the actual R037 phone event.

The next high-value fake-server gate is to **discriminate which stack generated the alternate SYN (GCloud/NApollo/RpcConnector) and determine the correct next-service 0x1002 ACK/session/key contract** using original source. R042/R045 original receiver shows that correct ACK type alone is insufficient. No speculative 63-byte first-service ACK replay, no APK patch, no redundant phone negative-control run. Do not integrate a new server reply until original-receiver accept predicates and a bounded negative-control plan are supported.

**Status: R059 original static name/endpoint route separation verified; actual alternate service route and accepted ACK/session remain unresolved.**

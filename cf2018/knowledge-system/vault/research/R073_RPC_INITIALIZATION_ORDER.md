# R073 — RPC unit initialization precedes service lookup; CTDir ownership remains unproven

**Date:** 2026-11-02. **Goal:** original 2018 CF fake-server restoration, not APK modification. **Evidence:** native static caller graph independently scanned from the owner-connected original 5,243,704-byte `libapollo.so` and source-only CI. Original Apollo SHA-256 pin (from R057/R071/R072) is enforced by the new auditor: `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`. Neither a live client experiment nor native full-function emulation is claimed for R073.

## Why this matters beyond R072

R069's actual handset report documented one extra **same-length changed SYN field** alongside the 12→10-byte named-route change, with **zero next-service ACKs sent**. R070 mapped the relevant application fields: field4=gameID, field5=unitID, field6=clientType. R072 found that the original `RpcConnector::Init` can obtain a unit from a parsed service-domain string, and that `CTDir::Initialize` invokes the RPC connector and supplies a 10-byte route-name literal. It remains unproven that either was the source of the phone reconnect.

**R073's correction:** the unit-domain parsing happens **during `RpcConnector::Init`, before its own address-service lookup is initiated**. The **response arriving later** is *not* demonstrated to write the unit. A transition observed after a response can mean the client starts a connector with **previously initialized** different parameters, not necessarily parameters copied from response contents.

## Independently verified original call graph

These are **actual direct Thumb BL targets from the original native file**, with original function ownership checked; addresses are analysis landmarks, not packet values:

| Ordering in native source | Native original callsite | Actual destination |
|---|---|---|
| CTDir initializes its RPC client | **0x36f0e0** | `RpcConnector::Init` |
| RpcConnector Init checks domain syntax | **0x3c4622** | `AddressService::IsDomainName` |
| Same Init optionally parses service-domain components | **0x3c464c** | `AddressService::ParseDomainName` |
| Same Init initiates LB address list lookup | **0x3c474c** | `RpcConnector::InitLbIpAddress` |
| LB initializer invokes service address API | **0x3c334e** | `AddressService::GetServiceAddress` |
| Later RPC Update can create connection | **0x3c52b4**, **0x3c5372** | `RpcConnector::CreateConnection` |
| CreateConnection performs load-balancer selection | **0x3c505a** | `RpcConnector::LBSelect` |

Additional real source producers: version service at **0x32fc74** and puffer URL at **0x36175e** also call `RpcConnector::Init`. `AddressService::GetServiceAddress` has another **separate** direct caller, `CDefaultNameService::Query` at **0x3a6890**. The original `ParseDomainName` is also invoked from `AddressService::ProcessRequest` at **0x39adfe**, and `IsDomainName` is also invoked from address request/response functions. Thus a lookup alone cannot identify the connector.

**14 original direct callsites across seven watched functions** were independently matched on the privately retrieved ELF this turn. The new static auditor checks *exact* caller sets and original symbol owners; `verify_init_order` checks that the three relevant source sites are in the same original `RpcConnector::Init` function and ordered domain-check → domain-parse → LB lookup. This proves source order, not dynamic branch execution or which callback fired on Android. Note that `RpcConnector::Update` is separately called directly by version/puffer clients; **no direct CTDir Update edge was found** in this scan. That does not rule out indirect/virtual scheduling or CTDir runtime usage.

## Important limits

- R072's unit1→unit3 native emulation was with **synthetic domain input and C++ string/number stubs**. It can reproduce a same-length **field5** change while retaining ACK-parser compatibility in the bounded configuration.
- R071's selector2 allows a same-length **field6** change, but R072 showed the examined RPC CreateConnection sets selector0, so selector2 does not come from that specific examined path.
- The 10-byte **CTDir** route literal is a real original-code string of matching length, **not identified** as the 10-byte route observed on the handset. CTDir is a **directory-service client**, not proof of a lobby/authenticated game server.
- Neither `RpcConnector::Init` nor `OnGetServiceAddress` has been observed on the actual handset after the R037 reply in this run. The initial address response's content has **not** been proved to select the unit.
- No new ACK sent, authentication, lobby, match or gameplay. The previously reported 2/7 functional protocol milestones do not change.

## Verification and next discriminating experiment

- [R073 exact-source auditor](../../../experiments/r073_rpc_initialization_order.py): size/SHA-pinned, read-only, checks **14 direct callsites, seven target functions, original owning function names and source-site order**. No packets, service domains, private routes, client data or original native bytes emitted.
- [R073 tests](../../../tests/test_r073_rpc_initialization_order.py): **11 source-only negative/positive tests pass**, including altered/missing/synthetic CTDir→RPC, RPC→lookup, Update→CreateConnection and site-order controls. One private-original test is **skipped** in public CI.
- [GitHub Actions run 41366556022](https://github.com/despairarc000/temp/actions/runs/41366556022): **SUCCESS**. Public CI tests the validator and synthetic controls; original callsite read was separately performed from the owner-connected Drive ELF. Do not mistake this for full native runtime or phone acceptance.

**The shortest next path is already available:** run the *existing* sanitized `prepare_syn_difference.py` diagnostic on the actual phone, which **hard-disables** the second-service ACK and emits only changed field numbers/kinds. The expected report is `CF2018_SYN_DIFFERENCE_Result.txt`. Interpret:

| Actual changed SYN field | Consequence |
|---|---|
| **5 only** (plus route14) | Supports R072's unit field explanation; it does not prove CTDir ownership or response-driven mutation. |
| **6 only** | Supports examining client-type supplier; R072's specific selector0 RPC path cannot explain a 101→102 override. |
| **4 only** | Game-ID supplier or changed common-state path becomes relevant. |
| **1/2/3/7 or other field** | Different or security/account/state evidence. Reopen exact original native supplier, do not relax ACK gate. |
| No changed field except route | Recheck comparison/experiment state before any authorized ACK test; do not infer server acceptance. |

**Do not repeat the R069 one-ACK experiment**, which could not send a second ACK due context mismatch. Do not generate another APK, new speculated ACK or duplicate kit. No owner phone access is available in this runtime; no live diagnostic was executed.

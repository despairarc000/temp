# R046 — Original GCloud named-route setter and SYN writer

Date 2026-11-01. ORIGINAL_NATIVE_STATIC, not an observed phone call stack. 26/26 exact instruction pins and 9/9 focused unit tests including the private-original gate PASSED locally. No new phone test. No proven game login or gameplay.

## Why R046 matters

R045 traced the Unity ApolloLoginConnector through a **NApollo** connector. But this exact original library also contains a separate **GCloud** TGCP path. Equating R045's NApollo execution with the owner's GCloud-protocol 131-byte SYN was not proven. R046 directly identifies the GCloud transport's type-4 named-route writer and connects its setter to the outgoing SYN construction. The latter is relevant to the original phone's 131-byte SYN pattern, not proof the entire native call chain executed on that phone.

Original libapollo.so: 5,243,704 bytes; SHA256 4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8. Private original used read-only with LLVM Thumb disassembler. No game binaries, packets, route strings or credentials committed.

## Exact instruction findings

**GCloud::CTGcp::SetRouteInfo at 0x3a33a0:** route discriminator loaded at 0x3a33f2, type4 gate at 0x3a33fa, input string at 0x3a347e, AString::c_str call at 0x3a3482, 0x80 local buffer size at 0x3a3486; forwards to gcloud_tgcpapi_set_route_info at 0x3a34d0.

**gcloud_tgcpapi_set_route_info at 0x3a9d02:** type4 gate 0x3a9d1e; transport +0x3400 route area 0x3a9d22; maximum 0x7f name copy at 0x3a9d2a; route discriminator stored at 0x3a9d50. Thus the named-route value is stored on the GCloud transport handle BEFORE SYN construction.

**gcloud_tgcpapi_send_syn_msg at 0x3aba5c:** stored route kind read at 0x3abb80, type4 branch 0x3abb86, name source 0x3abba0, SYN route kind stored 0x3abba4, bounded name copy 0x3abbac–0x3abbb2. This is the native path from stored name-route config to outgoing SYN state. R037 phone evidence separately confirmed field14/nested union4/name1 with a 10-byte name after a correctly sequenced response; exact string UNKNOWN.

**GCloud::CTGcp::OnQueryNameResult at 0x3a60b4:** checks result status, copies IP collection at 0x3a60e4, selects first nonempty string and saves endpoint via 0x3a6194. The separate OnThreadStart at 0x3a4a04 loads stored endpoint [this+0x2dc] at 0x3a4a7c and calls gcloud_tgcpapi_start at 0x3a4a80. Do NOT conflate this callback with the distinct AddressService::Recv_QueryAddrInfo callback without a verified caller linkage.

**ACK:** gcloud_tgcpapi_recv_ack_msg at 0x3ac0b8 checks type0x1002 (0x3ac106), calls TGCPBody::unpackTLV (0x3ac1b6), then tests its status (0x3ac1ba). The ACK head itself has no named route (R042); that alone does not establish the old synthetic 63-byte ACK will pass another service's state/key checks.

## Reproducible verification

- [26-pin static original auditor](../../../experiments/native_gcloud_route_syn_audit.py); [9 focused tests](../../../tests/test_native_gcloud_route_syn_audit.py) and 26 per-pin mutation/missing cases.
- Original private hash gate 26/26 PASS; nine focused tests PASS with original provided. Public source-free tests skip the private binary gate.

## Open blocker / next

The caller that configures the observed 10-byte route, its actual name, the relevant managed-to-GCloud runtime bridge and the second-service ACK/session/key requirements remain unverified. R037 vs R038/R039 shows strong RPC64-dependent route-switch behavior, NOT a completed login. Continue tracing calls into GCloud::CTGcp::SetRouteInfo and the original ACK/session parser. Do not rerun R039, assume the NApollo and GCloud paths are identical, or blindly ACK the 131-byte SYN.
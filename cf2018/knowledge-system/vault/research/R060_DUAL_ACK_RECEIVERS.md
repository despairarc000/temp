# R060 — Distinct original 2018 Apollo ACK/auth receive pipelines

Date: 2026-11-02. **Primary lane: original-client fake server.** Evidence: **read-only original libapollo.so, static ARM Thumb executable-section direct-callscan** and public synthetic regression controls. No APK modification, game phone experiment, ACK transmitted, accepted login, lobby or bot match.

## Motivation

R037/R039 confirmed the original phone changed its SYN named-route pattern after a correctly correlated candidate `0x4013` reply. R057–R059 traced original GCloud service query/endpoint setup, but these are static paths and do not prove which stack owns the observed follow-up SYN. R042/R045 studied **GCloud** ACK `0x1002` receiver checks; those conclusions cannot simply be applied to every Apollo connector. R060 tests that specific risk.

## Original native receiver ownership

Same original 2018 ARM ELF: **5,243,704 bytes**, SHA256 **`4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`**, original file from owner-connected Drive; previous R057 fingerprint reproduced independently. Read-only exact original symbol table and direct Thumb BL scan now distinguish **two separate receiver families**:

| Stage | Legacy TGCP | GCloud TGCP |
|---|---|---|
| ACK receiver | `tgcpapi_recv_ack_msg` **0x1c195c** (788 bytes) | `gcloud_tgcpapi_recv_ack_msg` **0x3ac0b8** (316 bytes) |
| ACK call from synchronous connect | **0x1bad08**, `tgcpapi_start_connection` | **0x3a845a**, `gcloud_tgcpapi_start_connection` |
| ACK call from key-synchronization state | **0x1beb6a**, legacy `OnStateKeySyning` | **0x3a9fb0**, GCloud `OnStateKeySyning` |
| Auth-response receiver | `tgcpapi_recv_authrsp_msg` **0x1c1e34** (540 bytes) | `gcloud_tgcpapi_recv_authrsp_msg` **0x3ac306** (152 bytes) |
| Auth caller: connect / relay / auth state | **0x1badf0 / 0x1bb47e / 0x1bec68** | **0x3a850a / 0x3a8a5e / 0x3aa012** |
| Packet gather | Legacy gather **0x1c0c50** | GCloud gather **0x3ab5ec** |
| Gather consumers: done / receive-decrypt | **0x1bef10 / 0x1c17ca** | **0x3aa14c / 0x3abe4c** |

These are **14 independently matched original native direct-call sites across 6 receiver targets**, not packet captures. For each direct caller the method owner is verified against the original symbol table. The two receiver families have different actual code lengths and function owners; although they may share protocol ancestry or some compatible field types, **they are NOT assumed interchangeable**.

## Why that changes the next fake-server decision

The currently examined R042 `0x1002` acceptance, key modes, GCloud TGCPBody and timestamp-to-auth behavior are original GCloud-path findings. R037's later 131-byte SYN is a named route, but that does not independently establish whether the phone selected a GCloud connector or a legacy/NApollo connector. An ACK that reaches authentication in one original pipeline could fail a different receiver. This report does NOT assert that the two expect different ACK wire bytes; it establishes **different receiving functions and states** and demands an actual contract comparison.

Previously verified real-phone facts remain: first 133-byte SYN → 63-byte synthetic ACK → client auth `0x2001`, and correlated address-service reply → alternate 131-byte SYN. Neither phone fact is an accepted second-service ACK. The route's exact string, server endpoint/port in live phone state, encryption method, key response and accepted session remain unresolved.

## Code / controls

- [Exact-original gated callgraph auditor](../../../experiments/r060_dual_ack_receivers.py): verifies file size, SHA256, original ELF executable/symbol parser, **four ACK/auth function identities**, **14 direct Thumb BL callsites**, receiver owner labels and distinct gather functions. Read-only, fixed-label summary; no credentials, route strings, packet bytes or original game bytes in GitHub.
- [Source-only controls](../../../tests/test_r060_dual_ack_receivers.py): 11 public synthetic cases for receiver identity, distinct paths, wrong/missing original call owner, call graph mutations, altered source and original-only gating; **one optional private-original test SKIPPED in public CI**. Correct count is 11 source-free + 1 private-only test.
- Source-only CI can verify auditor/test logic but **does not read the original private ELF**. This turn separately examined the owner original native file and verified the 14 callsites/receiver function symbols. CI PASS once observed: [GitHub Actions 41348636553](https://github.com/despairarc000/temp/actions/runs/41348636553).

## Next discriminating test

1. Trace **which concrete GCloud/NApollo connector constructs the observed second SYN**, using original `CTGcp` startup and named-route serialization callsites. Be explicit that legacy `tgcpapi_*` vs `gcloud_tgcpapi_*` represent separate native recipient state.
2. Compare original ACK acceptance predicates across both functions: decoded envelope, header type, key response/mode, timestamp, body, auth send, state transitions and error propagation. Develop a bounded native receiver matrix with source checks; no guessed credentials, key or arbitrary ACK bytes.
3. Only after native contract and a two-connection negative-control test can an alternate-route handler be integrated into owner-private Termux fake server; no automatic phone traffic.

**Result: two distinct ACK/auth/gather receive pipelines established. Next-service receiver ownership and full accepted handshake remain UNKNOWN.**
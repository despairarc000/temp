# R061 — Original ACK/auth body decoder fork: legacy vs GCloud

**2026-11-02; fake-server primary lane.** Original 2018 private Apollo static evidence + independent public synthetic tests. No APK edits, phone run, real ACK written, accepted session, lobby or bots.

## Source and why this is more than named-route classification

Original 2018 `app/lib/armeabi-v7a/libapollo.so` from owner-connected Google Drive, **5,243,704 bytes**, previously SHA256-pinned by R057 as `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`. Binary privately read again in this run, exact-size and ELF-original code inspected in memory. Original bytes, routes, accounts and packets remain uncommitted.

R060 showed separate SYN senders and ACK/auth receivers for legacy `tgcpapi_*` and `gcloud_tgcpapi_*`. **R061 establishes the downstream decoder split:**

| Original native path | Legacy / NApollo | GCloud |
|---|---|---|
| ACK receive | `tgcpapi_recv_ack_msg` at `0x1c195c` calls at **`0x1c1b90`** | `gcloud_tgcpapi_recv_ack_msg` at `0x3ac0b8` calls at **`0x3ac1b6`** |
| Auth response | `tgcpapi_recv_authrsp_msg` at `0x1c1e34` calls at **`0x1c1f1e`** | `gcloud_tgcpapi_recv_authrsp_msg` at `0x3ac306` calls at **`0x3ac366`** |
| Body decoder called | **`gcp::TGCPBody::unpack`** at `0x1f9f6a` | **`gcloud_gcp::TGCPBody::unpackTLV`** at `0x3b8860` |
| Immediately lower decoder | `gcp::TGCPBody::unpack(TdrReadBuf)` at `0x1f9e78` via **`0x1f9f86`** | Marker/length reader; varint `0x3b8488` via **`0x3b88c0`**, no-varint `0x3b8674` via **`0x3b88c6`** |

Both ACK and auth receivers preserve their respective class namespace. GCloud decoder explicitly calls `TdrReadBuf::readUInt8` at `0x3b888e`, tests `0xAA` and `0x99` at `0x3b8896` / `0x3b889a`, branches to rejection for neither at `0x3b889c`, then calls `readUInt32` at `0x3b88a6` before the versioned TLV unpack. This matches the independently reviewed GCloud native auth response-body failure in [AUTH_RECEIVER](AUTH_RECEIVER.md) (unwrapped `A5` rejected, wrapped `AA` fixture parsed with further limits).

**Critical caution:** the legacy wrapper delegates directly to a different `gcp::TGCPBody::unpack(TdrReadBuf)` method, but its accepted entire wire envelope and outer gather behavior have **not been fully established here**. The result **does NOT prove that the same wire bytes cannot work in both**, nor that a legacy reply can omit all framing. GCloud's AA/99 body gate cannot be blindly transplanted to the legacy receiver.

## Checks and reproduce

[Source-only auditor](../../../experiments/r061_ack_body_decoder_fork.py) requires pinned original Apollo size/SHA and checks five decoder function identities, nine **required** original direct callsites (without denying other real shared-helper callers), and fourteen native halfwords. The 9 native call destinations and 14 instruction pins were independently compared against the private owner-original bytes in this run: **9/9 and 14/14 MATCH**, no raw original data emitted. SHA pin lives in the auditor; this in-memory read independently confirmed size and instruction data, not a second independent SHA calculation.

[Regression tests](../../../tests/test_r061_ack_body_decoder_fork.py): **12 public synthetic tests PASS; 1 private original test SKIPPED in public CI**. Negative tests mutate decoder callsites, owning function, original identity, and GCloud marker. The first public CI run exposed that a broken escaped-newline comment had disabled validator iteration; it had two FAILED negative tests. This was corrected in commit `d85c46faeb75295a0c674707eefaf2facdba652a`. [Corrected GitHub Actions run 41350373758](https://github.com/despairarc000/temp/actions/runs/41350373758) **SUCCESS**; 491 total canonical tests, 126 skips across the full repository (private-source tests skipped without original). Do not cite the failed first run as success.

## Decision and remaining falsifiable gates

1. **Receiver ownership:** [R045 managed-to-NApollo evidence](R045_MANAGED_NATIVE_ROUTE_ORIGIN.md) shows the game's managed `ApolloLoginConnector.DoConnect` creates a NApollo connector, while R046–R059 trace a separate GCloud name-service and SYN path. Neither has been definitively assigned to the actual *post-R037* 131-byte SYN. The new body decoders provide a concrete discriminator only once packet producer/receiver path is pinned.
2. **ACK contract comparison:** for each concrete stack separately, identify its original packet gathering, base header type `0x1002`, key-mode / key-response, nonce/timestamp, body format, then auth/session and Bingo handoff. Treat legacy and GCloud as separate predicates. Do not replay 63-byte QueryAddrSvr ACK or treat parsed body as validated identity.
3. **Runtime gate:** The user-owned v3.8 Termux source/bridge has not been reopened and no new phone response was tested in this run. Actual next accepted-service reply, login/lobby, TDM/Bomb bots remain **NOT VERIFIED**.

**R061 result: a native, source-backed reason to stop treating all Apollo ACK paths as one generic protocol receiver. Source understanding advanced, real-world gameplay milestone count unchanged.**
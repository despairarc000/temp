# Evidence registry — initial historical import (2026-10-30)

Historical results described here come from the user's Termux runs and TXT reports, plus native static review described in the conversation. Reports/hashes and original binaries are **not** checked into this public repo; verify them before stronger claims.

| ID | Class | Evidence | Supports / limits |
|---|---|---|---|
| E-01 | ON_PHONE | PCAPdroid older connection capture | Failed TCP to 45.113.69.32, 211.159.211.105, 119.28.34.12 on 8080/8085; `cfm-na-conf.cfmna-tencent.com` NXDOMAIN |
| E-02 | ON_PHONE | `CF2018_Redirect_Test_Report.txt` | 53 observed TCP connections, 32 diverted, each 133 client bytes |
| E-03 | ON_PHONE + ANALYSIS | `CF2018_Real_Request_Bytes.txt` | 32 payloads have single SHA-256 `3b91f9be6acde7e6f0be56970bc2c7f6d6d4ba8d5fd8392d4536fa0edb85f9dd`; route `QueryAddrSvr` |
| E-04 | ON_PHONE | `CF2018_TGCP_v03_Report.txt` | 33 SYNs, 17 on 8085/16 on 8080, 0 replies |
| E-05 | ON_PHONE | `CF2018_TGCP_v04_ACK_Result.txt` | Synthetic 65-byte ACK sent; peer closes; report accumulates older sessions and reuses port-local IDs, counts unreliable |
| E-06 | ON_PHONE | `CF2018_TGCP_v05_AB_Report.txt` | 8 passive/8 ACK controlled; passive median ~7003 ms, ACK median ~11 ms, no client follow-up |
| E-07 | ON_PHONE LOGCAT | `CF2018_TGCP_v06_Native_Log_Report.txt` | Apollo initialization + traffic; no reliable TGCP reject diagnosis; too-broad log filter matched unrelated touch `0x1002` |
| E-08 | HISTORICAL_NATIVE_STATIC + REPORTED_LOCAL_TEST | `CF2018_TGCP_v07_Audit.txt` | Client TX 43 66 prefix, syntactic candidate ACK fields, no verified server handshake |
| E-09 | HISTORICAL_NATIVE_STATIC + REPORTED_LOCAL_TEST | v0.8 FrameGate package | Native incoming 16-bit marker test consistent with 66 43; server acceptance **not** proven |
| E-10 | ON_PHONE | signed-only vs edited DLL controls and `CF2018_XAPK_Comparison_Report.txt` | identical original payload except modified managed DLL; modified DLL early-exits, cause such as integrity not yet proven |

## Coordinator-reviewed evidence — 2026-10-30

| ID | Class | Evidence | Supports / limits |
|---|---|---|---|
| E-11 | SOURCE_AUDIT + LOCAL_TEST_ONLY | [CF18-01 result](../../coordination/incoming/CF18-01/RESULT.md); eight audit tests rerun | The Python helper accepts only the modeled prefix and ignores suffix/size/stream state. Does not verify native RX or ACK acceptance. |
| E-12 | CONNECTED_DRIVE_METADATA + DIRECTORY_LISTING | [CF18-04 result](../../coordination/incoming/CF18-04/RESULT.md) | Known folder hierarchy accessible; Data sample capped at 100. Search failed a known-file control, so absence claims are unsupported. No target hash/version/native library verified. |
| E-13 | ORIGINAL_CODE + LOCAL_TEST_ONLY | [Passive relay research](research/RELAY.md), original core and 19 relay tests | Both observed EOF directions, half-close, byte preservation, error/timeout/local-stop attribution and bounds tested locally. No historical source audit, SOCKS5/device compatibility or Q-02 resolution. |

E-08/E-09 are imported historical native-review summaries without an independently
verified library fingerprint/address trace here. Do not promote them using E-11
or treat serializer syntax as receiver acceptance.

## Grounded known strings
TGCP variants: client SYN 0x1001, ACK 0x1002. Route name `QueryAddrSvr`. Related native symbols: `tgcpapi_encrypt_and_send_pkg`, `tgcpapi_gather_and_split_entire_pkg`, `gcloud_tgcpapi_recv_ack_msg`, `TGCPHead::packTLV`, `TGCPAckHead::packTLVWithVarint`. Native address service `QueryAddrSvrClient::QueryAddrInfo` is **later** than the current handshake; no authenticated session established.

## Provenance & limits
Source locations to re-open with authorized Drive access: [Drive manifest](../../sources/DRIVE_MANIFEST.md). Do not treat static symbol names, a parser's own unit tests, or locally synthesized replies as official-server capture. Treat v0.8 inference as testable, not accepted.

## E-14 — bounded SOCKS5 handoff, 2026-10-30

Class: ORIGINAL_CODE + LOCAL_TEST_ONLY. Source:
[CF18-03 result](../../coordination/incoming/CF18-03/RESULT.md), submitted in
`9f77b2cbf9f0249b566c75e8a4e42666cb44c292`; canonical
[implementation](../../experiments/socks5_handoff.py) and
[tests](../../tests/test_socks5_handoff.py).

Twenty-three canonical handoff tests passed, including a real localhost
fragmentation/pipelining handoff and a synthetic canonical-core attachment.
The full canonical suite passed 52 tests. This establishes the bounded stage's
parsing, scope, ownership, limits and metadata behavior only. No actual upstream
connection, deployed passthrough interface, device compatibility, historical EOF
cause, TGCP ACK acceptance or original native validation was demonstrated.
Q-02 remains UNKNOWN and G2 BLOCKED.

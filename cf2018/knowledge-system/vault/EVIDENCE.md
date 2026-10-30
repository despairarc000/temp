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
| E-09 | HISTORICAL_NATIVE_STATIC + REPORTED_LOCAL_TEST | v0.8 FrameGate package | Imported raw 66 43 inference; superseded for the pinned mirror path by E-16; no phone acceptance |
| E-10 | ON_PHONE | signed-only vs edited DLL controls and `CF2018_XAPK_Comparison_Report.txt` | identical original payload except modified managed DLL; modified DLL early-exits, cause such as integrity not yet proven |

## Coordinator-reviewed evidence — 2026-10-30

| ID | Class | Evidence | Supports / limits |
|---|---|---|---|
| E-11 | SOURCE_AUDIT + LOCAL_TEST_ONLY | [CF18-01 result](../../coordination/incoming/CF18-01/RESULT.md); eight audit tests rerun | The Python helper accepts only the modeled prefix and ignores suffix/size/stream state. Does not verify native RX or ACK acceptance. |
| E-12 | CONNECTED_DRIVE_METADATA + DIRECTORY_LISTING | [CF18-04 result](../../coordination/incoming/CF18-04/RESULT.md) | Known folder hierarchy accessible; Data sample capped at 100. Search failed a known-file control, so absence claims are unsupported. No target hash/version/native library verified in that Drive inventory; see separate mirror E-15. |
| E-13 | ORIGINAL_CODE + LOCAL_TEST_ONLY | [Passive relay research](research/RELAY.md), original core and 19 relay tests | Both observed EOF directions, half-close, byte preservation, error/timeout/local-stop attribution and bounds tested locally. No historical source audit, SOCKS5/device compatibility or Q-02 resolution. |

E-08/E-09 are imported historical native-review summaries without an independently
verified library fingerprint/address trace in the historical import. E-16/E-17
are independently sourced mirror evidence, not retrospective validation of those
reports. Do not treat serializer syntax as receiver acceptance.

## Grounded known strings
TGCP variants: client SYN 0x1001, ACK 0x1002. Route name `QueryAddrSvr`. Related native symbols: `tgcpapi_encrypt_and_send_pkg`, `tgcpapi_gather_and_split_entire_pkg`, `gcloud_tgcpapi_recv_ack_msg`, `TGCPHead::packTLV`, `TGCPAckHead::packTLVWithVarint`. Native address service `QueryAddrSvrClient::QueryAddrInfo` is **later** than the current handshake; no authenticated session established.

## Provenance & limits
Source locations to re-open with authorized Drive access: [Drive manifest](../../sources/DRIVE_MANIFEST.md). Do not treat static symbol names, a parser's own unit tests, or locally synthesized replies as official-server capture. The v0.8 raw-prefix premise is retired for the E-16 mirror path; phone equality
and runtime selection remain unverified.

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


## E-15 to E-18 — coordinator-reviewed recovered mirror

Reviewed at c52243228e8d2d38dd6b4c1d85f464d9f94461f8. Source receipt:
[canonical provenance](../../sources/SOURCE_PROVENANCE.md) and
[MIRROR_RECEIPT](../../sources/MIRROR_RECEIPT.json).

| ID | Class | Actual source / conclusion / limit |
|---|---|---|
| E-15 | MIRROR_SOURCE_PROVENANCE + INTERNAL_V1_SIGNATURE_VERIFICATION | [CF18-04](../../coordination/incoming/CF18-04/SOURCE_RESULT.md), c52243228e8d2d38dd6b4c1d85f464d9f94461f8. Exact v1.0.11.11 package, native/managed member hashes, ARM ELF identity and 1212 signed-entry digests rechecked. External certificate trust, full XAPK/OBB and phone equality unverified. |
| E-16 | ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS | [CF18-01](../../coordination/incoming/CF18-01/NATIVE_RX_RESULT.md), fefd0dc224851fefc2b74a51fc95e0fa0090e9a2. Pinned GCloud RX compares decoded marker 0x4366 after AA/99 TLV; raw prefix orders fail. TX prepends 43 66 independently. 32 lane tests rerun; nine execute native splitter/decoder controls with explicit stubs. No phone runtime/path claim. |
| E-17 | ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS | [CF18-02](../../coordination/incoming/CF18-02/RESULT.md), 56db53d81326810d5bea342b11ea4e07dc351e01. ACK selector/type, key-mode/body branches, error side effects and state/auth boundary traced; 25 controls rerun. Mode-0 empty-stage return does not establish later crypto/session; server field generation remains unknown. No accepted server ACK. |
| E-18 | ORIGINAL_CODE + LOCAL_SYNTHETIC / PRIVATE_SOURCE_VERIFICATION | Canonical [framing](../../experiments/rx_envelope.py), [17 tests](../../tests/test_rx_envelope.py), [source verifier](../../tools/verify_private_source.py), [14 controls](../../tests/test_verify_private_source.py). 83 canonical tests passed with private APK selected. Strict subset policies and signature checks do not establish full native receiver parity or G2. |

[CF18-G2-ACK-01](research/ACK_RECEIVER.md) combines the ordered receiver trace,
explicit emulation boundaries and remaining body/session/runtime/relay gates.
No original binary, capture, game key or raw disassembly is published. No new
phone packet or device experiment was obtained; Q-02 and G2 remain blocked.

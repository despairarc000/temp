# CF2018 v1.0 — actual on-phone authentication request after AA_DIRECT

**2026-10-30 — CF18-05 evidence packet, ready for CF18-00 review.**
User-uploaded, privacy-redacted report: `CF2018_v10_Followup_Structure.txt`.
Evidence: REAL_CLIENT_PHONE_REPORT + LIMITED_PROTOCOL_STRUCTURE. No original payload bytes or account/token values copied.

## Reproduced observations

2 sessions; both `deadline_after_followup` (~8019.96 and ~8084.93 ms), each had 250 client bytes = 133 SYN + 117 follow-up. Both received one 63-byte experimental AA_DIRECT ACK; then a 117-byte frame at 7.28/7.94 ms after ACK. Follow-up header length 42, body length 73. Both follow-up frame SHA-256 exactly `5b71ff58c86e96d6e9d4d961b7d4fcd04613e2061b5f1b74e60653967e61ae75`, body digest `eb040cb5895e2e11d8effa911998d24338bfe89a7fd38c3cdd72ccd7467a2ccb`. No further client protocol packet during the 8-second observation.

**Key decoder bug discovered:** report prints `ext_type=[]` because v1.0 Python `inspect_client_frame` filters `extension_types` to `f.kind == 5`. Actual v1.0 report separately records extension field pair `[8193, 1]`. Number 8193 decimal equals `0x2001`, and **kind 1 is a valid scalar selector observed in the real request**. Therefore this IS an observed `0x2001` extension selector; the empty display is a reporting error, not missing extension. Native GCloud `TGCPExtHead::packTLVWithVarint` has explicit branch for `0x2001`; existing native session analysis identifies the subsequent `0x2002` auth response receiver. The report's field pairs are kind-0 for base fields 1-5 and 7-9, kind-1 for base field6; this is **client TX**, not the server's incoming AA header. Do not apply the inbound strict kind-1 policy to captured outbound client format.

**Status:** G2 advanced to `CLIENT_SENT_AUTH_REQUEST`. The server HAS NOT sent a valid auth response; no authentication/account, Bingo completion, AddressService, config update, lobby, or offline match was observed. The socket remaining under observation for ~8 seconds is NOT proof of an authenticated state.

## Exact next engineering packet

1. CF18-00: update canonical CHECKPOINT, EVIDENCE, OPEN_QUESTIONS and acceptance to mark verified `0x2001` client-request *only* and retire outdated 'no post-ACK client packet' descriptions. Preserve user report hashes/times.
2. CF18-02: trace native `gcloud_gcp::TGCPAuthRspBody::packTLVWithVarint` at 0x3b374e, `unpackTLVWithVarint` 0x3b39c0 and receiver `gcloud_tgcpapi_recv_auth_msg` ~0x3ac306. Determine exact synthetic `0x2002` header extension, body account/status/strings, stage checks and any authentic account binding. Existing receiver state-4 and account-copy controls are not acceptance proof.
3. Produce a structural `0x2002` encoder with narrow synthetic tests, no real credential copying, no client side effects, and no auto-phone deployment. Test against the private pinned native decoder if possible, noting all stubs. Do not call it authenticated until real subsequent client traffic or game progress is demonstrated.
4. Relay worker: preserve direction/EOF metadata and session state; confirm old SOCKS5 external passthrough still scopes to known endpoints.

**Privacy:** Do not add authentic 73-byte auth body, raw PCAP, account/token/UID contents to public GitHub; only this structural metadata and hashes.

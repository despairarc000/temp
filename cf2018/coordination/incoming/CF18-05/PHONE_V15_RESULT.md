# CF18-05 — v1.5 phone outcome: synthetic Bingo triggers authentic client 0x4013

**2026-10-31 / source: user-uploaded `CF2018_v15_Bingo_Stage_Result.txt`**. File SHA256 `48cd8dff64c63c8e3c9b1c57a5f91f29f10ed0c0eb08b091559497a27b62eb60`. User confirmed the local phone experiment by uploading the metadata-only report. **ON-PHONE OBSERVATION**, **NOT authenticated login**. CF18-00 canonical integration requested; this handoff is not a direct canonical edit.

## Experimental comparison (2 trials per arm)

All six sessions: exact 133-byte client SYN, established 63-byte AA_DIRECT ACK, actual 117-byte `0x2001` auth request with SHA256 `5b71ff58c86e96d6e9d4d961b7d4fcd04613e2061b5f1b74e60653967e61ae75`, followed by the same *synthetic* 54-byte correctly enveloped `0x2002` reply.

| Arm | Sessions | Additional server stage | Client frames | Outcome |
|---|---|---|---|---|
| CORRECTED_ONLY | #1/#4 | none | 2 / 2 | no later frames; ~8052ms listener deadline in #1 and local EOF at ~6824ms in #4 |
| CORRECTED_WAIT | #2/#5 | 60-byte `0x3002` WAIT after 150.61/151.79 ms | 2 / 2 | EOF ~216.13/182.41 ms after auth reply; no further client data |
| CORRECTED_BINGO_SYNTHETIC | #3/#6 | 91-byte `0x6002` Bingo after 150.74/150.66 ms | **3 / 3** | **authentic new `0x4013` client message** 23.46/15.39 ms after Bingo, then listener deadline #3 / later EOF #6 |

The two post-Bingo client messages are 161 and 166 bytes with respectively SHA256 `f7005b63673007f8cfb720a7fddde57053d047afa62c80878993333d52d7e829` and `954521030d57d7e8255bfd5fb77ea17d96d6683cb757a83063fe963f204dc2fe`. Their lengths/hashes differ, and payload/account/UID/seq/credentials were never persisted. **Never call this a QueryAddrInfo request solely from the type `0x4013`.**

## Independent original native explanation for 0x4013 (reviewed here)

Private actual `libapollo.so` 5,243,704 bytes, SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`. Thumb disassembly using `llvm-objdump -d --arch-name=thumb --start-address=0x3a930e --stop-address=0x3a9398 <private lib>`, no emulator or Android hook used:

- `gcloud_tgcpapi_send_with_route` at 0x3a91ec first has a route/session eligibility branch. At **0x3a9318–0x3a931e** it reads handle offset `+0x6c8` and requires numeric state **5** in this examined branch.
- At **0x3a9372–0x3a937c**, a Thumb MOVW encodes `0x4366` and stores it as the base marker in the outgoing packet header `head+0x20`.
- At **0x3a9390–0x3a9396**, Thumb MOVW encoding bytes `44 f2 13 02` represent **0x4013** and `strh r2,[r7,#0x26]` writes it into the same outgoing header. This exactly matches the client's observed extension type `0x4013`.
- The `gcloud_tgcpapi_send_with_route` name, caller-visible arguments and state5 gate support that **`0x4013` is a post-Bingo *routed client data frame***, not itself evidence of a named AddressService method or proof of authenticated account. A separate service RPC may be carried in its data body; the present phone report contains only opaque-frame metadata and cannot identify it.

**Evidence classes:** frame type/size/timing = real device metadata; outbound `0x4013` header creation and state5 branch = pinned original native STATIC; actual executed ARM branch on Android and contents/meaning of the body = unobserved. It is plausible but not proven that the specific observed phone frames came through this exact method; do not equate native code paths with a traced call stack.

## Next bounded gate (no immediate broad payload sweep)

1. Preserve successful SYN→ACK→`0x2001`→corrected `0x2002`→synthetic `0x6002` sequence as a **laboratory-only working progression**, not valid login or general identity policy.
2. Investigate `0x4013` GCloud routed-data envelope and its body, particularly whether it contains a Thrift `QueryAddrInfo` method or another RPC. First trace call chain of `AddressService::Send_QueryAddrInfo` and `gcloud_tgcpapi_send_with_route` using original native code, and locate the outer-to-inner RPC framing; do not assume from name/length alone.
3. If further phone evidence is needed, propose an opt-in, bounded **metadata-only** v1.6 probe that captures *only* structural discriminator (header extension kind, body wrapper/magic, recognized method name allowlist if unencrypted) and perhaps next target connection event. Do not persist original auth/account/session body or raw client payload, and don't publish copyrighted wire bytes.
4. Avoid testing guessed account IDs, relay identities or sequence echoes; identity `CF18LAB-RELAY-01`, server ID1/session ID1 in v1.5 were synthetic.
5. CF18-00 should reconcile CHECKPOINT/EVIDENCE/OPEN_QUESTIONS and stop claiming 'no post-Bingo packet'. Schedules remain paused, original client assets unchanged.

**G2 status: real client post-Bingo TX `0x4013` confirmed in 2/2 synthetic Bingo trials. Session/account legitimacy, AddressService response, updates, lobby and bots remain unverified.**

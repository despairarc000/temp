# R040 — R039 live wrong-RPC64 control and native 0x5001 identification

2026-11-01. Evidence classes: **PHONE_OBSERVED** (owner uploaded sanitized CF2018_R039_RPC64_Negative_Result.txt), **ORIGINAL_NATIVE_STATIC** (exact 5,243,704-byte Apollo, SHA256 4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8), and **OFFLINE_CONTROL** (R039 single-byte mutation tests). Do not publish actual identifiers or packet captures. **Not playable; no authenticated account, login, lobby or match.**

## R039 phone result

Four sessions. Slot1 contained original 133-byte QueryAddrSvr SYN -> 117-byte auth 0x2001 -> original synthetic ACK63/auth54/Bingo91 -> original client qualified 161-byte 0x4013 routed address request. Local probe recorded **one 169-byte candidate sent**, R039_CONTROL: reply_sent=True, rpc64_intentionally_wrong=True, other_reply_bytes_same=True. The response is the same as R037 except **one bit of the 64-bit Thrift RPC sequence is flipped** at the application response's 8-byte session ID position.

**All four first frames were exact, unmodified 133-byte QueryAddrSvr SYNs** (`R035_FIRST class=REFERENCE_SYN`), with R036/R037 zero deltas and original named-route reference. No 131-byte shorter named-route follow-ups. All four sessions reached synthetic auth0x2001. Two client 0x4013 qualified requests were seen (161 bytes in slot1 and 166 bytes in slot3). Crucially, the negative control did not prevent a client from making the address request; it stopped the *previously repeatable different route* pattern.

Prior R033/R035/R036/R037 runs, with a correctly matching RPC64 response but same provisional framing/result, each observed 3 shorter 131-byte SYNs with name-route bytes two shorter, while R034 passive, R038 no-reply immediate-close and now R039 wrong-RPC64 produced original 133-byte SYNs. The controls make the **pending RPC64 match / callback** explanation markedly more credible than connection-close-only or arbitrary packet-receipt effects, but these are separate runs with synthetic ACK/auth/Bingo and not randomized. They do not establish end-to-end client parse/accept, authenticated session, or the identity of the post-reply ten-byte route. The R039 report has no native callback trace.

Source-only R039 writer `r039_wrong_rpc64.py` explicitly calls the valid response builder, verifies full original structure and exactly one altered response byte at the beginning of the 64-bit Thrift sequence (XOR 0x40). It verifies the method, frame, result/reason and contents are otherwise unchanged, and the parsed 64-bit sequence cannot equal the pending request ID. This is a good negative control, not a complete proof of client-side successful processing. R028 original native trace already pins pending QuerySession lookup by RPC64 before Recv_QueryAddrInfo.

## New 0x5001 observation

R039 slot2 additionally reported one 59-byte TGCP frame with extension type `0x5001`, header43/body14, ~11.53 s after preceding synthetic stage. Original hash-pinned Apollo native static analysis resolves **0x5001 to client-initiated stop-session construction**, not an address response or gameplay message:

- `gcloud_tgcpapi_stop_session` at 0x3a96c2 requires transport state5 (0x3a96e2), writes magic 0x4366 (0x3a96ea), sets packet/header type `0x5001` at 0x3a970a–0x3a970e, sets body type `0x5001` at 0x3a9724, packs `TGCPBody` at 0x3a9730, sends via `tgcpapi_encrypt_and_send_pkg` at 0x3a974e and then stores state6 at 0x3a9756.
- `gcloud::tgcpapi_inner::OnStateDone` at 0x3aa1a2–0x3aa1c2 recognizes `0x5002` and calls `tgcpapi_on_sstop_session`. This is a native **response-side stop-session handler**, not proof any `0x5002` occurred in the phone result.
- Original data strongly support interpreting the phone's `0x5001` as a stop-session protocol message. Static similarity alone does not demonstrate that exact callsite produced that one phone frame, why it was initiated or which peer sent FIN. No reason/excode inferred.

Locally **13/13 original native instruction pins PASS**, with **7/7 synthetic plus original-gated mutation tests PASS**. [Read-only audit](../../../experiments/native_stop_session_audit.py) and [tests](../../../tests/test_native_stop_session_audit.py) are source-only; original private library is not committed.

## Next work — avoid another speculative phone test

1. Trace the original **QuerySession pending lookup, parsed QueryAddrInfo result and higher-level consumer callback** following a correctly correlated response; distinguish the negative failure branch from the positive response branch.
2. Source-identify the **ten-byte named route** using original service definitions and original route-selection code without fabricating a route name or exposing live identities. It is not yet known.
3. Only then test a **route-specific SYN/ACK** if native protocol evidence supports it. The existing 63-byte ACK builder is tied to QueryAddrSvr, so do not blindly ACK unknown 131-byte SYNs. No more R039 phone repetition needed.

**Confidence:** high that matching RPC64 is associated with subsequent route switch; moderate that native pending-session processing is the direct mediator; no proof of login/complete response acceptance.

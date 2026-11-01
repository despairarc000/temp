# R034 — First live experimental 0x4013 reply: local send only; unknown 131-byte reconnects

**Date:** 2026-11-01. **Evidence:** owner-uploaded sanitized `CF2018_R033_OneReply_Result.txt` (27 lines). This is **PHONE_OBSERVED + ORIGINAL_R033_SOURCE_AUDIT**, not validated phone reply acceptance or authentic login. Do not copy raw phone payload or identifiers into GitHub.

## Live observation

- Four accepted local sessions, all port8085. First entered the exact reference `0x1001` SYN/auth/Bingo path: 133-byte reference first frame (induced by exact hash check), 117-byte auth0x2001 request, unchanged 63-byte ACK, 54-byte synthetic auth reply and 91-byte Bingo stage.
- First session then sent a real routed **0x4013**, frame161/body80, exact `QueryAddrSvr` route, independently verified TGCP sequence prefix and **`qualified_address_request=COMPLETE_STRUCTURAL_CANDIDATE`**.
- On that same local connection the probe reported **`R033_RESPONSE slot=1 status=r033_reply_sent length=169 reason=none`**. This means `socket.sendall()` completed and the local probe recorded one send. It does NOT establish the game consumed the response or that the remote end ACKed/accepted its application content.
- Session1 ended **`read_eof_after_route`** after ~299 ms total; the report contains no `R033_POST_REPLY` and no additional `LATER` client frames.
- Three immediately following sessions (slots2–4) each presented **one completely parsed 131-byte initial TGCP frame** and terminated with `unexpected_first_frame` in ~9 ms, before any ACK/auth/Bingo bytes were sent in those sessions. The saved report does **not** disclose their extension selector, base-field shape or similarity to the 133-byte golden first frame.
- Reader-reported EOF/half-close counts in the SOCKS relay cannot identify which peer initiated a TCP FIN. There is no corroborated lobby, accepted RPC, valid account, port transition, native response callback or playable match.

## Important R033 implementation limitation

Original source-only R033 preparer introduced a single claimed response into the passive V3.8 observer. It guards the **first frame** by both exact SHA256 of a known *133-byte* `golden_request.hex` and exactly `[[0x1001,5]]` extension shape. Any alternate *valid* initial TGCP frame (including 131 bytes) is labeled `unexpected_first_frame` and immediately closed **before** the probe records the extension type or body/header field shapes. `inspect_client_frame` parsed the 131-byte frames successfully: they are not proven malformed, and their meaning cannot be inferred from their length alone.

The same code records `R033_POST_REPLY` only on a *subsequent fully parsed client frame in the same session*. Hence the lack of the label is **absence of observed follow-up** on session1, not a verified client rejection or failure to read the reply. If the client reacted via a new connection, the old exact-golden guard prevented observing that connection's protocol type.

R026 earlier passive phone test had four valid auth requests and two routed 0x4013 requests; it was a different run, not a randomized concurrent control. Therefore **no causal conclusion** should be drawn that R033's 169-byte reply caused the 131-byte reconnects. A controlled no-reply run with fixed-label first-frame classification is the next discriminating experiment; do not repeatedly send unverified replies or vary multiple response fields at once.

## Next diagnostic

Prepare a passive **R034** (zero experimental 0x4013 replies) which logs only protocol extension type, header/body lengths, base/extension field *shapes*, and exact reference-SYN match for *every fully parsed first frame*, including mismatches. Do not record SHA hashes, raw request bytes, tokens, addresses, RPC sequences or identifying values. Compare R034 131-byte first frames with the R033 pattern; only if a stable, understood first-frame family emerges should an active reply A/B be reconsidered. Keep the original R026 and R033 sources unchanged.

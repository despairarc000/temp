# CF2018 v0.9 — confirmed client follow-up (user phone report, 2026-10-30)

**Evidence classification:** AUTHENTIC_ON_PHONE_CLIENT_TRAFFIC (limited metadata, user-uploaded TXT); no raw auth content committed.
**Report:** `CF2018_v09_Envelope_Result.txt` from the user's Termux on-phone 8-session test.

## Observations
| Arm | Count | Result | Per-session follow-up |
|---|---:|---|---|
| PASSIVE | 2 | both timeout at ~7 seconds | 0 |
| OLD_ACK | 2 | both read_eof at ~8.03/9.76ms after reply | 0 |
| **AA_DIRECT** | **2** | **both emitted client follow-up** | **117 bytes** |
| PREFIX43_66_AA | 2 | both read_eof at ~8.14/6.33ms after reply | 0 |

AA_DIRECT sends a synthetically constructed **63-byte AA frame** with its first-stage base fields encoded as kind 1. Both client follow-up frames started with **`43 66 aa 00 00 00 2a 15`** (observed first eight bytes), total follow-up size **117 bytes**, and the exact same SHA-256:

`5b71ff58c86e96d6e9d4d961b7d4fcd04613e2061b5f1b74e60653967e61ae75`.

The two AA_DIRECT sessions reported **250 total client bytes** each = initial 133-byte SYN + 117-byte follow-up; 63 bytes server reply each. Response-to-followup was approximately 6.04 and 11.87ms. At the time of this experiment the listener **exited the session at the first follow-up chunk**, so its EOF/longer session evolution is not observed.

## Interpretation
This is the **first real post-ACK client data** under a first-stage-corrected AA reply, a genuine G2 *progress signal* and falsifies the previous assertion that no client continuation is possible with any attempted candidate. It does **not** demonstrate: full receive-path parser parity, ACK acceptance as a session, authenticated account, valid key negotiation, actual auth response, lobby, or offline game.

Likely next type is TGCP auth request (hypothesis; the report captures only first 8 bytes, not enough to decode extension selector or body). The 0x2a header size can plausibly be 42 with 73 following bytes (117 total including two outer bytes), but body length must be confirmed from decoded base fields, not inferred from arithmetic alone.

v0.8's raw flipped-prefix premise remains retired. Prefix + AA failed in this test, while **AA_DIRECT** caused client continuation.

## Next reproducible test
v1.0 standalone Termux diagnostic prepared in the conversation, **not committed here** because its historical fixtures contain authentic protocol data. It repeats only the two successful AA_DIRECT sessions, keeps the socket alive up to 8 seconds, and parses header/base/extension field structure; shareable TXT includes only lengths, field numbers/kinds, extension union type, SHA-256 and subsequent EOF/deadline. No raw auth bytes are persisted; original APK/OBB unchanged.

**Coordinator action:** Update canonical checkpoint/evidence and G2 acceptance as **post-ACK client packet observed, full handshake/auth still BLOCKED**; review the new observation before designing next server reply. CF18-02 can trace a 0x2001 effective extension and auth request semantics if the new report confirms that type. CF18-03 can audit socket end and relay provenance. Never claim active session/login from this report.

## Source provenance
User directly uploaded `CF2018_v09_Envelope_Result.txt` in the conversation. No live packet contents (beyond the already reported eight-byte prefix), credentials, session tokens, APK/OBB or proprietary code published. Counts are reproduced from that report.

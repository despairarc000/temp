# CF2018 v1.1 on-phone result — synthetic 0x2002 ZERO_ACCOUNT rejected/closed

2026-10-30. **Evidence:** user-uploaded `CF2018_v11_Auth_Result.txt` (sanitized phone report). `cf2018/coordination/incoming/CF18-05` handoff, not canonical integration.

## Results (two trials per arm)
- **SILENCE** after authentic `0x2001`: sessions #1/#3; local diagnostic deadline after ~7022.6/7031.2 ms; client bytes 250 = 133 SYN + 117 auth, 2 client frames; no later data.
- **AUTH_ZERO_STUB**: sessions #2/#4; experimental server sends a 66-byte `0x2002` with empty account, zero scalar/strings, after earlier AA_DIRECT 63-byte ACK; local `read_eof` after 32.79/31.87 ms from session start; client bytes unchanged 250; no later frames.
- All four observed authentic 117-byte `0x2001`, header=42, body=73, same SHA256 `5b71ff58c86e96d6e9d4d961b7d4fcd04613e2061b5f1b74e60653967e61ae75`; observed after the AA_DIRECT response within 3.97–12.29 ms. No real auth/account/token data persisted.
- The report's `read_eof` only means the listener's recv returned empty; whether the app, SOCKS5 relay, or another layer initiated termination is unproven.

## Interpretation
AA_DIRECT reliably advances to client auth request `0x2001`. The **synthetic** empty-account response changes the observed connection lifecycle (early EOF rather than 7s wait), but does not cause any third client frame. The specific failure gate is **unknown**: outer framing, body parsing, dummy account semantics, session/state checks and relay behavior have not been separated. It is NOT a working authenticated session, login, or access to the game.

Native reference: [ACK_SESSION](../../../knowledge-system/vault/research/ACK_SESSION.md) describes a downstream receiver requiring effective extension type 0x2002, then body decoding/account copy and state 4; exact empty-account semantic validity was never proven. The v1.1 user ZIP `CF2018_TGCP_v1.1_Auth_Probe.zip` implements `native_auth_stub.py` with empty nested TSF4GAccount. Local tests were structural and loopback-only, not native full-auth acceptance.

## Next bounded investigation
Use the pinned Apollo library to compare actual TSF4GAccount serializer vs v1.1's empty-account body, and isolate whether a serializer-shaped *zeroed synthetic* account changes behavior versus the original empty nested account. Keep a pure-SILENCE baseline and a body-empty negative control; leave auth credentials and original game untouched. Record reply-to-EOF timing, per-arm frame counts, session state, and only SHA/structural metadata.

**Promote to G2 session accepted only after genuine later client packet and semantic evidence.** Coordinator should update canonical checkpoint/EVIDENCE and mark all four v1.1 trial outputs as observed, not inferred success.

# Diary — page013, current

Previous [page012 archive](diary/012.md): R081–R090. See [current state](vault/CURRENT.md).

## R091 — [FINDING] Original transport crypto executes successfully on synthetic controls (2026-11-02)

**ORIGINAL_NATIVE_EMULATION_WITH_STUBS; SYNTHETIC_ONLY inputs.** Rehashed original Apollo (5,243,704B; SHA `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`). Existing `native_control.NativeControl` executed actual set-key `0x3ab24a`: method0/empty succeeds, method4/empty returns−31, methods3/4 with synthetic16-byte key succeed, method2 returns−29. No setup stubs. Both resulting AES schedules decrypt the published FIPS197 Appendix C.1 AES128 vector via original `0x2833ac` correctly, without stubs.

Original encrypt/decrypt wrappers `0x3ab296/0x3ab31e` round-trip synthetic payloads1/16/33B under methods3/4 (cipher lengths16/32/48B); non-block-aligned inputs reject−33. **15 inline controls matched expectations**:5 setup,2 known-answer,6 round-trips,2 malformed-length. Only encryption randomness (`lrand48` PLT0x193e78→constant7), bounded libc and runner error boundaries substituted; AES/custom framing not stubbed. Fifth length-pointer argument supplied at original SP; no sockets, auth or game execution.

This adds working original-crypto controls, not full ACK or phone negotiation. **UNKNOWN:** actual next-service mode/key/state. NEXT exercise supplied-key ACK dispatch through real parsing/setup/body decoding with synthetic controls and suppressed auth send. Phone remains R077; no login/lobby/bots.

# Diary — page013, current

Previous [page012 archive](diary/012.md): R081–R090. See [current state](vault/CURRENT.md).

## R091 — [FINDING] Original transport crypto executes successfully on synthetic controls (2026-11-02)

**ORIGINAL_NATIVE_EMULATION_WITH_STUBS; SYNTHETIC_ONLY inputs.** Rehashed original Apollo (5,243,704B; SHA `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`). Existing `native_control.NativeControl` executed actual set-key `0x3ab24a`: method0/empty succeeds, method4/empty returns−31, methods3/4 with synthetic16-byte key succeed, method2 returns−29. No setup stubs. Both resulting AES schedules decrypt the published FIPS197 Appendix C.1 AES128 vector via original `0x2833ac` correctly, without stubs.

Original encrypt/decrypt wrappers `0x3ab296/0x3ab31e` round-trip synthetic payloads1/16/33B under methods3/4 (cipher lengths16/32/48B); non-block-aligned inputs reject−33. **15 inline controls matched expectations**:5 setup,2 known-answer,6 round-trips,2 malformed-length. Only encryption randomness (`lrand48` PLT0x193e78→constant7), bounded libc and runner error boundaries substituted; AES/custom framing not stubbed. Fifth length-pointer argument supplied at original SP; no sockets, auth or game execution.

This adds working original-crypto controls, not full ACK or phone negotiation. **UNKNOWN:** actual next-service mode/key/state. NEXT exercise supplied-key ACK dispatch through real parsing/setup/body decoding with synthetic controls and suppressed auth send. Phone remains R077; no login/lobby/bots.

## R092 — [FINDING] Full encrypted ACK path verified; optional directory one-ACK copy tested (2026-11-02)

**ORIGINAL_NATIVE_EMULATION_WITH_STUBS / SYNTHETIC_ONLY / LOOPBACK_ONLY.** Exact original Apollo enforced. New `native_ack_crypto_controls.py` executes real mode2 key parser/setup, AES/body decryption and ACK body parsing through suppressed auth-send, with synthetic10-byte route/unit3. Eight native methods/15 cases PASS; wrong-key/length/body/extension negatives and no-key later-decryption failure discriminate stages. No crypto/parser success stub, socket auth or phone run.

[Copy-only preparer](../cf2018/tools/prepare_directory_ack.py) SHA-verifies reconstructed original R077 handler, preserves cached63-byte ACK and original-route loader, admits only exact CTDir route plus same-width changed unit5/route14, requires explicit opt-in, prior address reply and locked one-attempt budget. It closes after observing one following frame, without second-service auth/Bingo. Local preparation PASS;113 original regressions,8 guard tests,5 lifecycle tests PASS;30 added checks completed (29 PASS/1 SKIP). Both local knowledge doctors PASS. [Proof/limits](../cf2018/knowledge-system/vault/research/DIRECTORY_ACK_OFFLINE_READINESS.md).

**UNKNOWN:** actual handset ACK acceptance/mode/session; phone remains R077. NEXT owner-controlled single-ACK observation. User says prepared R077 is in Android Download; script discovers a unique pinned folder there, refuses ambiguity. No repeated route-only test, new encrypted phone reply or client edits.

## R093 — [FINDING] Phone directory ACK prompts auth request; next auth/Bingo control verified (2026-11-02)

**PHONE_OBSERVED:** Owner DIRECTORY_ACK TXT SHA `e5e6a14e2f3abfbd79802f29a5f5a0b43bcac09e31a313d4a5eed7caed49f136`: slot2 exact CTDir route/changed unit5 received63B ACK, then0x2001/kind1 (`AUTH_REQUEST_OBSERVED`;117B inferred). Probe deliberately closed without auth/Bingo; slots3/4 held by consumed one-shot budget. This is real handshake continuation, not account authentication or a rejected auth reply.

**ORIGINAL_NATIVE_EMULATION_WITH_STUBS / SYNTHETIC_ONLY:** Existing54B auth alone reaches state4; plus existing91B Bingo reaches transport state5 with zero synthetic account. Bad body/truncation remain4. Four native methods PASS. [Next copy-only preparer](../cf2018/tools/prepare_directory_stage.py) verifies exact preceding source/helper, preserves all route/unit/security/prior-reply/one-shot gates, requires new explicit opt-in, reuses existing54/91 replies and stops after one following frame without answering it. Six lifecycle tests and113 original regressions PASS; both local knowledge doctors PASS. [Proof/limits](../cf2018/knowledge-system/vault/research/DIRECTORY_AUTH_STAGE_PHONE_RESULT.md).

**UNKNOWN:** actual directory auth/Bingo acceptance and subsequent operation. NEXT owner bounded stage test; no new directory reply, login/lobby/bots claim.

## R094 — [FINDING] Phone sends directory application frame;92-byte size does not identify method (2026-11-02)

**PHONE_OBSERVED:** DIRECTORY_STAGE TXT SHA `8ca511b14fbf77f6c36ad020bfb97fca30b33bf955d152ce6325e87064320809`: slot2 received63B ACK +54B auth/91B Bingo and emitted0x4013/kind5,171B frame/92B body. Probe intentionally closed without application reply; slots3/4 held by budget. This advances application traffic, not authenticated login/lobby/bots.

**ORIGINAL_NATIVE_EMULATION / SYNTHETIC_ONLY:** Rehashed original Apollo. Actual binary header and three directory pargs writers (`0x369c18/369e50/36a0d4`, original vtable) emit92B for all/by-id/by-ids with synthetic strings12/3/3 (legacy64),9/0/0 (strict64). Only bounded memory sink substituted;4B synthetic TGCP prefix added separately, complete sender not executed. Thus all three methods fit reported size; none identified on phone.

[Single-file identifier](../cf2018/tools/prepare_directory_identify.py) pins previous stage source/helper, preserves replies/gates/budget and exports only exact method/encoding/reason labels after route, packet-sequence, cipher/compression and full argument-shape checks. No directory response or raw capture.11 parser/frame/native methods,6 lifecycle methods and113 baseline tests PASS; both doctors PASS. [Proof/limits](../cf2018/knowledge-system/vault/research/DIRECTORY_REQUEST_IDENTIFICATION.md). NEXT owner bounded identifier run; method and pending response remain UNKNOWN.

# Directory-service one-ACK control — offline readiness

2026-11-02. R092. **Original-native emulation with stubs, independent synthetic inputs, and synthetic loopback only.** Phone evidence remains R077; no second-service ACK, account login, lobby or bot match observed here.

## Native result

Exact original Apollo SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8` and size5,243,704B enforced by existing NativeControl. New [control](../../../experiments/native_ack_crypto_controls.py) executes original SYN preparation with ten-byte synthetic name/unit3 (outgoing SYN send suppressed), transfers context to a fresh emulator, and executes original key-syn state `0x3a9f8c`. Supplied-key mode2, encryption methods3/4, real ACK extension parser, key setup `0x3ab24a`, AES schedule `0x2845fc`, body decrypt `0x3ab31e`, body parser `0x3b8860` and ACK component `0x3b49a6` reach suppressed auth-send sentinel−77. Neither crypto nor parser success is stubbed. State remains2 because auth-send is suppressed.

Wrong synthetic key or ciphertext length rejects−33 before body parsing. Malformed decrypted body rejects−18 (inner−32). Truncated key extension rejects−18 before key setup. Unsupported method2 rejects−29. Mode0/method4 with a plaintext body can reach auth-send yet a flagged encrypted body fails−31 without a key: ACK parsing alone does not establish subsequent cipher readiness. Explicit stubs: deterministic encryption lrand48, bounded libc, logging/error boundaries, no-new-data read, outgoing SYN and auth sends. No real credentials, phone frames or remote service used.

[Eight native test methods](../../../tests/test_native_ack_crypto_controls.py), 15 cases PASS with exact private original; all8 SKIP without explicit source. Existing three SYN/ACK handoff test methods PASS. These results do not identify the phone's negotiated mode or prove Android runtime execution.

## Optional owner experiment

[Single-file preparer](../../../tools/prepare_directory_ack.py) takes exact prepared R077 SHA `7cf88b9e011960f334d5eb1a627e04946e27dfae2a5e5bed568b1d449cc6410d`, verifies original SYN-parser SHA, and creates a separate output. It preserves the original first-stage reply and cached63-byte ACK. **No new supplied-key wire reply is deployed.** Existing original-Apollo loader/route comparison remains. Only when candidate131/reference133 have exact same encoded base, matching ordered fields, unchanged non-route fields except same-width varuint unit5, and named route byte-equal to original CTDir does the new guard qualify. Explicit `CF2018_DIRECTORY_ACK=YES` is additionally required; existing address-reply prerequisite and locked one-attempt budget remain. It observes one following frame then closes without next-service auth/Bingo. Default is no second ACK; four-session limit retained. Original APK/OBB and R077 source untouched.

Actual preparation from reconstructed SHA-verified R077 PASS. Original113 prepared-copy baseline tests PASS;30 added prepared-copy checks completed (29 PASS, one optional class SKIP);8 public guard/refusal tests PASS;5 new lifecycle tests PASS covering explicit opt-in, no prior address reply, changed security, one-shot exhaustion and follow-up classification. These are loopback tests, not phone acceptance. Both knowledge doctors PASS on the available local workspace; no remote CI result claimed.

Preparer searches Android Download for exactly one pinned prepared R077 folder if --source is omitted. --print-library reuses CF18_APOLLO_LIBRARY or finds the exact SHA-matching original in Download; missing/ambiguous inputs refuse. Owner report: `~/storage/downloads/CF2018_DIRECTORY_ACK_Result.txt`.

**Falsification:** AUTH_REQUEST_OBSERVED means a later0x2001 frame after ACK, not authenticated login. ACK_WRITTEN without such a frame does not establish acceptance. If no ACK was written, inspect the local gate; do not call that client rejection. No phone test has been run with this new copy.

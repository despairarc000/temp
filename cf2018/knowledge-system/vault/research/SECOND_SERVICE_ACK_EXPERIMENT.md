# One second-service ACK experiment

2026-11-01 UTC. Prepared and offline tested; **no phone run or authenticated login**. Uses the supplied pinned R037 chain, [exact non-route gate](SECOND_SERVICE_DISPATCH_PATCH.md) and [original native SYN/ACK controls](NATIVE_SYN_ACK_HANDOFF.md).

## Question and hard limits

Does the phone send an auth-request frame after the previously working63-byte ACK on its changed-route connection, **when every encoded non-route field matches the working reference**?

The additional ACK is disabled unless CF2018_SECOND_SERVICE_ACK=YES. Original R037 live opt-in is independently required at startup. The handler must see MATCH_EXCEPT_ROUTE after the earlier address reply was locally written. A lock-protected per-run budget permits one additional ACK attempt across all connections; claiming precedes the write, so a write failure cannot cause retries. Wrong context, no previous reply, disabled flag and exhausted budget remain HOLD_NO_ACK. The ACK is the same existing reference-stage buffer, not a guessed new serializer. No key/credential values are logged or synthesized for the next service.

After that ACK the next-service connection is observed only through its next complete frame or existing bounded EOF/deadline. Exact extension0x2001/kind1 yields AUTH_REQUEST_OBSERVED; other frames yield OTHER_FRAME_OBSERVED. The handler then closes without sending next-service auth/Bingo. A local ACK write is not acceptance. A phone auth request would establish transport progress, **not successful account login**. Missing follow-up/EOF does not identify the reason for failure.

Existing four-slot/12-second connection bounds, loopback service bindings and PCAPdroid SOCKS routing remain unchanged. Reference-stage ACK/auth/Bingo and the one correlated address reply retain their existing behavior. New run directory `~/cf2018_second_service_ack_runs/` and report `~/storage/downloads/CF2018_SECOND_SERVICE_ACK_Result.txt` preserve old R037 output. No new game/experiment version label is assigned.

## Offline validation

- 113 original regressions PASS on the prepared handler.
- 5 real-loopback lifecycle tests PASS: permitted ACK then observed auth request/no auth response; disabled; no previous address reply; changed security; other-frame labeling. Positive test confirms second ACK equals the first63-byte ACK, only one address reply, no second-service auth reply, and a third connection cannot reuse the ACK budget.
- 2 preparer refusal tests PASS. Unknown runtime source and unpinned original ZIP are rejected. All60 baseline hashes, supplied kit hash and exact generated handler hashes are checked through the preparer chain.
- Both knowledge doctors PASS. ZIP-input positive extraction is a convenience path guarded by the historical original ZIP hash; this runner's positive preparation used its exact60-file source directory. No original client binaries/captures are bundled.

## Owner-controlled Termux procedure

Use the new source-only kit, the existing original V3.8 probe source ZIP and existing PCAPdroid profile. This is a new one-variable ACK test, not a repeat HOLD-only capture. Stop previous probes with Ctrl+C and force-stop CrossFire before a phone run. PCAPdroid selects CrossFire and excludes Termux; same SOCKS5 127.0.0.1:1080 and scoped forward redirector as before. Do not broaden routing.

From Downloads:

```sh
unzip CF2018_second_service_ack_test.zip -d "$HOME/cf2018_second_service_ack_kit"
cd "$HOME/cf2018_second_service_ack_kit"
python cf2018/tools/prepare_second_service_ack.py --source-zip "$HOME/storage/downloads/CF2018_TGCP_v3.8_GCloud_DataHead_Flags.zip" --kit inputs/CF2018_R037_ROUTE_DELTA_Kit.zip --output cf2018/private/second_service_ack
cd cf2018/private/second_service_ack
bash START_SECOND_SERVICE_ACK.sh
```

The last command performs offline tests only. If the existing V3.8 source is already extracted, use `--source /absolute/path/to/that/folder` instead of `--source-zip`. Do not rename a different archive to bypass a hash failure.

When the owner chooses to run the single phone experiment, from the prepared directory:

```sh
CF2018_SECOND_SERVICE_ACK=YES CF2018_R037_LIVE_REPLY=YES bash START_SECOND_SERVICE_ACK.sh
```

Then use the existing PCAPdroid profile and launch the original game. Share only `CF2018_SECOND_SERVICE_ACK_Result.txt`. No raw capture, account data or game files are requested. Do not retry unchanged failures; inspect the fixed labels first. SYN_CONTEXT REFUSED means no second ACK was authorized. ACK_WRITTEN without AUTH_REQUEST_OBSERVED remains unresolved, not proof of an account rejection. AUTH_REQUEST_OBSERVED identifies the next research gate: next-service auth response/session handling.

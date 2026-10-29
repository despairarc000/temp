# WORKLOG — initial handoff (2026-10-30)

- Earlier: signed-only original-code client reached update checking. DLL patch and one-byte DLL control exited early; APK/OBB editing frozen.
- v0.1–v0.3: local PCAPdroid SOCKS5 and Termux bridge captured real 133-byte TGCP SYN for `QueryAddrSvr`. Framing/decoder prototyped.
- v0.4: synthesized 65-byte ACK; massive retries, immediate socket closes, no new client frame; diagnostic IDs/log accumulation defective.
- v0.5: 8 passive/8 ACK bounded comparison; median SYN-to-end ~7003ms passive vs ~11ms ACK, zero next client frames.
- v0.6: ADB native-log attempt; Apollo initialization observed; TGCP reject logs unavailable in Android logcat. Filter had false positives from touch `0x1002`.
- v0.7: static native audit of sender/receiver, identified unverified mirrored fields and framing.
- v0.8: static candidate correcting first two server bytes `43 66`→`66 43`; local tests only, no verified real client acceptance.
- 2026-10-30: setup of isolated public `temp/cf2018` knowledge workspace and Drive reference, not a replacement for authorized original binary store.

Next: [CHECKPOINT](CHECKPOINT.md) and [TGCP](research/TGCP.md).

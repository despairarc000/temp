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

## 2026-10-30 — coordinator integration

Reviewed live main ec0d55fd338df6cc6f7d1e7aad59c7885fa88f06 and incoming CF18-01/04
packets; no remote CF18-02/03 packet existed. Integrated prefix-model limitations
and source-search coverage limits into canonical knowledge; corrected helper
text that presented an unverified native premise as known. Reviewed the preserved
local CF18-03 original draft, integrated a passive loopback core and 19 transport
tests (16 adapted plus three coordinator controls). Canonical suite: 29 PASS;
CF18-01 audit suite: eight PASS; knowledge doctor PASS. No native/client/device
acceptance evidence was added. Historical Q-02 and G2 remain unresolved.
[Integration record](../../coordination/INTEGRATION.md) identifies actual inputs,
local draft hashes and scope. Assignments are maintained by the coordinator only.

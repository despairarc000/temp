# CHECKPOINT — 2026-10-30

**GOAL** actual offline TDM and Bomb/S&D bots in 2018 CrossFire: Legends. **NOT PLAYABLE YET.**

## Confirmed
- Re-signed original-code APK reaches update-check screen; modified managed DLL failed to start normally.
- PCAPdroid→local SOCKS5→Termux intercepts real TGCP SYN packets to old GCloud endpoints (v0.1/v0.3 on-phone).
- 133-byte `QueryAddrSvr` request, one identical payload across observed retries.
- v0.5 on-phone controlled test: no reply median SYN-to-end 7003.04 ms; 65-byte synthetic ACK median 10.99 ms; ACK-to-end median 8.44 ms; zero follow-up packets.
- v0.6 Android logcat showed Apollo init, but no usable TGCP rejection diagnostics.
- v0.7 native audit: candidate field encoding syntactically matches some native methods; mirrors client base fields without server-response proof.
- v0.8 proposal: native receive prefix expects `66 43` vs old candidate `43 66`. **Static receive-path inference**, not on-phone acceptance.

## Not confirmed / blockers
- TGCP ACK accepted; auth; AddressService; updater and DNS workaround; offline lobby; any real bot match. None can be marked DONE.
- v0.8 on-device result not yet supplied.
- Connected Drive verified unpacked OBB folder, but not all original binaries. See [DRIVE_MANIFEST](../../sources/DRIVE_MANIFEST.md).
- Historical experiment scripts v0.1–v0.8 exist as ChatGPT-generated artifacts and Termux downloads; **not yet claimed as source-committed here**. Codex must import/reimplement only from separately verified, rights-safe evidence.

## NEXT EXACT TASK
Review Apollo incoming framing at `tgcpapi_gather_and_split_entire_pkg` and `gcloud_tgcpapi_recv_ack_msg` and audit server-vs-client prefix/endian expectations. Check byte-level v0.8 candidate, SOCKS5 relay's EOF provenance and sample boundedness. Once tested offline, design one small, explicit A/B/C device test, then capture whether new client message appears.

See [TGCP](research/TGCP.md), [EVIDENCE](EVIDENCE.md), [OPEN_QUESTIONS](OPEN_QUESTIONS.md).

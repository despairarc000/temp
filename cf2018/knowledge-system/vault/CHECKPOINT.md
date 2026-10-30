# CHECKPOINT — 2026-10-30

**GOAL** actual offline TDM and Bomb/S&D bots in 2018 CrossFire: Legends. **NOT PLAYABLE YET.**

## Historical results (imported reports; originals not revalidated here)
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

## Coordinator integration — 2026-10-30
- Earliest unmet prerequisite: original 2018 source identity/provenance (G0); G2 remains BLOCKED.
- [CF18-01 audit](../../coordination/incoming/CF18-01/RESULT.md) proves only the Python model's prefix/suffix/stream limits. Exact native RX instructions remain unverified; Q-01 is unchanged.
- [CF18-04 inventory](../../coordination/incoming/CF18-04/RESULT.md) verifies accessible folder metadata, not the target package/library. Search omitted a known retrievable APK; capped/empty results cannot prove file absence. Q-07 stays PARTIAL.
- [Passive relay core](research/RELAY.md) is integrated as original LOCAL_TEST_ONLY diagnostics, disabled by default, loopback-only, with no device-tested bridge, ACK construction or device test. Nineteen relay tests passed within the 29-test canonical suite; eight framing audit tests also passed.
- No new original binary, receiver-state trace, historical relay source or real post-ACK client packet was obtained. No on-phone A/B/C packet is ready.

[Current assignments](../../coordination/assignments.json) reserve one task per lane. The bounded CF18-03 negotiation stage is integrated; deployment wiring now awaits recovered bridge/passthrough source. Native/source tasks still await verified provenance.

## SOCKS5 packet integration — 2026-10-30
- [CF18-03 packet](../../coordination/incoming/CF18-03/RESULT.md) was reviewed and its bounded NO-AUTH/CONNECT stage integrated into experiments/socks5_handoff.py and tests/test_socks5_handoff.py.
- Canonical suite: 52 PASS (23 handoff tests, 19 relay tests, ten existing tests); eight framing-audit tests also PASS. Knowledge doctor PASS. No listener, target connector or phone experiment was installed.
- Handoff preserves pipelined payload and returns unrelated requests for normal dispatch. CONNECT success and actual target connection are not implemented by this stage; the historical post-method passthrough hook remains unverified.
- G0 source provenance and G2 remain blocked. Stop unchanged blocked activations without re-submitting integrated packets or inventing a native/phone trace.

## NEXT EXACT TASK
Review Apollo incoming framing at `tgcpapi_gather_and_split_entire_pkg` and `gcloud_tgcpapi_recv_ack_msg` and audit server-vs-client prefix/endian expectations. Check byte-level v0.8 candidate, SOCKS5 relay's EOF provenance and sample boundedness. Once tested offline, design one small, explicit A/B/C device test, then capture whether new client message appears.

See [TGCP](research/TGCP.md), [EVIDENCE](EVIDENCE.md), [OPEN_QUESTIONS](OPEN_QUESTIONS.md).

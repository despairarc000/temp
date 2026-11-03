# R105 — Complete synthetic version reply dispatches; actual phone connection still unidentified

2026-11-03 (Asia/Manila). Offline research continued through complete component/header/transport dispatch and negative controls. No server packet sent, game started or phone test run.

## Complete typed fixture, independently checked

**ORIGINAL_NATIVE_EMULATION / SYNTHETIC_ONLY:** Exact Apollo5,243,704B/SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, ARM32/Thumb, verified by every runner. Original `ResVersionUpdate::write`0x33bef8 identifies six GNU string fields on a bounded synthetic object. Independent fixture initialization supplies empty strings at offsets48/96/100/104/108/112. Actual generated pointer-result writer0x33deb4 plus original binary protocol produce a **134B** component identical to independently constructed typed bytes for no-update, optional, forced and nonzero-result cases. Original binary header writer0x39c3bc produces the independently matching **43B** legacy64 REPLY header, method VersionUpdate:ReqUpdateVersion, RPC sequence0x100000002. Combined body177B. These are test sizes, not phone predictions.

Synthetic comm_info has seq7/product11/product_type12/req_type20, fixed non-sensitive64-bit test versions, and empty business data. Explicit update_info includes VersionPackageInfo, kind0 and empty strings. The test version is not an original/local-cache version or a new game label. A265B independent AA frame uses **SyntheticVersion** as a deliberately fictitious route, with transport packet sequence0x11223344. It is not a deployable reply or recovered phone route.

## Original pending map and generated version receiver

Shared [native dispatch control](../../../experiments/native_directory_dispatch_controls.py) now has explicit directory/version profiles; directory remains default. Version profile binds actual std::function invoker0x33e1b0, generated asynchronous receiver0x33ea9c and pointer-result reader0x33ddfc. Original protocol factory, MsgBuffer, RPC header/read/dispatch, one-node pending map lookup, function invocation and erase execute. The pending node is synthetic; real registration/connection ownership are not claimed. RTTI, bounded allocation/libc, function-manager ownership, exception observation and final application callback are explicit runtime substitutes, as in R099.

Matching full64-bit RPC sequence delivers callback status0/result0, presence flags7, update kind0, test versions and comm_info values, and erases pending. Original GCloud receive0x3abe34 also hands a complete frame into this dispatch via a synthetic caller bridge. High-word mismatch, low-word mismatch or truncating the pending key to32 bits yields no callback/erase even while dispatch returns1. Bad AA marker never enters RPC. Missing outer success calls callback−11 and original throw/type5; execution stops before C++ unwinding, leaving pending. Nested empty success still delivers a zero/default object with flags0, so it is not a qualified usable update fixture.

Further source-grounded negative controls:

- A different reply method label still delivers to the already bound version receiver when its pending key matches. Header text alone is not validation of this receiver or phone ownership.
- Changing comm_info.seq7→8 does not change the RPC lookup; it is carried into the result. Transport packet sequence changes also do not replace the full RPC sequence key in this fixture. These are three distinct fields, not interchangeable correlation numbers.
- RPC status0 can carry result1. Feeding that observed pair into the separate R104 decision control stops before no-update decisions. The complete result0/kind0 scalar result feeds the separate original no-update/event controls successfully. This is segmented scalar handoff, not continuous Android execution.
- Only the six known presence bits at object+0x9c are reported (mask0x3f). A transport-path fixture exposed an unrelated upper bit in the raw byte; it is not treated as a seventh schema field, encryption indicator or parsing failure.

This does not establish the live channel's framing/security negotiation, actual route binding or version/product semantics. A wrong label passing in a synthetic bound pending map is not a vulnerability claim or permission to send mismatched replies.

## Technical evidence gap and existing-log reader

The uploaded phone result has aggregate relay counts but not destination classes or over-cap session detail. Actual phone VersionUpdate request/connection remains unidentified. Static execution cannot recover those discarded runtime observations. The richer metadata exists only in the owner's Termux `cf2018_directory_config_runs/run_.../events.jsonl` and `relay/events.jsonl`; there is no authorized local copy here. Sending this synthetic fixture or merely extending another timeout would guess that association.

[summarize_resource_run.py](../../../tools/summarize_resource_run.py) reads the latest saved run, with optional exact --run-dir. **It starts no listener/game and makes no network requests.** It exports fixed counts for accepted/finished/open-at-snapshot sessions, over-cap decisions after the settings event in the same file, settings/discovery writes, eligible address frames, and relay connections/bytes grouped by fixed source-destination class, forwarding mode and port bands. Source server events have no timestamps; the reader explicitly refuses cross-file timing/connection attribution. Host/IP/account/error contents are never printed. Missing/changed/oversized/malformed metadata is not treated as proof of a successful or absent request.

Thirty-five known DNS fingerprints (DIRECTORY14, VERSION14, ASSET7) were independently derived in memory from the exact original GcloudSetting_ TextAsset/ciphertext used in R100. Only allowed settings rows and columns Default/regional were inspected, excluding app keys and comments. SHA256 host fingerprints classify exact normalized hostnames; no original DNS names or secret values are added to reports. IPs remain UNCLASSIFIED_IP even if an address is supplied in a map. A VERSION label identifies a configured frontend hostname, not a decoded RPC method. Both pre-existing redirector named targets classify as DIRECTORY and VERSION respectively; actual IP-based routing still needs the run metadata.

Reports use `CF2018_RESOURCE_RUN_SUMMARY_<UTC timestamp with microseconds>_<random suffix>.txt`, exclusive creation, and a validated saved-run reference. Existing prepared probes and their logs are unchanged. No raw JSON/capture upload is requested. If the latest saved run is not the supplied one, its distinct reference/counts expose that limitation rather than silently merging reports.

## Actual verification

- New version dispatch suite12 methods PASS, including original writer parity, full reply/transport, all correlation and result negatives above.
- Shared-directory regression7 methods PASS after adding the version profile.
- Saved-run summary7 methods PASS: synthetic private-field non-export, immutable input files, IP non-attribution, untrusted label refusal, malformed JSON, bounded lines, file/parent symlink refusal, newest run selection and unique outputs. No actual phone logs processed here.
- **Total26 methods PASS.** Source-free version suite1 PASS/11 SKIP. Old baseline113 was not relabeled as rerun. Knowledge doctors remain blocked by historical local snapshot omissions; no CI success claimed.

Commands use unittest discover patterns `test_native_version_dispatch.py`, `test_native_directory_dispatch.py` (explicit private Apollo/PYTHONPATH) and `test_resource_run_summary.py` (stdlib only). [Synthetic reply/writer control](../../../experiments/native_version_reply_controls.py), [native tests](../../../tests/test_native_version_dispatch.py), [summary tests](../../../tests/test_resource_run_summary.py).

**Next bounded check requiring owner:** run the read-only summary against the already completed Termux run and upload its uniquely named text. Determine configured version-frontend forwarding and session-budget effects before choosing further source work or a new phone experiment. UNKNOWN actual version request/peer/callback, why Loading seemed faster and whether server stop caused the UI error. No guessed live reply, modified game files, resource completion, login/lobby/bots or resumed schedules.

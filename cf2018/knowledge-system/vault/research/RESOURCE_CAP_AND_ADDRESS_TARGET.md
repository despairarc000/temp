# R106 — Saved-run session cap and exact address-target identification

Date: 2026-11-03 Asia/Manila. Original CF2018 v1.0.11.11; game files unchanged. No phone, remote service or live game run performed here. Schedules remain paused.

## Actual owner summary

**PHONE_REPORT:** Uploaded saved-run summary SHA256 `989ebbd0bd00ea090390be813533a0d001f9defdf3c8571e877680ce6e99f3ea`, source run `run_20261102T215652Z_050a9af5`: stable read, one server run, zero malformed lines. Accepted862, finished861, open1, over-cap858 (all after settings in server-file order), settings writes1, discovery writes1, qualified address candidates2. Emulator relay connections:8080=430 and8085=431; all destination classes UNCLASSIFIED_IP. No IP-to-service or cross-file connection attribution follows from these counts.

**CONFIRMED_REPOSITORY_SOURCE:** The observation helper ignored completed-session state for180s while Handler immediately returned for slots above4. This caused repeated probe-side closes, not180s of useful SDK service availability. R101's stronger availability interpretation is **superseded**; its fake-clock test verified duration but missed the handler interaction. These closes obstruct later traffic; whether they caused the particular UI error or faster Loading remains UNKNOWN.

The revised copy keeps the four-session and existing reply budgets. First excess session sets an abort event; the observation loop returns within its200ms polling interval with `session_budget_exhausted`, and existing main-finally terminates only its own proxy child/closes listeners. It does not label this `window_elapsed`, increase the cap or repeatedly reject retries for the remaining window. Completed sessions alone still allow a bounded quiet observation until an excess connection/window/manual stop.

## New original-code control, distinct from historical R025

**ORIGINAL_NATIVE_EMULATION / SYNTHETIC_ONLY:** Exact original Apollo size5243704/SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, ELF32 ARM little endian Thumb, verified again. [Control](../../../experiments/native_address_producer_controls.py) executes `AddressService::ParseDomainName`0x3993c8 on synthetic `dir.3.42.synthetic.invalid` and `download.1.42.synthetic.invalid`, then `Send_QueryAddrInfo`0x3998d4 through actual protocol-vtable message begin, generated args0x39ed4c and message end. Stops0x399928 before transport flush/route assignment; bounded GNU string/libc substitutes and byte sink are explicit. No claim of native connector/network execution.

Original parser yields service/unit/game `(dir,3,42)` and `(download,1,42)`. Original RPC bytes equal an independently written grammar. Including a **separately modeled**, zero four-byte packet prefix yields80/85B. The sender itself does not emit that prefix. Strict-write positive takes the distinct versioned header and the narrow legacy target detector refuses it.

The qualified method name and old colon-policy false negative were **already established in R025**. They are not new discoveries; the historical observer is preserved. New evidence is execution of the domain parser plus whole RPC writer on these independently synthetic lookup keys. This does not identify the old phone bodies, their game/unit values, actual runtime owner, or successful authentication. Source-configured directory/update names are hypotheses for the two reported candidates, not recovered payloads.

## Bounded next discriminator

[address_query_target.py](../../../experiments/address_query_target.py) checks exact qualified legacy64 request, packet-sequence equality, typed nested fields and complete consumption. Full-frame path requires exact QueryAddrSvr route, declared body length, routed type and clear cipher/compression guards. It returns only fixed labels: DIRECTORY_ADDRESS_QUERY for service dir/unit3; VERSION_ADDRESS_QUERY for download/unit1; OTHER_ADDRESS_QUERY for other complete tuples. No field values, RPC/packet sequence, game ID, body or private strings are exported. A label identifies requested address content, **not** a VersionUpdate request, successful lookup, response acceptance or connector identity. Strict/other encodings remain unclassified.

Copy-only [preparer](../../../tools/prepare_directory_config.py) option `--identify-address-queries --observe-seconds 180` embeds this reviewed source, logs fixed labels and stops on VERSION_ADDRESS_QUERY **before the R033 candidate branch**, with `version_address_identified_no_reply` and observation stop `version_address_identified`. Existing directory/settings gates and replies remain unchanged. No additional address/version reply is generated. Fresh output directories and timestamp/random-suffix exclusive result files remain mandatory. No original/source tree overwritten.

**HYPOTHESIS:** The second qualified address candidate requests the update-service endpoint, but the global one-discovery-reply budget leaves it unanswered. If the next bounded identifier labels it DIRECTORY/OTHER or cannot parse it, this hypothesis is not confirmed. A cap stop without a label is inconclusive, not permission to raise the cap or guess a reply. Existing saved logs discarded these field values, so they cannot retrospectively answer this predicate.

## Verification and next action

- Address target suite8 methods PASS: original parser/writer byte parity and strict negative; complete/truncated/trailing/wrong-type/wrong-sequence controls; route/cipher/compression/length guards; fixed-label privacy; embedded-source equality; actual handler receives synthetic routed input and stops with only established ACK/auth/Bingo writes, no R033 application response.
- Observation9, preparer5, existing settings lifecycle7 methods PASS: **29 total**. Lifecycle uses loopback sockets only; observation uses fake time/fake I/O, including actual over-cap handler and explicit abort/identification stop reasons. Source-free target suite4 PASS/4 SKIP. Original source stays optional in public CI; no new CI success claimed.
- Commands: `python -m unittest discover -s cf2018/tests -p test_address_query_target.py -v` with explicit CF18_APOLLO_LIBRARY/CF18_DIRECTORY_IDENTIFY_PREPARED/private dependency PYTHONPATH; directory suites use `-p 'test_directory_config_*.py'` plus CF18_DIRECTORY_CONFIG_PREPARED pointing at the separately prepared copy. Both knowledge doctors retain historical local snapshot omissions; no new errors added.

**Next requiring owner:** one manual bounded run of this exact target identifier, then upload its unique text report. The goal is a fixed label, not UI progress. Stop criteria are identified update lookup, first excess session,180s or manual Ctrl+C. No speculative live reply, DLL/APK/OBB patch, resource completion/login/lobby/bots claim.

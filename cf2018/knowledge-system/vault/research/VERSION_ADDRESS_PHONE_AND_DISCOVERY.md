# R107 — Phone updater-address lookup and bounded next-service discovery

2026-11-03 Asia/Manila. Original CF2018 v1.0.11.11. No phone/game/remote-server run or original game modification performed by this agent. Schedules remain paused.

## Actual uploaded phone result

**PHONE_REPORT:** `CF2018_DIRECTORY_CONFIG_Result_run_20261103T022837Z_202f1c3f.txt`, SHA256 `29a4369e8390bb81bf35732a3c00236f6ce9348e835a92f0d158033b2228d03a`.

- Slot1: DIRECTORY_ADDRESS_QUERY / COMPLETE_LEGACY64, existing169B discovery response written, later0x5001. Slot2: CTDIR_STATIC_ROUTE_MATCH, ACK/auth/Bingo, BY_ID_COMPLETE/LEGACY64 and223B settings reply written; connection remains open at report snapshot.
- Slot3: VERSION_ADDRESS_QUERY / COMPLETE_LEGACY64, status `version_address_identified_no_reply`. Under the exact R106 discriminator, this is a complete qualified QueryAddrSvr:QueryAddrInfo request for service download/unit1, with route, independent packet sequence, declared length and clear cipher/compression guards. No raw phone values were recovered from the report; these are the discriminator's fixed categories.
- Observation elapsed53.52s, stop `version_address_identified`. It intentionally ended upon identification, **not** at180s or from over-cap exhaustion. Four accepted slots/three finished and one open are visible;21 relay CONNECTED records include other traffic and do not identify21 SDK sessions. Slot4 has the reference SYN/auth stages but no routed follow-up before shutdown.
- Owner says the script ended around Checking resources/update. This is consistent with the designed identification stop, not proof of a completed resource check, accepted settings callback, all replies accepted, or the cause of earlier faster Loading.

This resolves R106's runtime **address-target** hypothesis for this run. It does not identify an actual VersionUpdate RPC yet, prove a particular native object owned the phone connection, or establish authentication/login/playability. Earlier reports are not retroactively decoded.

## Original source and bounded execution

**CONFIRMED_NATIVE_STATIC:** Exact Apollo size5243704, SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, ELF32 ARM little-endian Thumb reverified. Generated sender0x33e400 constructs method VersionUpdate:ReqUpdateVersion. Its transport service-name operand resolves via literal0x33e524 plusPC0x33e48a to exact **VersionUpdate**,13 bytes; setServiceName virtual call0x33e494. This is an original operand, not ownership inferred from a matching string scan. Actual phone SYN route remains to be checked.

**ORIGINAL_NATIVE_EMULATION / SYNTHETIC_ONLY:** [Request controls](../../../experiments/native_version_request_controls.py) execute original pargs writer0x33dc88→ReqVersionUpdate::write0x33b6e4→comm writer0x33b394 against the original binary-protocol vtable. Required outerfield1 STRUCT contains commfield1 STRUCT and user-data STRINGfield2; optionalfield3 STRUCT contains three strings. Comm fields1–4 I32,5–6 I64,7 STRING, optional8 I64/9 I16. Both optional profiles byte-match independent synthetic fixtures. No request bytes from the phone are available here.

Original FillReqUpdate0x32e538 executes with an injected configuration getter, synthetic version-text conversion and bounded string runtime. Modes20/21/22/23 map `(comm.product_type, comm.request_type)` to `(1,1)/(2,1)/(1,2)/(2,2)`; modes22/23 set custom-request presence. **Do not confuse configuration mode20–23 with either wire scalar.** Read-only version labels use product_type1 APPLICATION /2 RESOURCES; request type and all values remain private. This is branch/schema proof, not a real configured phone mode.

Original SYN→ACK handoff on a13B synthetic named route reaches the suppressed auth-send boundary. Wrong magic, unsupported key mode, client-prefixed ACK and truncated ACK do not. Existing10/12B controls also pass. No crypto/account/auth-send success is inferred; the native receiver fixture is synthetic, not proof of real version-channel acceptance.

## Narrow next manual control

[prepare_version_discovery.py](../../../tools/prepare_version_discovery.py) is a single stdlib-only download embedding the reviewed R106 preparer and [version control](../../../experiments/version_discovery_control.py). It copies only the exact pinned directory-identify source to a **new** directory; original/prepared earlier probes and game files stay unchanged. Explicit CF2018_R037_LIVE_REPLY=YES, CF2018_VERSION_DISCOVERY=YES and --live-opt-in are required to launch manually. Listeners/proxy stay loopback/scoped to the existing endpoints. Four-session cap, first-excess-session abort and180s ceiling remain.

1. Preserve existing one discovery response and one directory settings response. After the settings socket write succeeds, allow **one separate** reply only to a fully validated download/unit1 address query. Reuse the existing R033 required-result/reason, exact RPC64 correlation and127.0.0.1:8085-only response builder; no new address format, credential/key or version result.
2. After that write, allow at most one VersionUpdate SYN only if its complete encoded base and every non-route SYN field match the pinned discovery reference byte-for-byte; exact route changes12→13B. Wrong unit/client/security/route, missing prior lookup write and reused ACK budget get no ACK. Never authorize by route length alone.
3. Reuse the tested ACK63/auth54/Bingo91 sequence for that context as a **new bounded phone hypothesis**. Report fixed stages; a new typed VersionUpdate request must independently match exact route/method, clear transport, packet sequence, required/optional typed schema, bounded strings and full consumption. No payload/IDs/strings are logged.
4. Stop on a complete request with `version_request_identified_no_reply` / observation `version_request_identified`, cap, deadline or Ctrl+C. **No VersionUpdate application reply is constructed or sent.** A refused context or unrecognized request remains inconclusive; do not loosen guards or increase budgets automatically.

The extra address reply is an intentional extension from R106's identification-only stop. Reply writes and callback/real-client acceptance remain distinct; one loopback address already working for directory does not prove the updater instance's runtime callback. A successful next identifier would establish the next request and product group, not an accepted no-update result or completed resources.

## Actual verification

`test_version_discovery.py`: **12 methods PASS**, including3 original controls (route/request parity, FillReq profile,13B ACK handoff),5 prepared-source controls and4 source-free controls. Complete four-session loopback exchange validates discovery→settings→scoped update lookup→strict version SYN→typed request, exactly one reply at each allowed stage and no version result. Negatives cover absent settings/reused lookup budget, absent lookup/reused ACK budget/wrong unit, security/route changes, malformed/trailing/truncated/duplicate/missing fields, cipher/compression/sequence guards, embedded-source equality and private-canary non-export. Source-free command:4 PASS/8 SKIP.

`test_native_syn_ack_handoff.py`: existing3 methods PASS. **Total15 methods PASS.** Commands use unittest discover patterns above, PYTHONDONTWRITEBYTECODE=1, private analysis dependency PYTHONPATH and explicit CF18_APOLLO_LIBRARY; prepared tests additionally set CF18_VERSION_DISCOVERY_PREPARED to the separately generated copy. No previous113-test baseline/Android experiment relabeled as rerun. Both knowledge doctors retain historical local snapshot omissions; no new errors/CI success claimed.

**Next requiring owner:** one manual scoped version-discovery run, upload the timestamp/random-suffix `CF2018_VERSION_DISCOVERY_Result_run_….txt`. It may end while the UI still checks resources because this control deliberately stops before an updater result. UNKNOWN real version SYN/context acceptance, full request contents, response acceptance, resource completion/login/lobby/bots and Loading timing cause.

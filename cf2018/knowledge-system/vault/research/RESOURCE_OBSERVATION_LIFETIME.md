# R101 — Probe lifetime confounds the later resource error

2026-11-02. Existing game/version; no new phone run performed.

**PHONE_REPORTED:** Owner clarifies the last settings-reply test reached Checking resources, ran there for a while, then errored. The script had already finished around entry to that stage or a few seconds afterward. The quicker Loading transition remains an untimed comparison; exact error text, timestamps and successful settings acceptance remain unknown. This supersedes R100's pending question about whether checking finished. It did not finish on that run.

**CONFIRMED_REPOSITORY_SOURCE:** The prepared directory configuration probe has two independent lifetime limits: `Handler.handle` uses `while time.monotonic()-started<12.0`; `Run.stop` sets `done` when four sessions finish; `main` waits on `run.done` and then terminates the SOCKS5 child in `finally`. Thus the report's12s connection deadline is not a resource-update timeout, and the proxy can disappear while the game continues checking. Early shutdown is a competing explanation for the later error, not a proven cause. Resource updating is not yet implemented just by holding the process open.

## Optional controlled observation

[prepare_directory_config.py](../../../tools/prepare_directory_config.py) adds `--observe-seconds 180` (integer60..300 only). Omitted option preserves the previous preparation/timing behavior. Explicit option makes a separate copy, changes the per-connection ceiling to the selected duration, and holds the proxy for that bounded duration even if all four sessions finish. Manual Ctrl+C and unexpected proxy exit still stop/report early. The outer observation clock starts after listeners/proxy startup. No automatic phone run.

Replies, exact source/helper hashes, security/context checks, one directory ACK/reply budget, and four-session cap remain unchanged. Additional rejected connections do not gain ACKs or responses. Existing peer EOF, frame/byte caps and deliberate closure after a subsequent application frame also remain. This tests availability/lifetime, not an unrestricted server or a new updater reply.

The result remains `CF2018_DIRECTORY_CONFIG_Result.txt`, with an added fixed-label `RESOURCE_OBSERVATION configured_seconds=... elapsed_seconds=... stop=...` row. Stop labels distinguish window_elapsed, proxy_exit, manual_stop and interrupted_or_error. No raw frame, endpoint, original asset or account content is added.

## Verification actually run

**SYNTHETIC_ONLY:** Six new timer/control methods PASS: completed session budget does not stop the observation window; fake proxy death reports early; Ctrl+C survives; invalid bounds reject; default source unchanged/reply gates retained; actual prepared Handler with an idle fake socket/fake clock survives12s and terminates at180s without sending anything. Fake-clock testing is not a real180-second Android run.

Existing copy/preparer4 PASS. Prepared extended-window loopback lifecycle7 PASS, including qualified one reply, disabled/no-prior/security-mutation/wrong-method refusals and one-shot budget. Baseline113 PASS on the extended prepared copy. Commands used `python -m unittest discover -s cf2018/tests -p test_directory_config_observation.py -v`, corresponding preparer/lifecycle patterns with explicit private prepared-source environment variables, and `python -m unittest discover -s cf2018/private/directory_resource_observation/tests -v` with its folder on PYTHONPATH. Total130 test methods PASS, not phone acceptance. Knowledge doctors retain historical local-snapshot omissions.

**Bounded next check:** owner runs this same settings-reply control with the explicit180s option, launches the game promptly, and reports whether the resource error occurs while the script is still active, exact error text, and the result file. An error before the observation window ends with no proxy-exit label falsifies shutdown as a sufficient explanation for that run. No error before180s is not resource completion or login proof. UI/proxy clocks, network selection and updater application replies remain separate unknowns; no game patch/login/lobby/bots claim.

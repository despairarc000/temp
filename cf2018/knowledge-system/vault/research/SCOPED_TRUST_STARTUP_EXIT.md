# Scoped-trust copy exits at startup

## Existing exit report and attribution correction — 2026-11-08 UTC

PHONE_REPORT: CF2018_STARTUP_EXIT_20261108T230135_845334Z_9a907bd0.txt,
SHA256 f0dfe6d0c583caf680fb13f1a594d175301ebfbe6aea6be13b28e07ec7b82470.
Both acquisition reads succeeded. Three listed main-process records are EXIT_SELF
with NONZERO status. Crash-buffer target_java_fatal_records0/fixed_mentions{}.
Android therefore recorded app-requested nonzero termination in this history;
this is not a recorded unhandled Java exception. The report explicitly does not
bind those exits to this installation/attempt. No exact exit code was retained.
No absence-of-crash proof or B integrity-cause conclusion follows.

The first reader was too coarse for this next distinction: it discarded useful
OS exit status and installation timing. Updated reader retains only self-exit
codes0–255 (otherwise OUT_OF_RANGE), reads package lastUpdateTime privately and
compares each exit timestamp as BEFORE_UPDATE/AT_OR_AFTER_UPDATE/UNKNOWN. These
are local phone timestamps, with no absolute time exported; timezone/clock
changes and old history still limit attempt attribution. It does not claim that
AT_OR_AFTER_UPDATE identifies a particular launch.

It also reads `dumpsys package`, `pm path` and shell `sha256sum` on exactly one
validated /data/app/.../base.apk path. No APK is pulled/downloaded. Only a fixed
ORIGINAL/SIGNATURE_CONTROL_A/SCOPED_TRUST_B/OTHER_APK/UNKNOWN label and read
statuses are exported, not path, package dump, signing/account data or digest.
Multiple/unsafe paths, failed permissions or unknown date formats remain
explicitly unresolved. No install, relaunch, log clearing or game edit.

CONFIRMED_NATIVE_STATIC / NATIVE_CONTROL_WITH_EXPLICIT_SUBSTITUTIONS: original
libtprt.so actually present this turn, SHA256
f608b142822b888f4e5b44bbb0167e8d5c02e1680ea89bab8171aeaab59b4f0a.
Existing [post-load comparator](../../../experiments/native_integrity_controls.py)
rerun with independent checksum inputs1/2 requested termination18 at0x31ac;
1/1 and0/2 reached normal-return boundary0x36a8. Actual instructions with
synthetic lookup/context substitutions, stopped before syscall; no original
game runtime, phone execution or termination occurred. This revalidates an
already documented path, not a new causal finding. Exit18 alone is not unique
call-site identification, nor proof of a manifest/resource check or checksum
failure on this phone. See [prior limits](INTEGRITY_NATIVE.md).

SYNTHETIC_ONLY: revised reader12 methods PASS (previous8 plus bounded exit-code
retention, update-time ordering/unknown controls, installed-APK hash classification
without export, and unsafe/multiple-path rejection before shell hashing).
The same curl/read command below now fetches the corrected reader. NEXT owner
read existing records again; no new game attempt. Keep the failed installation
until evidence is read. Immediate B transport test remains paused.

Earlier text below describes the pre-report state and first reader; missing
summary/exact fixed-status wording is superseded by this update.

2026-11-08 UTC. OWNER_OBSERVATION: newly packaged XAPK backs out; owner compares
the behavior to earlier modified builds that would not run. No startup exit
summary, B packaging receipt, installed APK hash or matched crash trace has yet
been supplied. Do not label this a successful trust comparison or infer an
integrity guard from the symptom alone.

The preceding [A transport report](CONFIGURATION_DNS_TLS_CONTROL.md) did reach
local configuration TLS and returned a certificate alert. Its positive routing
and negative certificate evidence remain valid for that request; B startup is a
separate newly failed gate. The previously proposed B HTTPS run is now paused.

CONFIRMED_REPOSITORY_SOURCE / PRIOR OFFLINE CHECKS: the prepared B changes
AndroidManifest.xml/resources.arsc and adds trust XML/CA resources; original
DLL/Dex/native/assets were preserved in prepared outputs. This does not establish
phone launchability. Android resource/security-config initialization errors and
broader game termination checks are competing explanations. Historical
[native integrity evidence](INTEGRITY_NATIVE.md) is not proof of this new cause.
No further game changes, replacement APK or protection-disable patch is proposed.

## Next discriminating evidence

The existing account-log reader requires a live PID and examines only SDK
messages. It cannot adequately diagnose an already closed process. New
[startup exit reader](../../../tools/summarize_startup_exit.py) instead reads
existing `adb shell dumpsys activity exit-info com.tencent.tmgp.cfmnac` plus
`adb logcat -b crash -d -t 256 -v brief`. It never launches/installs/uninstalls,
clears logs, reads a tombstone/account token or modifies app storage. Reads are
bounded to20s each and refuse input above8MiB before parsing. Raw output remains
in memory only and is never exported.

CONFIRMED_PLATFORM_SOURCE: Android15
[ApplicationExitInfo.java](https://github.com/aosp-mirror/platform_frameworks_base/blob/android-15.0.0_r1/core/java/android/app/ApplicationExitInfo.java#L1247)
dump prints process/reason/subreason/status. Reasons1/4/5/7 mean EXIT_SELF,
unhandled Java exception, native crash and initialization failure respectively;
reason2 carries an OS signal. Exit-self is not proof of integrity failure; a
signal can have more than one cause. Parser uses exact main-process match and
at most3 records in dump order, with fixed enum/status labels. No raw descriptions,
PIDs, UID, original hostnames or exception messages reach the report.

Crash reader associates AndroidRuntime FATAL EXCEPTION blocks with an exact
main-process/PID marker and emits only known resource/XML/network-config,
certificate/link/security/null-pointer labels. It resets on another fatal block
for the same PID; unrelated app records are excluded. Historical record age,
installation identity and attribution to this particular attempt are unverified.
Missing records, inaccessible adb or unsupported dump formatting are inconclusive,
not evidence of clean exit or deliberate termination. Native crash detail is not
collected; only a recorded native-crash/signal classification may be available.

SYNTHETIC_ONLY: [8 reader tests](../../../tests/test_summarize_startup_exit.py)
PASS: reason/signal enums, exact process filtering and3-record bound, malformed
input, package-scoped Java markers, PID reuse, private-description suppression,
input bound, and exact two read-only adb command arguments with partial failure.
First test execution had str/bytes fixture mistakes; corrected fixture encoding
before the passing run. No actual Android/ADB collection performed here.

## Owner command: read the saved failure, no relaunch needed

Keep the failed copy installed for now and do not clear its logs. Stop the
network test and disable its two temporary DNS mappings. With the existing
Wireless debugging adb connection available, paste:

```bash
(
set -e
adb get-state
D="$HOME/storage/downloads"
curl -fL --max-time 30 \
  https://raw.githubusercontent.com/despairarc000/temp/main/cf2018/tools/summarize_startup_exit.py \
  -o "$D/summarize_startup_exit.py"
python3 "$D/summarize_startup_exit.py" --output-dir "$D"
)
```

Share only CF2018_STARTUP_EXIT_timestamp_suffix.txt; optional existing
CF2018_SCOPED_TRUST packaging TXT helps confirm what was packaged, but never
share private APKs, keys, raw crash buffer or original resources. If adb is
disconnected, restore the Wireless debugging connection first; no game rerun is
needed merely to collect this existing record. Choose the next research from
the reported reason/markers, with historical-attribution limits retained.

Diaries remain near8KiB; no append or archival. Schedules paused. No B TLS,
configuration/account acceptance, playable game or exact cause is claimed.

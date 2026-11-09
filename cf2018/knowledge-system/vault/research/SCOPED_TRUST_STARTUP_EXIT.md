# Scoped-trust copy exits at startup

## Initialization boundary and negative JNI controls — 2026-11-09 UTC

CONFIRMED_NATIVE_STATIC: original pinned TPRT ELF dynamic tags contain
DT_INIT_ARRAY0x22458/size0x20, seven nonzero Thumb constructor entries and one
zero. No separate DT_INIT tag. .rel.dyn/.rel.plt have no targets within
.tptext0x177ac–0x18398. This excludes a missed separate DT_INIT or ordinary
recorded relocation into this region as a sufficient initialization recipe;
it does not exclude runtime writes or explain its runtime code/results.

JNI_OnLoad0x3100 obtains an environment through JavaVM.GetEnv, requires result0
AND nonnull environment, looks up a class through JNI function-table slot+0x18,
then uses RegisterNatives slot+0x35c with18 entries at0x23224. Registration requires
nonnegative result before auxiliary initialization0x7d80. The failure handling
0x3174–0x3176 forms return-1, distinct from the FileChecker code4 landing.
JNI table names are not resolved from the untouched on-disk table here;18 target
function pointers are source metadata, not successful runtime registration.
The registration-table address uses the aligned Thumb PC-relative literal at
0x31a8 plus PC0x3170; an exploratory unaligned literal calculation was discarded.

NATIVE_CONTROL_WITH_EXPLICIT_SUBSTITUTIONS: new `jni_registration_gate` in the
[native audit](../../../experiments/native_integrity_controls.py) executes only
the actual post-call guards with supplied results/environment pointer. GetEnv
result0 + nonnull environment passes; result0/null, -1/non-null and4/non-null
take failure handling. Class lookup null fails/non-null passes. Registration-1
fails while0/1 pass. Every control stops BEFORE lookup/registration/auxiliary
initialization or before failure handling; no JNI call, checker, constructor,
real initialization or termination is executed. These results cannot be used
to claim a working initialized library or exclude other constructor/thread exits.

[Native suite](../../../tests/test_native_integrity_controls.py):16 methods PASS
with explicit original TPRT/Mono; default3 PASS/13 SKIP. Guard input-shape negative
rejects an unknown stage before source access. Source files remain unchanged;
no APK preparation, guard disabling, decryption, binary/raw-code publication or
Android/phone/network run.

TECHNICAL BLOCKER REACHED: available private originals and reports do not provide
the initialized JNI/protected-native state or the actual FileChecker input/result.
Neither the malformed static instruction interpretation of .tptext nor arbitrary
stubbed successful initialization would establish the real check. There is no
attached Android target/emulator or verified specific runtime collector here.
A matched read-only native startup trace, or independently reproduced complete
initialization with explicit proven dependencies, is needed to advance beyond
this boundary. No additional identical exit report/reinstall is requested. Do
not claim research continues in the background after this turn. Existing B TLS
test stays paused; no login/gameplay acceptance. Diary near cap, no append or
rotation. Schedules paused.

## Checker hierarchy and scope of a hypothetical removal — 2026-11-09 UTC

Owner asks whether this is an integrity checker and whether disabling it would
permit unrestricted changes. No removal/patch was performed. Source supports a
file-verification/protection candidate, not a proven particular integrity check
or a sufficient change for successful launch, TLS, authentication or gameplay.

CONFIRMED_NATIVE_STATIC: original TPRT SHA f608b142… reverified by existing pins.
FileChecker typeinfo0x2248c has typeinfo-kind __cxxabiv1::__si_class_type_info,
resolved through its metatype vtable, before interpreting the base pointer at+8.
Base pointer is0x224ac, name tpshell::TPThread; its metatype is ordinary
__class_type_info. Thus the candidate is statically a TPThread subclass. This
does not attest thread creation, scheduling, execution on the phone or the
upstream checker input. The method0x50fc/code4 association remains as above.

The separately verified Mono-loader/post-load comparison uses another wrapper
and status18/26. Native type inheritance plus the distinct check path provides
no basis for treating one FileChecker alteration as removal of every guard.
Provider initialization, resource correctness and SDK/account session gates also
retain their own acceptance requirements. Disabling an examined termination
branch would not demonstrate that failed initialization became successful; this
is a limitation of the inference, not a tested removal result.

Added bounded nested-name decoding and metatype validation to the existing
[read-only audit](../../../experiments/native_integrity_controls.py).
[Suite](../../../tests/test_native_integrity_controls.py):14 methods PASS with
explicit originals; default3 PASS/11 SKIP. Nested-name positive controls include
TPThread, the SI metatype and unrelated simple class; malformed lengths, truncated
names, single nested component and trailing data are rejected. Actual original
metadata asserts base/typeinfo-kind alongside the candidate virtual target.
No Android run, memory patch, protection removal, raw code publication or secret
extraction. Existing graph routes still point to this audit/test/document.

UNKNOWN: checked file/condition, actual phone call site and full initialized
.tptext result. Next remains a justified read-only way to observe those inputs;
no verified collection method is available here yet. Do not request another
identical exit report or replacement install as a substitute. Diary near cap,
no append/rotation. Schedules paused.

## Candidate is statically owned by FileChecker — 2026-11-09 UTC

CONFIRMED_NATIVE_STATIC: original libtprt.so SHA256
f608b142822b888f4e5b44bbb0167e8d5c02e1680ea89bab8171aeaab59b4f0a
reverified from the available private original. Primary vtable0x22478 has
offset-to-top0 and typeinfo pointer0x2248c. Typeinfo name pointer0x1b031 holds a
valid simple Itanium name for FileChecker (encoded length11). The third function
slot0x22488 contains Thumb pointer0x50fd, resolving to0x50fc: the method whose
failure path selects exit4. This establishes static C++ ownership of the candidate
method; it does not prove this virtual method executed on the phone.

Added read-only `startup_checker_identity` to the
[existing native audit](../../../experiments/native_integrity_controls.py), with
size/hash/ELF/ISA checks and bounded file-backed metadata reads. No Android
constructor or checker is executed by this metadata audit. No game modification,
guard change, decryption, original byte dump or secret export.

SYNTHETIC_ONLY / CONFIRMED_NATIVE_STATIC: simple-name decoder tests distinguish
valid FileChecker and unrelated OtherType, reject mismatched lengths, embedded
NUL/trailing data, invalid bytes and malformed lengths. Original-source test
verifies the complete vtable→typeinfo→name and virtual-target association.
[Native suite](../../../tests/test_native_integrity_controls.py):13 methods PASS
with explicit original TPRT/Mono; default2 PASS/11 SKIP. Earlier code4/predicate,
code18 mismatch and equality/missing-checksum controls remain covered.

Read-only original APK330453… was rehashed; literal-name negative check finds
zero on-disk ASCII occurrences of AndroidManifest.xml, resources.arsc or
Assembly-CSharp.dll in libtprt (FileChecker occurs once). Absence does not exclude
checks against those files, indirect/resource-ID access or runtime string
construction. It provides no basis for assigning a checked file. No decoded
runtime string/table, file trace or full initializer result is claimed.

INTERPRETATION: file verification is a source-grounded candidate, consistent
with a startup difference after metadata/resource changes despite unchanged DLL.
Neither the RTTI label nor exit4 identifies the checked file, algorithm, rejected
condition or phone call site. Do not collapse this into “confirmed integrity
failure”, or assume the historical DLL checksum path is responsible.

REMAINING TECHNICAL BOUNDARY: method calls .tptext0x17e74, whose initialized
runtime semantics/result are unverified; the fallback still has multiple routes.
Next required evidence is checker input/result or a matched runtime call trace.
No verified collection method for that specific state is available in this
workspace yet; no adb target/emulator is attached. No additional user phone run
or replacement APK is requested merely to repeat the known exit. The current
installation and saved failure should be retained. Schedules paused; no diary
append/rotation and no TLS/login/gameplay acceptance.

## Installed B and exit4; separate native failure path — 2026-11-09 UTC

PHONE_REPORT: CF2018_STARTUP_EXIT_20261109T000839_389418Z_c7b3a600.txt,
SHA2561295dee2db824e5c35506514cc4b888a67ae1d3c5d8a6ee737a81eba8bf1e80b.
All acquisition/hash reads READ; installed hash class SCOPED_TRUST_B;
package update time parsed. All3 listed main-process records are EXIT_SELF,
exit_status_code4, AT_OR_AFTER_UPDATE. Target Java fatal records0. This now ties
the installed artifact to reviewed B and places these records at/after its update,
superseding the previous unknown-install/unknown-code status. Exact launch
attribution and clock/update-time limits remain. No Java-crash or configuration
TLS acceptance is established; no new game execution was requested here.

CONFIRMED_NATIVE_STATIC: original libtprt.so SHA256
f608b142822b888f4e5b44bbb0167e8d5c02e1680ea89bab8171aeaab59b4f0a
reverified; ELF32 little-endian EM_ARM. A different native failure landing0x5194
sets r0=4 and branches0x5164 to wrapper0x43ac. Wrapper sets r7=248 and reaches
SVC at0x43b2, the ARM exit_group boundary. This is distinct from previously
examined0x31ac loader guard using18/26. The phone's4 does not support identifying
the known unconditional18 mismatch fallback as its direct exit source.

The enclosing function0x50fc calls unresolved0x17e74 in .tptext at0x511e, then
predicate0x47f6. Predicate accepts0 or101–200; otherwise fallback searches up to8
records for type4 and may attempt a dynamic callback. Missing record, failed
resolution or nonzero callback result can converge on landing0x5194. Exit4 is
therefore a shared failure code here; it does NOT reveal the upstream returned
status, record meaning, original check, manifest/resource integrity condition or
phone call stack. Callback/config alternatives also prevent treating the code
as unique call-site identification.

NATIVE_CONTROL_WITH_EXPLICIT_SUBSTITUTIONS: added bounded controls in
[existing native audit](../../../experiments/native_integrity_controls.py).
Starting at failure landing with independent r0 inputs0/18 yields r0=4,r7=248
at0x43b2; wrapper-only input18 preserves18. Every run stops BEFORE SVC; no real
termination. Separate native predicate controls accept0/101/150/200 and reject
1/4/18/100/201/0xffffffff. These execute original instructions in synthetic
entry contexts, not the phone's upstream check or actual runtime initialization.
[Suite](../../../tests/test_native_integrity_controls.py):11 methods PASS with
explicit original TPRT/Mono sources; default1 PASS/10 SKIP. No original bytes,
raw disassembly, patches or secrets published.

CONFIRMED_ORIGINAL_DEX_STATIC: original APK330453… rehashed and direct termination
references inspected. TPShellApplication.preInitial exception fallbacks0x52/0x96
pass constant1; finalInitial0x52 also passes1. These inspected Java fallbacks do
not explain4. Other native/reflection/runtime termination paths remain open;
absence of Java fatal markers still does not exclude handled exceptions.

TECHNICAL BOUNDARY: original binaries are available; initialized Android native
state and the runtime semantics/result of .tptext call0x17e74 are not reproduced
here. No decryption, key extraction, guard disabling or further APK edit was
performed. NEXT read-only .tptext initialization/fallback provenance research
before another phone test or replacement build. Do not resume B TLS simply from
matching exit code, and do not ask for another copy of the same exit report.
Diary near cap; no append/rotation. Schedules paused; login/gameplay unproven.

Earlier unknown installed-identity/status statements below are historical and
superseded by this report; exact integrity-cause uncertainty remains current.

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

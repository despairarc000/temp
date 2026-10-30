# CF18-INTEGRITY-01 — protected managed input and native loader guard

Coordinator, 2026-10-30. Base main
`6a0ecc16877adbdc4eed03cefebb5b4144f7bd6f`. Direct user-requested offline
investigation; session work and schedules remain paused and unchanged.
Classes: ORIGINAL_FILE_FORMAT_OBSERVATION, ORIGINAL_NATIVE_STATIC,
NATIVE_EMULATION_WITH_EXPLICIT_SUBSTITUTIONS, INDEPENDENT_SYNTHETIC_CONTROLS.

**Confirmed:** the stored game DLL is not an ordinary PE image, Mono image loading
is detoured into libtprt, and one examined post-load checksum mismatch path
requests termination. **Not confirmed:** which condition caused the historical
edited-DLL phone exit, or a safe working modified build. No APK/OBB/DLL patch,
repack, installation, device experiment, anti-cheat interaction or network run.

[Historical controls](STARTUP.md), [acceptance](../../../coordination/CF18-INTEGRITY-01/ACCEPTANCE.md),
[actual matrix](../../../coordination/CF18-INTEGRITY-01/NATIVE_MATRIX.json),
[original native controls](../../../experiments/native_integrity_controls.py),
[read-only preflight](../../../tools/managed_image_preflight.py).

## Sources and first verified format boundary

The private original APK is the previously [pinned mirror](../../../sources/SOURCE_PROVENANCE.md),
30884905 bytes, SHA-256
`33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9`.
Required native members were read from that APK into private analysis storage;
the original APK, assemblies and OBB were not changed. ZIP member reads checked
CRC. Native sources are ELF32 little-endian ARM EABI5, with ARM/Thumb interworking.
Addresses below are source-relative virtual addresses, Thumb bit cleared.

| Private input | Size / actual SHA-256 |
|---|---|
| Assembly-CSharp.dll | 13423104 /174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9 |
| Assembly-CSharp-firstpass.dll | 317440 /4ac2b58a02cc1d3ad1e345d9b21dd78c758b0077c19354862792d25bcaa8ba60 |
| libmono.so | 3889708 /025e971133d24a38ddb2493cf2adee8208555bb5967247fa889a6ad7b91dac91 |
| libtprt.so | 153676 /f608b142822b888f4e5b44bbb0167e8d5c02e1680ea89bab8171aeaab59b4f0a |

Actual APK inspection:15 managed members.13 have MZ/PE/CLI metadata headers;
Assembly-CSharp and firstpass have no MZ prefix and no BSJB occurrence. This is
not evidence of a corrupt download: hashes match the reviewed original and
the original native loader has a distinct transformation path. It is a protected/
transformed on-disk representation, not a directly editable ordinary managed PE.
Absence of PE by itself would not identify an encryption scheme or a checksum
failure. No decoded proprietary output or secret is published.

The preflight reports MANAGED_HEADERS_PRESENT only for supported bounded PE/CLI
header/metadata-root ranges. It does not verify IL, metadata table contents,
strong-name signatures, Mono loadability or protection acceptance. STORED_NON_PE
does not by itself mean encrypted or malicious. Public tests use synthetic images;
actual15-member descriptive results are in the matrix.

## Ordered original-native trace

| Boundary | Actual finding / limits |
|---|---|
| libmono0x196c38 | Export mono_image_open_from_data_with_name begins with a branch to0x14da4, rather than the original function prologue at+4. |
| libmono0x14da4 ->0x3d5fec | ARM veneer changes to Thumb; wrapper resolves g_tprt_pfn_array and reads slot+0x68, index26, at0x3d5ffc. Dynamic relocation record is at mono0x3d8f94. |
| libtprt0x23e68 | Actual original table slot26 contains Thumb target0x33fd. Real Mono entry/veneer/wrapper transfer to0x33fc reproduced, stopping before provider execution. Only the needed GOT/table relocation is supplied; no Android initialization claim. |
| Provider0x33fc–0x3490 | Resolves original function/context and checks provider setup. Initialization failure can call0x31ac with marker0x1a at0x344a–4c. This path is static, not observed on phone or reproduced as actual initialization failure. |
| Enabled path0x3490–0x34ca | Runtime flags gate extra processing. Disabled context forwards to original loader. Branch controls explicitly start at enabled signature branch0x34ca; they do not establish actual Android flag state. |
| Signature0x34ca–0x3512 | MZ takes0x351e. Synthetic non-MZ/non-TXP selects transform mode6 on original input. TXP prefix is copied/replaced then input advances4 bytes; tested lengths4096/8192 select modes7/8. Controls stop before transform0xeb48; they do not decode original DLLs. |
| MZ/name path0x351e–0x35be | Static filename/context conditions can also select transformation for MZ input. Plain MZ is not established as a safe drop-in bypass. Full name/context branch has not been emulated. |
| Pre-load checksum0x35c2–0x3642 | Filename/length conditions can compute CRC over first4096 bytes at0x363a via0xe000, storing pre-load value before original loader call0x35f2. These enabling conditions are not inferred to hold on the historical phone. |
| Post-load0x35fc–0x3618 | Calls monitor/lookup0x802c/0x824c. Missing pre-load or missing/zero looked-up value avoids mismatch comparison. Two nonzero values compare at0x3616; equality returns, mismatch enters guard path0x361a. |
| Lookup0x824c/0x82e6–ee | Static module/mapping lookup can compute first4096-byte CRC through0xe000. Actual module enumeration is not emulated; synthetic controls supply lookup result explicitly. |
| Mismatch0x361a–0x36a4 | With injected zero dynamic-guard configuration, actual original instructions request termination marker0x12 through0x31ac. A dynamic callback/configuration can change this path. Controls intercept0x31ac before any syscall. |
| Termination0x31ac–0x31b2 | Static ARM Linux syscall wrapper sets r7=248, then SVC: exit_group. No syscall was executed by the controls or on a device. Marker18 identifies this examined path, not the historical exit code. |

Native CRC0xe000 was executed on four independent synthetic vectors, including
standard123456789 and4096 zeros; all match Python zlib.crc32. No CRC result,
post-load module result or decoded image is fabricated as a phone observation.

**Important distinction:** this specific comparison checks pre-load versus
post-load values under its enabling predicates. It is not evidence of a hardcoded
trusted hash of the entire original DLL. It cannot establish that every managed
edit must fail, and disabling it is not an evidence-supported correction.

## Actual controls, substitutions and failed exploration

Nine native/bounds test methods passed with explicit pinned sources:
actual Mono-to-provider handoff; synthetic signature selection/MZ distinction;
TXP size classes; native CRC standards; equal/mismatched/absent checksum branches.
Seven preflight/diff controls passed. Host input and originals remain unchanged;
signature copies occur only in isolated synthetic emulator memory.

Fresh PT_LOAD mappings and per-run source size/hash/ISA checks. TPRT controls:
100000 instructions/one second; CRC input<=4096; trace bounded by small control
sites; signature4 bytes and declared length<=16MiB. Mono handoff:128 instructions,
one second. No generic Android linker/runtime/environment completeness.

| Control | Explicit supplied boundary |
|---|---|
| Mono handoff | Synthetic relocation of mono GOT g_tprt_pfn_array and provider slot26 at isolated base0x500000; synthetic args/stack; stop before provider instructions |
| Signature selector | Injected enabled-path entry0x34ca, r4 input and saved length; TXP-only bounded4-byte memcpy0x171dc; stop at0x3512/0x351e |
| CRC | Actual original routine, independent synthetic bytes, no function-success stub |
| Post-load comparator | Injected saved pre-load checksum and context;0x802c singleton supplied;0x824c lookup hash supplied; zero dynamic-guard config; stop before exit wrapper or normal return boundary |
| Preflight | Host PE/CLI range checks only, no assembly execution |

A private exploratory mode6 transformation in uninitialized provider context
changed the first4096 bytes but did not produce MZ. This is **not** a decode,
original corruption or phone failure result; context/key initialization is
unresolved. It was stopped before tail transformation, retained privately, and
not used as positive acceptance. No key/credential was invented. The first TXP
host probe initially omitted its libc copy boundary; that harness issue was fixed
before tests, not classified as a native rejection.

## What is needed to modify reliably

1. Recover the actual historical edited DLL/APK or precise patch offsets/values
   and tooling. Determine whether edits targeted stored protected bytes or a
   decoded PE; compare against the original without changing either.
2. Trace provider initialization and the MZ/name-dependent mode selection using
   the exact version. Establish a byte-identical decode/encode round trip before
   proposing any changed managed image. Current context is insufficient.
3. On a private derived copy, verify decoded PE/CLI/IL and target Mono compatibility,
   then one reversible semantic change. Preserve the provider format and required
   initialization rather than assuming a plain DLL can replace it.
4. Identify the earliest runtime divergence using matched startup/termination
   evidence. Only then choose the minimal correction and request a controlled
   on-device comparison. No blind protection-disable patch is provided here.

Historical modified APK/DLL bytes, exact one-byte offset and matched startup /
termination logs are absent from this runner. No Mono executable or Android game
runtime is installed here. Consequently the exact phone failure remains open;
structural/loadability comparison of the historical edited assembly is unrun.
The current result narrows the investigation to a verified native provider path
and gives reproducible controls; it does not yet deliver a safe modified APK.

## Actual verification

```text
python tools/knowledge.py route 'startup Mono DLL integrity early exit'
python tools/knowledge.py doctor
CF18_TPRT_LIBRARY=<private libtprt> CF18_MONO_LIBRARY=<private libmono> \
 CF18_APOLLO_LIBRARY=<private Apollo> CF18_APK_SOURCE=<private APK> \
 PYTHONPATH=<private deps> python -m unittest discover -s tests -v
  176 PASS, zero skips
python -m unittest discover -s tests -v
  176 total:106 PASS/70 explicit private-source SKIP
PYTHONPATH=<private deps> python experiments/integrity_native_matrix.py --tprt <private libtprt> --mono <private libmono> --apk <private APK>
  native controls and15-member source matrix; reproduced exactly
python tools/managed_image_preflight.py
python experiments/integrity_native_matrix.py
  inactive without explicit private paths
```

Unit/native controls are offline evidence, not a repaired launch. Session findings
and original files are preserved. No scheduled worker was resumed.

## CF18-INTEGRITY-02 — original Unity caller and initialization boundary

Continued from main6144a7cc271ac6b66e3e56b0f4247eb194c5576b; originals and
session lanes unchanged. [Acceptance](../../../coordination/CF18-INTEGRITY-02-ACCEPTANCE.md).
Pinned original Unity11178032 bytes SHA256
fb4577bb258cf8898b904865787c3f2ebae411fae61b6eb08ede21a32a2174c2,
ELF32LE ARM. Actual ELF JUMP_SLOT relocation0xaa924c for
mono_image_open_from_data_with_name resolves PLT0x55f60. Static direct-call scan
locates ARM call0x20f87c. This is the caller in the original file, not a phone trace.

Caller prepares data pointer/length at0x20f858–64, sets need_copy=1 at0x20f878,
status output pointer at0x20f870, refonly0 at stack[0] and name pointer at
stack[4]. Earlier buffer preparation calls0x3e99d8; its file-read helper0x3e98f8
can use a virtual reader or fread. Actual stored APK bytes cannot yet be equated
to the bytes entering Mono: provider initialization and file-reader effects are
not reproduced. Therefore the earlier explanation “unwrap/edit/rewrap” remains
an investigation strategy, not an established sufficient recipe for this build.

Actual native caller controls start immediately after the Mono call0x20f880,
with independent supplied image/status. Image nonnull AND status0 reaches
0x20fb28; null image/status0 and nonnull image/status3 take diagnostic branch
0x20f898. Controls stop there, before diagnostic logging or further processing.
No direct exit is executed or inferred from these branches. A malformed image
load and an explicit protection exit must remain separate candidate causes.
Four new tests pass; the return/status are injected, not a decrypted DLL load.

Original libtprt init_array at0x22458 contains seven nonzero constructor targets
0x27b8,0x2960,0x2a4c,0x2bac,0x2c0c,0x2c38,0x2ca8. Static review identifies
string/container setup, dynamic symbol lookup and mutex/runtime setup. JNI_OnLoad
0x3100 also obtains JNI environment/registers methods. Slot28/0x857c handles
additional runtime metadata/path work; it is not assumed to be a decoder init.
These Android initialization steps have not been emulated completely. No key is
guessed; the previous uninitialized transformation failure is not evidence about
correct decoding. Unchanged-image decode and byte-identical re-encode remain
unachieved. Next offline boundary: exact virtual/file reader and provider setup
before calling the transform; then validate the actual input, not arbitrary modes.

Current canonical checks:180 PASS with explicit private Unity/TPRT/Mono/Apollo/APK;
source-free180 total107 PASS/73 SKIP; doctorPASS. The additional Unity tests use
32 instructions/one second, fresh original PT_LOAD mappings, injected return and
status, and stop before side effects. No transformation or initialization success
is stubbed as completed. No original modifications, deployment or phone run.

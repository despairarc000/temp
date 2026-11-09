# Prepared trust copy conflicts with protected package records

2026-11-09 UTC. Supersedes the earlier claim that lack of a full Android runtime
prevented further investigation. The owner clarified: continue through research
uncertainty; stop for actual tool/turn limits or required owner input. No new
phone attempt or game-file modification was needed for the findings below.

## Evidence and result

CONFIRMED_ORIGINAL_NATIVE_WITH_EXPLICIT_MODELS: original APK SHA256
33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9 and
libtprt SHA256 f608b142822b888f4e5b44bbb0167e8d5c02e1680ea89bab8171aeaab59b4f0a
were actually available and verified. The original native parser reads1210
protected records. Every record names an original APK member; record fields
match its ZIP CRC32 and uncompressed size. Complete original/control/candidate
ZIP payload CRCs were also checked independently.

| Compared private workspace archive | Matched protected records | Original native count guard |
|---|---:|---|
| Exact original |1210/1210|passes|
| Signature-only preparation |1210/1210|passes|
| Scoped-trust preparation |1208/1210|fails|

The two mismatches are AndroidManifest.xml and resources.arsc, exactly the two
changed original members. Synthetic extra unlisted resource preserves the match
count; changing only the original manifest CRC reduces it and fails the native
count guard. This isolates changed protected declarations from merely adding
the trust XML/CA resources. No actual archive CRC was forged or source file edited.

These are privately prepared workspace controls from the same preparation method,
not a newly downloaded/read-back copy of the installed phone APK. The owner's
separate report attests installed phone B and exits4 after update; its preparation
report attests the same changed-original-file pair and unchanged metadata/native
payload. This combination strongly explains B's startup exit, but a matching
phone native call stack/full FileChecker run is not claimed.

## How the former initialization gap was resolved

The native registration constructor0x27b8 executes in the bounded emulator
without substitutions and fills18 method names/signatures. initialize maps to
0x2fcc. The third constructor0x2a4c calls0x538c: normal .tptext preparation,
including original native checksum verification and memory-protection/cache
services. Running that routine in isolated memory returns0 and verifies the
original expected checksum. Only mprotect/cache services are modeled, restricted
to the original requested address ranges and order; no real OS operation occurs.
Source bytes remain unchanged, and no prepared code bytes are dumped/published.
An independently corrupted emulator copy fails the native checksum. This is
normal in-memory preparation, not disabling a check or claiming complete Android
initialization. Earlier no-transform statements describe past turns, not this run.

The revealed FileChecker body0x17e74 calls protected-metadata processing0x4e14.
Java initialize arguments plus native0x63a0 map the relevant inputs to the APK
path and native-library directory. First metadata header is assets/__tpcfinfo.tsa
(272B); its original native parser0x5250 accepts it and resolves the CRC binding
to assets/__tpinfo.tsa (74064B, SHA256
18e881afa5d98318060366a1d85c5b1c5036ec0cd900dbbd88471a86ea6476a6).

An initially empty configuration field produced invalid record contents; those
results were discarded. The actual configuration initializer derives its field
from CRCs of packaged libtprt architecture copies. The audit executes the original
enumeration/composition code using real ZIP names/CRCs through an explicit
archive-I/O model, with no cache hit assumed. No key values are extracted or
exported. The original metadata operations/record iterator then yield valid
records matching all1210 original files. All original payloads remain private.

Native0x43d4 signature composition agrees with independently computed CRC32 of
name plus little-endian size/CRC fields for selected actual records. A host
membership calculation models that source-defined map. Native count branch
0x17df2 is then executed with the resulting counts, stopping at0x17dfa (pass) or
0x17dd4 (failure) before further effects. Failure sets status1, rejected by the
previously verified status predicate, and can converge on the known code4 exit
absent a successful configured fallback. It is not a unique phone exit-site proof.

Symbolic native lookups also identify DetailSecurityCheck, libtersafe.so and
tss_sdk_ioctl. The latter fallback receives command5; the real APK's libtersafe
member was checked against the private local source (1963376B,
SHA256c857cbd6e38e3ecaeed5ea631fcefa7d8ccff4825a30cbf37c10acbdbb516c97).
No SDK call or policy override was sent or executed. That branch remains separate
from the APK-record discrepancy and does not establish a supported override.

## Verification and practical limits

[Read-only audit](../../../experiments/original_package_integrity.py),
[audit tests](../../../tests/test_original_package_integrity.py),
[native initializer/gates](../../../experiments/native_integrity_controls.py),
[native tests](../../../tests/test_native_integrity_controls.py).

Actual result:19 native methods PASS with original TPRT/Mono and5 audit methods
PASS with explicit original/control/candidate APKs. Default suites:24 total,
7 PASS/17 SKIP. Audit validates native header binding, record layout, original
records, signature composition and count branch; mocked services are bounded
standard memory/string/allocation operations, destructor registration and archive
enumeration. Full Android launch, phone call stack and game/session acceptance
remain unverified. No network, phone, install or derived APK was created here.

The metadata verifier accepts the original verification trailer and rejects a
one-byte payload change and a one-byte verification-block change in emulator
copies. Thus a record rewrite alone is not an established repair. A purported
codec mode tested on non-sensitive synthetic input did not create a fresh
acceptable block; static inspection shows it searches for an existing marked
block. No signing capability, replacement signed metadata, private signing key
or completed repair is claimed. Do not call it a verified encoder.

The native harness had retained return hooks across sequential calls, creating
a false budget failure. Hooks now clean up in finally; independent sequential
calls are tested. Long metadata runs use only scoped import/return tracing,
20million instructions/5seconds, with unexpected syscalls refused. Initial
whole-instruction tracing exceeded its budget and was not reported as success.
Page-bounded C-string reads fixed a modeled over-read near the end of stack.

## Next scope decision

The prior private trust-copy preparation preserved native/Dex/DLL/assets and
changed two original Android metadata files. This investigation stayed read-only
with respect to game files. Investigating/preparing a narrowly scoped native or
protection-mechanism change would expand that scope and the owner's earlier
no-patching research instruction. Obtain an explicit owner direction for that
expanded client change; no blanket integrity disable, DLL edit or automatic
installation is authorized/claimed by this finding. No new phone test is ready.

Diary remains near8KiB: no append or archival. Schedules remain paused. Detailed
historical context is in [startup exit evidence](SCOPED_TRUST_STARTUP_EXIT.md).

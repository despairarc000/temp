# Startup controls — do not redo blind DLL patch

Target app: `com.tencent.tmgp.cfmnac`, 2018 Unity Mono-era v1.0.11.11, original XAPK + OBB. The separately re-signed original-code control could reach `Checking for update packages...`; a 5-byte IL update-skip patch and a one-byte changed `Assembly-CSharp.dll` control backed out of app early without a clear crash popup. Original and edited APK contents were compared: managed DLL was the material altered payload; re-signing alone worked. Suspicion of integrity/loader checks remains **HYPOTHESIS**, not established fact.

The old `PermissionGrantActivity` smali has user-cancel exit branch; secondary dex showed zero direct exit invocations. Logs include native/Java initialization warnings, but do not prove which branch terminates on DLL modification.

Preferred path remains **unmodified managed DLL, original OBB, local network service emulation**. Never distribute or commit original client binaries to public `temp`. Further startup patch only on a separate control branch with hash, diff, logs and validated root cause.

See [Drive inventory](../../../sources/DRIVE_MANIFEST.md), [EVIDENCE](../EVIDENCE.md).

## Direct native investigation — CF18-INTEGRITY-01

[New pinned native trace](INTEGRITY_NATIVE.md) confirms original game/firstpass
DLLs are stored as non-PE inputs;13 other APK assemblies have managed headers.
Original Mono image-open entry detours to libtprt slot26. An enabled post-load
nonzero CRC mismatch can request exit_group through marker18; equal/missing hash
negative controls do not. Exact historical edited-DLL exit cause is still unknown.
Do not infer every edit is rejected or try a blind native bypass. Proper provider
initialization/format round trip and historical edited bytes remain prerequisites.
No original file was modified, repacked or installed. User explicitly authorized
this separate offline investigation; scheduled/session work stayed paused.

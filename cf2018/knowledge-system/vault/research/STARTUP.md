# Startup controls — do not redo blind DLL patch

Target app: `com.tencent.tmgp.cfmnac`, 2018 Unity Mono-era v1.0.11.11, original XAPK + OBB. The separately re-signed original-code control could reach `Checking for update packages...`; a 5-byte IL update-skip patch and a one-byte changed `Assembly-CSharp.dll` control backed out of app early without a clear crash popup. Original and edited APK contents were compared: managed DLL was the material altered payload; re-signing alone worked. Suspicion of integrity/loader checks remains **HYPOTHESIS**, not established fact.

The old `PermissionGrantActivity` smali has user-cancel exit branch; secondary dex showed zero direct exit invocations. Logs include native/Java initialization warnings, but do not prove which branch terminates on DLL modification.

Preferred path remains **unmodified managed DLL, original OBB, local network service emulation**. Never distribute or commit original client binaries to public `temp`. Further startup patch only on a separate control branch with hash, diff, logs and validated root cause.

See [Drive inventory](../../../sources/DRIVE_MANIFEST.md), [EVIDENCE](../EVIDENCE.md).

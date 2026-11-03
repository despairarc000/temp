PHONE_XAPK_PACKAGING_SUCCESS (2026-11-03 UTC): owner report CF2018_SIGNATURE_CONTROL_20261103T145351_877789Z_93f59684.txt SHA256c277c47597398115ebdeb78c3ebf90bb386ac0798b6c37c7b4a8463bcee4f1fd reports exact reviewed control APKe851f9f236afe2042f21acf2cd5bd74720d087800c35e4da94996f3fa89c2797, original APK33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9 and all_output_payloads_verified=true. Owner-side source/readback OBB SHA2566855c2f4d339f1039079708eeb78d21072a98bea767caa6c81926c52193bef31; first complete OBB digest reported, not independently rehashed in this workspace. Deliverable CF2018_SIGNATURE_CONTROL_20261103T145351_877789Z_93f59684.xapk. installation_performed=false/android_runtime_tested=false. NEXT owner manually install signature-only control A through usual XAPK installer (ADB not required for install), with original XAPK retained; original-app removal may be needed because signer differs, owner already accepts local reset. Start same bounded startup server before launching; no Google/Facebook sign-in. Observe early exit versus reached screen, capture exact error; no TLS/account/gameplay claim. Scoped-trust B not installed. Diary near cap: no append/rotation; schedules paused.

Manifest-schema correction (2026-11-03 UTC): owner packaging stopped at Unsupported XAPK manifest before output/game changes. Root cause was packager/test assumption manifest_version; original source uses xapk_version=2. Original Drive XAPK tail64KiB read through validated HTTP206; manifest central-directory CRC/size verified, SHA25605a9bab976ba63cd34aa104c96a6860089e3eb2efa23d18ff1b46e36541127bc. Metadata uses package_name and total_size767933772; raw manifest stays private. Fixed explicit xapk_version support, retained legacy alias, reject conflicting declarations; output preserves source field name. Tests7 PASS (fixture now actual xapk_version shape, metadata/expansion/split preservation, legacy and conflict controls). Exact original manifest + original APK/workspace control + full-size synthetic737048867B OBB packaging/readback PASS. No original OBB, owner package output, Android runtime or installation acceptance claimed. Previous5-test fixture repeated wrong schema assumption and was insufficient; superseded for this issue. NEXT owner re-download corrected packager and retry packaging only. Source guard remains unchanged; no APK/OBB regeneration required. Diary near cap: no new entry/rotation; schedules paused.

# Signature-only XAPK packaging — verified route

2026-11-03 UTC. Owner prefers usual XAPK delivery and installer, avoiding manual APK/OBB installation through adb. XAPK is a container, so packaging the same signed control APK with unchanged original OBB preserves the intended first control. It does not bypass Android signer checks: original may still need removal before the test copy installs. Owner says no game progress needs preserving and holds original XAPK.

The [packager](../../../tools/package_signature_control_xapk.py) reads ~/storage/shared/Download/Original.xapk and the staged ~/cf2018_control_test/control.apk. It requires the exact original APK SHA33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9 and the reviewed phone-control SHAe851f9f236afe2042f21acf2cd5bd74720d087800c35e4da94996f3fa89c2797. Four-entry original layout, unique safe paths, one APK/one OBB, package name, manifest version and original APK/OBB size guards apply. Wrong sources are refused before output.

Creates a unique separate XAPK in Downloads, preserving internal filenames and original OBB/icon payloads. Replaces only the APK payload and standard manifest total/file-size/APK-digest metadata. OBB is streamed with source ZIP CRC checking and SHA256 calculation. Every output payload is then independently streamed/read back and compared by SHA256 before the .part file is renamed ready. Writes a separate sanitized report. Original XAPK/staged files are untouched. No game download, installation, uninstall, adb command or game execution.

**Actually performed:** execution recovered after earlier canceled/unavailable environment. [Five synthetic test methods](../../../tests/test_package_signature_control_xapk.py) PASS: payload/metadata preservation and update, wrong original refusal, wrong control refusal, extra-entry refusal and distinct repeated outputs. Fixture fingerprints/sizes are explicitly mocked; production defaults stay pinned to owner's reviewed artifacts.

**Full-size mixed-source packaging check actually run:** original hash-verified private30,884,905B APK, previously verified workspace signature-only APK, and a synthetic737,048,867B zero-filled OBB in a private four-entry test container. Workspace-control fingerprint was substituted only in the harness (it has a different private signer from the phone). Packaging, CRC/readback and report completed. This checks realistic size/streaming and actual APK payload handling; it is NOT a full original-XAPK/OBB verification, the owner's exact control, their installer, Android runtime, integrity-safe startup, TLS, account session or gameplay acceptance. All game-containing artifacts stayed private. The old unexecuted-helper note is superseded only for these stated checks.

Manual packaging, no adb or game/server running required:

```bash
(
set -e
D="$HOME/storage/shared/Download"
curl -fL --max-time 30 \
  https://raw.githubusercontent.com/despairarc000/temp/main/cf2018/tools/package_signature_control_xapk.py \
  -o "$D/package_signature_control_xapk.py"
python3 "$D/package_signature_control_xapk.py"
)
```

Needs roughly another0.8GiB free. Runtime refuses insufficient space. Share only the new CF2018_SIGNATURE_CONTROL_<timestamp>_<suffix>.txt, not the game-containing XAPK. Do not install yet: review report first, then use the owner's usual XAPK installer for signature-only control A. Scoped-trust B is not this deliverable. ADB remains useful for diagnostics but is not required by this packager; installer/OBB permissions on Android15 remain device-specific and untested here.

Diary near8KiB: no new entry/rotation. No phone/live experiment performed. Schedules paused.

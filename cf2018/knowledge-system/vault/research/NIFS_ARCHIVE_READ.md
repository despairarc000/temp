# R100 — Assets.png is NIFS; original reader and bundle manifests validated

2026-11-02. Read-only original-source investigation; no new phone run, server reply, game-file patch, login or gameplay.

**Continuation:** The owner subsequently supplied the original XAPK link. Its base settings and resource-version references are now resolved in [original package settings](ORIGINAL_PACKAGE_SETTINGS.md). The intermediate missing-link statements below are superseded by that continuation.

## Source access blocker resolved

Owner supplied the direct download URL for the previously metadata-only Drive Assets.png. The ordinary download link first returned a small Google confirmation page. Following that page's normal download form produced HTTP206 for a64KiB range, then a complete private download of **431,231,509 bytes**, SHA256 **9cda9c149b6e9c03bba295e5dfa9641d76d5318b345acf5eeafcd5d0acb265f9**. No account credentials or third-party GitHub connection were used. Original bytes remain private.

This resolves the connector's256MiB download limit for this file. **The owner does not need to run the R099 scanner or transfer slices.** The previous UNKNOWN-format statements are superseded: the file starts with `nifs`, not a PNG/standard ZIP/Unity bundle header. Its declared image/png MIME and filename are not its content format.

## Native header verification and archive open

**ORIGINAL_NATIVE_EMULATION / ORIGINAL_ASSET_STATIC.** Each NativeControl instance verifies exact Apollo5,243,704B/SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, ELF32 ARM/Thumb. The original172-byte header's MD5 over its first156 bytes matches its trailing16 bytes independently in Python. Actual original ConvertIFSHeaderToFormat4 **0x293a50** returns0 for this header and109 for either a changed header byte or changed digest byte. Original checksum/MD5 code executes for these controls; only functional bounded libc memcmp is substituted. Original file unchanged.

A local private analysis prototype executes **SFileOpenArchive0x29cd28**, which returns1 and a constructed archive. Source reads include header[0,172], compact table ranges430763923/622B and430764561/9315B, list-file ranges430763230/8B and430763238/669B, bitmap431205216/26293B and validation range430784512/420704B. These are observed read offsets/sizes, not guessed archive semantics for every field. The archive's original hash/table/decompression logic executes. No blanket-success parser substitute or original-code patch.

Explicit runtime substitutions: bounded allocator/free/new/delete/libc operations; read-only virtual stream backed by the private file; single-thread mutex operations; synthetic errno storage; runtime ASCII ctype import tables; functional Python MD5 primitive for the larger validation block, with original comparison/check code retained. Native execution is capped per stage at12M instructions/20s. Initial fixture failures were unresolved runtime imports/limits, not game rejection. Prototype is local research, not a complete cross-platform NIFS implementation or Android execution.

## Configuration bundle and second source-defined layer

Direct native filename lookup for the opaque GCloud resource reference returns null in this archive. A configuration entry **Config/AssetBundleCfg_1.0.9.0.unity3d** exists instead. This is its actual filename; it does not relabel the game or experiment version.

Original TNIFSArchive::OpenFile_i **0x29b66c**, SFileGetFileSize **0x2a1794**, and SFileReadFile **0x2a0d48** return a complete **67,072-byte** entry, SHA256 **cc3c71bd875d5d747675290a99b4fe40cf904e685e2210df10a7a64371b1dfd8**. Initial Unity parsing yields zero objects because those bytes have another layer. Read flags0/1 produce identical bytes for this entry; no general meaning of that flag is inferred.

**CONFIRMED_MANAGED_STATIC:** Exact original DLL SHA256 `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9` verified. AssetBundleResourceManager.LoadGameCfgAB **0x06001755** reads file bytes atIL0xf8, obtains AESHelper parameters at0x101/106, invokes AESDecrypt at0x10b, then CreateFromMemoryImmediate at0x16b. AESHelper source getters0x060026be/bf and decoder0x060026c3 ground the byte derivation, CBC/default padding and32/16-byte parameters. Parameters are resolved only in memory; **no original key, IV or plaintext asset is committed or printed**. This is offline source-defined asset decoding, not managed runtime or game modification.

The resulting plaintext has valid padding and a Unity signature; UnityPy1.25.4 parses9 objects. Wrong-key negative: invalid padding/no Unity header. Wrong-IV negative: padding remains valid but Unity header is invalid. **Padding alone is not successful asset decoding.** These three inline controls were actually run.

## Complete manifest records, limited conclusion

The bundle contains a MonoScript identifying WNEngine.ABInfoJsonCfg and seven MonoBehaviour manifests. Their stripped custom type trees cannot be read automatically. Original managed field definitions ground a bounded reader: AssetsInfoJsonCfg contains AssetID/int, AssetKey/string and three string-array RefAB variants; ABInfoJsonCfg contains AssetsList and LocalAbs. Each object is checked against its script reference and serialized name, then parsed with string/count limits and exact final-byte consumption.

All seven parse completely: asset counts2747/399/1715/1424/1642/0/46, total **7,973**; LocalAbs counts10/50/21/31/69/0/14, total **195**. No asset-key match for GCloudSetting occurs in these decoded maps. This is not proof that settings are absent from the entire game or another packed binary configuration. The R099 original mainData pointer to external7346236864af94314bae0701e3cddcd2 still needs its actual base resource bytes. No endpoint values recovered; no new updater response justified.

## Verification and next input

- Inspector suite **9 PASS**, including two added NIFS checksum controls; it now identifies the actual source as NIFS/checksum MATCH while keeping configuration presence UNKNOWN.
- Original native header test **1 PASS**, comprising original/two corrupted-copy cases0/109/109.
- Manifest suite **2 PASS**, one public source-refusal guard and one private original decoding/full-record test. Source-defined original parameters are never test fixtures in public code.
- Three private inline cryptographic negative/positive controls above; full native archive/open/read prototype observations are separate from these unittest counts.
- Knowledge doctors run; historical local-snapshot omissions remain. No new remote CI result claimed or earlier server regressions relabeled as rerun.

Root Drive metadata and the known CF2018 extracted folder were inspected. The matching extracted APK and unpacked assets are located; the full original XAPK/OBB file was not located through these listings/searches. Do not turn that into a claim it does not exist. The owner subsequently supplied its direct link; [bounded package reads](ORIGINAL_PACKAGE_SETTINGS.md) resolved both base references here. No owner-side scan, game test or speculative reply is required.

Reproducible public checks: [NIFS header control](../../../experiments/native_nifs_header.py), [native test](../../../tests/test_native_nifs_header.py), [manifest reader](../../../experiments/original_bundle_manifest.py), [manifest tests](../../../tests/test_original_bundle_manifest.py), [source inspector](../../../tools/inspect_resource_container.py). Private originals/dependencies must be explicitly supplied; public runs skip original-only tests. No original asset/decoded bundle is published.

# R100 — Original package supplies the missing settings and resource version

2026-11-02. Read-only source continuation of [NIFS archive investigation](NIFS_ARCHIVE_READ.md). No game-file changes, live game/server run or new reply.

## Actual access and provenance

Owner supplied the direct Drive link for file `10GUAbzSZALUBQNAu5FIFV5Wcf3Ck3lef`. Connected metadata names `com.tencent.tmgp.cfmnac.xapk`, **768,008,878 bytes**. The ordinary Google download form and validated HTTP206 byte ranges expose a four-entry ZIP directory: original APK, icon, manifest and **737,048,867-byte** `Android/obb/com.tencent.tmgp.cfmnac/main.11.com.tencent.tmgp.cfmnac.obb`. The outer OBB entry is stored, so bounded ranges can inspect its ZIP without downloading everything. Its directory has **21,204 entries**.

A whole-package download timed out after a partial private transfer. **No complete XAPK/OBB SHA256 is claimed.** The relevant original entries were separately read completely with Python ZipFile, which verifies their central-directory CRC. A local-header CRC field of zero uses the normal data-descriptor path; it is not evidence of corruption. The final bounded inspection used seven validated ranges. Nothing fetched is published as a source asset. The complete APK entry is available within the partial transfer and independently matches the original30,884,905B/SHA256 `33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9`. This grounds the package against the previously verified client instead of trusting its filename.

**ORIGINAL_ASSET_STATIC:** R099's exact APK mainData reference `config/system/gcloudsetting_`, fileID518/pathID1, resolves to OBB entry `assets/bin/Data/7346236864af94314bae0701e3cddcd2`. Complete **10,540 bytes**, SHA256 `bc00133a6bc82a6430dbe5d0ffaf96e6e7e9c883f697fa148180c1d1c1c6dd0b`. UnityPy parses exactly one TextAsset, pathID1/name `GcloudSetting_`, with **6,416-byte** encrypted body. This resolves the actual reference; it is not a filename-substring guess or redacted-metadata payload.

## Source-defined settings decoding and selection

**CONFIRMED_MANAGED_STATIC / OFFLINE_ASSET_DECODE:** Exact original DLL hash remains `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9`. `GetTextReaderForCSV` **0x06000229**, TextAsset bytes atIL0x159, source getters0x15e/163 and AESDecrypt0x168, ground this decoding path. Parameters are obtained only in memory from the exact source; no key, IV, settings values or plaintext table is printed/committed.

The result is valid UTF8, **6,408 bytes**, **24 CSV rows ×20 columns**: header, one descriptor row and **22 settings**. All22 keys were independently matched against the source GCloudSettingKey enum constants. Seventeen columns represent region/language combinations. ParseData **0x06002b5b** loads `CurrentBundleVersion.LocalizationMode` at0x2e/3e; global mode uses Default, other modes format `{0}({1})` at0x39/4d using current language0x48, then read the selected column0x59. `CurrentBundleVersion..cctor` **0x060057b3** initializes global atIL0x47; `ZoneSwitchManager.SwitchLocalizationMode` **0x06000512** can change it. The current phone's mode and persisted language are not established by the initial constant.

`GCloudSettingConfig.GetValueString` **0x06002b61** tests m_Value with IsNullOrEmpty at0x6; branch0xb selects m_Value at0x1b/1c when nonempty, otherwise m_DefaultValue0x10/11. A bounded interpreter executes this original36-byte CIL method on synthetic fields. Four controls verify regional value overrides an empty Default, empty/null regional values fall back, and whitespace is not IsNullOrEmpty. **SYNTHETIC_ONLY / BOUNDED_CIL_INTERPRETATION**, not CLR/Android execution. Thus reading only the empty TVersion Default cannot establish the effective runtime address.

The TVersion regional cells have3 raw DNS-form strings and17 after a separate whitespace-strip comparison. That comparison is a lexical control, **not proof of the runtime CSV trimming result or successful DNS/network use**. The original CSVReader has its own trimming policy; do not silently substitute Python csv semantics. No endpoint, app key, ID or table values are included in public results.

Source getters0x06000181/187/188 select THIRD_TVERSION_SERVER and THIRD_TVERSION_CHANNELID_ANDROID_PUBLISH (the latter in both APK/resource getters). `ProjectSetting.GetTclsConfig` **0x0600018c**, publish callsites0x177/183/19d, carries them toward server setup. `VersionUpdateCheckController.SetupServerConfig`0x0600a961 calls GetTclsConfig0x2. Native updater transport selection/current on-phone request remains unknown.

## Bundled version reference also resolved

Exact original APK ResourceManager maps `config/versionfile` to **fileID755/pathID1**, external `c6a11ba720a945c4a893b4ded55ff305`. Matching OBB entry is **4,128 bytes**, SHA256 `3d91a3e114833ddad3ee87b78f05876c80521571a82ca67f58d9898057d8d5de`, central CRC verified. It contains one TextAsset with numeric resource-version text **1.0.9.0**. ConfigManager.GetTVersion **0x060001ed** loads `Config/VersionFile` at0xf, reads TextAsset.text0x1b and Trim0x2e.

This is the original **bundled resource version**, not a new experiment/game label or a proven value of the phone's persisted resource cache. Mission/client remains2018 v1.0.11.11. Resource updater0x0600a92b also consults persisted package version; extraction0x0600a943 and APK updater0x0600a94c are distinct setup paths. Finding the bundled version does not prove any of these completed.

## Verification and bounded next check

New settings suite **3 PASS**: wrong-source refusal, original complete-resource/table/source-predicate audit, and four synthetic selector cases interpreted from original CIL. Reused manifest suite **2 PASS** after sharing only the in-memory decoder; bundle signature validation remains in the bundle reader, while settings require valid UTF8/CSV/schema instead. Inspector9 PASS and original native header1 PASS remain separate: **15 test methods PASS** across the four suites. Source-free runs skip original-only methods. Knowledge doctors show exactly the same pre-existing snapshot omissions; no remote CI result claimed.

Public [settings audit](../../../experiments/original_gcloud_settings.py), [tests](../../../tests/test_original_gcloud_settings.py), [shared source-defined decoder](../../../experiments/original_bundle_manifest.py). Private originals/dependencies must be supplied explicitly.

**Next bounded check:** match the owner's actual resource-screen text/progress/error after a sustained wait to extraction versus APK/resource updater paths, then trace that selected setup/transport before preparing another phone experiment. Generic Checking resources, a quicker transition or a written directory reply is insufficient attribution. No further owner asset scanning is needed. Real settings-reply acceptance, resource completion, login/lobby and bots remain unverified; schedules stay paused.

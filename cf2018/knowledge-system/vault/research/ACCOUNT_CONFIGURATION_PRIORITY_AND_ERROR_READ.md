# R116 — Regional account configuration and a read-only error discriminator

2026-11-03 UTC. This is source evidence and offline synthetic checking, not a new phone result. Resource startup reached sign-in in R111; account login, game lobby, bot play and fully offline operation remain unverified. Schedules remain paused.

**CONFIRMED_MANAGED_STATIC:** Protected original Assembly-CSharp.dll SHA256 174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9 was inspected read-only, with decoding in memory. WNLogin.ZoneSwitchManager.SwitchTo0x0600050f calls SwitchiTopNBeaconConfig at CIL0x97; overload0x06000510 at0x85. SwitchiTopNBeaconConfig0x06000515 adds IMSDK_SERVER_SDKAPI from ProjectSetting.get_iTop_SERVER_SDKAPI at0x1c/0x21 and IMSDK_SERVER_CONFIG at0x3c/0x41, then calls IMTool.UpdateConfigs0xad. IMTool.UpdateConfigs0x0600a4e7 contains the Android bridge method-name literal updateConfigs at0x17. Generic bridge calls were not executed on Android. This resolves R115's missing managed caller, without proving the phone executed that path.

ProjectSetting getters0x06000165/166 load TVERSION_MODE and compare to4 at CIL0x5/0x6; unequal branches to0x1d. Equal4 passes enum indices31/32; otherwise27/28. Original Constant rows independently map31/32 to IMSDK_SERVER_SDKAPI_SHIPPING/IMSDK_SERVER_CONFIG_SHIPPING and27/28 to the normal keys. Thus TVERSION_MODE selects these account rows; do not substitute the different BUILD_MODE used for lobby fallback.

**CONFIRMED_ORIGINAL_RESOURCE_STATIC:** The APK mainData resource reference config/system/localizationsettingconfig_ resolves fileID602/pathID1, external aeeaa717a8b334366a2e9096b58df6bb. Its OBB entry is already inside the available private partial XAPK. Exact ZIP filename, raw-deflate length and following data-descriptor CRC/compressed/uncompressed lengths were verified. Extracted resource17880B SHA256 a3242408f71255ed852e33dc47d8f197032e233bf8c9c97f54360ad302cf5834; one TextAsset pathID1, LocalizationSettingConfig_. Encrypted asset payload13744B SHA256 7c4f73de37f151f258400bf1dbae01740ad00da044f2f93ec061cdc8e6d18e1d was decoded only in memory through the existing source-defined helper. CSV76x16 includes a descriptor row. Four allowed account/config row names at zero-based CSV rows68,69,72,73 have eight populated regional columns each: na/global/sea/br/ru/we/id/IN. Other columns are empty. No endpoint, app-key, decode parameter or plaintext table is published. Partial package verification is not a whole-XAPK/OBB hash or actual runtime selection.

**CONFIRMED_ORIGINAL_DEX_STATIC:** APK SHA256 33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9. IMSDKConfig.updateConfigs calls updateUserDB. ConfigManager.updateUserDB merges into mUserConfigCache (putAll0xa). getOrDefault checks that cache at DEX0x2..0x26 and returns0x2a, consulting mConfigCache only at0x2c..0x48. Its key-present user entry wins even if empty/null. getOrMetaData may then fall back to manifest data; it does not redo the downloaded-cache lookup. Therefore changing only downloaded configuration cannot replace an existing populated user-cache account host. This is conditional on that cache entry being present; phone cache state and updater execution are UNKNOWN. No unconditional claim that every host override is impossible.

**SYNTHETIC_ONLY negative control:** [Exact-APK bounded selector interpreter](../../../experiments/original_account_config_priority.py) walks the original getOrDefault instructions with synthetic maps, fixed field/call allowlists and48-instruction budget. Six inputs cover populated/missing/null user cache, missing both, empty/null user values. Sixteen downloaded-only replacements all retain the synthetic regional value. This is not JVM/Android execution. [Three test methods](../../../tests/test_original_account_config_priority.py) PASS with original APK; default1 PASS/2 SKIP. Existing24-check account-chain audit remains2 methods PASS with original. Wrong APK is rejected before optional dependency loading.

**Transport limit:** Original default HurlStack constructors pass null URL-rewriter and SSL-factory; openConnection sets a custom SSL factory only if non-null (DEX0x44/0x48/0x56). This path leaves platform TLS in place. No certificate acceptance, global trust state, pinning absence or actual phone TLS failure was established. A SOCKS destination redirect alone does not prove the client will accept local HTTPS.

**Concrete next discriminator:** [Standalone summary script](../../../tools/summarize_account_log.py), with [seven source-free tests](../../../tests/test_summarize_account_log.py), reads an existing local file/stdin or, explicitly with --adb, the running original game's recent PID-filtered log buffer. It never launches the game, clears logs, changes preferences/trust or sends login. The original LoggerImpl.logChunk uses iMSDK tag (DEX0x6/0x12/0x1e/0x2a). Output is fixed exception/status mention labels/counts, unknown-stage warning and timestamp/random-suffix filename, created exclusively. Arbitrary numbers, IDs, token fields, hosts, raw text and exception messages are omitted. HTTP-code labels follow original IMSDKHttpClient$2.onErrorResponse constants: -100 auth, -111 no connection, -110 network, -120 parse, -131 client, -130 server, -140 timeout. Primary1/4/6 are reported separately; mentions are not paired callbacks or login acceptance. Old operations can share these labels. Zero SDK lines is inconclusive.

No Android target/adb connection exists in this workspace. The existing uploaded relay summary contains connection totals, not these SDK error details, and cannot reconstruct them. Wireless-debugging availability is the outstanding owner question; do not assume it or require another login/resource run yet. If already paired/connected, a manual existing-buffer read is:

```bash
(
set -e
D="$HOME/storage/downloads"
curl -fL --max-time 30 \
  https://raw.githubusercontent.com/despairarc000/temp/main/cf2018/tools/summarize_account_log.py \
  -o "$D/summarize_account_log.py.part"
mv "$D/summarize_account_log.py.part" "$D/summarize_account_log.py"
python3 "$D/summarize_account_log.py" --adb --output-dir "$D"
)
```

The owner would share only the generated CF2018_ACCOUNT_ERRORS_<timestamp>_<suffix>.txt. No raw logcat/account database requested. adb must already be installed and manually paired to the owner's phone; this command does not configure it.

Validation: PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s cf2018/tests -p test_summarize_account_log.py -v =>7 PASS. Selector original tests use PYTHONPATH=cf2018/private/analysis_deps and explicit CF18_ORIGINAL_APK;3 PASS. Same command for test_original_account_sdk_chain.py =>2 PASS. Selector without original =>1 PASS/2 SKIP. No phone/logcat/TLS request or real-provider authentication run was performed here.

Both knowledge doctors were run before and after: pre-existing local snapshot omissions remain (66/114 output lines), with zero new error lines. This is not a clean doctor PASS or a claimed CI result.

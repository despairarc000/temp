# R117 — Phone SDK DNS mentions and endpoint-role discriminator

2026-11-03 UTC. **PHONE_REPORT:** owner-supplied CF2018_ACCOUNT_ERRORS_20261103T081313_118563Z_d012dd28.txt SHA256 a5e4ab28f3d0af197a632dcb390abdd010f0ab950638ecdf6b4b764ab62c9fb1. Reader reports RUNNING_GAME_PID_FILTERED_LOG_BUFFER and610 iMSDK-tagged lines. Mentions: BACKEND_STATUS_1=7, SDK_STATUS_1=3, HTTP_NO_CONNECTION=1, NoConnectionError=2, UnknownHostException=2, UNRECOGNIZED_STATUS=2.

These are counts of log mentions, not independent requests or paired login callbacks. SDK/HTTP success mentions can belong to other SDK operations; they do not establish account login or a usable game session. UnknownHostException suggests hostname-resolution failure was logged, but this summary omits the failed hostname and operation. It does not prove Google, Facebook, Tencent account API, SDK configuration or game lobby caused the visible error. Owner was instructed to reach sign-in without a new provider attempt; exact report timing/callback ownership remains UNKNOWN. No raw account log was uploaded or inspected here.

**CONFIRMED_ORIGINAL_RESOURCE_STATIC:** R116's hash-pinned original LocalizationSettingConfig_ resource and protected DLL were read again locally, with plaintext only in memory. Normal/shipping IMSDK_SERVER_SDKAPI and IMSDK_SERVER_CONFIG rows supply32 populated cells and7 distinct canonical DNS hostnames:3 account-only,3 config-only,1 shared. The public reader now contains only SHA256 hostname fingerprints and fixed roles. No original hostname strings, regional value table, decode parameters, accounts or tokens are published. All regions are included; this is a role match against shipped configuration, not runtime region or operation attribution.

**Concrete discriminator:** [summarize_account_log.py](../../../tools/summarize_account_log.py) recognizes only iMSDK-tagged lines with the explicit phrase Unable to resolve host followed by a quoted DNS hostname (also escaped quotes). It lowercases/removes a trailing dot, hashes privately in memory and emits only ACCOUNT_API_ENDPOINT / SDK_CONFIG_ENDPOINT / SHARED_ACCOUNT_CONFIG_ENDPOINT / OTHER_HOST_UNKNOWN_ROLE counts. The shared endpoint is deliberately ambiguous; an unknown hostname is not identified as analytics/provider traffic. Generic exception names, arbitrary URLs or unrelated log tags cannot identify a role. Output stage remains UNKNOWN; exception/class/status mentions remain separate. The old summary cannot be upgraded locally: the omitted hostname is not recoverable from counts.

**SYNTHETIC_ONLY:**11 stdlib test methods PASS. New controls cover exact normalized match versus subdomain mismatch, shared-role retention, escaped-quote DNS extraction without hostname export, and inability to identify service from an exception name/URL/unrelated tag alone. Existing sensitive-field suppression, input-size limit, timestamp/random exclusive files and bounded PID-specific adb command tests remain passing. Command: PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s cf2018/tests -p test_summarize_account_log.py -v.

**Private-source verification actually run:** regenerated the whole7-entry fingerprint map from the original resource and compared for exact equality with reader.HOST_ROLES. Passed all7 original-host cases through the reader in memory and checked expected role and absence of hostname in output. No Android execution or original-host network request was performed here. No account/server/game reply or asset/trust/cache modification.

NEXT one manual download and existing-buffer read while the original game remains running and adb connected. No repeat resource/login experiment required at this stage:

```bash
(
set -e
D="$HOME/storage/downloads"
curl -fL --max-time 30 \
  https://raw.githubusercontent.com/despairarc000/temp/main/cf2018/tools/summarize_account_log.py \
  -o "$D/summarize_account_log.py"
python3 "$D/summarize_account_log.py" --adb --output-dir "$D"
)
```

Share only the newly generated CF2018_ACCOUNT_ERRORS_<timestamp>_<suffix>.txt. A missing DNS role may mean the relevant log text was absent, had another format or rolled out of the bounded recent buffer; it does not falsify earlier DNS errors or establish successful sign-in. Logs are not cleared, game not launched, login not sent, and no raw log text saved by this reader. Schedules paused; game/lobby/bots remain unverified.

Both knowledge doctors retain the same historical snapshot omissions (66/114 output lines); zero new error lines. No clean doctor or CI PASS claimed.

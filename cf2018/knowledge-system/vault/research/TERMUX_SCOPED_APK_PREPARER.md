# Standalone Termux scoped APK preparation

2026-11-03 UTC. Owner authorized preparation/offline checks, not installation. [Prior private control results](SCOPED_TRUST_APK_OFFLINE_PREPARATION.md) remain historical; fresh keys make subsequent output APK hashes differ.

**Deliverable:** [prepare_scoped_trust_apks.py](../../../tools/prepare_scoped_trust_apks.py) is one stdlib Python script embedding the reviewed resource utility. Requires Java/OpenSSL CLI, available as Termux openjdk-17/openssl-tool (confirmed against official aarch64 Packages.gz). No apktool/aapt/zipalign or replacement XAPK download required.

Default reads the installed original APK via paired adb: fixed-package pm path, validated /data/app/.../base.apk path, exec-out cat and exact source hash check. An altered/re-signed installed source is refused. Optional --source reads an existing original APK or bounded APK entries within an existing XAPK, never the OBB. Original files remain unchanged.

Default scope reads only the running game's bounded PID-filtered iMSDK logs. Explicit DNS-error hostnames are matched in memory to the seven original-host fingerprints. Empty/out-of-scope input is refused; only observed accepted hosts are included, potentially fewer than seven. No Google/Facebook domains are allowed. No raw log/hostname enters the shareable report. Optional private --hosts-file enables offline reproduction. No automatic game launch/login or log clearing.

**Dependency download actually checked:** only bytes8177106–9156442 of the official Android build-tools35 ZIP,979337 compressed bytes producing1074241-byte apksigner.jar. HTTP206/exact Content-Range required, decompression capped2MiB and SHA256 pinned to00ef9948f843fe395d2440ae3ef41405b8040a6d5d46493bd1902ac0ee6deae7. Range refusal stops before reading a full SDK. Actual bounded download hash matched. No game download.

**Private outputs:** timestamp/random run directory under ~/cf2018_private_apk_controls, mode0700/umask077. Fresh signing key, local/wrong CA and same-host leaf certs stay private. Signature-only and scoped-trust copies undergo v1/v2 signature checks, exact payload verification and stored-entry4-byte alignment. Original APK/DLL hashes pinned; only manifest/resources.arsc modifications plus two trust resources allowed. OpenSSL accepts the correct CA and rejects wrong-CA chain offline. This is not Android certificate acceptance.

**Report:** uniquely named CF2018_APK_PREPARATION_<timestamp>_<suffix>.txt in Downloads exports fixed verification fields/counts and hashes, explicitly android_runtime_tested=false and phone_installation_performed=false. Do not share private run files/keys. No install/uninstall, global trust change, provider request or game execution.

**ACTUAL OFFLINE CHECKS:** script completed a full build here with explicit original source, private host list and cached exact signer. Both outputs independently passed aapt2 resource parsing, zipalign, Androguard targetSdk26 and resource-ID checks:2999 original IDs retained, exactly two candidate additions. This is workspace/Linux evidence, not Termux execution. Default adb adapters were mocked, not run on a phone here. Eight new preparer tests PASS: embedded-source equality, source/path/host/subdomain/JAR refusal, bounded PID log adapter, HTTP-range refusal before body read and changed-payload refusal. Eight existing binary-resource tests PASS. A verification harness initially lacked private dependency PYTHONPATH; corrected harness passed both APKs. No APK implementation failure inferred from that harness error.

Manual preparation, with paired adb connected and existing game still running; no new sign-in:

```bash
(
set -e
pkg install -y openjdk-17 openssl-tool
D="$HOME/storage/downloads"
curl -fL --max-time 30 \
  https://raw.githubusercontent.com/despairarc000/temp/main/cf2018/tools/prepare_scoped_trust_apks.py \
  -o "$D/prepare_scoped_trust_apks.py"
adb get-state
python3 "$D/prepare_scoped_trust_apks.py"
)
```

Share only the new preparation report, or fixed error message. Do not install APKs yet. If exact installed-source hash fails, use an existing original via --source; do not weaken the guard or automatically download an XAPK.

UNKNOWN: actual Termux result, original source/log availability there, Android installation/integrity-safe launch/TLS acceptance, Google OAuth signing compatibility, account session and gameplay. No new live run/acceptance claim. Diary remains7631B near8KiB: no new entry or rotation; archival needed.

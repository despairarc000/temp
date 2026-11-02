# R098 — Settings reply written; owner reports Checking resources; updater traced

2026-11-02. No new reply variation, game modification or additional phone run during this review.

## Phone report and screen account

**PHONE_REPORTED:** Owner supplied DIRECTORY_CONFIG report SHA256 `6589c0501c249baf4dae35a5bd62d0d9858b6be44d751841afb2a9991b9fd6aa`. No original packets, account/session values or report payload are committed.

Slot1 repeats established discovery sequence and writes169B address reply. Slot2 reports exact CTDir route comparison and only unit-field change; writes63B ACK,54B synthetic auth,91B Bingo. Its171B/body92 request is BY_ID_COMPLETE/LEGACY64/COMPLETE. New `directory_config_reply_written` event confirms **223 bytes written**. R097's227B example was synthetic with other packet/RPC sequence values, not a fixed phone-size requirement.

Slot2 then ends at `deadline_after_auth_attempt`, duration12,224.38ms, client_frames3/client_bytes419 (131+117+171), no `directory_after_reply_frame` event. That deadline label is inherited bookkeeping: the connection had already sent an application request and received the settings candidate. It does not mean the test stopped at authentication or establish client rejection. No later complete frame is reported on that connection before the probe deadline. Slots3/4 are discovery traffic, not an identified updater response or authenticated login.

Owner subsequently says: **"kinda the loading got faster, it went to checking resources quick"**. This is a reported screen change from R096, without screenshot, timed comparison, percentage, or final screen state. Treat "faster" as subjective. The report alone did not establish this visual change; the owner supplied it separately. Whether resource checking completes, stays, or produces an error is currently requested.

## Competing explanation: directory timeout can also advance startup

**CONFIRMED_MANAGED_STATIC:** Exact original DLL hash `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9` checked before in-memory analysis. `LoadingFlowLoginCheckTdirController.RunTimeLimitation` token0x0600a7eb returns30.0f. Base OnFlowStart0x06005df0 reads the virtual runtime limit atIL0x18, binds virtual OnOverTime at0x2e and calls StartTimer at0x3a. OnOverTime0x0600a7ef calls its OnFlowFinish atIL0x3f; that method0x0600a7ed calls base finish at0x20. The ordinary OnDirCallback0x0600a7f1 also has its empty-notice base finish at0xa3.

Thus a later screen can follow a callback or a timeout. No timestamp ties the owner's screen change to either. A source timeout value is not measured phone timing. **Do not upgrade CONFIG_REPLY_WRITTEN into accepted callback, successful authentication, or proven response-caused progression.**

## Separate resource/version machinery in the original client

`LoadingFlowVersionUpdateCheckController.StartFlow`0x0600a868 calls CheckAndUpdateFromTVersion at0x53 (and another conditional site0x94). That controller0x0600a95f reads ConfigManager.GetTVersion at0x64 and starts checking at0x6f. StartCheckUpdate0x0600a960 sets server config, then has distinct APK/extract branches. This is a candidate match for the reported screen, not exact runtime attribution from text alone.

`CheckIfNewResourceExsists`0x0600a968 starts IIPSClient.BeginUpdate at0x30. IIPS Tick0x0600a912 drives StartCheckUpdate at0x79; IIPS StartCheckUpdate0x0600a90b calls StartCheckIfNewVersionExists at0x7. The latter0x0600a90d creates IIPSMobileVersion's manager at0xac and invokes MgrCheckAppUpdate at0xc7. Separately, extract decision0x0600a93f compares packaged/persisted resource versions at0x3e; extract StartCheckUpdate0x0600a942 can call ExtractLocalPkgSuccess at0x5f. APK tick can proceed to extraction; extraction tick can proceed to resource update. Local extraction/checking and remote version/update work are distinct alternatives.

The progress renderer0x0600a98c references distinct localization fields including UIText_Update_CheckingMd5 and UIText_CheckResourceMD5. Their English translation and the exact on-phone state are not recovered from the owner's short description. Runtime limit for the outer version-update flow0x0600a86b returns0.0f; this alone does not prove no timeout/retry inside IIPS.

**CONFIRMED_NATIVE_STATIC:** Original Apollo hash `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8` checked. It contains the native updater; it is not necessary to assume a missing standalone IIPS.so. A conditional GCloud updater implementation (`dolphin::gcloud_version_action_imp::run`) constructs RpcConnector at0x32fbe2→0x3c31a0, initializes it at0x32fc74→0x3c4530, calls doGetVersion at0x32fd9a→0x32e6d4, and updates the connector at0x32fdf8→0x3c5248. doGetVersion constructs VersionUpdateClient at0x32e6f8→0x33effc and fills its request at0x32e7ac→0x32e538. **Six exact direct-call checks PASS.** Another legacy version_action_imp also exists; the actual phone's selected updater/endpoint/request is UNKNOWN. No new updater reply is justified yet.

Original APK availability was independently rechecked:30,884,905 bytes/SHA256 `33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9`. ZIP entry names inspected read-only; no original library/assets extracted or uploaded this run. No game/CLR/native updater execution, live server call or patch.

## Validation and next discriminator

[Auditor](../../../experiments/startup_resource_source.py) and [tests](../../../tests/test_startup_resource_source.py): **3 test methods PASS**, comprising23 managed predicates,6 native direct calls and wrong-build refusal. Initial native verifier had an incorrect constructor target constant; exact original inspection corrected it to0x3c31a0 before PASS. A default source-free run passes the guard test and skips2 private classes. No server behavior changed, so the earlier113 server regressions were not relabeled as rerun.

Both knowledge doctors ran; historical snapshot link omissions remain. As in R097, those targets exist in the current remote repository; new report links resolve locally. No new remote CI result claimed.

**Next bounded check:** obtain the current exact screen text/percentage or error, then match it to the resource/extraction/version state before changing the server. If another connection is implicated, identify its original updater route/operation first. Do not repeat the directory test solely to produce the same223B-written event, assume a generic resource label proves a particular network request, or send a speculative version-success response. Goal remains original offline bots; login/menu/gameplay still unverified.

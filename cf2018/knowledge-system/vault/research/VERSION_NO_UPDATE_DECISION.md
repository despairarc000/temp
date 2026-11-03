# R104 — Original no-update decision reaches the native bridge; managed success branch verified

2026-11-03 (Asia/Manila). Read-only original-source analysis with synthetic local inputs. No game/phone/server run, packet sent or game-file change.

## New result and its boundary

The original updater has a **no-update result path** distinct from optional/forced update handling. Segmented original native execution now carries a synthetic typed response through the actual scalar response assignment, decision blocks, event constructor, event dispatch and plugin callback to a synthetic managed-delegate boundary. Independent original managed-source checks show no-update conditions call `GotoState(ClientState.Succeeded)` for the APK/resource updater instances. This is a verified component/source path, not a complete accepted network reply, CLR/Android execution, resource completion or playable game.

## Decision source and negative controls

**CONFIRMED_NATIVE_STATIC:** Hash-verified ARM32/Thumb Apollo remains5,243,704B/SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`. `CreateNextAction`0x32f35c calls manager virtual slot0x2c. CActionMgr's effective vtable0x4ee8f8 binds that slot to **GetUpdateType0x2f20b8**, which reads factory+0x60 through manager+0x6c. This refines R103's unnamed configuration selector: it is the manager's update type, not the unrelated localization mode.

Manager values20/22 enter the app-family block0x32f3ca;21/23 enter resource-family0x32f734; other-mode fixture0 goes to0x32fa5a. Reply update kind is stored at self+0xe8 after actual ResVersionUpdate assignment. Decision/version blocks begin at0x32f46a (app) and0x32f76a (resource).

| Reply update kind | App flags: app / need / forced | Resource flags | Observed native branch |
|---:|---|---|---|
|0|1 /0 /0|0 /0 /0|No-update result boundaries0x32f4e2 /0x32f7ee|
|1|1 /1 /0|0 /1 /0|Update handling0x32f534 /0x32f896|
|2|1 /1 /1|0 /1 /1|Update handling; forced flag set|
|3 (negative control)|0 /0 /0|0 /0 /0|Still update handling, **not** the no-update branch|

The kind3 control disproves identifying the no-update branch solely from three zero flags. It is not labeled a supported reply kind or sent to the game. Manager modes were not observed on the phone; the two modes within each family are not assigned extra semantic names without evidence.

## Actual scalar copy and native event/plugin bridge

**ORIGINAL_NATIVE_EMULATION / SYNTHETIC_ONLY:** Original ResUpdateCallBack0x32d864 and **ResVersionUpdate::operator=0x33c214 execute**, replacing R103's whole-response assignment substitute with the original generated scalar assignment. Synthetic GNU string pointer assignment/copy and version-text conversion remain runtime substitutes; these do not establish original string ownership/content validity. A test-only64-bit version `0x1111222233334444` and update kinds0–3 survive assignment into self+0xc8/e8. This number is synthetic test data, not a game/resource/experiment version label.

The original mode getter/dispatch executes using a bounded synthetic manager/factory. Explicit boundaries stop at the selected family entry; intervening string/configuration/action-factory work is skipped before resuming original decision blocks with the copied scalar data. No complete CreateNextAction invocation is claimed. Zero RPC status/result reach decisions; either nonzero callback status or result prevents entry in the negative controls.

Original CAppCallbackVersionInfo constructor0x3257e8 copies the24-byte tag, DoEvent0x2f441c dispatches it, and **PluginVersionMgrCallback::OnGetNewVersionInfo0x2a3030** forwards it through the original plugin vtable0x4ed810. A synthetic delegate/handle captures the24-byte structure at the final managed boundary. All three flag bytes and version parts0x1111/2222/3333/4444 are preserved. No CLR, managed GCHandle target or actual application delegate runs. Full object/callback registration, scheduling and file actions are not simulated as accepted.

## Original managed consumer

**CONFIRMED_MANAGED_STATIC:** Exact protected DLL SHA256 `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9`, read-only/in-memory metadata. VERSIONINFO fields0x0400ba91/92/93 are `isAppUpdating`, `isNeedUpdating`, `isForcedUpdating`, each U8 (field signature0x06/0x05), matching the native bridge's initial three bytes.

ClientState.Succeeded is **7**, independently resolved from its Constant row and owner enum, not inferred by ordinal. `IIPSClient_ApkIpa.OnGetNewVersionInfo`0x0600a94e tests need-update0x3b/40, then forced-update0x47/4c. With both false it reaches0x147 and GotoState7 at0x159. Need-update true or forced-update true takes the update-handling side. `IIPSClient_Resource.OnGetNewVersionInfo`0x0600a92c tests need-update0xd8/dd; false jumps0x2d7 and calls GotoState7 at0x2e9, followed by CheckApkNeedToInstalled0x2ef. These seven source predicates pass; they are not interpreted managed execution or a claim that installation/other startup stages finished.

## Validation and next check

Native decision suite **8 methods PASS**: four invalid-input guards;17 synthetic cases including mode families, optional/forced/unknown-kind controls, unsupported manager mode, and callback failures. Fourteen decision cases cross the original native event/plugin bridge. Managed source suite **2 methods PASS**, including wrong-source refusal and seven exact source predicates. Total **10 methods PASS**. Source-free runs give2 PASS/8 SKIP. Commands use `python -m unittest discover -s cf2018/tests -p test_native_version_decision.py -v` with explicit private CF18_APOLLO_LIBRARY/PYTHONPATH, and the corresponding `test_managed_version_no_update.py` with CF18_MANAGED_LIBRARY/CF18_DIRECTORY_IDENTIFY_PREPARED. No earlier server baselines relabeled as rerun; doctors remain blocked by historical local snapshot omissions.

Public [native segmented controls](../../../experiments/native_version_decision_controls.py), [native tests](../../../tests/test_native_version_decision.py), [managed source checks](../../../experiments/managed_version_no_update_source.py), [managed tests](../../../tests/test_managed_version_no_update.py).

**Next bounded check:** verify generated VersionUpdate receiver/pending correlation and a complete explicit typed no-update component with matching synthetic product/sequence/version fields. The real phone's version request still has not been identified. A no-update response must reflect the matching request/local source versions, not a guessed empty object; no candidate is yet sent. No new phone test needed for this next offline work. Unique owner deliverable names and paused schedules remain in force.

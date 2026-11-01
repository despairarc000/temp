# R051 — Original standalone match entry, game builders and bot-spawn prerequisites

Date 2026-11-01. **ORIGINAL UNITY STATIC, no runtime test or authenticated session.** Read-only original 2018 Assembly-CSharp.dll, SHA256 `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9`, 13,423,104 bytes. No DLL/APK/OBB changes or bytes committed.

## Reproducible audit

Build-pinned offline CIL audit checks **28 method-call opcode/token pins plus eight literal/branch pins across 13 methods**. **36/36 exact original pins PASS**, **9/9 focused tests PASS**, including every missing/wrong target, constant mutation, short/fat header fixture, wrong-hash refusal, and exact original gated test. Source-only kit in the user's chat: `cf2018_R051_Standalone_Research_Kit.zip`, SHA256 `1758505a079d6a4df551f4801ab64202e7db9f4016359921e37bbdb7a49b0ef3`. No original game code is shipped.

## Standalone map stage: verified ordering

`WNGameBase.LoadingStage.OnLoadMapComplete` RID37919/RVA0x340648 first confirms a match map (IL+0x0b3), calls `WNOnlineSubSystem.StartProcessProtocol` (+0x0c3) **BEFORE** `LogicalMapStore.IsStandalonePVE` (+0x0ef). If standalone, then `ProcessInitWorldGame` (+0x11d), sets `GameInfo.GameSubType=2` (+0x127/+0x128), and invokes **short** `EnterGame()` (+0x12e). Otherwise uses subtype1 and **longer** `EnterGame(localPlayer,location,rotation)` (+0x16c). The world is initialized BEFORE the subtype2 assignment. This is a code-order observation, not evidence startup needs a remote server response.

Short `LoadingStage.EnterGame` RID37917/RVA0x3405e8 is 12 CIL bytes and just activates stage3. Longer `EnterGame` RID37918/RVA0x3405f8 is 67 bytes and explicitly calls `BaseGame.PlayerLogin` (+0x2f) and `LocalPlayer.CreateInitialPlayer` (+0x3c). Thus setting subtype2 or activating stage does NOT itself prove local player/spawn initialization. Other paths may fill that gap; trace them.

## Map-mode gates are not an offline menu shortcut

`LogicalMapStore.IsStandalonePVE` RID24181 calls `IsMapModeType(mapId,2)`; separate `CheckMatchTypeStandalonePVEByMapID` RID24248 checks match type against 0x3001, 0x3002, 0x3003. The latter is used in PvP and Team menu **latency warning checks**: `PVPModeMenuController.OnStartMatchBtnClick` RID27128 calls `IZoneServer.GetLastSendDuration` at +0x23a, the standalone-type predicate +0x25b, and normal `StartMatchProcess` at +0x2c0/+0x2cb. `TeamModeMenuController.OnStartMatchBtnClick` RID28518 similarly calls zone latency +0x158, predicate +0x179, and normal `StartMatchProcess` +0x1de/+0x1e9. The predicate affects whether the ping-warning branch is taken, **not proven ability to start an unauthenticated local match**.

## Builder and assets depend on data

`WNStageManger.ProcessInitWorldGame` RID801/RVA0x12c40 calls `SceneStore.GetGameModeWithMapId` (+0x0d), `GameConstructFuncCenter.GetGameConstructFuncByMode` (+0x14), `WorldManager.InitWorld` (+0x3d), and `BaseWorld.PostInitGame` (+0x6d), with a no-builder early-return branch. `GameConstructFuncCenter.GetGameConstructFuncByMode` RID22978/RVA0x1d2ae4 looks up `GameDefManager.GetGameDefByTag`, then uses `System.Type.GetType`, `Type.GetMethod` and `Delegate.CreateDelegate`; embedded method name `CreateGame`. Config-driven game mode-to-builder mapping is required; seeing the builder class does not prove the active mode resolves to it.

`GameDefManager.ParseGlobalGameDef` RID10309/RVA0xcc05c loads resources named **`Config/GlobalDef/GlobalGameDef`** and **`Config/GlobalDef/GlobalMapDef`**, with error logging if missing. Connected Google Drive search did not find files with these exact names. They may be embedded in asset bundles; resource presence and usable definitions are not yet verified.

## Original local AI constructs exist, not an observed playable bot match

`WNTrainGame.AITrainGameBuilder.CreateGame` RID54387/RVA0x460b70 constructs `WNTrainGame.AITrainGame` (newobj IL+0x08). `TrainAIPawnSpawnCheckerController.SpawnAIPawns` RID54581/RVA0x465074 iterates checkers and calls `AIPawnSpawnChecker.Activate` (+0xac). Separately `AIPawnSpawnPoint.SpawnAIPawn` RID47449/RVA0x3d3e68 calls `ActorSpawner.SpawnActor` (+0x14). These are NOT a verified single runtime chain; bot and local player construction remain to be established.

## Next investigations

1. Locate/read original Unity/OBB resource definitions `GlobalGameDef` and `GlobalMapDef`, choose an actually configured standalone-compatible map, and verify builder registration.
2. Follow `WorldManager.InitWorld`/`BaseWorld.PostInitGame` to establish how the standalone player and AI controllers/spawn points are constructed.
3. Independently continue R049/R050 native GCloud route-supplier and `0x1002` ACK/session work. No blind phone test, no login/gameplay claims.

**Current conclusion:** standalone simulation is present, but menu/startup/service dependencies and a playable bot-match have not been resolved. R051 is offline original-code progress, not login bypass.
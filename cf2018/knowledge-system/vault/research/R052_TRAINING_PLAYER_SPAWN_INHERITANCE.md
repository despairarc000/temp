# R052 — Original AI training-game inheritance reaches local player spawn

Date 2026-11-01. **EXACT ORIGINAL UNITY MANAGED STATIC, not a runtime test.** Source is private original 13,423,104-byte Assembly-CSharp.dll, SHA256 `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9`. All decoding in memory; original DLL unchanged and not committed.

## Evidence and reproducibility

R052's new read-only SHA-pinned auditor verifies **seven ECMA-335 TypeDef inheritance entries and 14 exact CIL opcode + method-token pins** from eight original methods. **21/21 checks PASS on the original, 7/7 focused tests PASS** including every negative type inheritance mutation, every changed opcode/target and the exact-original gate. Together with R051 this is **57/57 original code pins and 16/16 focused tests**; none is an Android gameplay or server acceptance test. Combined source-only chat kit `CF2018_R051_R052_Standalone_Source_Kit.zip`, SHA256 `43d72977b7c488c7fac451094676dc9e51239c4a4049c9c46a529aa23ff8113d`, includes no proprietary game DLL.

## Inheritance proof (original ECMA-335 TypeDef.Extends)

- `WNTrainGame.AITrainGame` (TypeDef RID7062) **extends** `WNStoryGame.StoryGame` (RID7118).
- `WNStoryGame.StoryGame` (RID7118) **extends** `WNPVEGame.PVEGame` (RID6930).
- `WNPVEGame.PVEGame` (RID6930) **extends** `WNGameBase.WNGame` (RID8780), which extends `WNEngine.BaseGame` (RID894).
- Training builder also inherits down the chain: `AITrainGameBuilder` RID7063 -> `StoryGameBuilder` RID7119 -> `PVEGameBuilder` RID6931 -> `WNGameBuilder` RID8782.
- AITrainGame's seven defined managed methods (RID54379–54385) do not define a new `StartMatch`; absent unseen runtime overrides, its `StoryGame.StartMatch` is inherited. This is static class/method metadata, not a phone invocation trace.

## Exact match-start and local player code flow

1. `WNTrainGame.AITrainGameBuilder.CreateGame` RID54387/RVA0x460b70 creates an `AITrainGame` via `newobj` at IL+0x08.
2. `WNStoryGame.StoryGame.StartMatch` RID54885/RVA0x46c424 calls `WNPVEGame.PVEGame.StartMatch` at IL+0x01, then gets local player, sets camp1, changes game state and emits round-start notification.
3. `WNPVEGame.PVEGame.StartMatch` RID53729/RVA0x452cc4 calls the WNGame base start (+0x01), then `PVEGame.InitialLocalPlayer` (+0x07), calls game event channel `OnMatchStarted` for relevant channel instances and optionally resets score.
4. `PVEGame.InitialLocalPlayer` RID53730/RVA0x452d30 obtains `GameTool.get_LocalPlayer` then calls **no-arg** `LocalPlayer.CreateInitialPlayer` (IL+0x05).
5. `WNEngine.LocalPlayer.CreateInitialPlayer` RID11092/RVA0xd87dc gets the world/game, creates a player controller (+0x36), switches to it (+0x3e), calls **`BaseGame.SpawnInitialPawn` (+0x4b)**, applies prop and bag information (+0x52/+0x58), and calls `BaseGame.RestartPlayer` (+0x5e). It assumes a live GameWorld/BaseGame; it cannot spawn if world initialization failed.
6. Independently `WorldManager.InitWorld` RID15074/RVA0x1262a0 constructs BaseWorld and calls its `InitGame` (+0x33). `BaseWorld.InitGame` RID7604/RVA0x9aaa4 invokes configured `GameConstructFunc` (+0x25) to create the game before calling BaseGame.Init. Therefore mode/builder configuration from R051 is required before any inherited training-match path can produce a player.

## What this resolves versus what remains

R051 found the shorter standalone `LoadingStage.EnterGame()` overload does **not itself** call `PlayerLogin`/`CreateInitialPlayer`. R052 now identifies the **separate inherited PVE `StartMatch` path** that does call the local player and pawn creation. So absence of explicit player creation in the stage-only overload does **not** imply the training game lacks it. We have closed a static source gap, not achieved a running match.

Still unresolved: whether the original client's standalone scene reaches **this game type's StartMatch**, whether valid map-to-mode and game builder definitions are available in assets (`Config/GlobalDef/GlobalGameDef`, `GlobalMapDef`), whether the correct player/avatar/weapon prefabs load, which AI controllers/spawn points are registered, and whether local maps/bots can run with no authentication. Network login remains a separate, unsolved track.

**Next priority:** extract or inspect only the necessary map/mode definition assets from the owner's extracted OBB/Unity data, pin a real standalone-compatible map and builder, then trace the match-start trigger and bot spawner. No speculative phone login/ACK experiment or direct-injection patch warranted yet.
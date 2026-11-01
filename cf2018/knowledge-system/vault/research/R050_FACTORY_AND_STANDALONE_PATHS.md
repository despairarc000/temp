# R050 — Original connector lifecycle and existing standalone gameplay path

2026-11-01. **Read-only, hash-verified original static code.** No live phone experiment, login, or gameplay claim. The original Unity Assembly-CSharp.dll and Apollo native ELF remain private; sanitized offsets and findings only.

## GCloud factory lifecycle: route not present at construction

Original native libapollo.so (5,243,704 bytes, SHA256 4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8) checked by ARM Thumb LLVM disassembly. **19/19 exact instruction/operand pins matched the original**, across bounded native functions. This check was run locally; the standalone R050 auditor was not committed because the repository tool rejected that write. Do not assert an R050 CI result.

CGCloud::CreateApolloConnection at 0x3c7e38 allocates 0x1d8 bytes (0x3c7ed2), invokes CGCloudConnector constructor at 0x3c7ee6, then returns the connector interface subobject at +0x14 (0x3c7f50). The two original constructor variants at 0x3c75a8 and 0x3c7784 both create an internal connector-init object (0x3c7634/0x3c7806) and set the TGCP pointer +0x198 and stored route pointer +0x19c to **zero** (0x3c766a/0x3c766e; 0x3c783c/0x3c7840). This means no named-route object is present at construction as inspected; it does not rule out later initialization/route changes.

R048's independently verified CGCloudConnector::Initialize at 0x3c60b8 receives an optional route at init structure +0x48, gates null, and dispatches through verified virtual SetRouteInfo slot+0x20. R047 cloned pointer is stored at +0x19c. R046 follows it into the TGCP type4 SYN writer. The actual caller that populates this initialization field, including the 10-byte name observed after R037, remains unknown. The mere existence of ReadFrom for serialized init info does NOT prove phone runtime populated the route from deserialization; it may be built in memory or sourced from configuration.

## Real application contains a separate local/standalone gameplay path

Original protected Assembly-CSharp.dll from connected Drive, 13,423,104 bytes, SHA256 174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9. Read-only CIL metadata/MethodDef mapping (no DLL edits) verified:

- WNEngine.GameInfo.IsStandalone, RID 10555/RVA0xcfd78, ten-byte CIL, checks m_GameSubType field 0x04002356 == constant 2.
- WNGameBase.NetSyncModule.NetWorkSend, RID65085/RVA0x54f5a4 and RID65086/RVA0x54f5d4, both have 36-byte method bodies; IsStandalone is evaluated first. Standalone returns false rather than calling IGameServer.Send. This is a specific game-server message suppression, not evidence all online services are bypassed.
- WNGameBase.LoadingStage.OnLoadMapComplete, RID37919/RVA0x340648, 532 CIL bytes; at CIL+0xef invokes LogicalMapStore.IsStandalonePVE; later sets GameInfo.GameSubType using literal 2 at CIL+0x128 (contrasted with literal 1 in another branch) and calls LoadingStage.EnterGame at CIL+0x12e. The same method contains login/relogin/online flow code for other map paths. Presence of this branch does NOT show it can be reached unauthenticated.
- WNGameBase.WNStageManger.ProcessInitWorldGame, RID801/RVA0x12c40, calls SceneStore.GetGameModeWithMapId, GameConstructFuncCenter.GetGameConstructFuncByMode, WorldManager.InitWorld and GameWorld.PostInitGame; proves mode/map-dependent world building code exists.
- WNEngine.TakeDamageComponent.TakeDamage, RID9611/RVA0xc11b0, checks IsStandalone and can call Pawn.SimulateTakeDamage, Pawn.Die and kill-count bookkeeping in local simulation.
- WNPVPGame.PVPGame.StartMatch, RID61206/RVA0x4e4c98, calls WNGameBase.WNGame.StartMatch; latter RID68425/RVA0x58ff2c sets up game physics, player input, match events and dynamic colliders.

## Decision and remaining blockers

Login is NOT the game's final challenge. The eventual offline goal still requires assets/map loading, match startup, local AI controllers/pawns, combat rules, and persistence. StandalonePVE may offer an alternate local-game route, but does not itself establish offline PvP BOT matchmaking, launch or bots. Do not replace server emulation work prematurely: retain two lanes: (A) native GCloud route source and correct ACK/session handling; (B) original scene/map/standalone entrypoint and bot spawning. Prioritize offline static checks until one falsifiable, bounded phone test is defined.

Current verified outcome: original connector initially has no route, and original Unity code has a local simulation branch. The unknown route-name source, authentication and playable game remain unsolved.

## Further standalone map classification (original Unity CIL)

`WNEngine.LogicalMapStore.IsStandalonePVE` (RID24181, RVA0x1e4aac) calls `IsMapModeType` with mode class constant 2. `CheckMatchTypeStandalonePVEByMapID` (RID24248, RVA0x1e5a88) calls `GetMatchTypeByMapID` and compares the match type against three original constants **0x3001, 0x3002 and 0x3003**. This narrows standalone map eligibility; it does not establish that any desired PvP bot map is in that set.

`LoadingStage.OnLoadMapComplete` uses two distinct `EnterGame` overloads: its standalone subtype-2 branch invokes RID37917/RVA0x3405e8, the 12-byte overload that activates a stage; the other branch invokes RID37918/RVA0x3405f8, whose longer 67-byte body also calls `BaseGame.PlayerLogin` and `LocalPlayer.CreateInitialPlayer`. Do not assume that the simple standalone stage activation performs all player initialization or bypasses game startup checks.

`WNTrainGame.AITrainGameBuilder.CreateGame` (RID54387/RVA0x460b70) calls the local `AITrainGame` constructor. `GameConstructFuncCenter.GetGameConstructFuncByMode` (RID22978/RVA0x1d2ae4) resolves builder types using `GameDefManager`, reflection, and `Delegate.CreateDelegate`; `WNStageManger.ProcessInitWorldGame` uses that construct-function center. This supports a **separate offline scene/bot-research lane**, not confirmation that PvP TDM/Bomb bots launch without lobby.
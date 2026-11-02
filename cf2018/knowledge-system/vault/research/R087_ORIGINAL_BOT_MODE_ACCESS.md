# R087 — Where 2018 CrossFire: Legends Bot Mode was actually accessed

**2026-11-02. HISTORICAL UI DOCUMENTATION + EXISTING HASH-SCOPED MANAGED ANALYSIS.** No phone login, offline match or bot run in this investigation; no original binaries, extracted assets, credentials or runtime data committed.

## A. Historical UI route is clear

A historical BlueStacks guide, *Crossfire Legends Ranked Matches and Bot Battles*, says **"Bot battles can be reached under the PvP menu"**, and documents **Team Deathmatch and Demolition** against bot-controlled teams with **Easy, Hard, Nightmare** difficulties. Its screenshots show a *Bot Mode (Hard)* lobby with both teams. Source: https://www.bluestacks.com/blog/game-guides/crossfire-legends/crossfire-legends-ranked-matches-guide-en.html .

A September 27, 2018 Uptodown review says TDM and Demolition bot modes can be played without an Internet connection: https://blog.en.uptodown.com/crossfire-legends/ . The community Bot Mode page describes a bot room with a human player, four allied bots, and five opposing bots (https://crossfirelegends.fandom.com/wiki/Bot_Mode). These are historical descriptions, **not proof of a fresh-install airplane-mode launch before first-ever login**.

Documented historical user-facing route:

**Normal game interface → PvP → Bot Mode / Bot Battle → TDM or Demolition / map and difficulty → bot room → match.**

Ordering/availability of specific map/difficulty controls may vary by build. Do not invent a direct offline option on the login/title screen; none is demonstrated by these sources.

## B. Original 2018 code already confirms local simulation, but NOT this Bot Mode entry

Existing [R050 exact-original static findings](R050_FACTORY_AND_STANDALONE_PATHS.md) identify:
- `WNEngine.GameInfo.IsStandalone` checking game subtype **2**;
- `WNGameBase.NetSyncModule.NetWorkSend` exiting without game-server sends for that subtype;
- local `TakeDamage` / pawn simulation;
- `WNGameBase.LoadingStage.OnLoadMapComplete` checking `LogicalMapStore.IsStandalonePVE`, building a world, setting subtype 2, and taking a **short** `EnterGame` overload.

Existing [R051](R051_STANDALONE_MATCH_ENTRY_AUDIT.md) adds decisive sequencing:
- `LoadingStage.OnLoadMapComplete` invokes `WNOnlineSubSystem.StartProcessProtocol` **before** its standalone map check. Calling an online-named subsystem alone doesn't prove it uses a server, but this is not a demonstrated login-free entry.
- `LogicalMapStore.IsStandalonePVE` checks map mode type 2; a separate standalone match predicate checks types `0x3001/0x3002/0x3003`.
- `PVPModeMenuController.OnStartMatchBtnClick` and `TeamModeMenuController.OnStartMatchBtnClick` check zone latency and a standalone-type predicate, then call normal `StartMatchProcess`. **These generic click handlers are not proven to be the exact Bot Mode selection handler** and their standalone check can merely influence ping-warning logic.
- The short standalone `EnterGame` only activates a stage; the longer normal entry additionally calls `BaseGame.PlayerLogin` and `LocalPlayer.CreateInitialPlayer`.
- `ProcessInitWorldGame` requires a mode-to-builder mapping, `GameDefManager`, `WorldManager.InitWorld` and game post-init.

Existing [R052](R052_TRAINING_PLAYER_SPAWN_INHERITANCE.md) identifies a **separate local training** source chain:
`AITrainGameBuilder.CreateGame` → `AITrainGame` (inherits StoryGame/PVEGame) → inherited `StartMatch` → `PVEGame.InitialLocalPlayer` → `LocalPlayer.CreateInitialPlayer` → `BaseGame.SpawnInitialPawn`. This shows that an AI-training-game **can have** a local player path when correctly constructed, **not** that the historical PvP Bot Mode lobby takes that path.

**DO NOT CONFLATE** the historical PvP Bot Battle UI, StandalonePVE, or AITrainGame based only on all three using locally managed AI/gameplay objects.

## C. How this relates to the current login blocker

Normal menu access appears gated by the client startup/login sequence in our current phone observations; [R044 managed login callgraph](R044_DRIVE_MANAGED_CALLGRAPH.md) shows a lobby connector and login callback, while actual phone R077 has reached only the second service SYN with its ACK deliberately withheld. We have **not observed** the historical bot lobby with the current original 2018 installation.

It is plausible that **bot combat** could run locally even if **mode selection and entry** require earlier online initialization or downloaded configuration. What does *without Internet* in the 2018 review mean—first launch, post-login disconnected play, or cached data? The historical sources do **not** settle that.

## D. Assets and menu handler gaps checked this turn

Connected Drive contains the original unpacked game tree and Unity `assets/bin/Data` serialized scene files. Exact-name Drive searches for `GlobalGameDef`, `GlobalMapDef`, `AITrainGame`, `BotMode` and `SceneStore` returned no named files. **This does not prove the resources are absent**: Unity may store them inside binary serialized level files, resource archives, or an OBB disguised as a PNG file. As of this audit, we have **not** extracted a verified map→mode→builder record proving an offline Bot Mode UI selection.

The current retrieved `Assembly-CSharp.dll` bytes are protected/opaque at the on-disk header rather than plainly exposing a standard MZ header, so a new independent full CIL traversal could not be completed in this environment. R050–R052 report earlier exact-original, SHA-pinned CIL checks, but **they are prior evidence, not a repeat live disassembly done today**.

## E. The minimum falsifiable next research

1. Recover or statically isolate the exact Bot Battle UI button/event handler and follow it from the PvP menu to match-create call. Identify whether it calls `StartMatchProcess`, a dedicated bot-room initializer, or a standalone local builder.
2. Resolve actual bot-map `GlobalMapDef` and `GlobalGameDef` records in the original extracted Unity assets; enumerate configured map mode, builder, scene, and AI spawn rules from **real** records rather than test fixtures.
3. Trace entry ordering: when game subtype 2 is assigned, when world initialization finishes, and when real bot controller/spawn event is invoked. Test each dependency separately.
4. Only after the code is proven, define a **read-only / bounded local no-network** experiment to distinguish cached-login menu availability from a fresh standalone entry; do not confuse reaching a menu, opening a match, and playable bots.

**Conclusion:** The original 2018 Bot Mode was user-accessed through **PvP**, not by a verified special offline login option. Local simulation exists. The **bridge from PvP Bot Mode selection to actual standalone match initialization remains UNVERIFIED**, so offline-mode restoration is promising but **not yet shown easier than handshake reconstruction**.

# IDEA PLAN — product goal, not implementation fiction

**User goal:** revive the discontinued 2018 CrossFire: Legends client for **fully offline local play against functional bots**, preserving its original look and gameplay wherever technically feasible.

**The success state** includes:
- Loading original game assets and launching on the user's Android device without external live Tencent services.
- Reachable offline menu/lobby or equivalent thin local flow that uses the real game, not a separate imitation app.
- Team Deathmatch against bots, with real spawning, movement, weapons, damage, combat, score, timer and result/return.
- Search & Destroy / Bomb Mode against bots, including teams, objectives, round phases and results.
- Repeatable relaunch and multiple matches, with diagnostics for network or asset problems.

**Non-goals:** connecting to live Tencent servers, bypassing other players' accounts, online multiplayer, selling or distributing proprietary game files, rewriting the game as a new shooter, declaring success from a mocked server, or conflating 2018 Mono with the newer IL2CPP game.

**Constraints:** Android 15 no-root Samsung environment; Termux + PCAPdroid VPN SOCKS5 already exercised; protected Assembly-CSharp.dll edits correlated with early exit. Prefer network-side local emulation; reconsider APK native modifications only if evidence demonstrates necessity.

See [implementation sequence](IMPLEMENTATION_PLAN.md) and [hard acceptance gates](knowledge-system/vault/specs/ACCEPTANCE.md).

# CrossFire: Legends 2018 — offline restoration workspace

**Mission:** restore original 2018 CrossFire: Legends (CF2018, `com.tencent.tmgp.cfmnac`) to **genuinely playable, local, offline bot matches**. This is not the newer IL2CPP `cfmobileoffline` project.

## Start here
1. [AGENTS.md](AGENTS.md) — required Codex agent operating contract.
2. [NAVIGATION.md](NAVIGATION.md) — compact ICM routing entrypoint.
3. [IDEA_PLAN.md](IDEA_PLAN.md) — product goal and non-goals.
4. [CHECKPOINT.md](knowledge-system/vault/CHECKPOINT.md) — what was proven, current blocker, next task.
5. [DRIVE_MANIFEST.md](sources/DRIVE_MANIFEST.md) — original assets in connected DespairArc Google Drive; **not stored in this public repository**.

## Target success
From a clean launch, game loads its original resources, reaches an offline interface and starts/finishes a real local TDM bot match and a Bomb/S&D bot match. AI, weapons, teams, scoring, match transitions, and restartability must be observable, not mocked. Prioritize a minimum working mode, preserve existing assets and gameplay.

## Current approach
Original re-signed APK + original OBB, no protected managed-DLL edits; app network traffic intercepted with PCAPdroid VpnService SOCKS5 to a Termux loopback service. Native Apollo/GCloud TGCP handshake is still a blocker. Do not confuse connectivity, packet encoding, ACK accepted, or lobby/gameplay: these are independent gates.

## Repository boundaries
This is a subproject of the existing public `despairarc000/temp` repository. Keep all CF2018 files under `cf2018/`. Do not overwrite the unrelated ChatGPT Browser Android app. Do not commit APK, XAPK, OBB, .so, managed assemblies, extracted assets, credential/token/session values, or full sensitive traces. Research documentation, original (new) server code, tests, and small sanitized fixtures are allowed, subject to rights/security review.

Codex: `cd cf2018 && python tools/knowledge.py doctor && python tools/knowledge.py route tgcp ack`.

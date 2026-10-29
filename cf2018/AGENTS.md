# AGENTS — CF2018 operating contract

Applies inside `cf2018/`. Read [NAVIGATION](NAVIGATION.md), [IDEA_PLAN](IDEA_PLAN.md), [CHECKPOINT](knowledge-system/vault/CHECKPOINT.md), and [Drive manifest](sources/DRIVE_MANIFEST.md) **before writing or asserting anything**.

## Objective and scope
Restore genuine offline bot-playable CrossFire: Legends **2018 / v1.0.11.11** (`com.tencent.tmgp.cfmnac`, Unity 4.6-era Mono). Work against this exact version. The separate `despairarc000/cfmobileoffline` IL2CPP project is NOT an evidence substitute. Correctness is observed game behavior, not synthetic emulator tests.

## Knowledge hierarchy
- User mission: [IDEA_PLAN](IDEA_PLAN.md).
- Current truth: [CHECKPOINT](knowledge-system/vault/CHECKPOINT.md) + [EVIDENCE](knowledge-system/vault/EVIDENCE.md) + repeatable tests.
- Engineering proposals: [TECHNICAL_PLAN](TECHNICAL_PLAN.md) and [OPEN_QUESTIONS](knowledge-system/vault/OPEN_QUESTIONS.md), **not** established facts.
- Original files: connected DespairArc Drive via [DRIVE_MANIFEST](sources/DRIVE_MANIFEST.md); Drive access is a connector permission, not implied by this link.

## Every task
1. Check `git status`, current branch and active edits; leave other contributors and unrelated root project alone.
2. `python tools/knowledge.py route "<task description>"`; inspect relevant vault evidence and immediate Graphify dependencies before inventing new work.
3. Define acceptance criteria, negative controls and failure modes **before** changing code. Distinguish client-native observation, logged real phone capture, local synthetic test, inference, and unknown.
4. Prefer **reverse-engineer the read/validation path** over blind response variants; never claim protocol-complete from byte-shape parity. Validate framing, TCP lifecycle, session correlation, key-mode negotiation, peer-vs-relay EOF.
5. Avoid any modifications to the original APK/OBB/DLL without explicit evidence justifying the need and a byte-preserving control. Previous one-byte DLL and update-skip patches exited early; don't repeat them without an integrity-root-cause investigation.
6. Implement minimal original server-side code with strict parsers, size/time limits, predictable logs, no internet exposure. Preserve PCAPdroid SOCKS5 path and Termux compatibility. Keep experiments bounded and disabled by default.
7. Run tests with exact command/results. A local replay **does not** equal real client acceptance. Never fabricate a server reply or observed client progress.
8. Update CHECKPOINT, EVIDENCE, WORKLOG, OPEN_QUESTIONS, graph links/edge list and decisions when claims/status change. Run `python tools/knowledge.py doctor` and unit tests.
9. Use real source provenance: Drive file link/path and hash when available; never invent Drive files, hashes, missing server capture, timings, or decompilation results.

## Working limits
- Public repository: **NO** original XAPK/APK/OBB/.so/.dll, raw decompilation, full game assets, keys, logins, private user data or proprietary extracted media. Do not automate uploads from Drive.
- Do not break OBB loading, block unrelated domains or apply global MITM. Keep redirection scoped to authorized game's known endpoints.
- No claim of offline playable, login complete, accepted TGCP handshake, or game build without verified phone evidence.
- Do not port the unrelated WebView Android app in root. No branch clutter: keep research/instrumentation in this folder; branch/PR only when it protects active concurrent work. Avoid disposable per-experiment branches.
- Stop endless retry storms; use 4–16 bounded requests max, with distinct run directories and unique IDs.
- If blocked, report exact missing evidence and next falsifiable action rather than unrelated scaffolding.

## Acceptance path
[P0](knowledge-system/vault/specs/ACCEPTANCE.md) → TGCP SYN/ACK → auth/AddressService → version/config/offline shell → client gameplay lifecycle → local TDM/Bomb AI parity → reproducible install and startup. Every gate has separate evidence requirements.

## Commands
`python tools/knowledge.py route tgcp ack`
`python tools/knowledge.py graph`
`python tools/knowledge.py doctor`
`python -m unittest discover -s tests`

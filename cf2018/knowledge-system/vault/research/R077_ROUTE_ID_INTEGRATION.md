# R077 — Copy-only R073 integration for private CTDir route equality

**2026-11-02 — SOURCE-ONLY INTEGRATION TESTED, ACTUAL OWNER SOURCE/PHONE NOT YET RUN.** The end goal remains unchanged original CF2018 v1.0.11.11 offline TDM/Bomb with bots. This experiment does not attempt login or enable a second-service ACK.

## Purpose

[R074 phone result](R074_PHONE_UNIT_FIELD_CONFIRMED.md) shows three changed-route SYNs (131 bytes), all with a changed non-route unit-ID field5 and route field14 shortened by2. [R075](R075_DIRECTORY_CALLER_DISCRIMINATOR.md) finds a plausible 10-byte route literal in original CTDir code. [R076](R076_OFFLINE_ROUTE_EQUALITY.md) provides a source-hash-pinned, read-only route comparator returning fixed labels. **The earlier TXT report contains no route string, and cannot answer equality retrospectively.**

## Copy-only integration

[`tools/prepare_r077_route_id.py`](../../../tools/prepare_r077_route_id.py) prepares a **fresh new directory from the owner's existing R073 diagnostic**; neither game nor R073 directory is edited. It requires:

- R073's already prepared `routed_probe_r037.py`, reconstructed through exact reverse substitutions to the **pinned R068 handler SHA** `7ab7ad90735201b6df96265c8dd379d08308690fb6956f3a46e4f793ba8c84d0`.
- Original R073 `second_service_syn_gate.py` fingerprint and unchanged source helper `syn_difference_labels.py`.
- Privately available, exact **original** 5,243,704-byte Apollo `libapollo.so`, validated by size/SHA and its 10-byte CTDir literal's shape; no binary or literal copied into the output.
- Repository `r057`, `r058`, `r075`, `r076` Python modules, copied into the fresh output for runtime classification.

The patch **only**:
1. At existing `syn_security_context` event recording, adds `route_label=classify_transient_frame(raw_frame,_R077_ORIGINAL_ROUTE)`.
2. Adds `route_label` to the sanitized `SYN_CONTEXT` TXT line, with no original or observed route name/value.
3. Uses fresh `CF2018_R077_ROUTE_ID_Result.txt` and `cf2018_r077_route_id_runs` paths and the correct diagnostic banner.
4. At script execution, **before main/server startup**, loads original route into transient memory from path specified by `CF18_APOLLO_LIBRARY`; missing/wrong original immediately refuses.

The guard that disables second-service ACK remains `if (assessment == 'MATCH_EXCEPT_ROUTE' and False):`; there is no new ACK permission or network transmission. A private route equality label is **never** supplied to this guard. If the filename/lib is wrong the command exits before any listener starts.

## Verification and limits

- [R077 source-only tests](../../../tests/test_r077_route_id_patch.py) cover preserving the disabled second ACK, new event/report fields, isolated result paths, fail-before-server source checks, and rejected missing/duplicated instrumentation, wrong ACK gate, wrong directory, absent original, and hash-unverified source.
- [GitHub CI successful run 41372943974](https://github.com/despairarc000/temp/actions/runs/41372943974): repository **598 tests total / 148 skipped**, R077 source-only positive/negative checks all passing; the owner-private prepared-copy test **SKIPPED** without both `CF18_R073_PREPARED` and `CF18_APOLLO_LIBRARY`.
- No exact R073 private handler is in public CI. Therefore, **actual R073-to-R077 preparation and 4-session loopback regression have not yet run on the owner source**. The test suite does not establish live phone behavior, source-loader robustness under Android, actual route match or accepted ACK.
- There is no original Apollo or private phone SYN committed. This report contains only fixed analysis labels and native method relationships.

## Next gated step

First, run **offline owner-local preparation** using the already prepared R073 directory and exact local original Apollo, and execute that prepared copy's existing offline regression suite. If source checks fail, **refuse without adjusting pins** and inspect the divergence. Only after offline preparation/regression is confirmed should a **single bounded owner-controlled R077 phone diagnostic** run with the same PCAPdroid setup, no second-service ACK and four-session limit. Report only `CF2018_R077_ROUTE_ID_Result.txt` (CTDir route MATCH/DIFFERENT/REFUSED labels). Do not reuse R074 diagnostic result as though it contained route values.

If MATCH, the CTDir literal is identical, **but not yet proof of runtime CTDir execution nor ACK/security acceptance**. If DIFFERENT, that static CTDir route does not explain the observed name. Either way, next research tracks the exact receiver and handshake; no session/login/playable match established.

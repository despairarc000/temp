# Directory handshake phone result and next auth/Bingo observation

2026-11-02, R093. **PHONE_OBSERVED**, separate from original-native emulation and loopback-only controls.

## New phone milestone

Owner supplied CF2018_DIRECTORY_ACK_Result.txt, SHA256 `e5e6a14e2f3abfbd79802f29a5f5a0b43bcac09e31a313d4a5eed7caed49f136`. No packet bytes, account/session fields or report copy committed. Slot1 repeated the discovery path and wrote its169-byte address reply. Slot2 had131-byte SYN, exact original CTDir route match, and only the known same-width unit5/non-route change. New guard allowed one63-byte ACK. Phone then sent a0x2001/kind1 frame: AUTH_REQUEST_OBSERVED. Client total248B minus131B SYN implies117B follow-up. No next-service auth/Bingo reply was sent; the probe closed intentionally. Slots3/4 were held with ACK0 by the exhausted budget. These are not failed auth-response attempts.

This advances from R077's silent second connection to observed directory-route handshake continuation. It does not prove account authentication, a completed service session, exact native runtime caller or game login/lobby/bots. The old local SYN_CONTEXT REFUSED line still describes the original strict route-only comparison, not phone rejection; ONE_SHOT_ACK_PROBE is the separate approved route-plus-unit guard.

## Offline continuation

Existing unchanged54-byte V14_BODY_ENVELOPED auth reply and91-byte CORRECTED_BINGO_SYNTHETIC stage were executed through the hash-pinned original native receiver using synthetic initialized state3. Auth alone reaches state4 waiting; both complete frames reach numeric state5 with zero synthetic account storage. Corrupting the Bingo body mode returns−18 and remains4; truncating its last byte remains4 with90B buffered. Four native methods PASS. Gather/header/body/account/Bingo parsing execute; only bounded libc, logging/error and no-data network boundary substituted. No auth construction, real credentials or successful application login is established. State5 is transport-ready, not authenticated gameplay.

Static original DirServiceClient has generated requests get_server_dirtree_all, get_server_dirtree_by_id and get_server_by_ids. These are candidate next operations, not decoded phone requests. No directory response is fabricated.

## Optional next owner test

Single-file prepare_directory_stage.py verifies exact previous one-ACK handler SHA `829398e786fa78aa9d2f83f6f3cca5a0c861962b415712533f7078744f26a9db` and gate-helper SHA `f50b39c587c25465c23984285dc8934c3d4fb428390e87411dc3f86416dd2b27`, creates separate output, retains original route loader and all exact-route/unit/security comparisons, prior address-reply requirement, four-session cap and locked single-connection budget. Explicit CF2018_DIRECTORY_STAGE=YES replaces the previous opt-in. After the one qualified directory ACK and actual0x2001 request, it reuses existing54/91 replies, then records one following frame and closes without answering application data. Routed-family label additionally requires0x4013/kind5, not just a type number. Report emits only fixed labels and frame/body sizes.

Local preparation and six loopback lifecycle controls PASS: disabled, absent discovery reply, changed security, one-shot exhaustion, non-auth follow-up, auth/Bingo then routed/other frame with no application reply. Initial local test failures exposed a reporting-variable typo and premature outer-loop exit; both corrected before distribution and the lifecycle suite rerun successfully. Original baseline113 regression checks also rerun on final prepared copy. Public CI without private source skips native/prepared controls; no new remote CI result claimed.

Final owner report goes to Android Download as CF2018_DIRECTORY_STAGE_Result.txt. Falsification: no follow-up after both replies leaves next-service stage acceptance unresolved;0x4013/kind5 identifies a routed family only, not a verified directory method. We deliberately send no speculative directory response. Actual phone next-service auth/Bingo acceptance remains UNKNOWN pending this separate run.

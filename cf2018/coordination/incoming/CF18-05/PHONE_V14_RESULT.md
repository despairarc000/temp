# CF18-05 — v1.4 actual phone test: corrected TGCPBody envelope

Received in conversation 2026-10-31 (Asia/Manila). Source: user-uploaded text file named `CF2018_v12_Auth_Body_Result.txt`, whose **contents explicitly identify v1.4**: `CF2018 v1.4 — native-identified TGCPBody envelope A/B/C phone comparison`. Do not misclassify this as the older v1.2 test.

Evidence class: **ON_PHONE_REDACTED_REPORT**, 6 completed phone sessions, two per arm, sourced from local Termux/PCAPdroid experimental service. Source report SHA256: `de7447abda184300af1f57eea94fedc4897a41996d6b13c51ce6a63c5652833e`. This file is a handoff to CF18-00 review, not a claim of authentication or a canonical change.

## Observations

All 6 connections: client SYN 133 bytes → server AA_DIRECT ACK 63 bytes → client auth request `0x2001`, 117 bytes, header 42/body 73. All auth-request frame SHA256 `5b71ff58c86e96d6e9d4d961b7d4fcd04613e2061b5f1b74e60653967e61ae75`. No third client protocol frame observed; each session has 250 client bytes / two frames.

| Arm | Trials | Auth-response length | Observed status and timing |
|---|---:|---:|---|
| SILENCE | #1/#4 | 0 | `deadline_after_auth_attempt`; duration 7032.16 / 7030.26 ms |
| V12_BODY_EMPTY | #2/#5 | 49 | `read_eof`; reply-to-end 11.19 / 9.61 ms |
| V14_BODY_ENVELOPED | #3/#6 | 54 | `deadline_after_auth_attempt`; reply-to-end 7010.91 / 7012.81 ms |

## Interpretation and limits

The single controlled five-byte native-identified TGCPBody envelope correction **eliminates the previous immediate local read-EOF** in both on-phone repeats. The corrected arm instead remains under the experimental listener until its programmed ~7-second deadline, matching the silence control's time scale. This result is consistent with the offline native replay that gets past auth body decode and reaches Bingo waiting; it is **not direct proof** of exact Android parser return, accepted account, a fully authenticated session, valid Bingo/relay, AddressService progress, lobby or gameplay.

The packet used a deliberately synthetic **empty-account** response and no legitimate login/session credentials. No further client message occurred in any arm. The report does **not contain** an actual directional relay-event appendix or packet-level FIN/RST capture, despite the v1.4 proxy code's logging capability. Therefore a timeout cannot prove peer socket still open outside the listener's deadline, and a `read_eof` cannot establish the initiating TCP endpoint.

The working ACK and client request remain unchanged. Avoid another random account-field sweep.

## Next CF18-00 / CF18-02 review

1. Update [CHECKPOINT](../../../knowledge-system/vault/CHECKPOINT.md), [EVIDENCE](../../../knowledge-system/vault/EVIDENCE.md), [OPEN_QUESTIONS](../../../knowledge-system/vault/OPEN_QUESTIONS.md) and queue to reflect **v1.4 corrected envelope tested on the actual phone, no immediate EOF**, without promoting G2 authentication.
2. Compare the native [AUTH_RECEIVER](../../../knowledge-system/vault/research/AUTH_RECEIVER.md) and [BINGO_SESSION](../../../knowledge-system/vault/research/BINGO_SESSION.md) with current [CONNECTION_CALLBACKS](../../../knowledge-system/vault/research/CONNECTION_CALLBACKS.md); state 4/5 or callback status zero alone is not an acceptance oracle.
3. Bounded offline next target is true `0x3002` waiting response and `0x6002` Bingo/relay semantics with valid message-type/body correlation and correct identity/session predicates. Then trace AddressService `Send_QueryAddrInfo` / `Recv_QueryAddrInfo`; no invented credentials. Seek a testable next-phase signal before another phone experiment.
4. If later phone test is justified, preserve the proven ACK+body envelope; add a deliberate, bounded, passive-by-default server-side session experiment and directional EOF source tracking. No APK/OBB changes, no live Tencent login.

**Milestone:** client SYN → ACK → authentic 0x2001 is confirmed. Corrected synthetic 0x2002 changes immediate EOF into a wait. Authentication, Bingo and usable offline gameplay remain unverified. All automated schedules remain paused.

# CF18-05 — v1.4 deployed bridge wrapper test handoff

Date: 2026-10-30. Status: **LOCAL_BUILD_TESTED, NOT PHONE_TESTED**.
Owner/user reported all prior automated schedules paused; this record does **not** restart any schedule or change existing CF18-00/01/02/03/04 ownership.

## Basis

Current `main` at `7a283f251f0ad4c75c0453d619ed7962178ae5a6` integrates [AUTH_RECEIVER](../../../knowledge-system/vault/research/AUTH_RECEIVER.md). The native exact-v1.2 failure was missing TGCPBody `AA + 4-byte big-endian length`, causing decoder -32, mapped to auth -18. A corrected empty-body packet passes the **offline native** body/auth receiver and reaches Bingo wait -12; this is not authentication.

The **original v1.2 phone ZIP** was found in the user's conversation files and actually inspected; it contains the original deployed `auth_probe_v12.py` and `cf2018_redirector.py` with known 63-byte AA_DIRECT handshake, SOCKS5 IP-and-port routing and normal unrelated passthrough. This resolves the *specific source-availability* gap for preparing a v1.4 probe; it does not establish the original historical EOF cause.

A **user-only v1.4 Termux ZIP** was built in this conversation: `CF2018_TGCP_v1.4_Body_Envelope_ABC.zip`. Historical `golden_request.hex` and other real/captured wire fixtures are included **only in that user-facing ZIP**; do not copy this full ZIP into public GitHub. The clean, reusable body encoder is already in [tgcp_body_envelope.py](../../../experiments/tgcp_body_envelope.py).

## Exact controlled arms

One opt-in 6-session run, two repeats per arm:

| Arm | Wire bytes | Difference |
|---|---:|---|
| SILENCE | 0 | No auth reply |
| V12_BODY_EMPTY | 49 | Exact pinned historical response, missing body preamble |
| V14_BODY_ENVELOPED | 54 | Identical header except base body length 7→12; body replaced with AA + `0000000c` + prior 7-byte union |

Old frame SHA-256: `527b6570d015c64355ab8d4d83c534dc3fe5975818485133a2c4b313edcbf4ca`.
New corrected frame SHA-256: `17ace86895dc499ea70045bac4132e9d8a5e9cc6056f350e7cf099a256495738`.
AA outer header size remains 42; first 42 bytes differ only at offset 32, the declared body-length field. The working ACK, account contents (none), key mode, and routing are unchanged.

## Checks already executed

A clean Termux-compatible Python package ran **21 tests PASS**, including old v1.2 baseline tests and new v1.4 direct-listener + real loopback SOCKS5 integration. `START_V14.sh` executes offline only without opt-in. ZIP 19 files, 39840 bytes, CRC integrity PASS; SHA-256 `22c127e7002c08839117e923ddbead9c4c341f42a6d2ffaa9f5a8b2ba049a6ce`.

Proxy event logging now includes `RELAY_READ_EOF` (direction of loopback reader returning empty), `RELAY_HALF_CLOSE` and `RELAY_LOCAL_CLEANUP`. These are **proxy observation boundaries**, not proof of the TCP FIN sender or native game rejection. The TXT report includes only frame metadata/hashes/timing and no raw auth body/credentials.

## Next action and interpretation

A user-controlled, CrossFire-only PCAPdroid/SOCKS5 phone run may be performed by explicitly invoking `CF2018_V14_LIVE=YES bash START_V14.sh` from the extracted folder. Max six sessions, localhost listener, preserved non-target forwarding, deadline 7 seconds per session. Ask for **only** `Download/CF2018_v14_Body_Envelope_Result.txt`; the actual result does not yet exist.

If 54-byte arm stays open rather than immediately EOF, it is consistent with fixing the body parser but **does not prove authenticated session**. Bingo expects further server response, not necessarily another client packet. If 54-byte arm still EOF, investigate relay-event direction/phone runtime and post-auth session state without another broad payload sweep. Do not invent Bingo, account identity, login, keys, or bots. Keep all automated schedules paused.

**No APK/OBB modification, no remote game login, and no phone test performed in this preparation.**

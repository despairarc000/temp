# R085 — GCloud SYN's DH helper is conditional on existing handle state

**2026-11-02. EXACT OWNER-ORIGINAL STATIC CODE, SOURCE-FREE NEGATIVE TESTS.** Continues R084. The original CrossFire 2018 client/server handshake is not authenticated or playable.

## Independent original sender evidence

In the original `libapollo.so`, the GCloud `gcloud_tgcpapi_send_syn_msg` function at `0x3aba5c` (size556) has an explicit branch before the optional `tgcpapi_generate_dh` call.

| Original site | Instruction evidence | Meaning |
|---|---|---|
| `0x3aba7c`–`0x3aba7e` | `f505 534f` | Address handle-relative state slot |
| `0x3aba92` | `6a9b` | Load pointer from that slot |
| `0x3aba94` | `2b00` | Compare pointer to zero |
| `0x3aba96` | `d039` | BEQ to `0x3abb0c`, **skips helper** |
| `0x3aba98` / `0x3aba9c` | `2303` / `7023` | Write branch-specific scalar only when pointer exists |
| `0x3abaa0` | `f7ff ff9e` | BL `tgcpapi_generate_dh` at `0x3ab9e0` |
| `0x3abb0c` | `e9d5 2302` | SYN construction continues after optional DH section |

The helper at `0x3ab9e0` independently addresses the corresponding handle-relative slot at `0x3ab9f6`–`0x3ab9fa`, and has a null-state guard at `0x3ab9fc`, branching to `0x3aba3c`. It does **not** unconditionally fabricate a public DH component.

Combined with [R084](R084_RPC_DH_CONFIG_SOURCE.md): the traced RPC constructor starts with a default-empty DH string and propagates that field into GCloud initialization. If no DH state is instantiated, the original sender is explicitly capable of continuing without invoking the DH serialization helper. This resolves the concern that the sender might always require a DH public component just to create its SYN.

## Verification, ownership and limits

[Read-only auditor](../../../experiments/r085_gcloud_syn_dh_guard.py) verifies the SHA-pinned original's branch instructions, decoded branch targets, original function sizes/names and actual sender-to-helper direct BL. [Source-free controls](../../../tests/test_r085_gcloud_syn_dh_guard.py) cover mutations at every pinned instruction site, wrong branches, identities, callsite/owner removal and no-network policy. Actual private-original Python audit is opt-in and skipped by public CI.

The original ARM halfwords above were independently read in memory from the user's connected original `libapollo.so` with no binary committed. This is **static source evidence**, not a phone call-stack trace or an actual observed handle pointer. R077 remains the last real-phone diagnostic, with all second-service ACKs intentionally held.

**Still unknown**: whether the specific phone second connection has an empty DH context, which ACK key mode the server expects or will supply, how any generated key/session will be accepted, and whether its account/auth response reaches login, lobby or bots. No new packet or ACK has been sent.

**Next**: original-native bounded key-mode 0 versus mode 2 receive/crypto controls on a synthetic *no-DH handle*, with sends/auth/Bingo suppressed; read-only report should distinguish parse acceptance from real session acceptance. No phone test until justified and explicitly approved.

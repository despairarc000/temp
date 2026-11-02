# R086 — Static comparison of GCloud ACK key-mode branches

Date: 2026-11-02. Scope: read-only review of the user's original 2018 native library. No real phone test or application change.

## Findings

The original `gcloud_tgcpapi_recv_and_decrypt_pkg` code contains separate paths for these decoded modes:

| Mode | Static code behavior | Limit |
|---|---|---|
| 0 | Clears the key-length field and proceeds to body processing without calling the key-setup routine | Doesn't establish that later encrypted body processing succeeds |
| 2 | Uses the supplied key information and reaches the key-setup routine | Key material, length, and encryption method remain independent constraints |
| 3 | Calls the key-derivation routine, then the key-setup routine | Requires a compatible current connection state |
| Other | Enters the unsupported-mode path | No accepted behavior established |

Original branch sites at `0x3abeb8`, `0x3abebc`, `0x3abec8`, and `0x3abee8` resolve to the expected mode-specific paths. The receiver's two required native callsites are `0x3abef2` (key derivation) and `0x3abefe` (key setup).

## Verification

[Source auditor](../../../experiments/r086_gcloud_ack_mode_branch_matrix.py) validates the expected original SHA, size, 32 instruction halfwords, branch targets, three original functions, and the two direct callsites. The separately accessed original binary matched all 32 instruction pins, all three function identities, and both callsite targets.

[Source-free tests](../../../tests/test_r086_gcloud_ack_mode_branch_matrix.py) cover each branch, malformed inputs, missing original callsites, and other negative cases. [GitHub CI run 41410971298](https://github.com/despairarc000/temp/actions/runs/41410971298) succeeded with 735 tests (578 passed; 157 intentionally skipped). The optional Python audit requiring the private original binary is skipped in public CI; source inspection took place privately.

## Interpretation

[R084](R084_RPC_DH_CONFIG_SOURCE.md) found an empty default parameter string on one specific RPC constructor path; [R085](R085_GCLOUD_SYN_DH_GUARD.md) found that SYN generation can skip an optional DH-state helper. Together, these justify examining mode 0 and mode 2 further without assuming that any mode has been selected on the actual Android connection.

The last real-phone observation remains R077: three later SYNs, no second-service ACK supplied. Source-level branch compatibility does not establish application session success, authentication, lobby access, or gameplay.

**Next:** offline review of the remaining body and state predicates, with no outbound traffic or actual session attempts.

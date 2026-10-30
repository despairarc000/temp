# CF18-05 — historical phone APK parity and v0.9 envelope preflight
Date: 2026-10-30. Status: **SUBMITTED FOR COORDINATOR REVIEW**. Scope: new evidence/experiment only; **no canonical files overwritten**.

## Recovered phone equality evidence
The user-supplied historical `CF2018_XAPK_Comparison_Report.txt` (read-only Termux scan of `~/storage/downloads/Original.xapk`) explicitly records the embedded original APK SHA-256:

`33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9`.

That EXACTLY matches the independent pinned mirror APK in [source provenance](../../../sources/SOURCE_PROVENANCE.md). The user's comparison report also records original Assembly-CSharp.dll SHA-256 `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9`, equal to the mirror's original DLL. It compares original APK with re-signed-only control and finds **0 differing non-signature payload entries** among 1212. Update-skip build differs only at the managed DLL payload. **Evidence class:** HISTORICAL_ON_PHONE_REPORT + INDEPENDENT_MIRROR_SOURCE_HASH. The actual original APK member bytes were not copied into this repository.

**Interpretation:** The historical Original.xapk embedded APK was bit-for-bit identical to Codex's recovered mirror APK at the time of that earlier calculation. This reduces G0 APK identity uncertainty for *that* original file and its embedded Apollo library, even though the report does not prove the current installed APK's bytes, runtime selected native path, entire XAPK hash, OBB SHA-256, or Drive OBB equality. Do not equate equality of separate APK members with equality of complete XAPKs.

## New first-stage receive-envelope preflight
The [reviewed ACK receiver](../../../knowledge-system/vault/research/ACK_RECEIVER.md) retires v0.8's raw-prefix check; native GCloud first decodes AA/99 then compares decoded base marker to 0x4366. The historical v0.4 ACK copies client wire kinds from SYN, including kind 0 for base fields. The strict AA receive-subset models kind 1 for those fields.

Independent offline preflight against exact 65-byte historical ACK generated from the known 133-byte SYN reports:

| Case | strict AA first-stage result |
|---|---|
| 65-byte 43 66 AA historical ACK | REJECT: raw prefix not AA |
| v0.8 66 43 AA flipped raw prefix | REJECT: raw prefix not AA |
| historical ACK with first two bytes stripped | REJECT: base field 1 kind 0 instead of kind 1 |
| v0.8 flipped ACK with first two bytes stripped | same kind-0 rejection |
| constructed 63-byte AA fixture with kind-1 base TLV | FIRST-STAGE PASS ONLY; effective ACK/session UNKNOWN |

Local original Python tool has 7 unit checks (pass). Eight fake-client localhost TCP sessions passed (2 per arm) and an 8-session SO​CKS5 127.0.0.1 handoff replay passed; each fake client sent authentic 133-byte SYN but **did not** perform real game-side ACK handling. No actual CrossFire game, phone, authentication or live server connection was tested.

## Private experiment material
A complete, user-facing v0.9 Termux ZIP was created in this chat for a strictly **opt-in** 8-session A/B/C/D comparison, using historical v0.8 SOCKS5 forwarding and redaction of full client data. It includes the historical original SYN bytes and synthetic ACK hex, so **do not commit the ZIP or its raw fixtures to this public repo**. Its code is not a native-verified complete ACK implementation. A/B/C/D arms: passive, old ACK, AA raw, 43 66 + AA. Only a **new client message** after a candidate could indicate advancement. The recipient has not yet supplied an on-phone v0.9 result.

## Coordinator action
- Reconcile this user-supplied original APK SHA in [CHECKPOINT](../../../knowledge-system/vault/CHECKPOINT.md), [EVIDENCE](../../../knowledge-system/vault/EVIDENCE.md) and Q-07 without overclaiming OBB/installed APK equality.
- Review the native receive parser and whether an outer 43 66 transport prefix may be stripped upstream before GCloud gather; first-stage strict-model parity alone does not establish wire acceptance.
- Review any on-phone v0.9 report before promoting claims, distinguish socket-level read EOF from game application rejection, and never mark G2 complete without post-ACK client traffic.
- No changes to `cfmobileoffline`, public proprietary game files, or root Android app.

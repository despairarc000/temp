# CF18-G2-AUTH-RX-02 — v1.3 offline native comparison packet

Date: 2026-10-30. **READY FOR COORDINATOR REVIEW; no phone test, no authenticated session.**

The new, original code [auth_v12_fixtures.py](auth_v12_fixtures.py) and [tests](test_auth_v12_fixtures.py) independently rebuild the exact three **synthetic** `0x2002` replies used in v1.2. Byte-for-byte equality was verified locally against `CF2018_TGCP_v1.2_Auth_Account_ABCD/auth_variant_v12.py` (which imports the v1.1 helper). All seven new regression tests passed. No original SYN/auth request bytes, account, token, UID, copyrighted library or network listener are committed.

| Case | Bytes | SHA-256 |
|---|---:|---|
| V11_EMPTY_ACCOUNT | 66 | `787fd8b6a013a1c469f065a8a6e269fa402968d6e2f503852411ab9e6d40d40e` |
| V12_BODY_EMPTY | 49 | `527b6570d015c64355ab8d4d83c534dc3fe5975818485133a2c4b313edcbf4ca` |
| V12_FULL_ZERO_ACCOUNT | 79 | `2aed3ae9a18a47497969bedad3332a2eb8a91aaf0e3a50839ace9843267199fa` |

The AA header length is 42 for all three candidates; all header bytes match except byte offset 32, which encodes the variant body length. This means v1.2's three negative response cases share **all other server base/session/extension assumptions**. Silence was the fourth arm.

## Exact Codex next task — not random server reply revisions

Use verified private Apollo SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`; check source availability and ARM Thumb identity each run.

1. Feed all three pinned fixtures to **actual** native GCloud envelope/base/extension decoder (or review its exact branches), record first nonzero result, effective type, declared lengths, decoded marker, key mode. Do not treat the Python structural checker as native proof.
2. Execute `TGCPBody::unpackTLV`, `TGCPAuthRspBody::unpackTLVWithVarint` and `TSF4GAccount::unpackTLVWithVarint` on the real variant bytes using fresh/native-owned read buffers and explicitly identified stubs; collect exact result codes and consumed cursor per stage.
3. Trace `gcloud_tgcpapi_recv_authrsp_msg` (approx. 0x3ac306) -> `OnStateAuthing` -> `Bingo` with real account/session guards where feasible. Distinguish **parser failure** from **parser returns zero but later session close**; a zero result with Bingo or parser stubs is *not* client proof.
4. Independently verify actual PCAPdroid/Termux relay end-of-stream direction if original deployed code is available. `read_eof` alone is not FIN/RST attribution.
5. Post a table of 3 variant × native stages, raw return codes and source/stub provenance. Only once the failing gate is localized consider ONE bounded phone experiment with a control.

**Stop condition:** If actual pinned library/emulation deps are unavailable, record BLOCKED_NATIVE and do not invent validation. No new live v1.3 trial exists or is warranted yet. Historical v1.2 phone observation is in [PHONE_V12_RESULT.md](PHONE_V12_RESULT.md); it showed early EOF in all three dummy auth variants and no third client packet.

Run offline fixture tests from this lane: `python -m unittest discover -s coordination/incoming/CF18-05 -p test_auth_v12_fixtures.py -v`. The test imports a sibling module; with `discover`, the lane directory is added to sys.path.

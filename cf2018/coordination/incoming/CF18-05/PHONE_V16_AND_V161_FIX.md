# CF18-05 — v1.6 phone report and selector-kind observer correction

2026-10-31. **Evidence class ON_PHONE_REDACTED_REPORT + INDEPENDENT_OFFLINE_REGRESSION**, not authenticated app access. Source phone report uploaded directly by user: `CF2018_v16_Routed_Fingerprint_Result.txt`, SHA256 `7777c7cf38844b4029e5935e128f51d2bbe4e8cabe84d210fda7ac4876e5a170`.

## Phone outcome

Two sessions, each with the confirmed 133-byte client SYN, 63-byte ACK, real `0x2001` 117-byte auth request, synthetic corrected `0x2002` 54-byte response and synthetic Bingo `0x6002` 91-byte stage after ~151 ms:

| Slot | Outcome | Actual later client packet |
|---|---|---|
| 1 | `routed_frame_seen` at 227.67ms | `0x4013` 161B, 34.77ms after Bingo |
| 2 | 8,192.53ms listener deadline | none |

Thus `0x4013` is now observed **3/4 Bingo trials across v1.5/v1.6**, not 4/4, with no real authentication, QueryAddrInfo identification, lobby or gameplay evidence.

## v1.6 observer defect (not necessarily a native protocol defect)

The deployed v1.6 source has:
```python
kind=sel[0][0] if len(sel)==1 else None
if sel == [[0x4013,1]]:
    run.record('routed_rpc_hint', ...)
```
A successfully parsed real routed frame whose `extension_fields` is `[[0x4013,5]]` (or any other kind) is **reported as `0x4013` in LATER, but silently excluded from ROUTED_HINT**. Actual phone selector kind was **not recorded** in the uploaded report, so we cannot claim it was 5. Absence of ROUTED_HINT therefore does **not** mean the application body is opaque/unrecognized.

This filter bug escaped v1.6 tests because synthetic frames used only kind 1.

## Minimal proven v1.6.1 repair

- [fix_v16_1.py](fix_v16_1.py): hash-pinned upgrade for the two generated files **inside the existing user v1.5 directory**: `route_fingerprint_v16.py` and `route_probe_v16.py`. Verify **both** original source hashes before writing anything. No TCP, APK, original library, private captured fixture, stage content, client key, account or native patch. Idempotent when already upgraded. A modified/unexpected installation fails closed.
- The repaired detector activates for **any unique observed `0x4013` selector**; classifier allows only kinds **1 or 5** under its strict local policy and logs the numeric selector kind. Other kinds get a visible `INSPECTION_REJECTED` hint rather than silently disappearing. No actual method result is fabricated.
- [test_v161_selector.py](test_v161_selector.py) adds **three** tests: both kinds 1/5 in the parser, unsupported kind rejection, and **actual local listener execution that produces ROUTED_HINT for both synthetic kinds**.
- Full local suite in original v1.5 folder: **36 tests PASS** (prior v1.5, v1.6, and new v1.6.1); original v1.5 stage source unchanged SHA `abfb6e46c54f71beb60769c4e6ca1221cccefbd9d72cecd902eb91cc59632f46`. A temporary replay of installer verified first install, safe rerun, and fail-closed behavior with corrupt source.
- Generated corrected source SHAs: `route_probe_v16.py` `8270595a913c2386acc3d19f07840934aa48a2ffc46fe64be03227018db84c5b`; `route_fingerprint_v16.py` `f6b75383ec5d078c25b676aaec716ca588464a5518c14b0c45d8a9e4194a0aeb`.

## Suggested user-only Termux follow-up

This is source-only, **no ZIP**, from user's already working `v1.5` folder:

```bash
cd "$HOME/CF2018_TGCP_v1.5_Bingo_Stage_ABC" || exit 1
BASE="https://raw.githubusercontent.com/despairarc000/temp/main/cf2018/coordination/incoming/CF18-05"
curl -fLsS "$BASE/fix_v16_1.py" -o fix_v16_1.py
curl -fLsS "$BASE/test_v161_selector.py" -o tests/test_v161_selector.py
python fix_v16_1.py
python -m unittest discover -s tests -v
```
After the offline tests pass, opt-in only and with old servers stopped, use unchanged `CF2018_V16_LIVE=YES bash START_V16.sh` with CrossFire-only PCAPdroid SOCKS5 `127.0.0.1:1080`. This runs exactly **two** synthetic Bingo sessions. New report location: `Download/CF2018_v161_Routed_Fingerprint_Result.txt`.

The next report's `ROUTED_HINT` should include `kind=...`, a body-envelope label and an allowlisted method hint **or** `NOT_IDENTIFIED`/`INSPECTION_REJECTED`; these remain structural hints, not decoded application proof. An unknown method does not imply encryption and no packet does not prove the correction failed.

**No scheduled tasks started.** Ask CF18-00 to integrate this outcome and reconcile the stale canonical CHECKPOINT after reviewing. No raw packet bytes may be committed.

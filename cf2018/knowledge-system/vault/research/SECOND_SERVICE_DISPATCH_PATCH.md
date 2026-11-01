# Guarded second-service dispatch integration

## R065: exact supplied R037 recovered and integrated

2026-11-01 UTC. Owner attached the original R037 kit: 35,193 bytes, SHA256 `c9837375ed0d5b37606e9619d1597c544d60de8d2684c3e8ea6eb657378fc380`, matching R037's recorded receipt. ZIP integrity passed. Its preparer chain validated all60 original V3.8 files and reproduced `routed_probe_r037.py`, SHA256 `2c28c09944770a66ffca7c7bdf19dd6065fce7ea59766b98bf58e5078e2e2e01`.

`tools/prepare_r037_dispatch.py` pins both the attachment and reproduced handler, then adds only the R056 first-frame decision and fixed-label report lines. Removing those two insertions recovers the original R037 handler exactly. Existing R035/R036/R037 diagnostics run before the hold. Address-reply bytes, RPC64 matching, one-reply guard, original exact-SYN gate, redirector, limits and live opt-in remain unchanged. R037 input and baseline sources are not edited.

Validation: **113 original prepared-copy regression tests PASS; 30 original R033–R037 focused tests PASS; one new real-loopback two-connection integration test PASS; two source-refusal tests PASS**. The new lifecycle check runs the supplied R037 socket test and additionally requires exactly one ACK and one address reply across both connections, exported reference classification for slot1 and ten-byte-route HOLD_NO_ACK for slot2. Original test assertions compare ACK/auth/Bingo/address reply and check existing redacted labels. No game client, internet service or phone participated. This supersedes the missing-R037-source limitation below; historical R064 baseline-only status remains accurate for that run.

Offline preparation:

```sh
python cf2018/tools/prepare_r037_dispatch.py --source /absolute/path/to/v38_source --kit /absolute/path/to/CF2018_R037_ROUTE_DELTA_Kit.zip --output cf2018/private/r037_dispatch
CF18_R037_PREPARED=/absolute/path/to/cf2018/private/r037_dispatch python -m unittest discover -s cf2018/tests -p test_r037_dispatch_lifecycle.py -v
```

No new experiment version or phone run. Next remains route-specific ACK/session evidence; do not run another HOLD-only phone capture. The preparer does not enable a second-service ACK.

2026-11-01 UTC. Owner authorized server patch/tests and diary archival. No client edits, schedule changes or phone test.

The baseline V3.8 Termux handler and SOCKS5 redirector match the public 60-file manifest. The handler's first-frame reference hash/type gate precedes ACK send. This patch inserts R056 classification there and a fixed-label TXT exporter. Only a reference-route candidate reaches the existing exact-byte gate. Other routes receive no ACK. Removing the two insertions recovers the original handler character for character.

## Compatibility correction

R056 originally applied the inbound server-reply `Receiver` to a client SYN. That strict parser expects kind1 base tags; the private baseline reference instead has kind0 varuint base fields except field6, a kind1 byte. The first regression run exposed a reference-ACK failure. `r056_second_service_syn.py` now checks the bounded client header length and client base grammar directly. Its synthetic fixture now represents that grammar, including field6. The verified private reference returns `REFERENCE_NAMED_ROUTE_CANDIDATE / DEFER_TO_PINNED_REFERENCE_GATE`. This supersedes the earlier R056 implication that its original synthetic tests established compatibility with the real reference SYN.

## Validation and limits

- `test_r056_second_service_syn.py`: 11 synthetic classifier controls, including wrong field6 kind, duplicate/unknown routes, malformed lengths, body/trailing input and privacy.
- `test_second_service_dispatch_patch.py`: 6 checks with explicit private source. Four private integration checks skip without that source. Actual handler execution uses in-memory IO and synthetic inspector/ACK/auth/stage boundaries: reference output equals baseline, then changed-route connection emits nothing. These are not actual socket/Android acceptance checks.
- The preparer verifies all 60 input hashes and copies only those pinned files into a fresh private output. Unknown/current R037 handler copies are refused. No listener is started by preparation.
- The original prepared-copy regression suite: **113 PASS** from its own directory after correction. Its socket tests use local loopback only; no phone or live game connection. Both knowledge doctors PASS locally.

The current R037 active-reply preparer was delivered separately in chat and is not in this repository. This patch targets the pinned baseline only; it is **not a replacement for the owner's active R037 experiment** and does not add its correlated address reply. Do not ask the owner to repeat a phone capture merely to observe HOLD_NO_ACK again. Before an active next-service test, source-pin the actual R037 integration and establish its appropriate ACK/session conditions.

## Reproduce offline

```sh
CF18_V38_SOURCE=/absolute/path/to/private/v38_source python -m unittest discover -s cf2018/tests -p test_second_service_dispatch_patch.py -v
python -m unittest discover -s cf2018/tests -p test_r056_second_service_syn.py -v
python cf2018/tools/prepare_second_service_dispatch.py --source /absolute/path/to/private/v38_source --output cf2018/private/dispatch_copy
cd cf2018/private/dispatch_copy
PYTHONPATH=. python -m unittest discover -s tests -q
```

No new game/experiment version is assigned. No original packets, binaries or source are included in the public patch.

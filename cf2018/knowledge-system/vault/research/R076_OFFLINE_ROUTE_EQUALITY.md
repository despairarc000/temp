# R076 — Offline CTDir route equality discriminator

**2026-11-02. Status: LOCAL_TEST_ONLY.** No phone experiment, no port listener, no second-service ACK, no login or gameplay. Builds on [R074's actual field5 result](R074_PHONE_UNIT_FIELD_CONFIRMED.md) and [R075's native CTDir route-length proof](R075_DIRECTORY_CALLER_DISCRIMINATOR.md).

## The question

The original game produced a second 131-byte named-route SYN. Its route field14 is two bytes shorter than the 133-byte reference, and its non-route field5 (unit ID) changes. The sanitized report did not disclose the new 10-byte route string. `CTDir` is a plausible caller with an embedded 10-byte route, but matching length does **not** establish identity.

The new `experiments/r076_private_route_equality.py` provides an **offline read-only** comparison between a transient, complete second-service SYN and the exact CTDir route literal decoded from the pinned original `libapollo.so`. Its public API returns only:
- `CTDIR_STATIC_ROUTE_MATCH`
- `CTDIR_STATIC_ROUTE_DIFFERENT`
- `REFUSED`

It emits no route values or user packet bytes and never sends an ACK. It validates a 131-byte framed second-service SYN before extracting the route, and the original ELF must match the known 5,243,704-byte size and pinned SHA-256. A matching label indicates literal equality only, **not** that CTDir executed or a 63-byte second-service ACK is valid. The comparison intentionally does not assert unchanged security/context fields; this is *not an ACK-permission gate*.

## Verification

- [Pure comparison implementation](../../../experiments/r076_private_route_equality.py) — no listener or send method.
- [Source-free and optional-private tests](../../../tests/test_r076_private_route_equality.py) — synthetic matching, changed route, invalid type, wrong size/truncation, missing/wrong original, labels not echoing input; explicitly confirms that changed non-route fields do not turn a route-equality label into a security verdict.
- [Corrected GitHub Actions run 41372103406](https://github.com/despairarc000/temp/actions/runs/41372103406): SUCCESS. **12 R076 synthetic tests PASS; 1 private-original test SKIPPED** without `CF18_APOLLO_LIBRARY`. The repo suite includes other skips. A passing CI on synthetic inputs is **not a real-phone route match**.
- The earlier R075 graph-index failure is fixed by adding a proper Vault `INDEX.md` Markdown reference (graph edges alone do not establish Vault reachability), and was green in [run 41371970947](https://github.com/despairarc000/temp/actions/runs/41371970947).

## Limits / next action

The phone report `CF2018_SYN_DIFFERENCE_Result.txt` contains only field numbers/kinds, not route strings. R076 cannot operate on that TXT after the fact. **Do not ask for a repeat of R074**. Before a user-run R076 experiment, make a **separately hash-pinned, copy-only diagnostic** that invokes this comparison in process memory on the already-working R073 observer, exports only a fixed label, refuses missing/wrong private Apollo and preserves the existing `HOLD_NO_ACK` behavior. Verify its prepared-copy lifecycle and safety controls offline before offering Termux commands.

Even a route match will not establish receiver/key/session ownership. Follow it with original-source ACK receiver research before any separately authorized second-service ACK experiment.

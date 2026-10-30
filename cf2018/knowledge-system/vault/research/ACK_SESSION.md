# CF18-G2-ACK-01 — reviewed body and session continuation

Coordinator CF18-00, reviewed main `37b808d095641c90e80a707209f656e9bf29c53f`,
2026-10-30. Source and ISA: [pinned mirror](../../../sources/SOURCE_PROVENANCE.md),
Apollo SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`,
ELF32 little-endian ARM EABI5; addresses are virtual, Thumb bit cleared.
Evidence: ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS, distinct from
independent synthetic fixtures. **G2 BLOCKED; no valid ACK/auth reply or phone auth.**

The coordinator reviewed the completed local CF18-02 continuation and reran all
40 lane methods; the continuation had no remote packet commit. Exact draft
hashes and canonical adaptations are in [integration](../../../coordination/INTEGRATION.md).
Incoming files are preserved. This extends the [ordered receiver](ACK_RECEIVER.md);
it neither implements a server nor validates historical phone-path selection.

## Received timestamp has a later use

Native base visualize references at `0x3af7a4` label base +8 dwTimeStamp and
+0x10 dwSequence. Receive/decrypt `0x3ac032` saves base +8 into handle+0x3490.
Auth-request buildup `0x3ab802`–`0x3ab80c` reads that value and writes request
body +0x50c, labeled dwXGCloudTimestamp by the request visualize routine at
`0x3b0a54`. The same field feeds the later string/hash construction chain near
`0x3ab83a`–`0x3ab858`; its exact formatting and server policy remain unestablished.

Four independent uint32 inputs execute the actual prefix and produce equal
request timestamps. Controls deliberately stop at `0x3dde18`, before account,
token or hash work. -77 is a probe stop sentinel, not a native auth return.
This establishes data flow, not timestamp units/freshness, an echo rule, token
generation, negotiated cipher success or a valid server-provided timestamp.
A lack of SYN-base equality checks in the examined ACK code does not make its
received base fields semantically unused. Do not fill them by assumption.

## Optional body storage and immediate caller

TGCPAckBody decoder `0x3b49a6` reads field 1 into object+0. Field 2 reads a
big-endian nested uint32 length, calls TGCPAuthRspBody `0x3b39c0` on object+8
at `0x3b4a2c`, then sets object+0 to 1 at `0x3b4a32` only after decoder zero.
Its bookkeeping reset is at +0x328, not a full object clear. Component controls
observe retained old presence when omitted, explicit zero clearing it, physical
truncation -2, and declared-end overrun -34. An empty nested component can set
presence 1 with zero account storage. No complete ACK was constructed.

In the examined OnStateKeySyning `0x3a9f8c` non-relay path, both injected presence
values reach the same suppressed auth-send boundary `0x3ab964`, leave account
destination unchanged, and remain state 2 because the send is suppressed.
The synchronous start-connection path also sends auth after ACK zero. There is
no demonstrated embedded-body shortcut in those callers; this is not a whole
library proof that no other caller uses the optional component.

## Separate auth response and account copy

| Code / predicate | Actual effect and limit |
|---|---|
| `0x3ac306`, call `0x3ac31c` | A separate receive/decrypt operation is made; it does not simply reuse the optional ACK body in this path. |
| `0x3ac322`–`0x3ac328` | Receive -10 maps to -7; other errors propagate. |
| `0x3ac32e`–`0x3ac352` | Effective header type must be 0x2002; mismatch records the type and returns -14 before body/account copy. |
| `0x3ac354`–`0x3ac37c` | TGCPBody parses into handle+0x1288; failure maps to -18. Real malformed-body controls preserve account destination. |
| `0x3ac37e`–`0x3ac390` | Parser zero leads to a 0x114-byte copy from decoded body prefix into handle+0x138, then state 4. TSF4GAccount decoder `0x3ad100` occupies that prefix. No account equality comparison is present in this bounded receiver. |
| `0x3a9ff6`, `0x3aa012` | State-3 auth handler invokes that receiver. Receive -12 becomes zero without Bingo. Receive success reaches Bingo at `0x3aa026` -> `0x3ac39e`, suppressed in controls. |

TSF4GAccount contains type/format/value/UID storage and bookkeeping. Fixtures use
only repeated independent Q/R bytes; logs expose match booleans rather than real
IDs. The successful copy/state control explicitly STUBS parser zero. It proves
that branch's copy/state behavior only. It cannot prove a semantically accepted
auth response, valid UID, login or Bingo success. Body union parsing can replace
the selector reference after the header check; no mismatched complete reply was
built. Semantic account/session checks elsewhere remain unfinished.

## Canonical reproduction and limits

Original [native runner](../../../experiments/native_control.py) verifies exact
library size/hash/ISA before execution. [Session controls](../../../experiments/native_session_controls.py)
use fresh Unicorn memory, 100000 instructions and one second per execution;
component/body inputs are capped at 512/256 bytes. There is no listener, connector,
serializer, source download or implicit execution. Dependencies load only for
explicit private-source controls. Android globals/GOT/runtime are not fully set up.

Stubs are explicit: decoded receive/decrypt, bounded libc operations, log/error
helpers, suppressed auth-send/Bingo, and supplied parser results only in labeled
branch controls. Other component-malformation controls execute real native parsers.
The timestamp prefix stops before token work. No socket or phone runs here.

[18 tests](../../../tests/test_native_session_controls.py): 15 adapted lane
methods, two independent coordinator native controls (fresh-context isolation and
state receive failure), and one dependency-free bad-fingerprint guard. With the
private source/dependencies selected all 18 pass. Default run passes the guard
and skips 17 native methods. The full canonical suite passes 101 with both private
sources selected; default has 82 PASS and 19 explicit SKIP. Knowledge doctor PASS.

```text
python tools/knowledge.py route 'native ACK optional body timestamp later auth session consumers'
python tools/knowledge.py doctor
python -m unittest discover -s tests -v
CF18_APK_SOURCE=<private pinned APK> CF18_APOLLO_LIBRARY=<private pinned Apollo> \
  PYTHONPATH=<private analysis dependencies> python -m unittest discover -s tests -v
```

Next bounded native work is downstream copied-account/Bingo/session validation,
state predicates and error propagation, with network and sends still suppressed.
Timestamp source/echo policy and full negotiation remain unknown. Phone build and
OBB equality, original SYN/failed-ACK construction and historical/deployed bridge
interface still block a justified complete candidate. A/B/C readiness remains
false; no device plan was activated. Only an authentic later client protocol
packet after ACK advances G2.

# CF18-G2-ACK-01 — reviewed receiver state and remaining gate

Coordinator review: `c52243228e8d2d38dd6b4c1d85f464d9f94461f8`, 2026-10-30.
Source identity/limits: [canonical provenance](../../../sources/SOURCE_PROVENANCE.md).
All native addresses below are Thumb-bit-cleared virtual addresses for Apollo
SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`.
Evidence: ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS, alongside distinct
ORIGINAL_CODE/LOCAL_SYNTHETIC tests. No phone acceptance is established.

Inputs: [CF18-01](../../../coordination/incoming/CF18-01/NATIVE_RX_RESULT.md)
(`fefd0dc224851fefc2b74a51fc95e0fa0090e9a2`),
[CF18-02](../../../coordination/incoming/CF18-02/RESULT.md)
(`56db53d81326810d5bea342b11ea4e07dc351e01`), and
[CF18-04](../../../coordination/incoming/CF18-04/SOURCE_RESULT.md)
(`c52243228e8d2d38dd6b4c1d85f464d9f94461f8`). Coordinator reran 32, 25 and
14 lane tests respectively with private source selected, no skips.

## Ordered read / validation trace

| Stage | Observed predicate and consequence |
|---|---|
| ACK caller `0x3ac0b8` | Calls receive/decrypt `0x3abe34` before its final ACK type check. |
| Receive/decrypt `0x3abe4c` | Calls GCloud gather `0x3ab5ec`; this is distinct from legacy gather `0x1c0c50`. Nonzero gather status propagates. |
| Gather header helper `0x3aab44` | Requires AA or 99 envelope and a big-endian declared header length, then invokes actual TGCPHead TLV decoding. Raw `43 66` or `66 43` fails before that decoder in the controls. |
| Decoded marker `0x3ab6f6` | Loads uint16 from handle+0x720, the decoded base structure. Requires 0x4366; mismatch returns -13. The marker is base field 1, not the first raw socket word. |
| Length/stream accounting | Pending length is decoded header+body. Short input returns -12/compacts; coalesced input caches lookahead. A malformed next header can reject a complete current frame. Gather itself does not consume it. |
| Effective type | Header decoding at `0x3b7244` calls the extension union; `0x3b724a` writes its selector into decoded base +6 (handle+0x726). A base field alone does not establish effective ACK type. |
| ACK configuration `0x3abe6a` | For effective type 0x1002, copies ACK encryption/key methods into handle+0x11c/+0x120 before key-mode validation. |
| Key dispatch `0x3abeb2` | Mode 0 clears key length and skips key setup. Mode 2 copies decoded key then calls set-key. Mode 3 calls compute-k then set-key. Other modes return -30, with the preceding configuration writes retained. |
| Set-key `0x3ab24a` | Empty key + nonzero encryption method returns -31. Nonempty key + unsupported method returns -29; methods 3/4 select AES setup. No explicit exactly-16-byte length check is established here. |
| Body `0x3abf08` | Empty body supplies zero output length. Nonempty body with base byte +0xc nonzero invokes decrypt `0x3ab31e`; plaintext branch copies bytes. Missing key/unsupported method/primitive failure remain separate errors. |
| Consume `0x3ac032`–`0x3ac056` | Saves decoded base word +8 to handle+0x3490, advances cursor, reduces count and clears pending before returning to the ACK caller. |
| ACK type `0x3ac100` | Requires effective type 0x1002 after receive/decrypt. Mismatch records type and returns -14, without rolling back frame consumption. |
| Compression / optional body | Copies compression method/limit. Empty body returns zero. Positive body invokes TGCPBody decoder `0x3b8860`; malformed body maps to -18. ACK-body field 2 can contain an embedded auth response; its later state/session use remains unfinished. |
| Key-syn state `0x3a9f8c` | Requires initialized handle, nonnegative descriptor and state 2. -12 becomes zero without auth send. ACK zero with state still 2 and no relay-progress flag reaches auth-send call `0x3a9fd8` -> `0x3ab964`. |

GCloud TX independently prepends raw 43 66 before packTLV at `0x3ab430`.
That does not supply the inbound envelope. The prior v0.8 raw-prefix argument
confused decoded storage with wire bytes for this mirror path. Runtime selection
and equality with the user's historical phone library remain unverified.

## TLV and session interpretation

ACK-head varint decoder `0x3b5ab6` reads methods as uint8, key information as a
length-delimited union, compression method as uint8 and limit/reserved as
varuint32. The nested key union can overwrite scalar key mode. It propagates
physical truncation (-2) and detects declared-end overrun (-34), potentially
after modifying decoded storage. Missing fields can retain prior storage;
duplicates can overwrite; unknown scalar fields can be skipped. Strict parser
policies must not be confused with these native behaviors.

No SYN-base/session equality check was observed in these bounded ACK functions.
This does not prove arbitrary/echoed/zeroed identifiers work later. Server field
generation remains unresolved. Mode 0 can reach an empty-body zero return here;
method 4 with a later encrypted body and no key returns -31. This does not prove
mode 0 is compatible with the historical SYN or later session encryption.
Successful cipher/DH negotiation was not executed. Static compute-k uses the
existing DH object and hashes a computed secret into key storage; controls stub
that computation to failure and do not invent a successful key exchange.

The receiver also has a conditional receive-error translation: -11 plus
handle+0x33a8 == 1 and +0x33ac == 10001 sets +0x33d4 and returns -38. Its broader
semantic meaning is not assigned from this branch alone.

## What the implementations establish

[Canonical offline parser](../../../experiments/rx_envelope.py) is the original
AA/varint framing subset, with 17 [synthetic tests](../../../tests/test_rx_envelope.py).
It has fragment/coalescence, declared bounds, marker, truncation, duplicate and
resource controls. `Frame.base_type` is only a base-field observation; extension
bytes remain opaque. It does not return an accepted/effective ACK type. Successful
finish is terminal. 99 mode, unknown/duplicate fields and native gather/lookahead
error timing are outside this strict subset; its resource bounds are local policy.

[Source verifier](../../../tools/verify_private_source.py) and 14
[controls](../../../tests/test_verify_private_source.py) verify pinned private
source integrity when explicitly selected. They do not run game code.

Lane native controls execute actual selected Thumb functions in a fresh Unicorn
mapping. Explicit stubs isolate network/splitter or decoded-receive boundaries,
bounded libc operations, log/last-error/error-string helpers, failure-only DH and
suppressed auth send. Globals/GOT/full Android runtime are not fully initialized.
Each stage's stub list is reported. No helper tests establish a complete native
socket session; a zero result or suppressed-send boundary is not a real packet.

## Remaining work and disabled device gate

CF18-G2-ACK-01 remains focused on the optional embedded-auth ACK body, its later
session consumers and actual negotiation requirements. The framing lane separately
owns remaining 99/boundary/lookahead questions. [Assignments](../../../coordination/assignments.json)
record one task per lane and precise prerequisites.

A/B/C readiness is **false**. No candidate wire replies or device runner are
supplied. Prerequisites still missing:

- Historical phone library equality/runtime path and original SYN/failed-ACK
  construction sufficient to establish the actual negotiation context.
- Supported complete receiver/body/session predicates and a justified candidate.
- Historical bridge/passthrough source or verified deployed interface, directional
  EOF controls and preserved unrelated dispatch.

Only after these exist may a separate explicitly disabled/passive-by-default
proposal define 4–16 attempts, unique run/connection IDs, loopback transport,
known game IP AND port scope, baseline/negative controls and failure attribution.
No automatic phone/live-network experiment is authorized by this document. G2
advances only on a later authentic client protocol packet after ACK, followed by
verified session state. Neither parser success nor native emulation counts.

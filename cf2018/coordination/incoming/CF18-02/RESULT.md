# CF18-02 — bounded native ACK/session trace

Base main: `fefd0dc224851fefc2b74a51fc95e0fa0090e9a2`.
Date: 2026-10-30 UTC. SUBMITTED; no active claim remains after submission.
Owner: CF18-02; writes only this lane. Canonical knowledge/assignments require
CF18-00 review. Acceptance was recorded in [ACCEPTANCE](ACCEPTANCE.md) before code.
Evidence classes: MIRROR_SOURCE_PROVENANCE, ORIGINAL_NATIVE_STATIC,
NATIVE_EMULATION_WITH_STUBS, ORIGINAL_CODE + LOCAL_SYNTHETIC.
**G2 remains BLOCKED. No complete server ACK, accepted phone handshake or login.**

## Source and workspace receipt

The live main was fetched through the authorized despairarc000 GitHub connection.
All nine startup documents, assignments, TGCP research, Graphify dependencies and
existing lane results were reviewed. This workspace is a connector-derived
snapshot, not a git checkout: git status exited 128. All 46 tracked CF2018 blobs
matched that base's Git blob hashes; no preexisting CF18-02 packet/claim existed.
The assignments still say BLOCKED_SOURCE, but the preceding
[CF18-01 native packet](../CF18-01/NATIVE_RX_RESULT.md) supplies genuinely new
source evidence. No repeated Drive inventory was needed.

The user explicitly authorized internet APK search/retrieval earlier. Source:
[APKPure package listing](https://apkpure.net/crossfire-legends-action/com.tencent.tmgp.cfmnac/download)
and the observed mutable
[XAPK entrypoint](https://d.apkpure.net/b/XAPK/com.tencent.tmgp.cfmnac?version=latest).
The prior packet records range retrieval, embedded Android/XAPK identity
`com.tencent.tmgp.cfmnac`, version `1.0.11.11`, code `11`, Mono files and internal
v1 signature checks. This activation independently recalculated:

| Artifact | Size / SHA-256 |
|---|---|
| Private APK member | 30884905 bytes; `33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9` |
| APK's lib/armeabi-v7a/libapollo.so and local extracted copy | 5243704 bytes; `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8` |

The native runner verifies the actual size/hash and ELF32 little-endian ARM ISA
before mapping the library. Relevant symbols are Thumb; addresses below are
virtual code addresses with the Thumb bit cleared. Capstone 5.0.9 and pyelftools
0.33 supported bounded static reads; Unicorn 2.1.4 executed controls.
The original remains ignored/local under
`coordination/incoming/CF18-04/private/armeabi-v7a-libapollo.so` on this runner.
No original, raw disassembly, key, capture or signed-download token is published.
Future runners must check source availability and hash rather than assume disk.

The mirror is not byte-proven equal to the historical phone's Original.xapk.
Internal signature integrity is not independent distribution attestation. This
packet supplies no new phone evidence or historical relay source. The unrelated
9.99 APK and cfmobileoffline were not used.

## ACK receive ordering and branch predicates

These are observations of the fingerprinted **GCloud** functions, not the
separate legacy overloads. CF18-01 owns framing; its splitter finding is a
prerequisite, not duplicated here.

| Address | Observed predicate / state effect |
|---|---|
| `0x3ac0b8` / `0x3ac0d2` | ACK receiver rejects a null handle (-1); otherwise calls receive/decrypt `0x3abe34` first. |
| `0x3ac0d8`–`0x3ac0fe` | Propagates nonzero receive errors, except -11 with handle+0x33a8 == 1 and handle+0x33ac == 10001: sets handle+0x33d4 to 1 and returns -38. The meaning of that historical/error state is not inferred. |
| `0x3ac100`–`0x3ac124` | Only after receive/decrypt returns zero, requires decoded uint16 at handle+0x726 == 0x1002. Mismatch saves the observed type at +0x33e4 and returns -14. This does not roll back earlier receive/decrypt side effects. |
| `0x3ac126`–`0x3ac130` | Copies decoded ACK compression method at +0xb4c into +0x33f4, and compression limit at +0xb50 into +0x33f8. No value-range check is present in this bounded function. |
| `0x3ac16e`–`0x3ac176` | A nonpositive decoded body length returns zero without parsing a body. Native framing supplies an unsigned body length; controls use zero, not a malicious negative framing length. |
| `0x3ac1a4`–`0x3ac1c8` | A positive body length invokes TGCPBody::unpackTLV at 0x3b8860 on the receive output buffer, with a discriminator initialized to 0x1002. Parser failure records an error string and returns -18; parser zero returns zero. |

### Header/extension type is decoded, not merely an echoed base field

TGCPHead varint decoding at `0x3b7244` calls the extension decoder. At
`0x3b724a`–`0x3b724c` it overwrites decoded base offset +6 with the extension
union discriminator. The extension decoder at `0x3b6a3c` dispatches by its wire
tag's field number; 0x1002 selects the ACK-head decoder `0x3b5ab6` through the
call at `0x3b6afa`. Consequently a base field labeled 0x1002 in a serializer
alone does not establish the ACK type observed at handle+0x726.

Optional body decoding is also a union dispatch: `0x3b8488` reads a wire
selector, and 0x1002 calls TGCPAckBody::unpackTLVWithVarint at `0x3b49a6`.
Other known selectors and unknown-field skipping also exist; the decoder writes
its selector back to the reference. The bounded ACK caller does not recompare
that reference after body parsing. This is not a recommendation to send a
mismatched body. The ACK-body decoder's field 2 delegates to an embedded
TGCPAuthRspBody parser and sets its presence byte to 1. The session/auth meaning
and later consumption of that embedded response remain a separate prerequisite;
no valid nonempty ACK/auth body was constructed or accepted in these controls.

## ACK component TLV rules: syntax is not session acceptance

The real ACK-head varint decoder `0x3b5ab6` reads tags as varuint32 and dispatches
by tag >> 4. Observed fields relative to the decoded ACK head:

| Field | Storage / read | Native label or use |
|---|---|---|
| 1 | +0, uint8 | bEncMethod; copied to handle+0x11c |
| 2 | +1, uint8 | bKeyMethod; copied to handle+0x120 |
| 3 | +4, 32-bit network-order nested length then TGCPKeyRsp union | stKeyInfo; union selector overwrites ACK +1 after decode |
| 4 | +0x40c, uint8 | bCompressMethod; copied by ACK receiver |
| 5 | +0x410, varuint32 | dwCompressLimit; copied by ACK receiver |
| 6 | +0x414, varuint32 | dwReserved; no semantic acceptance use established here |

The scalar labels were cross-checked against bounded native visualize references;
no serializer was used as an acceptance oracle. TGCPKeyRsp varint decoder
`0x3b00ee` dispatches its union by selector: 2 calls TSF4GKey at `0x3ae34c`,
3 calls TSF4GRawDHRsp at `0x3ae8b2`, and 4 calls TSF4GEncDHInfo at `0x3aee3e`.
The receiver's key-mode dispatch below nevertheless rejects mode 4. A syntax
branch therefore does not imply usable negotiation. Parsing field 3 can replace
an earlier scalar bKeyMethod; inspecting field 2 in isolation is insufficient.

Bounds observed: the ACK-head decoder loops to entry cursor + declared component
length, uses TdrReadBuf for physical input bounds, propagates read errors, and
returns -34 when consumed cursor overshoots the declared end. A field can already
have changed decoded storage before that final bound error. Controls distinguish
physical truncation (-2) from declared-bound overrun (-34). The decoder resets
presence bookkeeping, not all decoded scalar storage; omitted scalar fields can
retain prior values. An empty component returns zero on a zeroed control object,
duplicated method fields overwrite earlier values, and an unknown scalar field
can be skipped. Required-field, duplicate and unknown-field rejection must not
be presented as native rules based on this function.

TSF4GKey has a byte length and at most 128 byte-array iterations; the raw-DH
response has a uint16 length and at most 64 array iterations in these decoders.
These are observed container limits, not proof that every such key length/value
is cryptographically or semantically accepted. No live or historical key bytes
were obtained or published.

## Key-mode, encryption and body processing

Receive/decrypt `0x3abe34` first calls the actual splitter. Nonzero result
propagates before ACK configuration changes. With decoded type 0x1002:

| Branch | Observed behavior |
|---|---|
| `0x3abe6a`–`0x3abe76` | Stores ACK bEncMethod/bKeyMethod in handle+0x11c/+0x120 before validating key mode. |
| `0x3abeb2`–`0x3abec8`: key mode 0 | Sets key length byte at handle+0x458 to zero, skips compute/set-key and continues. It does not compare the selected mode with a stored SYN mode in this bounded routine. |
| `0x3abeca`–`0x3abee8`: key mode 2 | Copies decoded key bytes from +0x745 using length byte +0x744 to handle+0x459, stores length at +0x458, then calls set-key. |
| `0x3abeea`–`0x3abef8`: key mode 3 | Calls compute-k at 0x3abd7c with raw-DH response at +0x744; nonzero propagates. Success proceeds to set-key. |
| `0x3ac06c`: other modes | Returns -30, after method/mode storage has already changed. |
| `0x3abefc`–`0x3abf04` | set-key 0x3ab24a failure propagates, without consuming pending frame. |
| `0x3abf08`–`0x3abf4c` | Zero body skips decryption and supplies output length zero. Thus mode 0 plus an incompatible future crypto setting can return zero for this empty stage. |
| `0x3abf4e`–`0x3abf78` | Nonempty body with decoded base byte +0xc nonzero calls decrypt 0x3ab31e. Failure propagates before cursor consumption. |
| `0x3abfde`–`0x3abfea` | Nonempty body with that byte zero is copied as plaintext regardless of negotiated method in this bounded branch. |
| `0x3ac032`–`0x3ac056` | Saves decoded base word +8 at handle+0x3490; advances cursor, subtracts pending length and clears pending. This precedes the ACK caller's final type/body checks. |

Set-key `0x3ab24a`: zero key length succeeds only for method 0; another method
returns -31. Nonzero length with method 0 returns zero without AES setup;
methods 3/4 invoke tgcpapi_taes_setkey2 with a 128-bit setting. Unsupported
nonzero methods return -29; primitive setup failure maps to -31. The bounded
function does not impose an explicit "exactly 16 bytes" comparison on length;
do not invent one from the AES setting.

Decrypt `0x3ab31e`: method 0 uses a capacity-checked plaintext copy; methods 3/4
require nonzero key length then call tgcpapi_taes_decrypt/decrypt2. Missing key
returns -31; unsupported method -29; primitive failure maps to -33. Successful
cipher modes were not exercised. No crypto primitive is stubbed to succeed.

Compute-k `0x3abd7c`, **static only**: reads a raw-DH public value, uses the
handle's existing DH object at +0x33e8, calls DH_compute_key, hashes its returned
secret with MD5, copies 16 derived bytes into handle key storage, and sets length
16. Allocation/DH failure paths return -40; a returned length >128 returns -41.
The required client DH state is not known for the historical capture. Native
controls deliberately stub compute-k to a failure, never fabricate a DH success
or publish derived keys.

## Q-03 / Q-04 conclusions and outer state

Q-03 is **partially traced, not resolved into a server generation policy**.
No SYN-base/session echo equality comparison was observed in these bounded
ACK/receive functions. The saved decoded base word can vary across independent
controls and is still stored; that proves only lack of this comparison at this
boundary. It does not prove that arbitrary identifiers work later, that all
base fields are ignored, or that the server should copy/zero/generate them.

For orientation, outgoing GCloud build-frame-base `0x3aabd0` writes the marker
constant and requested type, fills base +0x10 from handle+0x12c and base +4 from
handle+0x348c, and clears base +0xc. That is client-side construction, **not a
server echo requirement**. The actual failing ACK bytes, exact SYN negotiation
and later auth/session predicates must be recovered before stronger claims.

Q-04 is **narrowly answered for this mirror/function**: key mode 0 reaches the
empty-body path without a SYN-mode equality test or key setup. A nonempty body
marked for decryption with method 4 and zero key length instead returns -31.
Passing an empty ACK stage cannot establish working subsequent encryption or
historical-phone mode-0 compatibility. SYN construction `0x3aba5c` starts its
key-negotiation byte at zero and sets it to 3 / generates DH when the handle's
DH object is present; actual runtime presence is unverified.

State handler `OnStateKeySyning` at `0x3a9f8c` requires an initialized handle,
nonnegative descriptor and state +0x6c8 == 2. In the non-relay branch it calls
this ACK receiver. Return -12 is translated to zero **without an auth send**.
ACK zero, relay-progress flag zero and state still 2 reach send-auth boundary
`0x3a9fd8` -> `0x3ab964`. Native controls suppress that call and deliberately
return -77; no socket/send occurs. The synchronous start_connection path also
calls ACK at `0x3a845a`, then send-auth at `0x3a84b2` on success. The actual
send-auth function builds type 0x2001 and changes state to 3 before its send;
those construction/state instructions were read statically, not executed here.
No auth packet, next client packet or state 3 on a phone was observed.

## Original implementation and native controls

[Original runner](native_ack_controls.py) contains no game binary/instruction
bytes and no server ACK builder. It maps private PT_LOAD segments into a fresh
zeroed Unicorn memory space and executes the selected native functions. Budgets:
100000 instructions / one second per execution; component input <=512 bytes,
synthetic body <=256 bytes; libc stub operations <=65536 bytes. These are local
harness policies, not claimed native protocol bounds.

Three isolated boundaries are explicit:

- `decoded_probe`: splitter is stubbed to return a supplied status after injecting
  decoded synthetic state. Receive/decrypt and optionally its actual ACK caller
  execute unchanged. DH is failure-only. This does not retest framing.
- `ack_probe`: receive/decrypt is stubbed at its decoded boundary; actual ACK
  receiver and optional state handler execute. Malformed body tests use the real
  TGCPBody decoder; an optional result stub exists solely for error propagation.
  Auth-send is always suppressed with -77, never an actual or successful send.
- `ack_tlv_probe`: actual ACK-head varint decoder runs on independent component
  fragments and synthetic TdrReadBuf. No full TGCP frame/valid server ACK exists.

Common stubs: bounded libc memset/memcpy/memmove; XLog no-op; last-error get/set;
error-string lookup only. ELF globals/GOT are not fully relocated or initialized;
this is not Android, a full dynamic loader, live sockets or full library state.
The functions under test and their relevant scalar/union/body readers are not
replaced by Python equivalents. Every boundary/stub is returned in test metadata.
The zeroed harness does not establish default field values in a live reused
handle. Dependency absence skips native tests only when no source is selected;
an explicitly selected wrong source or missing dependency fails visibly.

[Twenty-five tests](test_native_ack_controls.py) passed: 24 native test methods
plus one fingerprint guard. They exercise unsupported mode/method rejection,
side effects before errors, missing-key rejection, plaintext copy branches,
compute failure propagation, expected type, compression scalars, malformed body,
special error translation, waiting-vs-auth state, actual ACK+receive ordering,
component bounds/truncation, duplicate/missing/unknown fields and nested selector
overriding scalar key mode. Controls are entirely synthetic; no capture bytes.

Minimal validator proposal: after separately validated framing, classify the
**effective decoded** extension type and key method; report wrong type (-14),
unsupported mode (-30), and applicable set-key/decrypt failures as separate
stages. Keep partial-input (-12), decoded-field storage, frame consumption and
later state transition separate. Do not output "valid ACK" from these predicates.
A strict new parser may reject duplicates/unknown fields as an explicitly named
local policy; native parity must not be claimed for that policy. Full deployable
validation waits on the remaining body/auth/session and runtime evidence rather
than inventing server defaults. The bounded native runner is the executable
proposal here; no speculative server serializer or complete validator is added.

## Actual checks and integration recipe

From cf2018:

```text
python tools/knowledge.py route 'gcloud ACK session key mode receiver branch validation'
  Routes: [('tgcp', 1)]
python tools/knowledge.py doctor
  PASS: required files, links, vault and graph
python -m unittest discover -s tests -v
  Ran 52 tests; OK
CF18_APOLLO_LIBRARY=coordination/incoming/CF18-04/private/armeabi-v7a-libapollo.so \
  PYTHONPATH=private/analysis_deps \
  python -m unittest discover -s coordination/incoming/CF18-02 -v
  Ran 25 tests; OK; no skips
python -m unittest discover -s coordination/incoming/CF18-02 -v
  Ran 25 tests; OK (skipped=24); one fingerprint guard ran
CF18_APOLLO_LIBRARY=coordination/incoming/CF18-04/private/armeabi-v7a-libapollo.so \
  PYTHONPATH=private/analysis_deps \
  python -m unittest discover -s coordination/incoming/CF18-01 -v
  Ran 32 tests; OK; no skips
```

Coordinator: review this packet against the pinned library and rerun the native
controls; preserve mirror-vs-phone and emulation-vs-runtime distinctions. Update
canonical Q-03/Q-04/evidence/graph/assignments only within coordinator ownership.
Integrate the specific predicates/limits, not a claim that ACK mode 0 or copied
fields are correct for a simulated server. Keep CF18-G2-ACK-01 and G2 blocked on
actual runtime/phone evidence.

Next bounded native work is the optional embedded-auth ACK body and its later
session consumers, then byte-preserving confirmation of runtime selected path
and library identity. Recover historical SYN/failing-ACK construction and relay
sources privately to explain the observed EOF. No A/B/C phone run is ready from
this packet alone; no device/network experiment was run.

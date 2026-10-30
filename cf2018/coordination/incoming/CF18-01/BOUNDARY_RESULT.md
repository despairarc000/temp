# CF18-G2-RX-02 — 99 framing, bounds and buffered-error timing

CF18-01, 2026-10-30 UTC. Resumed base main:
`40c4aafe6665e671d08df6badb378121ec4ff213`.
Draft began at `37b808d095641c90e80a707209f656e9bf29c53f`; both SHAs are actual.
SUBMITTED; no active same-lane claim remains. Only this incoming lane is changed.
Evidence: ORIGINAL_NATIVE_STATIC, NATIVE_EMULATION_WITH_STUBS and separately
ORIGINAL_CODE / INDEPENDENT_SYNTHETIC. [Acceptance](BOUNDARY_ACCEPTANCE.md)
preceded the draft, and its resume addendum preceded corrections/new tests.
**G2 BLOCKED. No complete ACK, native session acceptance, phone packet or exploit claim.**

## Activation and source provenance

Live main, nine required startup documents, assignments, Graphify dependencies,
reviewed receiver/session/source and existing lane results were refreshed. Current
CF18-01 assignment is remaining native 99/bounds/lookahead, so unfinished local
framing work was resumed before another task. Git status exited 128: the local
snapshot is not a checkout. No worker process was active. The completed CF18-02
local continuation and pending coordinator assignments/integration/worklog handoff
are outside this lane and were preserved. Canonical code/docs are not changed.

Source: [canonical recovered-mirror receipt](../../../sources/SOURCE_PROVENANCE.md),
user-authorized internet retrieval, not a substitute 9.99 or cfmobileoffline build.
Observed [listing](https://apkpure.net/crossfire-legends-action/com.tencent.tmgp.cfmnac/download)
and mutable [XAPK entrypoint](https://d.apkpure.net/b/XAPK/com.tencent.tmgp.cfmnac?version=latest).
Prior source receipt verified embedded package com.tencent.tmgp.cfmnac, version
1.0.11.11, code 11, Mono and internal v1 signature. APK SHA-256 is
`33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9`.
No new download was needed. Actual private Apollo was reopened and recalculated:
5243704 bytes, SHA-256
`4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`;
ELF32 little-endian ARM EABI5, relevant functions Thumb. Every probe requires
that size/hash/ISA before native execution. Addresses below are virtual addresses
with Thumb bit cleared, scoped to these bytes only.

Private runner path is coordination/incoming/CF18-04/private/armeabi-v7a-libapollo.so;
optional dependencies are in private/analysis_deps on this runner. Availability
on later activations must be checked. Capstone 5.0.9, pyelftools 0.33 and Unicorn
2.1.4 support bounded reads/controls. Originals, raw disassembly and captures are
not published. Equality/runtime selection on the historical phone, matching OBB,
original v0.1-v0.8 probes and historical failed ACK construction remain unverified.

## 99 means fixed-width base values, not fixed-width tags

The earlier [receiver packet](NATIVE_RX_RESULT.md) independently traced ACK to
GCloud gather `0x3ab5ec`, not the separate legacy overload. Its decoded 0x4366
marker comparison and independent client TX prefix findings remain unchanged.
The canonical historical frame_gate.py raw-prefix model is not native evidence.

| Bounded native site | Observed read / implication |
|---|---|
| TGCPHead 99 decoder `0x3b726e`, tag call `0x3b72a4` | Still reads tags with varuint32. Top-level nested lengths use network uint32. A four-byte padded tag is not this encoding. |
| Base dispatch `0x3b72e0` | Calls base NoVarint decoder `0x3af5f0`, distinct from AA varint decoder `0x3af4cc`. |
| Base tag call `0x3af61e` | Tags again remain varuint32. Field numbers come from tag >> 4. |
| Base scalar branches, shared uint16 read `0x3af686` | Fields 1–4 are network-order uint16 in 99 mode. Field 1 supplies decoded marker; field 4 remains base metadata, not extension-resolved ACK acceptance. |
| Byte read `0x3af6b2`, uint32 read `0x3af6f0` | Field 6 is uint8; fields 5/7/8/9 are network uint32. Field 9 supplies declared body length. |
| UInt16 `0x1a3314`, UInt32 `0x1a333e` | Physical remaining-byte checks precede byte reads; network-order bytes are assembled into little-endian decoded storage. Cursors advance by 2/4 respectively. |

All-nine-field independent fixtures have header lengths 32 (AA) and 46 (99),
with two body bytes making totals 34/48. Native 99 parses the decoded marker
0x4366, waits for unavailable declared body length 0x01020304, and rejects the
swapped decoded marker 0x6643 with -13. Proper 99 controls enter the NoVarint
header/base branches; padded tags do not return success. This is a bounded base
trace; extension/ACK semantics remain CF18-02 ownership and opaque in the proposal.

## Declared and physical bounds have different error timing

The header helper `0x3aab44` rejects signed-negative outer lengths (-18), waits
for zero/unavailable header length (-12), and calls TGCPHead decoder. At
`0x3aaba8`–`0x3aabaa`, decoder -2 is translated to -12; other decode errors map
to -18. Thus malformed nested input is not guaranteed to produce one code.

The initial draft's 20-method run failed two subtest assertions: nested base
length +1 with default independently synthetic 00ff body returned -12, not its
assumed -18, in both modes. The library/runner was not changed to force a result.
The corrected test records the reproduced exact matrix:

| Nested length delta | AA, body 00ff | AA, body 5859 | 99, body 00ff | 99, body 5859 |
|---|---|---|---|---|
| -1 | -18 | -18 | -18 | -18 |
| +1 | -12 | -18 | -12 | -12 |

These are exact synthetic controls and helper error mappings, not a general
classification of malformed packets or proof of valid incomplete server data.
Outer lengths 0 / 0x7fffffff return -12 with the bounded unavailable input;
0x80000000 / 0xffffffff return -18. Partial header/body controls also wait -12.

### Unsigned addition is not a complete size validation

The gather additions at `0x3ab6e4` (current) and `0x3ab738` (lookahead) store
32-bit header+body totals without a checked-overflow branch in this bounded
function. Independent synthetic huge declared lengths reproduce wrap:

- AA header 36 + body 0xffffffff stores pending length 35 and gather returns 0
  even though that declared body is absent; 99 header 46 stores 45 similarly.
- AA header 36 + body 0xffffffdc stores pending zero and gather returns 0.
  The host-consumption helper refuses zero pending length.
- A wrapped 99 lookahead total can be cached as 45, then promoted by another
  real gather call after explicitly simulated current-frame consumption.

These demonstrate only isolated gather arithmetic on synthetic input. No later
receive/decrypt/ACK operation is run on those wrapped cases, no full receiver
acceptance/exploitability is asserted, and no runtime attack or device test is
proposed. The strict Python proposal intentionally uses nonwrapping addition and
a cap; it must never reproduce this arithmetic as a validity rule.

## Fragmentation, coalescence and remembered receive errors

A complete current frame can cache a following AA or 99 header when at least
32 bytes remain. Mixed modes promote the cached decoded header without another
header decode. Gather does not consume current data itself. The optional second
probe call performs an explicitly labeled **host simulation** of the caller's
cursor/count accounting, then executes actual gather again; it does not execute
the native consume/decrypt caller or a TCP stream.

Wrong next decoded marker can be cached without checking it until promotion,
then returns -13. A malformed next envelope produces -18 eagerly while the
current complete frame remains unconsumed. Incomplete next header is not cached;
lookahead -12 is tolerated. A decoded next header with unavailable body is cached,
then promotion waits/compacts. Partial data at nonzero cursor compacts to cursor
zero, with remaining bytes verified by calculated hash.

Injected recv -2/-4 become remembered -9/-10. A buffered complete frame can still
return zero first; after host-simulated consumption the next gather returns the
remembered error without a new recv. Partial input instead returns that error
immediately. Recv 0/-3 on partial input returns -12 in these controls. These
values are wrapper-status injections; they do not identify historical peer EOF.
Invalid capacity/cursor/count invariants return -1 before recv. A buffer already
at its capacity skips recv but can parse its existing frame.

## Standalone strict framing extension proposal

[boundary_envelope.py](boundary_envelope.py) extends the integrated original
AA parser into an offline AA/99 proposal; canonical experiments/rx_envelope.py
remains unchanged. No listener, connector, serializer or ACK validator exists.
Both modes use varint tags; 99 base values use the fixed-width network reads
above. Mandatory base marker/body-length, unknown/duplicate rejection, bounded
nonwrapping total, terminal failure and EOF remain intentional strict policies.
Opaque extension bytes never imply effective ACK/auth/session acceptance;
Frame.base_type remains base metadata only. Native 32-byte gather threshold,
lookahead poisoning/cache timing and remembered recv errors are not reproduced.

[14 independent tests](test_boundary_envelope.py) cover both modes/all scalar
widths, every fragment split, bytewise/mixed coalescence, both raw prefixes,
swapped decoded marker, each EOF truncation, fixed-scalar truncation, nested/body
size mismatch, uint32-wrap/cap refusal, duplicates/unknowns, padded tags, opaque
extension and terminal failure/finish. They use an independent fixture recipe,
not native serializers/captures or the native runner's fixture helper.

## Meaningful results and coordinator integration recipe

Actual checks from cf2018 on the resumed main:

```text
python tools/knowledge.py route 'native framing 99 declared bounds gather lookahead receive errors'
  Routes: [('sources', 1), ('tgcp', 1)]
python tools/knowledge.py doctor
  PASS: required files, links, vault and graph
python -m unittest discover -s tests -v
  Ran 101; OK (skipped=19): 82 PASS, 19 private-source SKIP
python -m unittest discover -s coordination/incoming/CF18-01 -p test_boundary_envelope.py -v
  Ran 14; OK
CF18_APOLLO_LIBRARY=<private pinned Apollo> PYTHONPATH=<private analysis dependencies> \
  python -m unittest discover -s coordination/incoming/CF18-01 -p test_native_boundary_controls.py -v
  Initial: Ran 20; FAILED with two subtest assertion failures, as recorded above
  Corrected: Ran 20; OK
CF18_APOLLO_LIBRARY=<private pinned Apollo> PYTHONPATH=<private analysis dependencies> \
  python -m unittest discover -s coordination/incoming/CF18-01 -v
  Ran 66; OK; no skips (32 prior, 20 new native methods, 14 new strict-parser methods)
python -m unittest discover -s coordination/incoming/CF18-01 -v
  Ran 66; OK (skipped=29): 37 PASS, 29 native-source SKIP
```

The optional [native runner](native_boundary_controls.py) pins source/ISA and
limits input/state to 64 KiB, 100000 instructions and one second per native call.
Explicit stubs: nonpositive recv wrapper result, bounded libc memory operations
and error-string lookup. The gather/header/base parsers are real native functions.
Fresh mappings are used per probe; globals/GOT/full Android loader are incomplete.
Host consumption and network-result injection are always labeled. No native
socket, positive network read, ACK or phone state machine is exercised here.

Coordinator should independently rerun controls against pinned source, review
99 scalar/tag details, length arithmetic and error distinctions, then integrate
only the useful offline parser extension and descriptive boundary findings.
Keep strict cap/terminal/opaque-extension protections, existing base_type meaning
and canonical tests. Do not relax policies to match native wrap, duplicates,
lookahead timing or deferred errors. Update shared EVIDENCE/Q-01/Graphify/queue
only after coordinator review; all such updates are outside this lane.

Q-01 is improved for the pinned mirror receive path, still open for the actual
phone path. No original/raw game code, binaries, captures, key/token or guessed
complete reply is included. Historical relay EOF attribution and phone/OBB
identity remain missing. No A/B/C candidate or device execution follows; only a
later authentic post-ACK client protocol packet can advance G2.

# v3.8 source audit and actual-native differential

2026-10-31, CF18-00. Base main44bb53ebf7aee223840a9fb87f8e5765e25de000.
This continues [the actual phone report](V38_BLOCKER.md); no phone run or worker
restart. User now supplied the exact private source ZIP. Source absence is resolved.

## Provenance and acceptance

CF2018_TGCP_v3.8_GCloud_DataHead_Flags.zip SHA256
`e3bbc31f7b93e738aff0d4205dd0d1418c7abd55b7c17b332ca5d426eb619df2`;
60 entries, extracted to private/v38_source locally. The archive includes a real
historical SYN fixture and is NOT suitable for public redistribution. Original
archive, APK and OBB untouched. Public [source pins](../../../coordination/V38_SOURCE_PINS.json)
identify dependencies without publishing their contents. [Native provenance](../../../sources/SOURCE_PROVENANCE.md):
Apollo5243704 bytes SHA2564812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8,
ELF32 little-endian ARM/Thumb. NativeControl validates hash/ISA per execution.
[Acceptance defined before implementation](../../../coordination/CF18-V38-SOURCE-AUDIT-ACCEPTANCE.md).

## Results and earliest unresolved boundary

| Stage / question | Actual result | Evidence class / limit |
|---|---|---|
| v38 DataHead read order | 3 native call edges +16 instruction pins PASS | Original-native static audit from supplied source; flag0 is compression off |
| RPC protocol / transport audit | 14 edges +23 pins PASS | Original-native static; not proof of phone packet producer |
| Exact source ACK63 | native return0; state2; method4 initial becomes0; key mode0/key absent/compression0 | Actual original receiver, synthetic lab input |
| Exact source auth54 | native return0; state4; method0 retained | Auth-send omitted; state3 supplied explicitly |
| Exact source Bingo91 | native return0; state5; method0 retained | Synthetic account/relay state; no real identity validation |
| Native legacy RPC header | BE32 name size +name +U8 kind +BE64 sequence | Actual original serializer; memory output sink replaces transport |
| v38 legacy classifier on native output | Recognizes synthetic request after4-byte prefix | Legacy positive / strict-header negative controls; no real request decoded |
| Report's actual80/85-byte bodies | Application remains not identified | Redacted report has no recoverable body/sequence/name; no new native failure localized |

The earliest verified failure in the current v38 investigation is **application
identification by the observer**, not an identified native rejection predicate.
No4013 reply was sent in that phone test, so it cannot establish a rejected service
response. The earlier v1.2 body-preamble failure remains independently localized
and corrected; it is not the current blocker. Numeric state5 alone is not login.

[Stage matrix, all reached stubs](../../../coordination/V38_STAGE_CONTEXT_MATRIX.json),
[reproducer](../../../tools/replay_v38_stage_context.py). Each stage loads a fresh
ELF and carries a fixed-address0x40000-byte context snapshot, avoiding accumulated
emulator hooks. Wrapper0x284fcc returns no-data-3; bounded libc memory operations,
XLog no-op and last-error helpers are substituted where listed. ACK/auth/Bingo
receiver entries0x3ac0b8/0x3ac306/0x3ac39e execute actual instructions. No socket,
Android initialization, actual auth-send, or legitimate account session is modeled.
This selects mode0 in this exact harness; it does not measure live Android context
or exclude a separate application-level transformation.

## Correction: the four-byte prefix is packet sequence, not UID

Earlier coordinator SERVER_PATH/E-30 wording called handle+0x12c and the routed
prefix a UID. That interpretation was wrong. Actual TGCPBase visualization loads
base+0x10 at0x3af85e; literal at0x3af8c8 plus PC0x3af86c resolves the original
field label `[dwSequence]`. Packer0x3af2b2 writes field7/tag0x70 at0x3af342 and
loads base+0x10 at0x3af34c. Routed TX copies handle+0x12c into that header field
and serializes the same value as a four-byte big-endian body prefix.

Encrypt-and-send0x3ab430 increments handle+0x12c at0x3ab5ae–0x3ab5b8 before
send-buffer submission0x3ab5bc. Extended [native TX controls](../../../experiments/native_routed_tx.py)
now execute real header packing and method0 body copying before suppressing only
send-buffer submission0x3ab3a6 (sentinel-77). The independent counter moves from
0x01020304 to0x01020305. [Eight-case matrix](../../../coordination/ROUTED_TX_MATRIX.json).
State4/uninitialized/oversize/negative-timeout/missing-route remain negative controls.
This does not identify any account UID or imply that every TGCP direction has the
same prefix. Earlier UID claims are explicitly superseded by this correction.

## Native application serializer differential

Original binary header entry0x39c3bc reads strict-write at+0x21. Legacy branch
0x39c3f8 writes the name;0x39c400 writes one-byte kind;0x39c412 calls the64-bit
network-order writer0x39c328. Actual writes captured by replacing only transport
write0x398ede with a bounded128-byte memory sink. Header/string/integer serializers
execute original instructions. Independent names and sequences only. Strict-write
positive control produces the distinct versioned format; v38's legacy classifier
correctly does not label it legacy. [Runner](../../../experiments/native_rpc_header.py),
[tests](../../../tests/test_native_rpc_header.py). AddressService init also selects
protocol0x20 at0x39a078 before factory call0x39a07e; this still does not establish
which service produced the phone body. No apparent BE64/order/4-byte-offset defect
was found in the supplied classifier. It already scans offset4, among others.

Source explains `different_prefix_16plus`: that label caps a common-prefix class
at16; the independent64plus classifier may still report64 shared bytes. Those
labels are compatible. No body field layout is inferred from the bands.

## Evidence-supported implementation and integration recipe

Added [bounded in-memory diagnostics](../../../experiments/routed_body_diagnostic.py):
compare body prefix with validated header packet sequence and classify failure at
only offsets0 and4. Export fixed labels only. Exact route `QueryAddrSvr` comparison
exports MATCH/OTHER/UNKNOWN; never export the actual route, body or sequence.
Malformed/oversized/inconsistent frames are NOT_COMPARABLE. These are observer
policies, not native rejection predicates or full RPC argument validation.

[Preparation tool](../../../tools/prepare_v38_observer.py) requires exact source
pins, copies into a new private directory, patches only diagnostic return/report
fields, and retains existing opt-in, known-IP-plus-port routing, loopback binding,
four-session bound, IDs and all outgoing stages. It refuses original-directory
output and never starts a relay. Local prepared copy: private/v38_observer_prepared.
No prepared archive or original fixture is committed.

From cf2018, preparation only:

```text
python tools/prepare_v38_observer.py --source private/v38_source --output private/v38_observer_new
```

Do not run its live starter automatically. A later authorized bounded diagnostic
phone run is justified to distinguish boundary mismatch from an unexpected
producer/encoding; **another guessed server response is not justified**. MATCH
plus failed legacy header narrows the investigation but does not prove encryption;
MISMATCH requires native boundary/context review, not blind prefix stripping.
A route MATCH identifies only the allowlisted route, not QueryAddrInfo or accepted
RPC arguments. No new operation response, tokens, credentials or key invented.

## Actual verification

- `python tools/knowledge.py route 'v38 routed application body packet sequence native binary serializer source audit'`: relevant native/phone/source context retrieved; routing now includes this audit.
- `python tools/knowledge.py doctor`: PASS.
- Original supplied v38 focused suite:9 PASS. Same9 tests PASS in prepared copy,
  including byte-identical original replies, localhost synthetic lifecycle and privacy.
- Canonical `python -m unittest discover -s tests -v`:205 total,117 PASS/88 explicit
  private-source SKIP. With actual pinned APK/Apollo/Unity/Mono/tprt, private analysis
  dependencies and CF18_V38_SOURCE selected:205 PASS,0 SKIP.
- New integration verifies actual source Run.compare_routed, private canary absent
  from logs, and no-opt-in startup refusal. Native stage matrix reproduced exactly.

No original edited, real phone run, authenticated account, service response
acceptance, lobby, match or bot gameplay claimed. Next offline work is the actual
routed application producer/reciprocal receiver; the available redacted phone
report cannot supply missing payload bytes. Keep local-server priority and paused
schedules.

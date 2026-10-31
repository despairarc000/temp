# Actual native AddressService fields and current blocker

2026-10-31, CF18-00, base main26cc7c0fcf77dd266d4e22a5c33401dd9df9694d.
[Acceptance before code](../../../coordination/CF18-ADDRESS-NATIVE-ACCEPTANCE.md).
This is useful offline continuation while the owner has not yet run v3.8.1.
No new phone result, guessed service reply, credential or original modification.

## Direct answer: what blocks progress

The real phone reaches routed0x4013, but its actual application encoding and
producer are unidentified. We cannot yet form a justified correlated reply.
Latest v38 sent no4013 response, so there is no observed rejection of such a reply.
This is an information gap requiring targeted runtime evidence plus native work;
not an unavailable APK, restarted handshake, or proof of generic authentication
failure. The redacted TXT cannot reconstruct omitted body bytes.

The ready [v3.8.1 diagnostic](../../../coordination/CURRENT_HANDOFF.md) measures
sequence/body alignment, bounded header failure reasons and one allowlisted route
using the existing PCAPdroid -> Termux SOCKS5 -> local fake server path. The next
AI must analyze those labels before selecting a response. Continue application
producer and reciprocal receiver tracing offline; do not wait by repeating plans.

## Verified source and execution scope

Pinned original Apollo5243704 bytes SHA256
4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8,
ELF32LE ARM/Thumb. NativeControl rechecks size/hash/ISA per execution.
[Provenance](../../../sources/SOURCE_PROVENANCE.md).
[Original runner](../../../experiments/native_address_fields.py),
[actual metadata-only matrix](../../../coordination/ADDRESS_NATIVE_MATRIX.json),
[12 tests](../../../tests/test_native_address_fields.py).
Fresh ELF per control,100000 instructions/1s native budget. Actual binary protocol
vtable0x4f4768; explicit synthetic recursion budget16 and memory transport pointer.
Only independent integers and repeated A service strings; no phone/account bytes.

## Actual request producer serializer

Generated QueryAddrInfo argument writer0x39ed4c calls ReqQueryAddrInfo::write
0x39dc30 at0x39ed78. Native argument wrapper is field1 STRUCT; request fields1/2
are I64 from object+8/+0x10, field3 STRING from+0x18; inner/outer STOP. Writer
returns34+N bytes for an N-byte service string. Original binary primitive and
virtual field writers execute; only transport-write0x398ede is a bounded256-byte
memory sink. No runtime allocation/string destructor stub is needed here.

Combining this actual argument output with the separately executed native message
header from0x39c3bc and the conditional clear4-byte packet-sequence prefix gives:

| Model | Service-string sizes | Routed-body sizes | First different byte |
|---|---|---|---|
| Legacy/native factory configuration |16/21|80/85|61|
| Strict/versioned comparison control |13/18|80/85|64|

The real v38 report says80/85 bytes and shared-prefix64plus. That does not fit the
simple complete clear legacy QueryAddrInfo model under these premises. Size
alone does not identify an operation; strict-mode comparison fits those coarse
bands but is NOT evidence the phone uses that mode. More importantly, actual
native-produced complete requests in BOTH modes are identified at offset4 by the
existing v38 application parser. Legacy also passes its dedicated legacy parser;
strict correctly fails only that dedicated legacy parser. All60 private source
hashes checked before differential. The real phone request remains unidentified,
so merely switching legacy/versioned recognition does not explain its absence.
This test composes two independently executed native serializers, not a full
Android AddressService send or live packet decode. Unknown outer/application
transformation or producer still requires evidence.

## New exact reciprocal decoder requirement

Executed generated result reader0x39eebc, which calls actual RspQueryAddrInfo::read
0x39e908 at0x39ef22. Actual required-field branches:

| Synthetic result input | Original native observation |
|---|---|
| success wrapper0 STRUCT with result1 I32=0 and reason2 STRING empty | consumes19, returns19 (byte count), wrapper-presence bit set |
| result absent, reason present | required-result branch0x39eaae reached before exception allocation |
| result present, reason absent | required-reason branch0x39ead8 reached before exception allocation; wrapper bit not set |
| success wrapper absent, STOP only | returns1, presence bit false; outer Recv_QueryAddrInfo must reject missing success |
| both fields present, result7 | still consumes19/sets wrapper; decoding is distinct from later result==0 policy |

Result presence is recorded at0x39e9bc and tested0x39eaac; reason STRING branch
0x39e9c0–0x39e9d2 sets the required flag, tested0x39ead2–0x39ead6. Empty is allowed;
absent is not. These missing-field paths were stopped at0x39eaae/0x39ead8 BEFORE
exception allocation; local sentinel-99 is NOT a native error code. The matrix
therefore reports native_return=null for those cases and exact failed predicates.
Truncated input raises the bounded memory transport refusal; no native truncation
error is inferred. No pending-map/process-response/endpoint callback executed.

Explicit decoder substitutions: transport-read0x398df4 bounded memory copy,
0x3f8f7c static-empty-name std::string assignment only,0x3f8a20 temporary-string
runtime destruction no-op. Wire field selection, primitive reads, required-field
checks and presence-bit updates execute original instructions. No decoder success
stub, key, account, service address or network operation.

## Implemented correction and integration

CF18-05's original [incoming preflight](../../../coordination/incoming/CF18-05/addr_response_gate.py)
allowed reason field2 to be absent, and its default laboratory fixture omitted
empty reason. That is less strict than the actual generated decoder. Incoming
ownership is preserved: no CF05 file changed. Coordinator integrated its original
bounded parser into [canonical address_response_gate.py](../../../experiments/address_response_gate.py)
with mandatory reason presence and [15 canonical tests](../../../tests/test_address_response_gate.py).
Synthetic fixtures now encode empty reason explicitly; missing reason is a
regression rejection. Existing strict caps, duplicate/trailing/truncation,
sequence/type/result and endpoint-policy controls remain. This is an OFFLINE
preflight, not a server reply encoder or live bridge change.

An earlier prototype without recursion initialization encountered the actual depth
error; decoder prototypes missing required fields reached exception allocation.
Those harness initialization failures were corrected/bounded before reporting
final controls. They are not real phone failures. Native required reason is a
verified future reply constraint, not an explanation of the current unknown
request or a claim that a valid address/session can now be generated.

## Actual verification

12 new native/bounds/differential methods PASS with pinned Apollo and exact v38
source.15 integrated strict-preflight methods PASS. Canonical236 PASS with all
explicit private sources/ZIP and dependencies; default236 total137 PASS/99 SKIP.
Knowledge doctorPASS. No change to the delivered v381 kit, original stage bytes,
Android game, schedule state or real-phone evidence.

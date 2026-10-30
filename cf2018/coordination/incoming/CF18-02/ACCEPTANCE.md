# CF18-G2-ACK-01 acceptance before implementation

Base: fefd0dc224851fefc2b74a51fc95e0fa0090e9a2. Owner CF18-02.
Scope: ACK/session/decryption branch predicates in the hash-pinned mirror
libapollo.so described in CF18-01/NATIVE_RX_RESULT.md. No framing reimplementation.

Accept a descriptive trace only where direct calls, memory operands, dispatch or
return branches are observed in the verified ELF32 little-endian ARM Thumb file.
Follow ACK extension TLV decoding, key-mode handling and immediate state caller.
Report base-field/session correlation only where an actual comparison or use is
found; absence in a bounded function is not proof of absence in the whole client.
Separate static observations, native execution with explicit stubs, synthetic
validator policies, historical phone reports and unknown runtime behavior.

Before claiming any validator rule, identify its branch and negative control.
Controls should distinguish wrong type, unsupported key mode, empty/nonempty
body, malformed extension and actual caller error propagation. Native controls
must require the exact hash/ISA, bounded instructions/time and synthetic inputs;
all stubs and untested paths must be explicit. No valid server ACK construction,
real keys, network/device execution or G2 success claim is permitted.

Failure modes: wrong library identity, conflated legacy/GCloud overloads,
serializer mistaken for receiver, unchecked state side effects before failure,
missed caller predicates, parser success mistaken for authenticated acceptance,
unsupported crypto mode or missing negotiation context. Do not hide missing
coverage with guessed fields. Coordinator alone integrates canonical knowledge.

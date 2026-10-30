# CF18-G2-RX-02 acceptance before implementation

Base main: 37b808d095641c90e80a707209f656e9bf29c53f. Owner CF18-01.
Live assignment: native 99/non-varint receive envelope, declared-end/size
arithmetic, cached lookahead and error timing. No ACK/session work or canonical
edits. Prior submitted CF18-01 packet has no active claim and is integrated.

Pin the actual private Apollo size/hash/ELF ISA before native claims. Follow the
real receive/base decoders, read-width/endian operations and unsigned additions;
never infer that NoVarint changes tag encoding or reuse a serializer as oracle.

Acceptance: bounded descriptive trace and independent synthetic/native controls
for 99 fixed-width values, both marker orders, truncation/declared-size mismatch,
AA/99 coalescence/cache promotion, partial-input compaction, delayed receive-error
returns and header+body addition bounds. Compare only observed framing behavior
against the canonical strict subset, preserving its intentional policy differences.
Do not claim full parity or silently add 99/relaxed bounds to shared code.

Any extended native runner must retain hash/ISA guards, <=64 KiB synthetic input,
100000 instructions/one second per native call, explicit non-network recv/libc
stubs, bounded state parameters and no full Android-loader claim. Keep frame
consumption simulation explicitly distinct from real native gather execution.
Record controls that fail, unsupported paths and branch/cursor observations.

Failure modes: wrong overload; tags confused with values; declared vs physical
bounds conflated; uint32 addition mistaken for arbitrary-precision validation;
lookahead parser return mistaken for current-frame validation; receive error
masked by buffered complete frames; simulated state mistaken for phone behavior.
No original/raw code bytes, complete ACK, keys, device/network run or exploitability
claim may be published. G2 stays BLOCKED; no prefix-only A/B/C candidate.

Resumed against live main 40c4aafe6665e671d08df6badb378121ec4ff213. The previous
framing run stopped; no active process remains. Canonical coordinator handoff and
CF18-02 local edits are preserved. Re-ran the 20 native draft methods: two failed
subtest assertions both expected -18 for base declared length +1; actual default
00ff payload returns -12 in AA and 99. Before correcting tests, reproduce the full
mode/payload/delta matrix, trace the helper mapping, and report the original
expectation error. Preserve actual native behavior; never force the runner to
match the failed expectation. Complete an independent strict AA/99 parser suite
covering both prefix orders, declared/truncation bounds, overflow cap, coalescence,
fixed-width values, opaque extensions and terminal failure/EOF.

# v3.8 DataHead — latest user-supplied test and exact remaining boundary

2026-10-31, coordinator, base d04cfe9a1e54f8c5e01e5839476e84beb834468a.
Actual attached text read locally,5383 bytes, SHA256
031dcb5bf33eb979cd95b161708c454006fd938f50ff08893db923fa81614cb3.
Source basename CF2018_v38_DataHead_Result.txt. Class USER_SUPPLIED_PHONE_REPORT
plus distinct PROBE_CLASSIFICATION; no new coordinator phone test. Private report
retained as supplied; only descriptive metadata published. No raw protocol data.
[Acceptance](../../../coordination/CF18-V38-REVIEW-ACCEPTANCE.md).

This supersedes v1.6 as the latest reviewed report. It does not erase older
controlled auth/Bingo experiments or turn an observer hint into native proof.
Overall goal remains NOT PLAYABLE; prioritize original-client local server,
integrity editing parked and schedules paused.

## What actually occurred in this run

All four trials use SYN133 -> ACK63 -> auth2001/117 -> synthetic corrected
auth54 -> synthetic Bingo91, stage around151ms after auth. No4013 reply was
generated. Later frames were reported in two trials:

| Trial | Later client frame | End status |
|---|---|---|
|1|4013,161 bytes,header79/body80,45.61ms after last reply|post_route_window_complete,1743.66ms total|
|2|none|deadline_after_auth_attempt,8179.11ms total|
|3|none|read_eof,4857.83ms total|
|4|4013,166 bytes,header79/body85,25.86ms after last reply|post_route_window_complete,1709.31ms total|

The two post-route-window completions are deliberate observer end states, not
failed server-reply tests. There was no server reply to accept/reject. Trial3
EOF and global relay counters do not identify a TCP FIN sender/native rejection.
Counters have no per-session/connection attribution sufficient for that claim.
Do not pool this2/4 with older3/4 as a controlled success probability.

## What the observer reports, and what it cannot establish

Both later frames: extension4013/kind5, same local route-group1, named-route
candidate, printable name length band9–16, compression_flag=no. The actual name
is withheld, so QueryAddrSvr is not established. The group is local to this run.
Body classifier, application RPC/TLV/length, protobuf, talker and legacy-Thrift
recognizers all failed to identify an operation. rpc_verified/auth_verified false.

The second sample reports shared prefix64plus, change start64–71 and suffix1–3,
despite a separate body_relation labeldifferent_prefix_16plus. Exact comparison
definitions cannot be reconstructed without the probe source. Do not infer a
field layout or treat either coarse label as an exact-byte comparison.

Compression off is only a transport compression observation. It is neither
encryption proof nor plaintext proof. Likewise no known signature does not prove
the application body is encrypted: recognizer offset/protocol/length assumptions
may be wrong. datahead_flags=native_order_verified is the probe's label; the
actual v3.8 source was not available here to independently verify its mapping.
The report intentionally omits body bytes, exact route name, UID and sequence.
It therefore cannot be used alone to decode the request or construct a response.

## Independent native clarification

Pinned Apollo5243704 bytes SHA256
4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8,
ELF32LE ARM/Thumb; NativeControl rechecks source hash/ISA on every execution.
TGCP send helper0x3ab430 reads crypto method+0x11c at0x3ab494 and selects length
for modes0/3/4, then packs header and calls actual encryption helper0x3ab296
at0x3ab55e. Compression context is independently consumed in send_with_route,
as previously traced in [SERVER_PATH](SERVER_PATH.md).

Actual helper0x3ab296 checks method at0x3ab2b0. Mode0 goes to bounded memcpy
0x3ab2d4–de. Nonzero method checks key-present byte+0x458 at0x3ab2b6–ba;
missing key returns-31 at0x3ab306. Methods3/4 then call their respective crypto
functions. No key or encrypted payload is created by the controls.

[Original controls](../../../experiments/native_routed_tx.py) now include
encrypt_boundary. With synthetic8-byte input, mode0 copies exactly with injected
compression context0 or1. Modes3/4 with no key return-31 and leave output unchanged
under both compression settings. Zero output capacity returns-2, short capacity
-21. [Four tests](../../../tests/test_routed_encrypt_boundary.py) PASS with pinned
source. Explicit substitutions are canonical bounded libc memcpy/log/error
helpers only if reached; method3/4 stop at real missing-key predicate, no crypto
success stub. Fresh synthetic context, no socket or game,100000 instructions/1s.
These controls do not identify the actual v38 connection's crypto method/key.

The earlier verified BE UID32 + application-data prefix is PRE-encryption with
compression disabled. Only if that exact unencrypted path is established for
the real connection would80/85-body bytes imply76/81 application bytes. This
conditional arithmetic is not a decoding of the uploaded report.

## Next exact task and evidence gap

Recover v3.8 source/installer or authorized private ZIP, not raw auth or packet
payload. Compare its actual header/body slicing, DataHead field ordering, flag
mapping, UID-prefix handling, route union and classifier offset policy with the
original serializer. Then connect MsgBuffer/protocol serialization to the actual
routed payload and reciprocal receiver. Preserve successful stages and inspect
only in-memory data with allowlisted metadata; no arbitrary route-name logging.

The workspace contains this report and public source through v1.6.1, not v3.8
source. A source-location question is pending; do not ask for another phone run
to compensate for unavailable code. No more blind type/field/account variations.
No4013 server reply, service acceptance, genuine authentication, lobby or bots.

Canonical suite191 PASS with explicit private inputs; default191 total109 PASS/
82 private-source SKIP; doctorPASS. These are offline validation, not phone progress.

# Server path priority — review and actual routed-TX continuation

2026-10-31, coordinator, base5d76e82696984717e394552cc6fb9c076e77e01f.
Decision: prioritize original-client local-server emulation; park DLL editing.
Schedules remain paused. This is an evidence-based priority, not an estimate that
the game is halfway complete or that a usable authenticated session exists.

| Route | Actual progress | What still blocks playable offline bots |
|---|---|---|
| Local server | Working phone ACK->auth; body correction removes immediate EOF; synthetic Bingo elicits authentic routed client traffic3/4 trials | Identify application payload/envelope; validated service replies; update/config/lobby; actual match lifecycle and bot support |
| Managed editing | Stored game DLL non-PE, original Mono/provider detour and synthetic checksum/loader error predicates traced | No decoded image or byte-identical round trip; exact historical edit failure unknown; a working edit still does not supply absent server/game state |

The server route is the better-supported near-term route because specific wire
corrections have caused real client progression. DLL access might later help
custom bots, but is not currently a demonstrated shortcut to playable matches.
Keep [integrity findings](INTEGRITY_NATIVE.md) available; no blind native bypass.

## Reconciled latest phone evidence

Incoming CF18-05 reports are user-uploaded redacted-report summaries, not a new
coordinator phone test. Original report bytes were not independently reopened
here. Preserve that evidence class and the report links rather than claiming a
new measured runtime trace.

- [v1.4](../../../coordination/incoming/CF18-05/PHONE_V14_RESULT.md): two corrected54-byte auth arms reach listener deadlines around7s, while old49-byte arms readEOF around10ms. Confirms differential behavior; no authenticated account.
- [v1.5](../../../coordination/incoming/CF18-05/PHONE_V15_RESULT.md): both synthetic Bingo arms emit authentic0x4013,161/166 bytes. Corrected-only and WAIT arms do not. No application method identified.
- [v1.6](../../../coordination/incoming/CF18-05/PHONE_V16_AND_V161_FIX.md): one of two Bingo sessions emits0x4013. Combined3/4 trials, not4/4. The observer silently filtered selector kinds other than1; actual phone kind was not logged. No hint is not evidence of encryption or absence of an RPC.
- The v1.6.1 repair is reported/tested by CF05. It is not a new phone result. Do not request another payload sweep or assume its outcome.

This supersedes old canonical statements of no post-Bingo packet and unavailable
bridge preparation. Synthetic lab session values remain synthetic; sending such
traffic and observing a response is not legitimate identity/login validation.

## Original-native routed application boundary

Source: [pinned original Apollo](../../../sources/SOURCE_PROVENANCE.md),5243704
bytes SHA2564812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8,
ELF32LE ARM/Thumb. Actual hash/ISA guard runs each execution. The examined
send-with-route function is0x3a91ec. Static CF05 TX findings were cross-checked
against original instructions and extended with actual isolated execution.

| Native stage | Actual observed predicate/dataflow |
|---|---|
|0x3a923c–0x3a9286|Nonempty input, positive length, nonnegative timeout; payload<=handle+0x6d0. Invalid input/timeout-2; oversized-16.|
|0x3a92c6–0x3a931e|Route kinds1/2/4 require pointer; initialized flag+0x124 required, else-4; numeric state5 required, else-8.|
|0x3a9328–0x3a936c|Compression negotiation at+0x33f4/+0x33f8; controls disable it explicitly. Actual compression implementation/phone setting not established.|
|0x3a9372–0x3a9396|Writes marker4366 and type4013 into outgoing header. Copies packet-sequence field+0x12c into outgoing base+0x30. Route/compression metadata resides in header structures.|
|0x3a93e2–0x3a9404|Copies that sequence into the first four send-body bytes in BIG-ENDIAN order. It is not an application length field in this examined path.|
|0x3a9406–0x3a941a|Copies application payload immediately after those four bytes, then passes total payload+4 to encrypt-and-send.|
|0x3a941c ->0x3ab430|Controls intercept before executing encryption/send, sentinel-77. No socket, encryption, final TGCP serialization or real routed frame generated.|

The new [original runner](../../../experiments/native_routed_tx.py) runs the entire
function with independent synthetic payload/context. Both1-byte and64-byte
payloads are preserved after the BE packet-sequence prefix, header4013/marker4366/compression0.
State4, uninitialized, oversize, negative timeout and missing route pointer take
the expected errors before submission. [Actual seven-case matrix](../../../coordination/ROUTED_TX_MATRIX.json),
[seven test methods](../../../tests/test_native_routed_tx.py),
[acceptance](../../../coordination/CF18-G2-ROUTED-TX-01-ACCEPTANCE.md).

Only bounded libc memcpy/log/last-error helpers use canonical NativeControl
substitutions; exact called helper labels are in the matrix. Synthetic packet sequence,
initialized handle, numeric5, route0/no pointer, disabled compression and injected
buffer capacity are premises, not a valid account. Fresh PT_LOAD memory;100000
instructions/one second. The pre-encryption prefix may not be visible as plaintext
on the actual wire. No generic claim that all TGCP directions have this body form.

## Next useful work, with acceptance criteria

1. Preserve the phone progression, inspect routed0x4013 with corrected kind-aware
   instrumentation. Identify the actual method/envelope from structural evidence;
   do not equate the four packet-sequence bytes with a length or log their value. The existing
   observer's scan may already cover the offset; this discovery alone does not
   warrant changing its classifier or sending a new reply.
2. Connect original AddressService write -> message buffer -> routed send, then
   trace the reciprocal receiver to establish compression/encryption and routing
   boundaries. A recognized method hint still needs independent framing validation.
3. [CF05 static Address response findings](../../../coordination/incoming/CF18-05/ADDRESS_RESPONSE_NATIVE_FINDINGS.md)
   locate pending64-bit sequence match, reply type2, success-field presence and
   numeric result0 gates. Its strict original checker14 tests and Bingo13 tests
   were rerun here, all PASS; these do not execute native response handling.
   Reproduce native response predicates before integrating or issuing a reply.
4. Only actual service response acceptance/new client behavior advances G3;
   updates/config/lobby and real match/bot gates remain separate. No server
   credential/key/relay generation policy has been established.

No new phone experiment or schedule started. Latest source-free canonical suite:
187 total108 PASS/79 explicit private-source SKIP. Explicit all-private source
suite187 PASS/no skips. DoctorPASS; incoming Bingo13 and address14 PASS. This
continues the chosen path with native evidence, not a claim of playable progress.

Latest reviewed test is now [v3.8 DataHead](V38_BLOCKER.md), not v1.6. It contains observed kind5/no-compression labels but no identified inner operation and no4013 reply. Prior phone observations remain historical; focus on actual v38 parser/source and application serialization.

Current correction: [v38 source/native audit](V38_SOURCE_AUDIT.md) proves the prefix is `dwSequence`, superseding earlier UID wording. Actual source is now available; exact-stage replay selects mode0. Extended runner executes packing/copy and counter increment with only final submission suppressed. Current205 private PASS /117 PASS+88 SKIP default.

## R056 continuation (2026-11-02): return to the fake server

The latest source-only server work is [R056 second-service SYN dispatch](R056_SECOND_SERVICE_SYN.md). The real phone's 131-byte named-route SYN is a route transition, not proof the previous 63-byte first-service ACK works there. Added a fail-closed SYN classification function with 10 synthetic tests; [CI 41341222988](https://github.com/despairarc000/temp/actions/runs/41341222988) PASS. It distinguishes reference QueryAddrSvr from ten-byte name-route candidates but sends **no** ACK for a new route, exports only fixed labels and remains separate from the private v3.8 Termux server. Do not claim deployment or service acceptance. Next source-pin the original v3.8 first-frame handler and integrate this guard without altering original ACK/auth/Bingo responses or SOCKS5 passthrough. Then resolve route-specific ACK/session/key from original library before a phone run.

## R057 verified original address-supplier callers — 2026-11-02

The owner Drive original `libapollo.so` independently passed full SHA-256 verification. Exact native Thumb BL xrefs: `GCloud::CDefaultNameService::Query` and `pebble::rpc::RpcConnector::InitLbIpAddress` each directly call `AddressService::GetServiceAddress`; `RpcConnector::Init` directly calls `InitLbIpAddress`. The CDefaultNameService callback and CTGcp observer are present in original symbol table, but their runtime virtual dispatch and the actual post-address 10-byte route are **unproven**. [R057 audit/report](R057_ADDRESS_LOOKUP_CALLERS.md), 11 synthetic tests, [CI PASS](https://github.com/despairarc000/temp/actions/runs/41343787854). Next trace which name service/connector owns the address-result callback then the exact subsequent ACK/session contract. Do not equate another SYN with authenticated lobby, nor reuse a reference ACK without native evidence. No game/server runtime test this turn.

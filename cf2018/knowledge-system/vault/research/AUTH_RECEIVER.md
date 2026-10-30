# CF18-G2-AUTH-RX-02 — earliest verified authentication-response failure

CF18-00 review, 2026-10-30, main
`9a0d6ef09c6b62a4543c8c9aadef15f1946df470`. Submitted
[CF18-02 packet](../../../coordination/incoming/CF18-02/auth_rx_02/RESULT.md),
[actual matrix](../../../coordination/incoming/CF18-02/auth_rx_02/NATIVE_MATRIX.json),
[CF18-05 fixtures](../../../coordination/incoming/CF18-05/V13_NATIVE_TEST_PACKET.md).
Classes: ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS +
INDEPENDENT_SYNTHETIC, separate from user-confirmed phone reports.
**Earliest verified native failure: missing TGCPBody preamble. No phone auth.**

## Preserved phone progression

[v0.9](../../../coordination/incoming/CF18-05/PHONE_V09_RESULT.md) observed
client follow-up only after AA_DIRECT; its listener stopped on that chunk.
[v1.0](../../../coordination/incoming/CF18-05/PHONE_V10_RESULT.md) identified
extension field [8193,1], meaning 0x2001. The empty ext_type display was a
reporting filter bug, not a missing selector. Client TX kinds differ from RX.
[v1.2](../../../coordination/incoming/CF18-05/PHONE_V12_RESULT.md) records eight
sessions: SYN133 -> AA_DIRECT ACK63 -> authentic auth117 (header42/body73).
All have two client frames/250 bytes; silence reaches about 7 seconds, three
synthetic response arms end in local read_eof about 8–11 ms after reply.
Those reports and the user's explicit confirmation establish the post-ACK hop.
No later packet, authenticated session, AddressService, lobby or gameplay exists.
Local read_eof does not establish the origin of FIN/RST or a native reject code.

## Source and exact original responses

Actual private Apollo: 5243704 bytes, SHA-256
`4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`,
ELF32 little-endian ARM EABI5. Addresses below are virtual, Thumb bit cleared.
Coordinator reran the [source verifier](../../../tools/verify_private_source.py):
pinned APK/member hashes, ISA, CMS and all 1212 signed entries PASS; external
certificate trust chain NOT_VALIDATED. [Provenance](../../../sources/SOURCE_PROVENANCE.md)
distinguishes mirror verification from historical reported APK parity and OBB gaps.

| Exact synthetic arm | Bytes | Recomputed SHA-256 |
|---|---:|---|
| V11_EMPTY_ACCOUNT | 66 | 787fd8b6a013a1c469f065a8a6e269fa402968d6e2f503852411ab9e6d40d40e |
| V12_BODY_EMPTY | 49 | 527b6570d015c64355ab8d4d83c534dc3fe5975818485133a2c4b313edcbf4ca |
| V12_FULL_ZERO_ACCOUNT | 79 | 2aed3ae9a18a47497969bedad3332a2eb8a91aaf0e3a50839ace9843267199fa |

## Actual unchanged full-path matrix

Zero is native parser status, not account/session validity. NR = not reached.

| Stage | Empty account | Empty body component | Full zero account |
|---|---:|---:|---:|
| Gather / header / extension decode | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Extension selector / effective type | 0x2002 / 0x2002 | 0x2002 / 0x2002 | 0x2002 / 0x2002 |
| Receive/decrypt, wire encrypted flag 0 | 0 | 0 | 0 |
| Header / body bytes | 42 / 24 | 42 / 7 | 42 / 37 |
| TGCPBody decode / consumed bytes | **-32 / 1** | **-32 / 1** | **-32 / 1** |
| Auth / account components | NR / NR | NR / NR | NR / NR |
| Auth receiver / state handler | -18 / -18 | -18 / -18 | -18 / -18 |
| Prior account / numeric state | unchanged / 3 | unchanged / 3 | unchanged / 3 |
| Bingo | NR | NR | NR |

TGCPBody::unpackTLV 0x3b8860 reads uint8 at 0x3b888e. Comparisons at
0x3b8896 and 0x3b889a require AA or 99. Actual byte A5 matches neither;
branch 0x3b889c reaches 0x3b88d8, returns -32 after one byte. A5 is the first
auth-union tag byte. Auth receiver 0x3ac306 calls body at 0x3ac366 and maps
that error to -18 at 0x3ac378. OnStateAuthing 0x3a9ff6 propagates -18.
Auth/account parsing and Bingo have not run; account semantics cannot be the
first failed condition on these exact bytes in this tested native context.

Independent static packer check: TGCPBody::packTLV 0x3b83ec writes AA at
0x3b8416–18, reserves four length bytes at 0x3b8422, packs the union, and
patches total at 0x3b8464. The outer header does not supply this body preamble.
Isolated auth components decode with status0, consumed17/0/30; isolated account
decodes0 consuming0/13 for empty/full-zero accounts. These are diagnostic calls,
not stages reached by the original replies, and do not validate any identity.

## Minimal original correction and its actual limit

[Encoder](../../../experiments/tgcp_body_envelope.py):
`body = AA || uint32_be(5 + len(serialized_union)) || serialized_union`.
Recompute the outer header's body length from len(body). No account, key,
credential, token or session value is added. Encoder cap is local safety policy.
The [fixture repair](../../../experiments/auth_fixture_repair.py) is separate:
only the three hash-pinned historical layouts may use its byte32 length patch.
A real server must serialize its own outer length, not patch arbitrary offsets.

| Corrected stage | Empty account | Empty body component | Full zero account |
|---|---:|---:|---:|
| Frame / body bytes | 71 / 29 | 54 / 12 | 84 / 42 |
| Gather / header / receive | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Body / auth component | 0 / 0 | 0 / 0 | 0 / 0 |
| Account component | 0, empty | absent | 0, synthetic zeros |
| Auth receiver / numeric state | 0 / 4 | 0 / 4 | 0 / 4 |
| Real Bingo receive / handler | -12 / 0 waiting | -12 / 0 waiting | -12 / 0 waiting |

No parser/gather/decrypt-success/Bingo-success stub is used. Real account copy
executes, but UID is synthetic zero. State4 is not authentication. Bingo
0x3ac39e calls receive/decrypt at 0x3ac3b6; absence of next server data returns
-12. Handler 0x3aa02a–2e converts that wait to zero. No third client packet
alone would not falsify the correction while this handler awaits server Bingo.
Static type branches 0x3ac3be–f2 distinguish 0x3002 and 0x6002: the parsed
0x3002 path records queue/wait fields/returns -28; the other parsed path copies
session fields and writes state5 at 0x3ac474. No valid Bingo was constructed.
Sending corrected auth twice actually yields Bingo -14/state4, not success.

## Every emulation substitution

[Native controls](../../../experiments/native_auth_rx.py) use the existing
[runner](../../../experiments/native_control.py), exact size/hash/ISA guards,
fresh PT_LOAD memory, synthetic FD42, initialized handle/state3, method0/no key,
output cap256, prior account filled with independent R bytes. Inputs <=512;
100000 instructions/one second per execution; trace <=512 events.

| Address | Substitution |
|---|---|
| 0x284fcc | net wrapper -3/no data; explicit -4 EOF-like negative control, no socket executed |
| 0x193e60 | memset <=64 KiB |
| 0x193ed8 / 0x193e6c | memcpy/memmove <=64 KiB |
| 0x393e80 | XLog no-op |
| 0x1b3b1c / 0x1b3b26 | last-error get0 / set no-op |
| 0x1c6544 | inert error-string pointer; native error codes preserved |

No protocol decoder or success state is stubbed. Android loader/GOT/globals,
actual installed context and real account/key/session semantics remain incomplete.
This is not a device snapshot. Deterministic decoder incompatibility is established;
actual phone close origin and whether additional failures follow remain unknown.

## Reproduction and integration

[Acceptance](../../../coordination/AUTH_RX_INTEGRATION_ACCEPTANCE.md) preceded
canonical edits. Coordinator reran incoming25 PASS, source integrity PASS and
reproduced the entire published JSON matrix exactly. Canonical adaptations retain
seven fixture regressions, 18 original auth controls, one cap-boundary control;
ICM gains a tested auth route. No incoming lane file is edited.

```text
python tools/knowledge.py route 'authentication 0x2002 Bingo'
python tools/knowledge.py doctor
python -m unittest discover -s tests -v
CF18_APK_SOURCE=<private APK> CF18_APOLLO_LIBRARY=<private Apollo> \
  PYTHONPATH=<private dependencies> python -m unittest discover -s tests -v
PYTHONPATH=<private dependencies> python experiments/auth_native_matrix.py --library <private Apollo>
python experiments/auth_native_matrix.py
```

No arguments: inactive. Initial auth-only draft checks were128 private-selected
PASS and95 PASS/33 SKIP by default. Current combined auth/Bingo integration has
149 private-selected PASS and97 PASS/52 SKIP by default. Both matrices reproduce
exactly from canonical runners.
Negative controls cover raw prefixes, wrong type, incomplete frame, stale outer
length, oversized inner length, encryption without key, no-data vs EOF-like
status, second auth at Bingo, source pin and size caps. Native failures stay
separate from Python strict-policy rejection and actual phone behavior.

## Targeted v1.4 decision

Envelope-only A/B/C comparison is justified in principle, **not operationally
ready** until the actual deployed bridge source and directional lifecycle hook
are reviewed. The original user-facing v1.2 ZIP/source is not available here.
This commit integrates offline code and evidence; deployment/wiring is unverified.

Disabled/passive default proposal: six connections, two each for silence,
unchanged BODY_EMPTY49, corrected BODY_EMPTY54. Keep successful ACK and all
account/session values fixed. Loopback-only SOCKS5; exact known game IP AND port;
preserve unrelated passthrough; unique run/connection IDs. Hold sockets open
until actual peer EOF/error or bounded deadline, record directional client,
upstream and local-stop metadata/write errors, never private payload contents.
No random account/key/Bingo variants or automatic phone run.

Next offline gate: the reviewed Bingo continuation below leads to state5
application/account/session consumers, with malformed/synthetic controls and
without inventing a successful identity/session. Next relay gate: retrieve deployed v1.2 source, attribute EOF.
G2 remains AUTH_RESPONSE_BLOCKED; overall offline game is NOT PLAYABLE.

## Coordinator resume at ccdd219

Auth native matrix reproduced again from the published packet. The reviewed
[Bingo/session continuation](BINGO_SESSION.md) identifies3002 as WAIT/queue, not
stop, and proves deliberately mismatched header/auth-body input can reach numeric
state5 without a Bingo component. State4 or5 is insufficient for authentication.
This does not change the earliest exact-v1.2 body-preamble failure.

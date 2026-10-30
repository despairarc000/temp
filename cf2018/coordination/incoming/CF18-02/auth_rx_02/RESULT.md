# CF18-G2-AUTH-RX-02 — earliest verified v1.2 failure

Base main `14a49c610826e6a08f6bc7d9bb06ad0e5ad30b75`, 2026-10-30. CF18-02.
SUBMITTED; no active same-lane claim remains. Evidence classes:
ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS + INDEPENDENT_SYNTHETIC,
separate from the user's confirmed real-phone observations. **No phone auth or gameplay.**

**Earliest verified failure: all three exact v1.2 replies omit the TGCPBody
AA/99 + uint32-length preamble. TGCPBody::unpackTLV reads 0xA5 as its mode byte,
returns -32, and the auth receiver maps this to -18 before auth/account parsing.**

## Preserved evidence and source

The explicit assignment supersedes stale shared ACK-first checkpoints. Preserve
real phone SYN133 -> AA_DIRECT ACK63 -> authentic 0x2001/117. The
[pinned v1.2 phone report](https://github.com/despairarc000/temp/blob/14a49c610826e6a08f6bc7d9bb06ad0e5ad30b75/cf2018/coordination/incoming/CF18-05/PHONE_V12_RESULT.md)
records eight sessions, all two client frames/250 bytes; silence reaches deadline,
three auth-response arms give early local read EOF. That does not identify FIN/RST
origin. No earlier ACK failure is reintroduced as the current blocker.

Inputs are the exact original-new-code fixtures and seven tests from
[CF18-05 v1.3 packet](https://github.com/despairarc000/temp/blob/14a49c610826e6a08f6bc7d9bb06ad0e5ad30b75/cf2018/coordination/incoming/CF18-05/V13_NATIVE_TEST_PACKET.md),
locally copied unchanged as auth_v12_fixtures.py / test_v13_fixture_pins.py.
All three length/SHA-256 pins were actually recomputed before native replay:

| Arm | Bytes / SHA-256 |
|---|---|
| V11_EMPTY_ACCOUNT | 66; 787fd8b6a013a1c469f065a8a6e269fa402968d6e2f503852411ab9e6d40d40e |
| V12_BODY_EMPTY | 49; 527b6570d015c64355ab8d4d83c534dc3fe5975818485133a2c4b313edcbf4ca |
| V12_FULL_ZERO_ACCOUNT | 79; 2aed3ae9a18a47497969bedad3332a2eb8a91aaf0e3a50839ace9843267199fa |

Actual private Apollo SHA-256:
4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8,
5243704 bytes, ELF32 little-endian ARM EABI5, Thumb. Actual pinned APK SHA-256
33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9,
30884905 bytes. Canonical private-source verifier reran: member hashes/ISA, CMS,
certificate fingerprint and all 1212 signed-entry digests PASS. External trust
chain, installed-phone state and OBB identity are not inferred. The source is the
previously user-authorized APKPure mirror receipt; no new download/Drive scan.
Only local authorized originals were opened, and none is included here.

## Native full-path matrix — unchanged exact replies

Zero means a native decoder returned zero, not valid identity/session acceptance.
NR means not reached on this actual full path. Structured actual results:
[NATIVE_MATRIX.json](NATIVE_MATRIX.json).

| Native validation stage | V11_EMPTY_ACCOUNT | V12_BODY_EMPTY | V12_FULL_ZERO_ACCOUNT |
|---|---:|---:|---:|
| Outer gather / complete frame | 0 | 0 | 0 |
| Header/base/extension decode | 0 | 0 | 0 |
| Observed extension selector / effective type | 0x2002 | 0x2002 | 0x2002 |
| Receive/decrypt (wire encrypted flag 0) | 0 | 0 | 0 |
| Header bytes / body bytes | 42 / 24 | 42 / 7 | 42 / 37 |
| TGCPBody::unpackTLV | **-32** | **-32** | **-32** |
| Body bytes consumed before first failure | 1 | 1 | 1 |
| Auth component decoder | NR | NR | NR |
| Account component decoder | NR | NR | NR |
| Auth receiver / auth-state handler | -18 / -18 | -18 / -18 | -18 / -18 |
| Account destination / state | unchanged / 3 | unchanged / 3 | unchanged / 3 |
| Bingo receive | NR | NR | NR |

Separate diagnostic component calls, explicitly not reached by the originals:
TGCPAuthRspBody returns 0 consuming 17/0/30 bytes respectively. Account component
returns 0 consuming 0 bytes (empty account) and 13 bytes (full-zero account);
BODY_EMPTY has no account component. This isolates the earlier body envelope,
without promoting component syntax or dummy identity to successful authentication.

## Exact failing predicate and independent serializer cross-check

Addresses are virtual, Thumb bit cleared, for the pinned hash only.

- Header decode 0x3b7340 and its extension union 0x3b6a3c return 0. At 0x3b724a,
  the observed decoded extension selector is 0x2002; this is recorded separately
  from the final effective type. GCloud gather 0x3ab5ec and receive/decrypt
  0x3abe34 return 0 and consume the frame.
- Auth receiver 0x3ac306 checks effective 0x2002 before calling body decode at
  0x3ac366. This type check succeeds for all three originals.
- TGCPBody::unpackTLV 0x3b8860 reads uint8 at 0x3b888e; compares AA at 0x3b8896
  and 99 at 0x3b889a. Neither matches observed 0xA5. Branch 0x3b889c reaches
  0x3b88d8 and returns -32 after one byte. Auth/account decoders are never entered.
- Auth receiver maps body error to -18 at 0x3ac378, leaves prior account unchanged
  and state 3; OnStateAuthing 0x3a9ff6 propagates it and never calls Bingo.
- Independent native TGCPBody::packTLV at 0x3b83ec writes AA at 0x3b8416–18,
  reserves four length bytes at 0x3b8422, packs the union, then patches its total
  at 0x3b8464. The body has its own preamble independently of the outer header.

0xA5 is the first varint byte of the existing auth-union tag, not an auth status.
Changing account fields cannot reach those fields while this earlier mode check
fails. No key/correlation predicate fails first on these exact unencrypted fixtures.
This is a deterministic native incompatibility, sufficient to reject these bytes
in the tested path. It does not by itself attribute the actual phone socket EOF.

## Implemented smallest correction and actual corrected path

[Original helper](tgcp_body_envelope.py) implements:

```text
body = AA || uint32_be(5 + len(existing_union)) || existing_union
outer_header.body_length = len(body)
```

The known server generator must wrap its already serialized union before computing
its outer body length. The helper generates no account, credential, token, key,
Bingo or auth success. The fixture-specific adapter changes only byte 32 (the
pinned fixtures' base body-length value) and inserts the five body-preamble bytes;
all other header and auth/account bytes are preserved. It verifies the exact
historical fixture pin/layout first. A general server must regenerate its length
field rather than apply that fixture-specific offset to arbitrary packets.

| Corrected native stage | V11_EMPTY_ACCOUNT | V12_BODY_EMPTY | V12_FULL_ZERO_ACCOUNT |
|---|---:|---:|---:|
| Wire / body bytes | 71 / 29 | 54 / 12 | 84 / 42 |
| Frame / header / receive-decrypt | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| TGCPBody / auth component | 0 / 0 | 0 / 0 | 0 / 0 |
| Account component | 0, empty | absent | 0, synthetic zeros |
| Actual auth receiver | 0 | 0 | 0 |
| Copy / numeric state | executed / 4 | executed / 4 | executed / 4 |
| Actual Bingo receive | -12 | -12 | -12 |
| Actual auth-state handler | 0, waiting | 0, waiting | 0, waiting |

These successful decoder/copy branches are real native instructions, with no
parser, gather, decrypt-success or Bingo-success stub. Account semantic UID stays
synthetic zero. Numeric state 4 remains insufficient for a valid session/login.

Bingo 0x3ac39e calls receive/decrypt at 0x3ac3b6 and waits on -12 because no next
server data exists. The handler converts that wait to zero at 0x3aa02a–2e. Static
checks at 0x3ac3be–f2 distinguish 0x3002 and 0x6002. The 0x3002 parsed path records
stop fields and returns -28 with state 4; the other parsed path copies Bingo/session
fields and reaches state 5 at 0x3ac474. No valid Bingo/session values or packet
were invented or executed. A second 0x2002 negative control actually reaches Bingo,
then returns -14 while state remains 4. No third client packet by itself would
not prove the envelope correction failed: this path waits for another server step.

## Stubs, fresh context, and limits

Runner: [auth_rx_native_controls.py](auth_rx_native_controls.py), using the
previously integrated canonical NativeControl from commit
40c4aafe6665e671d08df6badb378121ec4ff213. The original library is loaded from actual
PT_LOADs only after its size/hash/ARM ISA guard. Fresh zeroed memory, initialized
handle, synthetic descriptor 42, state 3, method 0/no key, output cap 256 and
independent prior-account R pattern are injected. This is not a phone snapshot.
Inputs are capped at 512 bytes; 100000 instructions/one second per execution;
trace events capped at 512. No loader-complete Android/GOT/runtime claim.

Every stub used by these runs:

| Address | Stub behavior / limit |
|---|---|
| 0x284fcc | net-recv wrapper returns -3 (no new data); explicit -4 control injects an EOF-like wrapper result. No socket/select/recv is executed. |
| 0x193e60 | bounded memset, at most 64 KiB |
| 0x193ed8 / 0x193e6c | bounded memcpy/memmove, at most 64 KiB; actual account copy executes through this memory-operation implementation |
| 0x393e80 | XLog no-op |
| 0x1b3b1c / 0x1b3b26 | last-error get returns 0 / set no-op; no native validation return is converted to success |
| 0x1c6544 | error-string lookup supplies inert storage only; body -32 and caller -18 are preserved |

No framing/header/extension/body/account/Bingo parser, key negotiation or auth-send
success is stubbed. No send, account-token construction, original modification,
phone or live-game network execution occurs. Globals and later real account/session
semantics are unknown. The same earliest body failure occurs without any account
component or Bingo, so it is not inferred from a later isolated failure.

## Actual verification, negative controls and next phone decision

From cf2018:

```text
python tools/knowledge.py route 'auth 0x2002 v1.2 exact native receiver earliest failure'
  Routes: [('sources', 1)] (stale router lacks auth keyword; manual direct dependencies read)
python tools/knowledge.py doctor
  PASS
python -m unittest discover -s tests -v
  Ran 101; 82 PASS / 19 private-source SKIP
python tools/verify_private_source.py --apk <pinned private APK> --library <pinned private Apollo>
  PASS: hashes, ELF, CMS and 1212 signed entries; trust chain not validated
CF18_APOLLO_LIBRARY=<pinned private Apollo> PYTHONPATH=<private analysis deps> \
  python -m unittest discover -s coordination/incoming/CF18-02/auth_rx_02 -v
  Ran 25; all PASS, no skips
python -m unittest discover -s coordination/incoming/CF18-02/auth_rx_02 -v
  Ran 25; 11 PASS / 14 explicit native-source SKIP
PYTHONPATH=<private analysis deps> python coordination/incoming/CF18-02/auth_rx_02/run_native_matrix.py --library <pinned Apollo>
  Actual NATIVE_MATRIX.json reproduced
python coordination/incoming/CF18-02/auth_rx_02/run_native_matrix.py
  Inactive; explicit --library required
```

Tests preserve all seven v1.3 regressions and add exact full-native gate/cursor
checks, correction byte preservation, stale outer length (-2), oversized inner
length (-2), incomplete frame (-12/wait), wrong effective type (-14), missing key
under an encrypted-flag control (-31), unencrypted flag behavior, duplicate auth
at Bingo (-14), and no-data vs EOF-like status after parse (-12 vs -10). Source-free
helper bounds/types fail closed. These are actual offline results, not phone auth.

**A targeted v1.4 envelope-only comparison is justified in principle, after
controlled integration and directional relay instrumentation.** Keep successful
ACK and all account/session fields fixed. Use a disabled/passive-by-default six-
connection plan: silence, unchanged old BODY_EMPTY/49 and corrected BODY_EMPTY/54,
two per arm, unique run/connection IDs, loopback SOCKS5, exact known game IP AND
port scope and preserved unrelated passthrough. Keep the connection open until
actual peer EOF/error or bounded deadline. Log client/upstream/local-stop directions,
write/drain errors and timing/hash metadata only; do not log credentials.

Its purpose is to test removal of this one decoder incompatibility, not arbitrary
identity/key/Bingo guesses. No new device run is requested or activated here.
Current deployed v1.2 bridge code and directional raw lifecycle are not available
in this checkout, so direct deployment/wiring is unverified. EOF source remains
unknown; the code-level defect is established independently. Do not require an
unsolicited third packet while the native path is waiting for Bingo, and do not
claim auth/session acceptance merely from a longer connection.

## Coordinator integration and remaining gates

Only this CF18-02 packet is submitted; all other lane and canonical local edits
are preserved. Prior scheduled role transitions produced unpublished local
framing/native drafts; their actual useful code was reused, not claimed as a
remote source commit or a second independent result. The public fixture/test
source remains the pinned CF18-05 packet. The active CF18-02 scope owns auth receive;
framing findings are reported only as the proven prerequisite to that receive.

Coordinator should integrate the helper at the existing original server union-
body construction, rerun these exact regressions, and update canonical checkpoint,
EVIDENCE, OPEN_QUESTIONS, ICM auth routing, Graphify and assignments. Shared stale
statements that no post-ACK client packet exists must be superseded by the verified
phone 0x2001 progression. Do not overwrite other pending coordinator edits.

Unresolved: actual installed context/keys and account semantics; decoded Bingo/
session fields needed for state 5; application callbacks/AddressService progression;
matching OBB; and deployed relay EOF attribution. No synthetic accepted account,
Bingo, key or playable game is supplied. The root WebView app and original APK/OBB
remain untouched.

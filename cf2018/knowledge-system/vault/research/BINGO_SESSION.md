# Bingo/session continuation — state5 is not an acceptance oracle

CF18-00 review, 2026-10-30, base main
`ccdd219f9ed121e77fc06ad20b50b77614079cbf`. Input is the completed LOCAL CF02
bingo_01 draft: no remote packet commit exists. Exact input SHA-256 values are
recorded in [integration](../../../coordination/INTEGRATION.md). Incoming files
remain untouched. Classes: ORIGINAL_NATIVE_STATIC + NATIVE_EMULATION_WITH_STUBS +
INDEPENDENT_SYNTHETIC. **No valid Bingo or authenticated session demonstrated.**

This extends [AUTH_RECEIVER](AUTH_RECEIVER.md); it does not replace the exact
v1.2 earliest failure: missing body preamble, native-32 -> auth-18 before account.
Real phone ACK63 -> authentic0x2001/117 remains confirmed; no later auth/session.

## Source and ordered predicates

Private Apollo5243704 bytes, SHA-256
`4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`,
ELF32 little-endian ARM EABI5. Addresses are virtual/Thumb bit cleared. Actual
pins/ISA are checked per native probe. Coordinator reran the [source verifier](../../../tools/verify_private_source.py),
CMS and all1212 signed-entry digests. Trust chain not validated; installed APK,
runtime context and OBB equality remain outside [source provenance](../../../sources/SOURCE_PROVENANCE.md).

| Stage | Actual native condition and result |
|---|---|
| OnStateReady0x3aa046 | Requires initialized handle, nonnegative descriptor and state4; otherwise-4/-1/-19 before Bingo. |
| Ready0x3aa060–6a | Calls Bingo0x3ac39e; only-12/no-data becomes handler0/waiting. |
| Bingo0x3ac3b6 | Calls receive/decrypt0x3abe34; errors propagate, including-10. |
| Header0x3ac3be–e4 | Requires effective3002 or6002. Wrong type records+0x33e4 and returns-14 before body. |
| Body0x3ac406 | TGCPBody::unpackTLV0x3b8860. Error maps-18 at0x3ac416, no relay copy. |
| Union0x3b865e–64 | After component0, replaces selector reference with decoded body tag number. |
| Post-body0x3ac41c–426 | Reads replaced selector; compares only3002 versus other branch. No explicit6002 recheck here. |
| Queue0x3ac428–44a | Stores flag+0x33b4, position/total/rough-time+0x33b8/+0x33bc/+0x33c0, retains state4, returns-28. |
| Other0x3ac44c–474 | Copies44 decoded bytes to+0x6d8, compression to+0x33f4/+0x33f8, writes state5 and returns0. |

**Terminology correction:** selector3002 dispatches TGCPWaitBody0x3b4e20 via
0x3b8596. Its visualize0x3b4ff0 labels dwPosition/dwTotal/dwRoughTime. Prior
auth packet's "stop" wording is superseded; -28/state4 observations stand.
TGCPSStopBody belongs to selector5002 ->0x3b55a6, a distinct message.

## Real negative control: mismatched body reaches state5

Only an existing public synthetic BODY_EMPTY auth fixture is reused, with its
verified body wrapper. Header selector changes to6002 or3002; body stays2002.
No Bingo component, credential, account identity or session value is generated.
This is deliberately invalid correlation, never a proposed phone response.

| Stage | Header6002/body2002 | Header3002/body2002 |
|---|---:|---:|
| Real gather / receive | 0 /0 | 0 /0 |
| Real auth component / body | 0 /0 | 0 /0 |
| Actual post-body selector | 2002 | 2002 |
| Bingo component reached | NO | NO |
| Receiver / numeric state | 0 /5 | 0 /5 |
| Copied prefix equality | true | true |

No protocol parser, receive-success or state-success stub is used for these wire
controls. Native code takes the general copy branch after selector replacement.
Therefore state5 alone is insufficient for header/body correlation or a valid
session. This does not establish the installed game's reaction, application
continuation, correct identity or playable state. Never imitate this permissive
correlation behavior in a server validator or use it to claim authentication.

## Component syntax and received-field use

TGCPBingoBody varint decoder0x3b76a6 reads field1 nested TGCPRelay0x3b0dd2,
field2 uint8 bCompressMethod at+0x30, field3 varuint32 dwCompressLimit at+0x34.
It resets bookkeeping+0x38, not the whole object. TGCPRelay stores field1
dwPosition at+0, field2 szIdentity16 at+4, field3 ullServerID at+0x18,
field4 signed llSessionID at+0x20; bookkeeping+0x28. Native visualize routines
0x3b78a8/0x3b105c confirm labels; names do not establish generation/echo policy.

Actual isolated controls: empty components return0/presence0 while retaining
prior payload; empty nested relay marks Bingo presence1 without supplying an
identity. Compression-only input returns0 with method3/limit4096 and no relay.
Zero identity length returns-37/consumed5 at0x3b0e7c. Physical truncation-2
differs from declared-end overrun-34. Exact17-Z-byte identity control returns-35
after22bytes; this is not a universal native length rule. The native identity
loop stores at most16 then continues outer parsing; leftover bytes matter.

The44-byte copied relay block lives at handle+0x6d8 (position),+0x6dc (identity),
+0x6f0 (serverID),+0x6f8 (sessionID),+0x700 (bookkeeping). A bounded actual
send-SYN prefix0x3abc0a–1e copies it into request storage+0x2888. Independent
M bytes and synthetic surrounding registers/branch entry isolate data flow;
control stops0x3abc20 with sentinel-77 before flags/state/send. No SYN frame or
credential is generated. This proves reuse, not an original-SYN echo rule or
valid server identity/session creation. Application consumers remain unfinished.

## Reproduction, explicit substitutions and limits

Original [controls](../../../experiments/native_bingo_controls.py),
[21 tests](../../../tests/test_native_bingo_controls.py),
[matrix runner](../../../experiments/bingo_native_matrix.py) and actual
[23-control metadata matrix](../../../coordination/CF18-G2-AUTH-RX-02/BINGO_MATRIX.json).
Coordinator reproduced the local21 tests and exact matrix, then adapted canonical
imports only. Full canonical149 PASS/private-selected; default97 PASS/52 SKIP.
Knowledge doctor PASS. Matrices contain synthetic metadata/results, no real tokens.

Fresh hash/ISA-pinned PT_LOAD memory, initialized synthetic state4/FD42, method0/no
key, output cap256. Input/declared cap512;100000 instructions/one second; trace
events128/pending32. Prior relay S bytes and component R bytes are independent.
Android loader/GOT/globals/account negotiation/application context are incomplete.

| Substitution | Exact boundary |
|---|---|
| Wire controls | net wrapper0x284fcc returns-3/no-data or explicit-4 EOF-like; no socket |
| Decoded branch controls | receive0x3abe34 status/length explicitly stubbed; selected body0x3b8860 results/storage explicitly stubbed, including0 |
| Common runner | bounded memset0x193e60, memcpy0x193ed8, memmove0x193e6c; XLog0x393e80 no-op; last-error0x1b3b1c/26 get0/set no-op; inert error-string0x1c6544 |
| SYN-copy prefix | synthetic register/branch entry; stop before send, sentinel-77 |

Parser-stubbed branches prove side effects only. Real malformed-body control
returns body-2 -> receiver-18 without relay copy. No-data and injected EOF-like
status remain distinct. No actual socket, live phone/game, full OnStateDone or
application callback runs. Source-free native tests explicitly skip.

```text
CF18_APK_SOURCE=<private APK> CF18_APOLLO_LIBRARY=<private Apollo> \
 PYTHONPATH=<private deps> python -m unittest discover -s tests -v
PYTHONPATH=<private deps> python experiments/bingo_native_matrix.py --library <private Apollo>
python experiments/bingo_native_matrix.py
```

No arguments: inactive. Remaining work is actual account/relay/session binding
and state5 application consumers, deployed relay source and directional EOF,
installed context/OBB identity. This finding does not justify a guessed Bingo
addition to v1.4. Keep any later experiment focused on the proven body-wrapper
correction after bridge instrumentation. No automatic device proposal or run.

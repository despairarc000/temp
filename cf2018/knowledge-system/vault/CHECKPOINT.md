# Latest reviewed test: v3.8 DataHead

[Actual uploaded report and current blocker](research/V38_BLOCKER.md):2/4 routed client frames, kind5/no-compression reported, inner application unidentified; no4013 reply sent. The older v1.6 review below is historical. Need v38 parser/source, not another handshake sweep.

# Current checkpoint — 2026-10-31 server continuation

**Priority: original-client local server; integrity editing parked. NOT PLAYABLE.**
Reviewed main5d76e82696984717e394552cc6fb9c076e77e01f. [Decision/native continuation](research/SERVER_PATH.md).
Latest CF05 phone reports supersede earlier historical sections below: v1.4 body
correction removes immediate EOF2/2; v1.5/v1.6 synthetic Bingo elicits authentic
0x4013 in3/4 trials. No identified application RPC, accepted account, lobby or bots.
The v1.6 observer had a selector-kind filter defect; missing hint is inconclusive.
No v1.6.1 phone outcome reviewed here. Original report summaries are linked in
SERVER_PATH; raw reports not newly reopened. No new phone run by coordinator.

Native continuation verifies routed TX pre-encryption body is BE UID32 + original
application payload, with actual4013/header and state/size/route guards. Stops
before encrypt/send, not a real session.187 canonical PASS with explicit private
sources; default108 PASS/79 SKIP; incoming Bingo13/address14 PASS; doctorPASS.
Schedules remain paused. Next: actual inner RPC/envelope identification and native
reciprocal routed receiver; preserve working sequence, no guessed reply sweep.

The following sections are historical records with their original limits;
statements of no later packet or v1.4 result are superseded by this checkpoint.

# CHECKPOINT — 2026-10-30, auth receive failure integrated

CrossFire: Legends 2018 v1.0.11.11 com.tencent.tmgp.cfmnac, Mono.
**NOT PLAYABLE. G2 first hop CONFIRMED_ON_PHONE; auth/session BLOCKED.**
Reviewed main `ccdd219f9ed121e77fc06ad20b50b77614079cbf`.

## Current verified progression

User-confirmed [phone v1.2](../../coordination/incoming/CF18-05/PHONE_V12_RESULT.md):
SYN133 -> AA_DIRECT ACK63 -> authentic 0x2001/117 (header42/body73).
All eight sessions produced two client frames/250 bytes. Silence timed out at
about7s; three synthetic 0x2002 response arms gave local read_eof at about8–11ms.
No later client packet, authenticated session, AddressService, lobby or game.
Older statements that no post-ACK packet exists are superseded; do not restart
ACK-prefix experiments. Local EOF still does not identify its origin.

## Earliest verified native failure

[Reviewed AUTH_RECEIVER](research/AUTH_RECEIVER.md) and [exact native matrix](../../coordination/incoming/CF18-02/auth_rx_02/NATIVE_MATRIX.json):
all three exact v1.2 replies pass frame/header/extension/receive with effective
0x2002. TGCPBody::unpackTLV 0x3b8860 reads A5 instead of AA/99 and returns
-32 at0x3b88d8 after one byte; auth receiver maps it to -18 at0x3ac378.
Auth/account components and Bingo are not reached; account remains unchanged,
state3. All three omit the separate five-byte body preamble.

Minimal [original encoder](../../experiments/tgcp_body_envelope.py) wraps the
existing union in AA + BE uint32 total length; outer body length must be
recomputed. Corrected native paths reach real auth/account decoders, copy and
state4, then real Bingo -12/waiting (handler0). No parser-success stub is used.
Synthetic zero UID/state4/wait are not valid authentication or session evidence.
The deployed v1.2 bridge source is missing, so deployment/wiring is unverified.
A v1.4 envelope-only comparison is justified in principle, not ready to run.

## Source, framing and transport limits

[Source](../../sources/SOURCE_PROVENANCE.md): exact mirror APK/native/managed
hashes/ARM ISA and CMS/all1212 payload digests rechecked. CF18-05 reports matching
historical Original.xapk embedded APK/DLL hashes; that is historical reported
parity, not a newly retrieved original report, installed APK or OBB equality.
Full XAPK/OBB matching and actual Android runtime context remain unverified.
No new Drive scan/download; originals unchanged/private.

[ACK receiver](research/ACK_RECEIVER.md) and [body/session](research/ACK_SESSION.md)
remain useful hash-scoped native traces; earlier parser-stubbed branch controls
are distinct from current full-wire auth replay. The raw66 43 hypothesis is
retired for this receive path. CF18-01 boundary packet0019 remains pending strict99 parser integration. Reviewed
[path packet ccdd219](../../coordination/incoming/CF18-01/PATH_RESULT.md) shows
examined wrapper preserves prefixes and virtual dispatch selects GCloud factory
under synthetic context; this does not prove the phone runtime path.
[Relay](research/RELAY.md) core/handoff are local stages, not deployed v1.2 source.
Historical v0.1–v0.8 scripts and v1.2 directional closure evidence remain missing;
Q-02 UNKNOWN. Never substitute frame_gate.py for those sources.

## Actual coordinator verification

Local snapshot is not a git checkout (git status128); no active native worker.
Tracked blobs checked; existing CF18-01/02 edits and coordinator handoff drafts
preserved. Incoming auth25 PASS/no skips. Published matrix reproduced exactly.
Source verifier PASS including1212 signed entries; certificate trust not validated.
Canonical149 PASS with explicit private APK/library/dependencies; default149 total,
97 PASS/52 private-source SKIP. Knowledge doctor PASS. These are offline/local
checks with the explicit stubs in AUTH_RECEIVER, not a phone authentication run.
[Integration](../../coordination/INTEGRATION.md), [evidence](EVIDENCE.md),
[assignments](../../coordination/assignments.json) track inputs/limits and next tasks.

## Next gate

CF18-02: actual state5 application/account/session consumers after corrected auth;
no guessed credentials, keys or valid Bingo. CF18-03: recover deployed v1.2 source
and directional lifecycle before phone instrumentation. CF18-01: path packet reviewed as bounded evidence; await framing review feedback.
CF18-04: wait for new precise historical report/installed/OBB locator; no repeated
inventory. CF18-00 next reviews submitted99/bounds separately. Bot work deferred.

## Bingo/session acceptance boundary

[Reviewed continuation](research/BINGO_SESSION.md):3002 is WAIT/queue metadata.
Actual body decoding replaces the header selector; a deliberately mismatched
header6002 or3002 with auth-body2002 reaches numeric state5 without running a
Bingo component decoder. No valid Bingo was built. Numeric state5 therefore
does not establish authentication or correct correlation. Received relay identity/
server/session fields are copied and later reused by a SYN prefix; generation/
account binding remains unknown. All21 new controls and both native matrices
reproduced; decoded parser-zero branch tests remain explicitly stubbed.

## Later coordinator investigation at c9b1d355

[Connection callback trace](research/CONNECTION_CALLBACKS.md) extends the native
consumer path: injected state5/writable event can schedule a locally constructed
zero result with zero connected-info account prefix. Separate dispatch controls
reach AddressService, whose result-code branch gates local buffer binding; open
is a no-op. These notifications do not establish authentication. Eleven new tests,
160 canonical PASS/private-selected; default98 PASS/62 SKIP; ten-case matrix
reproduces exactly. Existing CF02 local13 controls reproduced, incoming unchanged.

CF05 [v1.4 handoff](../../coordination/incoming/CF18-05/V14_DEPLOYED_BRIDGE_HANDOFF.md)
reports recovered deployedv1.2 bridge and prepared private six-session envelope
comparison. Earlier blanket source-missing statements are superseded for that
preparation; this coordinator has not independently reopened the private ZIP.
No phone result yet. Schedules remain paused. Next offline boundary is actual
QueryAddrInfo submission/response, not another guessed Bingo or connected flag.

## Direct DLL investigation at6a0ecc16

User requested finding why managed edits auto-exit. [Native integrity trace](research/INTEGRITY_NATIVE.md)
confirms stored Assembly-CSharp/firstpass are non-PE; original Mono image loading
routes through libtprt. Reproduced signature branches and an injected post-load
CRC mismatch requesting termination18, intercepted before syscall. This is a
real native guard, not yet the cause of the historical edited-DLL phone exit.
Historical edited bytes/precise diff and matched logs remain absent; provider
initialization and safe format round trip unresolved. No patched build delivered.

Added read-only image/diff preflight, bounded original native controls and actual
15-member/native matrix. Canonical176 PASS with all explicit private sources;
default106 PASS/70 SKIP; doctorPASS. No originals changed, phone test or schedule
started. TGCP/Bingo/session findings and separate pending work remain intact.

## Integrity caller continuation

[Native investigation](research/INTEGRITY_NATIVE.md) now locates actual original Unity->Mono call0x20f87c and its buffer preparation. Supplied null-image or nonzero-status controls take diagnostic branch, distinct from explicit native termination. Stored APK bytes are not yet proven identical to Mono input because virtual/file-reader and initialization effects remain unresolved. No decoded image or unchanged round trip achieved.180 canonical PASS private-selected; default107 PASS/73 SKIP; doctorPASS.

## Latest supplied phone test: v3.8 (supersedes v1.6 recency)

[Actual report review](research/V38_BLOCKER.md): four synthetic-stage trials, two later4013 frames/header79/body80 or85; kind5, named-route candidate, compression reportedoff, no recognized inner operation. No4013 reply sent; post-route-window completion is not reply rejection. Native crypto helper controls demonstrate compression off does not establish plaintext. Current blocker: actual application framing and v3.8 classifier/source review. No new phone run.191 canonical PASS private;109 PASS/82 SKIP default; doctorPASS.

# Current checkpoint — 2026-10-31

R074 (2026-11-02) **REAL ORIGINAL PHONE DIFFERENTIAL**: Uploaded sanitized SYN diagnostic confirms second-service slots2/3/4 each `syn_changed=[[5,0]]` (**field5=iUnitID, encoding kind0, value NOT exposed**), plus field14 named-route shortened2B. Base unchanged, no other non-route SYN differences; *all three had ACK0 intentionally*, so no second-service auth or ACK rejection. Supports R072/R073 unit-change explanation but CTDir/runtime source unverified. Added source-only read-only R074 class-only route+unit predicate, 13 negative/positive tests PASS in [corrected CI 41369763827](https://github.com/despairarc000/temp/actions/runs/41369763827), never authorizes ACK. [R074 report](research/R074_PHONE_UNIT_FIELD_CONFIRMED.md). Next source research concrete connector/receiver, not repeated phone test.


R073 (2026-11-02): Original static `RpcConnector::Init` performs the domain check and optional `ParseDomainName` before requesting LB addresses through `InitLbIpAddress → GetServiceAddress`. Later `RpcConnector::Update` calls `CreateConnection → LBSelect`. CTDir is a verified Init caller but not a proven producer of the real R037 alternate SYN. **Unit may be configured before reply arrives**; response did not demonstrably mutate it. Original private ELF 14 callsites checked; 11 public synthetic tests PASS, 1 original-only SKIP in [CI 41366556022](https://github.com/despairarc000/temp/actions/runs/41366556022). [R073 report](research/R073_RPC_INITIALIZATION_ORDER.md). Next use existing value-free changed-field-number diagnostic, without another ACK or kit. No accepted second-service login/bots.

R072 (2026-11-02), ORIGINAL NATIVE SOURCE/BOUNDED EMULATION: examined RPC CreateConnection explicitly keeps client-type override selector0, so R071 selector2 is not supplied by this caller. Its differing flag enables SetNameService, not demonstrated security/account change. RPC Init can replace configured unit with a numeric service-domain component; actual parser flow with functional synthetic string/number stubs, original override store and serializer unit1→3 controls pass. Unit1→3 changes only same-length SYN5 and still reaches suppressed auth-send; bad key remains blocked. CTDir is one verified Init caller and configures a10-byte route literal, a compatible candidate not phone attribution.4 native-gated methods PASS. Next use the existing field-number diagnostic to discriminate unit-field explanation from other paths; no new ACK attempt. [Evidence](research/RPC_DOMAIN_UNIT_SOURCE.md).

R071 (2026-11-01 UTC), ORIGINAL NATIVE STATIC/BOUNDED EMULATION: AddressService fixes unit1; connector initialization transfers caller unit to CTGcp. CTGcp starts client type101; connector selector2 overrides102, selector3 overrides0, selector1 sets101. Pinned reference agrees with discovery unit1/type101. Actual serializer:101→102 changes field6 at same length;101→0 shortens it by1, which does not fit R069 if field6 is its sole extra change. GameID comes from shared common state in both inspected branches.5 private-source tests PASS, previous handoff3 PASS. Compatible candidate is not phone identification. No gate relaxation or new phone test. Next trace actual downstream init-info suppliers. [Evidence](research/SYN_ATTRIBUTE_SUPPLIERS.md).

R070 (2026-11-01 UTC), ORIGINAL NATIVE STATIC/EMULATION WITH STUBS: mapped SYN4/5/6 to llGameID/iUnitID/iClientType via original writer and visualize names. Actual SYN preparation and serializer prefix show each synthetic application-attribute change yields exactly one same-length field difference, with key/encryption fields unchanged. All3 changes still reach suppressed auth-send on the same synthetic63-byte ACK.2 new methods/six mutation cases PASS;3 existing native handoff methods/seven cases PASS. This supplies concrete non-security alternatives to R069's extra field change, not that phone field's identity. Gate unchanged; no new phone test requested. Next trace attribute suppliers for address discovery versus next connector. [Evidence](research/NATIVE_SYN_APPLICATION_FIELDS.md).

R069 PHONE RESULT (2026-11-01 UTC): owner one-ACK report shows first-service address reply written, then3 reconnects with131-byte named-route SYNs; all SYN_CONTEXT REFUSED, ACK0. Each has route14 length-2 AND syn_same_length_modified_count1: at least one other SYN field differs, identity unknown. No second ACK attempt occurred; cannot call this ACK rejection or auth progress. New standalone diagnostic copy patch reports changed field numbers/types only and hard-disables next ACK.4 label tests +1 loopback integration +113 original regressions PASS. Next identify that field before native interpretation or weakening any condition. [Evidence](research/SECOND_SERVICE_ACK_PHONE_RESULT.md).

R068 (2026-11-01 UTC), OPTIONAL ONE-ACK EXPERIMENT PREPARED / PHONE NOT RUN: separately opted-in extra ACK requires exact SYN-context match, prior R037 address-reply write and a locked one-attempt budget. It reuses the working63-byte ACK, observes one next-service frame, then closes without sending next-service auth/Bingo. 113 original regressions +5 loopback lifecycle +2 refusal tests PASS. Default remains HOLD_NO_ACK. Separate report/run paths preserve old results. Next owner-controlled Termux/PCAPdroid experiment can test for AUTH_REQUEST_OBSERVED; this is transport progress, not account login. [Procedure](research/SECOND_SERVICE_ACK_EXPERIMENT.md).

R067 (2026-11-01 UTC), SOURCE/LOOPBACK ONLY: new exact non-route SYN comparison requires identical encoded base and every SYN field except the bounded12→10-byte named route. R037 now exports fixed SYN_CONTEXT labels while preserving HOLD_NO_ACK. Five gate tests, updated two-connection lifecycle and113 original prepared-copy regressions PASS. Historical redacted phone summaries cannot retroactively establish this exact match. No new ACK/phone/session acceptance. Next combine a successful runtime comparison with the source-backed ACK predicates in a separately bounded manual experiment. [Proof](research/SECOND_SERVICE_DISPATCH_PATCH.md).

R066 (2026-11-01 UTC), ORIGINAL NATIVE EMULATION WITH STUBS: actual GCloud SYN preparation with synthetic named routes then original ACK parsing reaches suppressed auth-send for both10/12-byte names. 3 methods/7 cases PASS, including malformed magic, unsupported mode1, TX prefix, truncation and relay-route negatives. SYN pack/send and auth send suppressed; prepared handle transferred between fresh emulator contexts. This narrows route-length-alone exclusion, not actual phone security/session acceptance. R065 unknown-route HOLD_NO_ACK remains. Next compare actual non-route SYN/security fields to working reference before any bounded manual ACK test. [Evidence](research/NATIVE_SYN_ACK_HANDOFF.md).

R065 (2026-11-01 UTC): owner-supplied R037 ZIP matches recorded 35,193-byte/SHA receipt; exact preparer chain and generated handler now pinned. R056 corrected dispatch integrated into active-reply R037 copy without changing original reply code, one-shot guard, redirector or live opt-in. 113 original regression +30 R037 focused +1 new two-connection loopback tests PASS; 2 source-refusal tests PASS. This supersedes R064's missing-active-source integration blocker. Changed route still HOLD_NO_ACK; no phone or login proof. Next establish second-service ACK/session predicates before another live experiment. [Details](research/SECOND_SERVICE_DISPATCH_PATCH.md).

2026-11-01 UTC — Guarded Termux dispatch patch: corrected R056's use of inbound reply grammar on client SYNs (client base kind0 except field6 kind1). Exact private baseline and redirector fingerprints verified; copy-only preparer verifies 60 files. 11 classifier tests + 6 patch controls PASS with private source; 113 original prepared-copy regression tests PASS. No new ACK, phone run or login; actual R037 active-reply source integration remains outstanding. [Details](research/SECOND_SERVICE_DISPATCH_PATCH.md).

**NOT PLAYABLE. No validated account/session, accepted service reply, lobby or bot match.**
Target2018 v1.0.11.11 com.tencent.tmgp.cfmnac, Mono. Prioritize original-client
local server; integrity editing parked. Scheduled workers remain paused.

Read [CURRENT_HANDOFF](../../coordination/CURRENT_HANDOFF.md) before choosing work.
It records the owner's actual PCAPdroid/Termux workflow, source access, exact next
artifact, controls and no-repeat rules. Base main0d6dc5edec04e687cc677f2cce5dca20b15171da;
this checkpoint consolidates earlier repeated historical sections. Original
findings remain in [EVIDENCE](EVIDENCE.md), [WORKLOG](WORKLOG.md) and linked traces.

## Latest real phone evidence: v3.8.1, now reviewed

[PHONE_V381](research/PHONE_V381.md):2/4 later4013 frames161/166, body80/85.
Both report sequence_prefix=MATCH, known_address_route=MATCH (QueryAddrSvr), and
METHOD_BYTES_POLICY at offsets0/4. This identifies the route and supports the
sequence boundary; operation/encoding still unknown. No4013 reply tested. Next
trace CTGcp::onDataOutEvent queue producer (direct send edge0x3a5476); do not repeat
this diagnostic. Older awaiting-phone-result paragraphs below are superseded.

## Repository/source re-audit and upstream trace

[Re-audit](research/REPOSITORY_SOURCE_AUDIT.md): actual private APK/Apollo/stored
DLL hashes recalculated; full XAPK/OBB absent from workspace/attachment roots.
Receipt confirms whole archive was not downloaded. Native work remains possible
with available Apollo. Complete live cf2018 tree181 files and23 incoming reports
reviewed. New static queue chain reaches CTGcp::Write overloads0x3a45bc/0x3a4708;
next trace their upstream payload construction and inverse receive path. No new
phone test or decoder acceptance inferred.

## Current verified progression

Real phone: SYN133 -> AA_DIRECT ACK63 -> auth0x2001/117. All three v1.2 response
arms failed natively because they omitted TGCPBody preamble; actual unpack modeA5
failsAA/99 at0x3b88d8 (-32), auth maps-18 at0x3ac378 before account parsing.
[Auth trace](research/AUTH_RECEIVER.md). Corrected54-byte response removes immediate
EOF in v1.4; synthetic Bingo91 elicits later real4013 in v1.5/v1.6 reports3/4.
Those earlier cohorts are separate from latest v3.8; do not pool as probabilities.

Latest real test [v3.8](research/V38_BLOCKER.md):2/4 later4013 frames161/166 bytes,
header79/body80 or85, extension kind5, compression off reported. Two deliberate
post-route windows, one deadline, one EOF. No4013 reply was sent. Application
operation unidentified. EOF does not diagnose an authentication rejection.

## What offline reverse engineering established

[Exact source/native audit](research/V38_SOURCE_AUDIT.md), [matrix](../../coordination/V38_STAGE_CONTEXT_MATRIX.json):
exact v38 synthetic ACK63/auth54/Bingo91 returns0 with states2/4/5 and method0.
Auth-send omitted/state3 supplied; no-data/memory/log stubs explicit. This is not
an actual phone crypto measurement or legitimate account validation. Numeric5
alone is not success. [Bingo/session](research/BINGO_SESSION.md).

Four-byte routed prefix is **packet sequence dwSequence**, not UID or application
length. Actual native increment and final mode0 queued-body preservation verified.
Original native legacy RPC writer emits BE32 name length +name +U8 type +BE64
sequence, recognized by v38 classifier at offset4 on independent synthetic input.
No simple endian/offset correction found. Current earliest failed boundary is
observer application identification; no native failing predicate for actual
redacted phone body established. See the audit for addresses/provenance/stubs.

## Additional actual-native application findings

[Request producer/result decoder](research/ADDRESS_APPLICATION.md): generated arguments are34+service-string-size; full native legacy and strict requests are both found at offset4 by v38 observer. Thus a simple endian/legacy-classifier switch does not explain the real unidentified body. Native response requires result AND reason STRING; absent reason fails0x39ead8 before exception allocation, empty is allowed. Integrated canonical offline preflight correction; no4013 reply or live bridge change.

## Ready next diagnostic and development continuity

[Patch-only v3.8.1 kit](../../deliverables/CF2018_v381_Patch_Kit.zip) consumes the
owner's existing exact v38 ZIP on their device, creates a new folder, adds fixed
sequence/header/allowlisted-route labels, distinct output and run/connection IDs.
No APK/OBB/DLL edits or new4013 response. Four-session budget and original protocol
handler unchanged. New diversion is exact known numeric IP AND8080/8085; normal
non-target passthrough retained. [Exact steps](../../coordination/V381_TERMUX_STEPS.txt).
Preparation/default startup never starts live listeners. Owner manual opt-in only.

Linux controls exercise actual supplied SOCKS5 NO-AUTH/CONNECT redirector -> fake
TGCP server, four synthetic game sessions, exact ACK/auth/Bingo bytes, privacy,
IDs, report and EOF. Non-target local binary passthrough control also passes.
This does not claim Android/PCAPdroid execution of v3.8.1. Latest phone result
remains v3.8 until the owner supplies a new TXT.

Next AI: follow the handoff decision table; continue native application producer
and reciprocal receiver work. Do not repeat ACK research, guess valid credentials,
request broad packet sweeps, or claim source missing without inspecting access.

## Actual source and remaining gates

[Source provenance](../../sources/SOURCE_PROVENANCE.md) and [Drive limits](../../sources/DRIVE_MANIFEST.md).
Exact APK/Apollo privately recovered/hash verified; v38 ZIP supplied and all60
files pinned. Private paths are runner-local/transient; recheck availability/hash.
Historical embedded APK/DLL equality is reported; current installed/fullXAPK/OBB
identity remains partial. No substitute9.99 or cfmobileoffline.

G3 accepted address-service reply, G4 update/config, G5 lobby, G6 real TDM bots,
G7 Bomb bots and G8 repeatable installation/matches remain open. Integrity route
has original Mono/provider/checksum predicates but no decoded unchanged round trip,
verified historical exit cause or safe edited build. [Integrity](research/INTEGRITY_NATIVE.md).

## Verification

Canonical236 PASS with explicit private APK/Apollo/Unity/Mono/tprt, v38 source/ZIP
and analysis dependencies. Default236 total:137 PASS/99 explicit private-input SKIP.
Four new patch-kit tests include complete local SOCKS5 integration; v381 default
starter runs9 original focused synthetic tests and starts no listener. DoctorPASS.
No new phone result, external-service experiment or scheduled worker activation.

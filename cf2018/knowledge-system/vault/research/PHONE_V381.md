# Latest real phone result — v3.8.1 sequence boundary

2026-10-31, CF18-00, base maine9a120fa54a9b4daeb5c2733382680fced507e35.
Owner uploaded CF2018_v381_Sequence_Boundary_Result.txt,5777 bytes,
SHA2568b4e60eb97f08c81cf6b904c674dd201652deead588c5f30d4e0a4393c298919.
Actual text read locally. Evidence class USER_SUPPLIED_PHONE_REPORT plus
SOURCE_AUDITED_OBSERVER_CLASSIFICATION; no attached device or coordinator phone
execution. Public record contains descriptive findings only, not the raw report,
run/connection values, packet payloads, account values or session captures.

## Acceptance for this review

Read exact report and fixed diagnostic code; distinguish body boundary, named
route equality and lexical method policy from full native request decoding.
Preserve all four outcomes and original stages. Do not call MATCH login/plaintext,
METHOD_BYTES_POLICY a native error, or EOF proof of authentication rejection.
No new server reply, game modification or automatic device experiment.

## Actual four trials

All four: SYN133 -> ACK63 -> auth2001/117 -> synthetic auth54 -> Bingo91.
Bingo sent150.91–151.46ms after auth response. No4013 reply generated.

| Slot | Observed later traffic | Observer end condition |
|---|---|---|
|1|4013/161 bytes, header79/body80,35.10ms after Bingo|post_route_window_complete,1756.12ms total|
|2|none|deadline_after_auth_attempt,8187.47ms|
|3|none|read_eof,4191.17ms|
|4|4013/166 bytes, header79/body85,26.52ms after Bingo|post_route_window_complete,1707.05ms total|

Do not pool2/4 with older cohorts as a controlled success probability. The two
window completions are deliberate observation stops, not rejected replies.
Global relay counts include30 connects/3 failures and cannot attribute slot3's
EOF to a phone FIN/native reject or establish per-slot causality.

## New discriminating results: both routed samples

| Check | Actual output | Exact meaning |
|---|---|---|
| sequence_prefix | MATCH | First four body bytes equal validated header field7 packet sequence |
| known_address_route | MATCH | Exact in-memory route equals allowlisted QueryAddrSvr |
| legacy_at_start | METHOD_BYTES_POLICY | At offset0, length passes1..64 and name bytes are present, but method-name lexical policy fails |
| legacy_after_sequence | METHOD_BYTES_POLICY | Same lexical failure after the four-byte prefix; not SHORT/TRUNCATED/NAME_LENGTH failure |
| compression_flag | no | Routed compression flag off; not an encryption verdict |
| app_rpc_offset / dedicated legacy parser | not_identified | No complete recognized application operation |

Source: [bounded diagnostics](../../../experiments/routed_body_diagnostic.py),
[exact patch kit preparation](../../../experiments/v381_termux_patch.py).
METHOD_BYTES_POLICY may fail either initial-letter/underscore or later allowed
ASCII character checks. Report does not reveal which byte/value or method length.
These are conservative Python observer policies, not native error return codes.

Boundary agreement and route identification are now measured on this phone run,
not merely synthetic/native assumptions. They support using the packet-sequence
boundary and focusing the QueryAddrSvr producer. They do NOT prove application
plaintext, actual QueryAddrInfo call, legitimate account, server response acceptance,
valid session or playability. Identical per-run sequence values/cipher coincidence
and separate application wrappers cannot be resolved from this metadata alone.

The second sample again reports64plus common body prefix and first change64–71.
[Actual native application controls](ADDRESS_APPLICATION.md) already show simple
complete native legacy QueryAddrInfo bodies80/85 first differ61; strict comparison
can first differ64 but is recognized by the existing complete application parser.
Both native-generated forms are positive controls. Current phone data therefore
still lacks an established mapping to either complete application form. Do not
change replies merely by toggling strict/legacy mode or guessing identifiers.

## Concrete next offline target, not another repeat observer run

Trace the real producer/queue boundary for QueryAddrSvr application bytes, then
reciprocal response dispatch. A fresh hash/ISA-checked original-native static scan
and symbol containment found these direct edges to send_with_route0x3a91ec:

-0x3a5476 inside GCloud::CTGcp::onDataOutEvent().
-0x3a94de inside gcloud_tgcpapi_send() wrapper.

These are bounded static candidate edges, not an exhaustive caller set (indirect
calls and alternate paths remain), nor proof which path the phone used. Next
inspect CTGcp::onDataOutEvent queue element's pointer/length/route origin, upstream
producer and any application wrapper/transform BEFORE routed TX. Preserve the
proven four-byte sequence boundary. Do not blindly strip arbitrary bytes, decrypt,
issue a new4013 reply or request identical phone diagnostics again.

If offline producer tracing cannot localize the mapping, specify a minimal
in-memory structural predicate grounded in that trace. Raw private request content
would require an explicit narrowly scoped local/private workflow; it is not
present in this TXT and must never be publicly committed. No immediate new phone
run is requested by this review. Continue existing PCAPdroid/Termux architecture.

## Verification and handoff

Live main and required repository docs refreshed; local directory is a snapshot,
not a git checkout (git status exit128), no active shared git edits inferred.
Route and knowledge doctorPASS. Default canonical suite236 total137 PASS/99
explicit private-input SKIP this activation. Prior236-private-PASS result remains
historical; it was not rerun for this report-only integration. Actual native source
hash/ISA rechecked for the static caller scan; no native acceptance test invented.
[CURRENT_HANDOFF](../../../coordination/CURRENT_HANDOFF.md) supersedes its prior
awaiting-phone-result state. No new kit/stage bytes, schedules or original edits.

# Current CF2018 handoff — read before choosing work

Updated2026-10-31, CF18-00, base main0d6dc5edec04e687cc677f2cce5dca20b15171da.
User explicitly requested this durable handoff and a usable next diagnostic.
Current target: **2018 v1.0.11.11 com.tencent.tmgp.cfmnac, Mono**. End goal remains
real offline TDM/Bomb bot matches. **Not playable; no validated login/session.**
All scheduled workers remain paused. Do not recreate/resume schedules.

## New original-native upstream trace (2026-11-01)

[UPSTREAM_REQUEST_CHAIN](../knowledge-system/vault/research/UPSTREAM_REQUEST_CHAIN.md) independently rechecked the exact original Apollo and verified 11 static instruction pins: `ProcessRequest -> Send_QueryAddrInfo -> generated args`; `MsgBuffer::bind/writeEnd` bound connector callback; concrete `CGCloudConnector::Write -> CTGcp routed Write -> queue -> onDataOutEvent`. The concrete virtual runtime path and phone operation remain unidentified. Next bounded original-code synthetic MsgBuffer/connector differential, then response handling. No repeat phone v381, guessed 4013 response, source download, XAPK patch or schedule restart.

## Latest update: owner completed v3.8.1 phone run

[Actual phone review](../knowledge-system/vault/research/PHONE_V381.md) supersedes
all awaiting-v381-result statements below:2/4 routed frames, both sequence MATCH,
exact QueryAddrSvr route MATCH, METHOD_BYTES_POLICY at offsets0/4. No4013 reply or
operation identified. Do not ask for this same test again. Next offline target:
CTGcp::onDataOutEvent queue/body producer, direct routed-send edge0x3a5476, and
reciprocal application response dispatch. No automatic new phone experiment.

## Original-file availability clarified and producer trace advanced

[Repository/source audit](../knowledge-system/vault/research/REPOSITORY_SOURCE_AUDIT.md):
no full XAPK or full OBB locally; verified30.9MB extracted APK plus Apollo and
stored protected DLLs are present and rehashed. Receipt explicitly records that
whole archive was not downloaded. v38 source ZIP is a probe package, not game
XAPK. Current native research has the required Apollo; do not reset to missing APK.
Live complete tree181 files and23 incoming reports reviewed. Historical receipt
G2/no-post-ACK status is superseded by v381, not current mission truth.
Queue chain now traced: CTGcp::Write0x3a45bc/route overload0x3a4708 -> send queue
-> PopOneSendBuffer0x3a43ac -> onDataOutEvent -> pointer/size handoff0x3a5476.
Next resolve upstream Write callers and AString construction/transform, not another
boundary phone test. No new operation/session acceptance claimed.

## How the owner actually tests

```text
Original CF2018 Android client, original OBB
  -> PCAPdroid VPN, CrossFire selected, Termux EXCLUDED
  -> SOCKS5 127.0.0.1:1080 in Termux
  -> Termux cf2018_redirector.py --mode forward
  -> fake TGCP server 127.0.0.1:8080 or 127.0.0.1:8085
  -> sanitized TXT in Android Downloads -> owner shares TXT
```

Android15/Samsung/no-root is reported environment context, not a device currently
attached to this runner. PCAPdroid is the VPN/SOCKS5 client; Termux runs both the
SOCKS5 redirector and fake TGCP service. Excluding Termux avoids proxy recursion.
Only one VPN and one probe instance. Stop older Termux probes using Ctrl+C before
starting another; do not change ports to conceal an old instance. No adb, root,
emulator, reverse tunnel or APK patch is required by the existing owner workflow.

Known numeric destinations:45.113.69.32,211.159.211.105,119.28.34.12 AND8080/8085.
The supplied v38 redirector also diverts two explicit domain aliases on those
ports. New v3.8.1 diagnostic diversion is numeric IP+port only; domain CONNECTs
and other non-targets retain ordinary passthrough. Do not silently broaden scope
or block unrelated DNS/traffic. Both local services bind loopback only.

Sources reviewed directly: exact supplied v38 README.md, START_V38.sh,
routed_probe_v38.py, cf2018_redirector.py, existing tests and report exporter;
[all60 pins](V38_SOURCE_PINS.json). These supersede old isolated-core documents
which said the deployed source was missing. Original v0.1–v0.8 historical scripts
remain unavailable unless independently recovered; do not relabel v38 as them.

## Current facts, separated by evidence class

| Class | What is actually established |
|---|---|
| User's real phone reports | SYN133 -> ACK63 -> auth0x2001/117. Corrected auth54 removes immediate EOF in v1.4. Synthetic Bingo91 elicits real0x4013 in later trials. |
| Latest real phone test: v3.8 | 2/4 trials emit161/166-byte4013, header79/body80 or85; extension kind5; compression off reported. No4013 reply sent. Operation unidentified. Two deliberate post-route windows, one deadline, one EOF. |
| Original-native execution | Exact v38 lab ACK/auth/Bingo returns0 and states2/4/5, method0. Auth-send omitted/state3 supplied; no-data/log/memory stubs explicitly recorded. Not a phone crypto measurement or account validation. |
| Original-native correction | Four-byte routed prefix is packet sequence `dwSequence`, NOT UID or application length. Counter increment verified. |
| Native serializer + observer differential | Actual legacy RPC header is BE32 name-size +name +U8 kind +BE64 sequence. v38 classifier recognizes independent synthetic native output at offset4. No obvious endian/offset fix found. |
| This continuation | Patch-only Termux kit prepared; four synthetic game sessions through actual SOCKS5 redirector -> patched server, original stage byte equality, report/ID/privacy and non-target binary passthrough controls. Linux only. |

[Latest report review](../knowledge-system/vault/research/V38_BLOCKER.md),
[source/native audit with exact addresses and stubs](../knowledge-system/vault/research/V38_SOURCE_AUDIT.md),
[stage matrix](V38_STAGE_CONTEXT_MATRIX.json), [server priority](../knowledge-system/vault/research/SERVER_PATH.md).
Latest report SHA256031dcb5bf33eb979cd95b161708c454006fd938f50ff08893db923fa81614cb3.

**Earliest failure:** v1.2's missing TGCPBody preamble was localized natively and
corrected. For the current v38 routed request, only observer identification has
failed; no native failing predicate or rejected service response is established.
EOF is not proof of authentication rejection. No new4013 reply is justified yet.

## Additional offline finding after this handoff

[Native application fields](../knowledge-system/vault/research/ADDRESS_APPLICATION.md):
actual generated request arguments execute and both complete native legacy/strict
requests are recognized by the existing v38 application parser at offset4. Plain
legacy size80/85 would first differ at61, inconsistent with the reported64plus
prefix under that simple model. Producer/encoding still unknown; do not swap RPC
formats by guess. Actual native response requires BOTH result and reason STRING;
empty reason allowed, absent reaches0x39ead8 missing-field path. Canonical offline
preflight now rejects missing reason; this is not a phone fix or valid reply.
236 canonical private PASS /137 PASS+99 SKIP default; source-native12 and canonical
preflight15 PASS. Delivered v381 kit and latest real phone result unchanged.

## Ready next artifact and exact test

[Patch-only ZIP](../deliverables/CF2018_v381_Patch_Kit.zip),
SHA256`6e2dd2b405b05ac9e81f42f89bd56e6fe6f00f0790cc0e31686d3bbd14ece701`.
[Complete Termux commands](V381_TERMUX_STEPS.txt). Four original-code/descriptive
files only; **no** APK/OBB/library/assembly/original SYN or private source archive.
Use the owner's existing CF2018_TGCP_v3.8_GCloud_DataHead_Flags.zip; hash must be
e3bbc31f7b93e738aff0d4205dd0d1418c7abd55b7c17b332ca5d426eb619df2.

Unzip the patch kit in Downloads, execute its apply_v381.py with `--zip` pointing
to that original ZIP and a **new** output folder. It validates all60 files and
does not modify the input ZIP or start listeners. Existing output is refused.
Inside the new folder, `bash START_V381.sh` runs nine offline synthetic tests.
Only manual `CF2018_V381_LIVE=YES bash START_V381.sh` starts the four-session
phone diagnostic. Then launch the original game with the existing PCAPdroid
profile. No APK, OBB or DLL editing. No automatic phone run by an AI.

Result: `~/storage/downloads/CF2018_v381_Sequence_Boundary_Result.txt`.
Separate `~/cf2018_v381_runs/run_<UTC>_<id>/` metadata; report includes run/connection
IDs. Old v38 output is not overwritten. Share only sanitized TXT. No raw packet,
route-name, account, token, sequence-value or payload logging. The redirector must
be in **forward**, not its standalone default capture mode. No4013 response.

Unchanged protocol handler: ACK/auth/Bingo bytes,150ms delay,8s per-session bound,
four accepted slots and post-route observation window. Preparation's report/ID
labels and exact numeric routing restriction are the other documented changes.
If no client connects, check same-phone VPN/app-filter/SOCKS5/old-process state;
the process may wait for manual Ctrl+C when fewer than four sessions arrive.
Do not call that a decoder rejection. Another random reply sweep is not needed.

## What the next AI must do with that result

| Observation | Next falsifiable action |
|---|---|
| sequence_prefix=MATCH, legacy_after_sequence plausible | Validate full argument structure and real producer/response consumer; header plausibility is not RPC acceptance. |
| MATCH, legacy fails | Use exact failure label to trace actual application producer/encoding. Method0 in the lab does not rule out application-layer transformation. |
| MISMATCH or NOT_COMPARABLE | Review header field7/body length/native boundary and actual connection context. Do not blindly strip or decrypt bytes. |
| known_address_route=MATCH | Allowlisted QueryAddrSvr route matched only; do not claim QueryAddrInfo arguments or real session. |
| OTHER/UNKNOWN | Find the actual producer; do not force AddressService framing onto it. |

Useful offline continuation: trace actual MsgBuffer/route callback into routed
send, and the reciprocal correlated service handler. Keep the supplied stage
sequence fixed. The redacted v38 TXT cannot reconstruct absent application bytes;
if labels still cannot localize it, define the least private local observation
needed before requesting data. Do not publish raw captures or account contents.

## Source access and no-repeat rules

The exact APK and Apollo were recovered and hash verified, not just an OBB.
[Provenance](../sources/SOURCE_PROVENANCE.md), [Drive manifest](../sources/DRIVE_MANIFEST.md).
APK30884905 bytes SHA33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9;
Apollo5243704 bytes SHA4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8,
ELF32LE ARM/Thumb. Current runner private files are under
coordination/incoming/CF18-04/private/; v38 extraction under private/v38_source/.
These are transient private paths, not public GitHub files or shared-worker mounts.
Recheck availability/hashes; do not assert private access from this handoff alone.
Original user ZIP/report were uploaded attachments; source pins do not provide
their bytes on a new runner. Do not ask again while actual inputs remain present.

Do not restart SYN/ACK research, resurrect raw6643, call state5/login, confuse
compression with encryption, assume UID-prefix, substitute9.99/IL2CPP, repeat
Drive asset inventories, build bots before prerequisite gates, or restart DLL
patching. Integrity findings are retained but parked: no safe edited build or
unchanged decoded round trip established. G3 accepted service response, update,
lobby and actual match/bot functionality remain open.

## Ownership and verification

CF18-00 owns this handoff and canonical files; incoming lanes retain exclusive
paths per [assignments](assignments.json). GitHub existing main only, connection
link_6ad1d4fc541c81919383550129f2bf06. Re-fetch before writes/CAS; no force push.
No automatic messages, schedules, original modification, live game/network test.
[Acceptance and controls](CF18-TERMUX-HANDOFF-ACCEPTANCE.md).
Run route/doctor/canonical tests, report actual skips and private input selection.
Offline test results and deployment instructions are not new phone evidence.

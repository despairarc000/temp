# Repository/source re-audit and queued producer continuation

2026-10-31, CF18-00, base mainb418e8b988b5b7e03c26448263a177dfaadf053f.
Owner asked whether the full XAPK is present and whether repository context was
missed. Acceptance: refresh live tree/startup/source docs, review worker evidence,
check actual local artifacts/hashes, separate old receipt status from current
phone evidence, and advance the bounded producer trace without claiming runtime
acceptance. No game/source modification, source download or phone experiment.

## Exact answer about original availability

**Full XAPK: not present in the searched workspace/attachment roots. Full OBB:
not present there.** The mirror receipt explicitly states whole_archive_downloaded
false, whole_archive_hash null. Archive Content-Range size768008878 is remote
metadata, not a locally downloaded XAPK or calculated archive hash.

Privately present and hashes recalculated this activation:

| File | Bytes | SHA256 |
|---|---:|---|
| com.tencent.tmgp.cfmnac.apk |30884905|33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9|
| armeabi-v7a-libapollo.so |5243704|4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8|
| stored Assembly-CSharp.dll |13423104|174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9|
| stored Assembly-CSharp-firstpass.dll |317440|4ac2b58a02cc1d3ad1e345d9b21dd78c758b0077c19354862792d25bcaa8ba60|

Original APK extracted from mirror XAPK; local source directory is
coordination/incoming/CF18-04/private/. Stored DLLs are protected/non-PE as already
recorded; their existence is not a usable decoded Mono assembly. Additional native
libraries were privately extracted for prior integrity work. The user-supplied
v38 source ZIP/extraction is a diagnostic package, NOT the game's XAPK.
[Provenance](../../../sources/SOURCE_PROVENANCE.md),
[receipt](../../../sources/MIRROR_RECEIPT.json),
[Drive limits](../../../sources/DRIVE_MANIFEST.md).

The existing APK/Apollo is sufficient for this native transport/producer trace.
Full OBB/installed identity and full archive verification remain separate later
asset/gameplay prerequisites. Do not block current native research on a redundant
whole-archive download or claim the archive is available. Original files stay private.

## Repository context actually reviewed

Fetched live main and its complete nontruncated recursive tree:181 cf2018 blobs.
Fetched mandatory operating/mission/checkpoint/source/assignment/Graphify records
and23 incoming result/finding/handoff documents across CF18-01 through CF18-05,
including prefix-model/bounds/path limits, ACK/auth native traces, SOCKS5 stage,
source receipts, phone09–15, Bingo and address-response findings. Current phone16
refinement and v38/v381 evidence remain in their linked canonical records.
[Current handoff](../../../coordination/CURRENT_HANDOFF.md) is the operating entrypoint.

Important reconciliation, not new hidden progress:

- Mirror receipt G2_status and historical-probes fields describe source acquisition
  time. Their no-post-ACK state is superseded by actual later phone reports; do not
  edit that original receipt into a fabricated new acquisition record.
- The early framing/relay/ACK worker packets are bounded historical inputs. They
  do not reset the completed ACK/auth body corrections or v381 route/sequence match.
- CF05 address response static findings were extended by actual generated-native
  controls; missing-reason correction is canonical, incoming remains unchanged.
- Locally retained unpublished CF02 draft packets are not GitHub submissions. The
  canonical integration records distinguish their provenance and explicit stubs.
- No newly reviewed report establishes an identified application request, accepted
  service response, login, lobby, match or bots. Latest real result remains v381.

## Concrete producer trace advanced

Actual pinned Apollo hash and ELF32LE ARM/Thumb verified before static review.
Original dynsym function GCloud::CTGcp::onDataOutEvent entry0x3a51f4 size1500.
Bounded original instruction review and named-symbol containment establish:

| Stage | Native evidence |
|---|---|
| enqueue Write(AString const&) | entry0x3a45bc,size212; AString assignment call0x39738c at0x3a462a; queue/vector append0x3a4594 at0x3a4640 on object+0x68 |
| route-aware Write overload | entry0x3a4708,size292; separate bounded producer candidate; route construction not fully resolved |
| dequeue | PopOneSendBuffer entry0x3a43ac,size74; begin/end pointers object+0x68/+0x6c; copy helper0x3a3804 at0x3a43ca; erase0x3a436c at0x3a43d4 |
| send event queue consumption | dequeue call0x3a53e0 into object+0x1d8 data-info; AString at+0x1dc |
| data/size handoff | AString::data0x3972f8 at0x3a5450; AString::size0x3972f0 at0x3a5458; pointer saved into R1, size into R2 before send |
| route and handle | route type object+0x200, route storage+0x208, additional argument+0x288, handle+0x58; routed branch permits kinds1/2/4 |
| routed send | actual direct call0x3a5476 ->0x3a91ec; fallback path uses plain send wrapper for other route kinds |

The queue copies/dispatches an already formed application buffer at this examined
boundary. No actual application RPC has been identified there. Do not infer the
originating request format solely from class names, an AString object or route.
AString copy/runtime internals and upstream producer callbacks require continuation;
no full queue native emulation or Android execution performed in this review.

**Next bounded work:** resolve the virtual/interface caller(s) of both CTGcp::Write
overloads, follow AString construction and any application wrapper/transform, then
compare its inverse receiver path. This moves the investigation upstream from the
now-measured sequence boundary. No identical phone test or guessed4013 reply is
requested. Original parser/serializer controls remain useful negative controls.

## Actual verification

Local snapshot is not a git checkout (git status128); no branch/active git edits
inferred. Source byte counts/hashes recalculated; original/native instruction and
symbol inspection executed locally. Route and doctorPASS. Default canonical suite
236 total137 PASS/99 explicit private-input SKIP this activation. No affected
protocol code changed. Prior236-private-PASS remains historical and was not rerun.
This document is descriptive research only, with no raw decompilation or originals.

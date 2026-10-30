# CF18-04 — bounded source/provenance inventory

Date: 2026-10-30 UTC. Base main commit:
`0a5cf7496471f25809bb62242c3365670ce006db`.

State: SUBMITTED; BLOCKED_SOURCE. No active claim remains. Evidence class:
CONNECTED_DRIVE_METADATA + DIRECTORY_LISTING, with explicit search-coverage
limits. No original binary, assembly, probe or raw capture was downloaded,
hashed, executed or disassembled. Q-07 is still PARTIAL; G2 is still blocked.

## Acceptance and scope

Establish exact target identity only from a provenance-backed 2018/v1.0.11.11
package or equivalent independently verified source identity and matching
library/assembly, not a folder label. Identify actual source links without
inventing them. Keep originals private. Treat capped listings as partial and
test search coverage with a known retrievable-file control. Native verification
cannot pass using asset names, metadata size, or the unrelated 9.99 APK.

The required operating documents, current evidence/questions, direct Graphify
dependencies and CF18-01 result were reviewed. Main was unchanged on refresh;
no assignments.json or prior CF18-04 packet existed. The local directory is a
connector-derived source snapshot, not a git checkout. The preceding snapshot
check matched all 28 tracked CF2018 blobs against their Git blob SHAs. Local
git status returned "not a git repository"; no local branch was assumed.

## Observed source locations

These are actual connected Drive metadata/listing results, not source identity
verification:

| Location | Observed result | Limit |
|---|---|---|
| [Unpacked OBB root](https://drive.google.com/drive/folders/1LecNOIlsGybp9V-3JqP6X5JrgU8IXW6Z) | Metadata name "CrossFire Legends 2018 - Unpacked OBB"; direct listing returned assets | Name alone does not prove package version or original-byte identity |
| [assets](https://drive.google.com/drive/folders/1H6DSp-kd5RVtOpv8f749IXEeOzGkDrR_) | Direct listing returned bin, Logoes.mp4 (865719 bytes), Assets.png (431231509 bytes) | Media not fetched; no inferred contents or hash |
| [assets/bin](https://drive.google.com/drive/folders/1hQrLIRYqzccWteaoctlaZDnzv8HJEzZd) | Direct listing returned Data | Parent relationship also returned by metadata |
| [assets/bin/Data](https://drive.google.com/drive/folders/1vzsxc8kK09cbhso8vCfOD_6-cud_bTjW) | Metadata parent is bin; one bounded direct listing returned exactly 100 items, including level3078/3079/3075 | Listing hits requested cap; not a complete manifest and not proof no Managed/library files exist |
| [Excluded 9.99 APK](https://drive.google.com/file/d/1GrWS-oaGqfYeXegIfpntODVyDsmr9UBR/view?usp=drivesdk) | Metadata lookup succeeded: CrossFire_Mobile_Offline_9.99_.apk, application/vnd.android.package-archive, 1062994494 bytes | Excluded as target evidence; not downloaded or substituted |

Metadata queries requested MD5/SHA-256 fields but returned no checksum values.
No checksum is claimed for any listed source.

## Search coverage control: absence is not established

All queries were metadata-only (`best_effort_fetch=false`), with no raw-file
fetch:

1. Raw filter for names containing apollo, CF2018, CrossFire or 2018, or exactly
   Assembly-CSharp.dll / Original.xapk, returned only the unpacked-OBB folder
   (topn=100).
2. Data-parent folder-only filter returned no results.
3. Data-parent exact names Assembly-CSharp.dll, libapollo.so, mainData and
   globalgamemanagers returned no results.
4. Keyword CF2018 returned no results for the historical probes/reports.
5. **Positive control:** exact-name filter for
   CrossFire_Mobile_Offline_9.99_.apk returned no results, even though direct
   metadata access to the known APK ID succeeded in the same inventory.

Therefore search results did not cover even this known retrievable file.
The reason is undetermined; do not invent an indexing, permission or provider
diagnosis. Empty search responses and the 100-item Data sample cannot establish
that target files are absent from connected Drive. No exhaustive search or
complete Drive inventory is claimed. No repeat scan of all game assets was done.

## Gate-specific missing evidence

| Required evidence | Current availability to this task | Impact |
|---|---|---|
| Exact 2018 v1.0.11.11 com.tencent.tmgp.cfmnac original package identity and original-code baseline | Not verified; folder label and historical summaries only | G0 identity/provenance cannot be promoted |
| Original libapollo.so with package link, actual hash and ISA | Not located/retrieved in this bounded inventory | CF18-01/02 cannot independently trace RX framing or ACK/session/key-mode branches |
| Original 2018 Assembly-CSharp.dll and matching OBB identity | Not verified/retrieved | No managed startup/gameplay claims |
| Historical v0.1-v0.8 source packages and raw reports, including CF2018_TGCP_v05_AB_Report.txt and CF2018_TGCP_v07_Audit.txt | Not obtained; canonical summaries are available, originals are not | Historical relay EOF cause, original packet construction and precise native audit cannot be revalidated from this packet |
| v0.8 phone result or later real post-ACK client traffic | Not obtained | G2 does not advance |

"Not obtained" describes this task's evidence, not a claim that the user's
on-phone files or unreturned Drive items do not exist. Public repo code
frame_gate.py is not the historical full probe package.

## Actual verification

From the verified local snapshot's cf2018 directory:

```text
python tools/knowledge.py route 'drive libapollo native sources'
  Routes: [('sources', 3)]
python tools/knowledge.py doctor
  PASS: required files, links, vault and graph
python -m unittest discover -s tests -v
  Ran 10 tests; OK
```

These are repository checks, not native/game/phone tests. This packet is
descriptive metadata only and needs no implementation tests. No proprietary
data, media, private tokens, raw captures or downloaded artifacts are published.

## Integration and next falsifiable action

Coordinator may link this packet into the canonical source manifest/questions
and record the search positive-control failure. Keep Q-07 PARTIAL, exact source
identity unverified and G2 blocked. Do not update canonical hashes from missing
metadata fields or treat the Data listing as complete.

Needed next input is an actual authorized private link/location for the original
2018 package/libapollo.so and historical probe/report bundle, or a source-lane
assignment that supplies a different verified locator. Verify metadata first,
retrieve only required originals privately, calculate actual hashes and inspect
package version/ISA before handing any address claims to CF18-01/02. No target
library URL can be supplied from this inventory because none was observed.
Stop on future unchanged missing-source activations; no repeated full asset
inventory or filler status commits.

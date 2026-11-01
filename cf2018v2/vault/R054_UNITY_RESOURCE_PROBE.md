# R054 — Unity Resources packaging hypothesis and bounded asset-surface probe

Date: 2026-11-01. Evidence class: SOURCE-DERIVED UNITY PLATFORM FORMAT + PUBLIC CI SYNTHETIC TESTS + EXISTING VERIFIED PRIVATE-SOURCE PROVENANCE. **No new original-game asset decode, map ID, authentication, or Android gameplay test.**

## Why filename search did not settle R053

The original game `GameDefManager.ParseGlobalGameDef` calls Unity `Resources.Load` using `Config/GlobalDef/GlobalGameDef` and `Config/GlobalDef/GlobalMapDef` (see R051). Unity build output serializes resources into player resource data or archives. No standalone `GlobalGameDef` filename need exist in Google Drive. Thus a negative filename search is inconclusive and should never be classified as evidence that training modes/assets are absent. In modern conventional player builds the resource file is named `resources.assets`, but this original Unity 4.6-era Android title can have a different packaging layout; do not blindly assume its contents or an `Assets.png` rename. Unity documents TextAsset serialization and binary `.bytes` loading.

Original owner-connected Drive locators observed in R053: APK-extracted `app/assets/bin/Data/mainData`, `sharedassets0.assets.split0/1`, `Resources/unity_builtin_extra`, and OBB `assets/bin/Data/level...`. The 431,231,509-byte OBB `Assets.png` is only a **file-name / size** observation; its signature and contents remain unexamined. No original assets were modified or published.

## Reproducible source-only probe

Tool: [`cf2018/tools/r054_asset_surface_probe.py`](../../cf2018/tools/r054_asset_surface_probe.py). Tests: [`cf2018/tests/test_r054_asset_surface_probe.py`](../../cf2018/tests/test_r054_asset_surface_probe.py).

- Inspect explicitly passed local files **read-only**, no network listener, no original file output or binary upload.
- Identify PNG/ZIP/UnityFS/UnityRaw/UnityWeb/UnityArchive, ELF, MZ or *candidate* Unity serialized-file headers by actual bytes rather than extensions.
- Scan at most 8 MiB/file by default for known literal markers and print only **offsets**, format hints, sizes, scan completeness; no raw game payload.
- Correctly mark incomplete scans; absence of direct literal bytes does NOT prove an actual resource is absent, as data may be serialized, packed, transformed, or compressed. A hit is not a validated resource definition either.
- Up to 16 explicit paths per run, 1–256 MiB configurable per-file prefix cap. No unbounded directory tree scans or payload dumps.

Usage from a repository checkout, with the owner's actual existing local paths substituted; do **not** invent paths or run this against an unverified/newer CFMobile build:

```sh
python cf2018/tools/r054_asset_surface_probe.py "<actual-private-mainData-path>" "<actual-private-assets-file-path>" --max-scan-mib 8
```

## Tests actually completed

- Source-only implementation committed as `61fcdff60bf72627cc095b9bab4f8a6ac9fe5c75`.
- Ten independent synthetic unit tests added in `0b37a2b1df8c23c14f3baaa2ea01b29d43c85bd5`, checking valid/fake PNG and Unity signatures, ZIP, valid vs malformed Unity header, cross-chunk matches, scan limits and read-only preservation.
- [GitHub Actions run 41309943658](https://github.com/despairarc000/temp/actions/runs/41309943658) **completed SUCCESS**, with `Validate required files, links, Vault and curated edges`, `Run knowledge tests`, ICM route and graph steps all **SUCCESS**. This run is PUBLIC CI (without private original binaries). Do not count the 10 synthetic tests as authenticated-client or asset-resource decoding.

## Next discriminating action

When a runtime capable of reading the privately connected bytes is available, run the bounded probe against *actual* resource-bearing assets to identify container signatures, then use a version-compatible Unity serialized object parser / archive reader to extract the names and data of relevant `TextAsset`/ResourceManager entries. Require a verified resource path, actual `mapId`, game-mode/tag and builder registration before claiming R055 map→`AITrainGameBuilder` linkage. Correlate the match-start event only after this; no Android phone test yet.

**R054 result:** a targeted, CI-tested forensic instrument and a corrected resource-location hypothesis; **the critical original map/config resource remains unidentified**. Independent network handshake/login lane remains unsolved.

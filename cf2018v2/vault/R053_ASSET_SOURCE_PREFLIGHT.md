# R053 — Original Unity source recheck and Drive asset-source preflight

Date: 2026-11-01. Classification: EXACT_ORIGINAL_MANAGED_STATIC + LOCAL_OFFLINE_TEST + DRIVE_FOLDER_METADATA + PARTIAL_BYTE_HEADER; **NOT** a phone/gameplay test.

## Repeatability / confirmed inputs

- Original game target: CrossFire Legends 2018 v1.0.11.11 Mono `com.tencent.tmgp.cfmnac`.
- Read-only original Unity assembly was materialized privately from connected Drive at `CrossFire Legends 2018 - Unpacked OBB/app/assets/bin/Data/Managed/Assembly-CSharp.dll`, 13,423,104 bytes. SHA-256 matches pinned `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9`. Original bytes **not** added to repository.
- Independent rerun using existing owner-provided source-only combined R051/R052 auditors: R051 **36/36** original method-call/literal pins PASS; R052 **21/21** original TypeDef/call pins PASS; **57/57** combined.
- `CF18_MANAGED_DLL=<private original DLL> python -m unittest discover -v` in extracted R051/R052 source-only kit: **16 tests, 16 PASS, zero skip**. Without that variable, the optional original gates skip two tests. These are static and offline test results, not match startup.

## Asset discovery (metadata only unless indicated)

- Connected Drive verified source root: https://drive.google.com/drive/folders/1LecNOIlsGybp9V-3JqP6X5JrgU8IXW6Z ; APK `com.tencent.tmgp.cfmnac.apk` is present at 30,884,905 bytes.
- APK-extracted `app/assets/bin/Data` includes `mainData` (2,112,488 B), `sharedassets0.assets.split0/1`, `Resources` (direct listing contained `unity_builtin_extra`), and `Managed` including the original DLL.
- The `mainData` file's first bytes indicate Unity serialized file version `4.6.9p1`; a bounded raw-literal search found no direct ASCII occurrence of `GlobalGameDef`, `GlobalMapDef`, `Config/GlobalDef`, or `AITrainGame` in this one file. This is **not** a valid negative on the actual Unity Resource asset table.
- The separate unpacked OBB `assets/bin/Data` directory has numerous `level...` serialized objects, and the OBB root contains a file named `Assets.png` reported by Drive as 431,231,509 bytes. No successful byte-level analysis of that large file; don't assume it is PNG, a bundle, encrypted, or holds configs.
- Exact-name Drive searches for `GlobalGameDef` and `GlobalMapDef` surfaced no standalone files; this does **not** imply the definitions are absent. Listings of large OBB Data folder are capped/incomplete.
- An attempt to analyze the 431 MB candidate in the container failed after materialization; no conclusion about its contents follows. The whole original XAPK has **not** been independently located/hashed in Drive in this run.

## Open gates / next falsifiable step

1. Locate and decode only relevant Unity Resource/asset bundle table entries for `Config/GlobalDef/GlobalGameDef` and `Config/GlobalDef/GlobalMapDef`, retaining exact source provenance and negative controls. Start with indexed/resource-bearing files, not a blind 3000-file scrape or full asset upload.
2. Prove at least one real map ID → mode/tag → registered `AITrainGameBuilder.CreateGame` mapping, and the triggering call to inherited `StoryGame.StartMatch`.
3. Only after these are source-backed, build a reversible manual phone test with predeclared pass/fail labels. Never equate CIL pin success with bot/gameplay success.

**Conclusion:** exact original CIL evidence reproducibly survives this independent run; R053 did not establish a valid map/builder configuration or playable training game. Network login/ACK lane remains independent and unresolved.

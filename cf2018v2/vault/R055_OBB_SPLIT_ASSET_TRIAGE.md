# R055 — OBB resource priority and validated virtual split-file scanner

Date: 2026-11-02. Evidence classes: **OWNER-SUPPLIED APK XML**, **HISTORICAL UNITY DOCUMENTATION**, **DIRECT CONNECTED DRIVE FILE METADATA**, and **PUBLIC CI SOURCE-FREE TESTS**. No original game asset byte-level decode or Android runtime test took place.

## New asset-location decision

The original APK-extracted `assets/bin/Data/settings.xml` contains `<bool name="useObb">True</bool>`. In Unity's older Split Application Binary scheme, the APK includes scripts/binaries and the first scene; remaining scenes, resources and streaming assets live in the OBB. The 5.4-era Unity manual explicitly describes this rule:
- https://docs.unity.cn/540/Documentation/Manual/android-OBBsupport.html
- https://docs.unity.cn/2018.1/Documentation/Manual/android-OBBsupport.html

This moves **OBB assets ahead of APK-only data** in the research queue for `Config/GlobalDef/GlobalGameDef` and `Config/GlobalDef/GlobalMapDef`. It does **not** prove those specific resources exist in the OBB or that the phone mounted a matching OBB. Historical docs are format context, not recovered CF2018 game config.

Unity's own content tooling describes `levelN` scene serialization, `sharedassetsN.assets` dependencies, a conventional `resources.assets` store for `Resources.Load`, and a `ResourceManager` index in global settings. It also warns output layouts change by version and some Android files are split into 1-MiB fragments; tools that don't reassemble the logical file may fail:
- https://github.com/Unity-Technologies/UnityDataTools/blob/main/Documentation/playerbuild-format.md
- https://github.com/Unity-Technologies/UnityDataTools/blob/main/Documentation/unity-content-format.md

## Direct Drive metadata reproduced (NOT decoded content)

Owner folder: https://drive.google.com/drive/folders/1LecNOIlsGybp9V-3JqP6X5JrgU8IXW6Z

- APK-side `app/assets/bin/Data/sharedassets0.assets.split0`: **1,048,576 bytes**; `.split1`: **438,372 bytes**. Logical size **1,486,948 bytes**, if these represent one contiguous Unity file.
- OBB-side `assets/bin/Data/level3.split0` through `.split3`: **1,048,576 bytes each**; `.split4`: **389,768 bytes**. Logical size **4,584,072 bytes**.
- The OBB `assets/bin/Data` folder listing exposes thousands of `level...` entries; listing 1,000 names returned only a bounded slice and is **not a complete asset index**.
- Exact-name or filename searches cannot prove `GlobalGameDef` / `GlobalMapDef` absent. The 431-MB Drive item `Assets.png` is still unclassified by file signature/content.

## R055 implementation and tests

- [Virtual split inspector](../../cf2018/tools/r055_unity_split_probe.py) takes one explicit local `.split0` path and discovers only its numbered sibling parts.
- Without creating a concatenated temporary file, it treats the part stream as a single logical binary, checks contiguous indices and nonempty parts, passes the combined size to R054's existing header classifier, and searches bounded prefix bytes for resource-name hints including across part boundaries.
- Outputs names, sizes, format hint and token **offsets only**. Default maximum: 8 MiB of bytes scanned (up to 256 MiB if explicitly requested), up to 64 split parts. No networking, original file rewrite, raw payload reporting, game patching or upload.
- [10 synthetic tests](../../cf2018/tests/test_r055_unity_split_probe.py) cover split-boundary PNG and Unity header recognition, cross-part token search, absent-token interpretation, noncanonical indices, missing segments, zero-length segments, bounded scanning, rejection of nonsplit input and no-modification controls.
- **Public GitHub Actions** [run 41339693524](https://github.com/despairarc000/temp/actions/runs/41339693524) **completed SUCCESS**, exercising the repository-wide knowledge doctor, tests, ICM and graph. This confirms only source-free regressions, **not original Unity resource parsing**.

## Reproducibility (only on owner-accessible private files)

From the checked-out public repo, point at the actual path where the owner has downloaded the **original matching** split family, not a guessed Android path:

```sh
python cf2018/tools/r055_unity_split_probe.py "/absolute/path/to/original/level3.split0" --max-scan-mib 8
```

The adjacent `.split1`, etc. files must exist beside `.split0`. The source never writes merged game bytes to the public repo.

## Remaining blocker and next falsifiable step

1. Run R055 against **actual** OBB `level3.split0` and APK `sharedassets0.assets.split0` and classify their logical file headers. No original bytes were executable from this session's container; direct connected Drive only provided metadata here.
2. Find the original OBB's **resource index** and the serialized object entries corresponding to both exact `Resources.Load` paths, using an appropriate Unity-version-aware parser rather than interpreting name offsets as complete proof.
3. Read an actual map ID, mode/tag and builder; establish `AITrainGameBuilder` and subsequent `StartMatch` trigger.
4. Only then consider a bounded, reversible phone test, distinguishing failed load, failed world init, local pawn spawn, bot spawn, playable offline match.

**Conclusion:** R055 is a validated tooling/asset-routing improvement in the **offline-gameplay restoration research track**, not a switch to a playable build, not verified login, and not a solved map-to-game-mode dependency.

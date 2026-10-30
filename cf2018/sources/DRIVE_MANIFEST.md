# DespairArc Drive — authoritative file locator (NOT game binaries)

**Verified through the connected Google Drive account (2026-10-30):**

| Source | Drive link | Verified observations |
|---|---|---|
| 2018 unpacked OBB root | [CrossFire Legends 2018 - Unpacked OBB](https://drive.google.com/drive/folders/1LecNOIlsGybp9V-3JqP6X5JrgU8IXW6Z) | Folder exists in connected Drive. |
| Root OBB assets | [assets](https://drive.google.com/drive/folders/1H6DSp-kd5RVtOpv8f749IXEeOzGkDrR_) | Contains `bin/`, `Logoes.mp4` and `Assets.png` (approx. 431 MB). |
| Nested bin | [assets/bin](https://drive.google.com/drive/folders/1hQrLIRYqzccWteaoctlaZDnzv8HJEzZd) | Folder exists. |
| Unpacked Unity Data | [assets/bin/Data](https://drive.google.com/drive/folders/1vzsxc8kK09cbhso8vCfOD_6-cud_bTjW) | Contains many `level...` asset files; connector listing of first 100 is partial, not a full manifest. |
| Other uploaded Android package | [CrossFire_Mobile_Offline_9.99_.apk](https://drive.google.com/file/d/1GrWS-oaGqfYeXegIfpntODVyDsmr9UBR/view?usp=drivesdk) | ~1.06 GB; **unverified relevance to the target 2018 client; do not substitute**. |

Historical on-phone files described by capture work: `Original.xapk` (~732 MiB), signed-only control, original OBB, `Assembly-CSharp.dll` (2018 Mono), `libapollo.so`. **These are NOT verified as residing in Drive above.** Do not invent URLs. The connected Drive folder currently confirms unpacked OBB assets, not all game binaries.

## Codex retrieval
To inspect these files, use the **connected DespairArc Google Drive tool with authorized access**, traverse the folder links, and fetch only required originals. A link alone is not a mount nor permission. If Codex lacks Drive access, report precisely which source is unavailable; do not pretend it was read or silently replace with the newer IL2CPP `cfmobileoffline` binaries.

## Security/legal
This GitHub repository is PUBLIC. NEVER upload originals, decrypted assemblies, OBB media, dumps, license-restricted data or private auth/session tokens here. Instead commit descriptive findings, hashes, original code written for the emulator, tests with independent synthetic fixtures and source pointers. Maintain hash/provenance per file in a private manifest, avoid publishing device secrets. Use legitimate archival/research access only.

## Coordinator-reviewed retrieval limits — 2026-10-30

[CF18-04 inventory](../coordination/incoming/CF18-04/RESULT.md) revalidated the
folder hierarchy using metadata and bounded direct listings. Data returned the
100-item cap; no complete inventory is established. Exact-name search omitted
the known 9.99 APK even though direct metadata access succeeded. Empty searches
cannot prove that a target library, assembly or report is absent from Drive.
No requested checksum fields were returned; no source was downloaded or hashed.
Exact 2018 package identity, libapollo.so, Assembly-CSharp.dll and historical
probe/report availability remain unverified. Resume only with new evidence or a
verified private source locator, rather than repeatedly listing all assets.

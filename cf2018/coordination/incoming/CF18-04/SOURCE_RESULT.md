# CF18-04 — recovered mirror source receipt and offline verifier

Base main: `56db53d81326810d5bea342b11ea4e07dc351e01`.
Date: 2026-10-30 UTC. SUBMITTED; no active claim remains.
Evidence: MIRROR_SOURCE_PROVENANCE + PRIVATE_LOCAL_HASH_VERIFICATION +
INTERNAL_V1_SIGNATURE_VERIFICATION. Acceptance defined before implementation in
[SOURCE_ACCEPTANCE](SOURCE_ACCEPTANCE.md). Machine-readable descriptive output:
[SOURCE_RECEIPT.json](SOURCE_RECEIPT.json).

**New disposition:** hash-specific native analysis is source-supported for this
recovered mirror. Equality with the historical phone build remains UNVERIFIED;
G0 is incomplete overall and G2 remains BLOCKED. This does not resolve Q-07's
connected-Drive inventory question into a claim that native files exist there.

## What changed since the initial inventory

The [initial Drive result](RESULT.md) accurately recorded an incomplete bounded
inventory, failed search positive control and missing native source at that time.
Afterward the user explicitly requested internet APK search. The APK/member
recovery was documented in [CF18-01](../CF18-01/NATIVE_RX_RESULT.md), commit
`fefd0dc224851fefc2b74a51fc95e0fa0090e9a2`; [CF18-02](../CF18-02/RESULT.md)
subsequently used its pinned library in commit
`56db53d81326810d5bea342b11ea4e07dc351e01`.

This source-lane activation independently rechecked package/version, actual
hashes, ISA, signature links and extracted copies, and added an original reusable
offline verifier. It did not download another package, repeat Drive scans or
claim new receiver instructions. There is no unresolved prior source-lane claim.
All nine startup documents, current assignments, relevant Graphify edges, startup
research and incoming results were refreshed from live main. The local snapshot
matched all 50 tracked CF2018 Git blob hashes before editing; git status returned
128 because this directory is not a git checkout. No branch/auth was assumed.

## Exact observed source and bounded acquisition

Source page:
[APKPure v1.0.11.11 package listing](https://apkpure.net/crossfire-legends-action/com.tencent.tmgp.cfmnac/download).
Observed download entrypoint:
[APKPure XAPK](https://d.apkpure.net/b/XAPK/com.tencent.tmgp.cfmnac?version=latest).
The endpoint is mutable; the file hashes below, not the word "latest", identify
this analysis source. No signed redirect query/token is published.

The prior local acquisition receipt records validated HTTP 206 ranges against
archive size 768008878. ZIP central-directory metadata identified four members;
only the APK (stored method 0, 30884905 bytes, CRC32 974cadd8) and 4776-byte
XAPK manifest (CRC32 1ca8ef8f) were retrieved. The 737048867-byte OBB and icon
were not retrieved. Full XAPK SHA-256 is unknown, not reconstructed from member
hashes. No current URL availability or unchanged future response is guaranteed.

This activation reread the embedded AndroidManifest.xml using Androguard 4.1.4:
package **com.tencent.tmgp.cfmnac**, versionName **1.0.11.11**, versionCode **11**;
valid APK true, v1 signed true, v2 signed false. The separately retrieved XAPK
manifest independently gives the same identity; its calculated SHA-256 is
`05a9bab976ba63cd34aa104c96a6860089e3eb2efa23d18ff1b46e36541127bc`.
libmono.so and managed assemblies occur inside this APK. No IL2CPP/9.99 source
was substituted and no original was installed, executed or modified.

| Artifact | Recalculated size / SHA-256 |
|---|---|
| APK | 30884905; `33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9` |
| lib/armeabi-v7a/libapollo.so | 5243704; `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8` |
| assets/bin/Data/Managed/Assembly-CSharp.dll | 13423104; `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9` |
| assets/bin/Data/Managed/Assembly-CSharp-firstpass.dll | 317440; `4ac2b58a02cc1d3ad1e345d9b21dd78c758b0077c19354862792d25bcaa8ba60` |

Both the embedded entries and the three extracted private copies have the stated
hashes. Apollo's ELF header is class 32, little-endian, ARM machine 40, DYN type
3, version 1, EABI5 flags 83886080. The native lane's Thumb addresses apply only
to that fingerprint; ISA/native addresses must not be inferred for other APKs.

## Actual signature integrity checks and their limit

Original [verifier](verify_private_source.py), stdlib plus OpenSSL 3.5.7:

1. Requires the pinned APK size and SHA-256 before ZIP/member interpretation.
2. Checks APK member CRCs and rejects duplicate ZIP names.
3. Verifies CERT.RSA CMS signature over CERT.SF with OpenSSL `cms -verify
   -noverify -binary`.
4. Matches the signed CERT.SF SHA1-Digest-Manifest to the complete MANIFEST.MF.
5. Verifies all **1212** manifest-listed payload SHA-1 digests and requires exact
   coverage of every non-directory payload outside the three signature files.
6. Requires one signing certificate and its pinned SHA-256; verifies selected
   member SHA-256 values, Apollo ELF identity and optional extracted library.

Calculated certificate SHA-256:
`dbfc84490cc286cb3e6cfa243c8c175dab6f33862997e6b45a2973aa41a262b4`.
Calculated certificate SHA-1:
`2d1305191dfaeb11ca7fe6dc28ccabd0fc3eb8cf`, consistent with the observed listing.
The certificate SHA-1 was independently reread using cryptography's PKCS7 parser.

`-noverify` deliberately does not validate the certificate trust chain. These are
internal cryptographic integrity and fingerprint-continuity observations, not an
independent Tencent distribution attestation, malware verdict or proof that the
mirror equals the phone build. The outer XAPK manifest is not covered by this
APK signature check. Different hashes reported by another mirror in CF18-01's
receipt remain separate unverified artifacts; a matching version string is not
byte equality.

## Reusable original implementation and controls

The tool never fetches anything, starts a listener, executes game code, modifies
an original or uploads files. Direct invocation without --apk prints its inactive
state. Explicit local paths are required. Output is descriptive metadata only;
no original bytes, extracted assets, keys, session data or raw error contents are
emitted. Temporary CMS inputs/certificate data stay in this lane's ignored
private directory and are removed afterward.

The CLI intentionally uses the known APK hash as its identity anchor. Embedded
Android identity parsing was performed separately above; the CLI does not
pretend to independently parse binary AndroidManifest.xml or verify a new build.
An unexpected file fails the pin check. To investigate a genuinely different
build, produce a separate provenance receipt rather than loosening these pins.
The digest helper is not a generic Android install/signature-policy validator.

[Tests](test_verify_private_source.py) include twelve independent synthetic
controls and two explicitly selected private-source controls. Synthetic changes
include altered payload/manifest, unsigned extras, missing entries, duplicate
ZIP names/manifest sections/attributes, folded names, ISA changes and wrong
APK size/hash. A synthetic archive whose digest links pass still fails actual
OpenSSL CMS verification: digest syntax alone is not a signature success.

The two private-source tests execute actual CMS/all-entry checks and reject an
extracted-library mismatch. Without CF18_APK_SOURCE those two tests explicitly
skip. Missing OpenSSL skips only the optional synthetic CMS control; an explicit
private-source verification reports CMS unrun/fails rather than inventing a pass.

Actual commands from cf2018:

```text
python tools/knowledge.py route 'source provenance private APK v1.0.11.11 libapollo Mono signature verification'
  Routes: [('startup', 2), ('sources', 1)]
python tools/knowledge.py doctor
  PASS: required files, links, vault and graph
python -m unittest discover -s tests -v
  Ran 52 tests; OK
python coordination/incoming/CF18-04/verify_private_source.py --apk \
  coordination/incoming/CF18-04/private/com.tencent.tmgp.cfmnac.apk --library \
  coordination/incoming/CF18-04/private/armeabi-v7a-libapollo.so
  Pinned APK/member/ELF/CMS checks PASS; signed_entries=1212;
  certificate_trust_chain=NOT_VALIDATED
CF18_APK_SOURCE=coordination/incoming/CF18-04/private/com.tencent.tmgp.cfmnac.apk \
  python -m unittest discover -s coordination/incoming/CF18-04 -v
  Ran 14 tests; OK; no skips
python coordination/incoming/CF18-04/verify_private_source.py
  Inactive: supply --apk for explicit offline private-source verification.
```

## Remaining source gates and coordinator integration

| Evidence | Current status / precise limit |
|---|---|
| Mirror APK identity, selected native/managed members | Privately available on this runner; hashes/identity/integrity revalidated |
| Same files in connected Drive | Not verified; prior partial inventory/search control limits remain valid; no repeated scan |
| Historical phone Original.xapk / APK or Apollo hash | Not supplied; byte equality and runtime selected receive path unverified |
| Full XAPK and OBB | Not acquired/hashed; the linked unpacked OBB has not been proven byte-matching this package |
| Historical v0.1-v0.8 relay/probe sources and original phone reports | Not obtained; frame_gate.py is not a substitute; EOF attribution still unknown |
| New authentic post-ACK client packet | Not obtained; G2 cannot advance |

CF18-00 should review the receipt, rerun the private verifier where the pinned
source exists, and update canonical source manifest, CHECKPOINT/EVIDENCE/questions,
Graphify/ICM and assignments. A blanket "no verified library available" blocker
is obsolete for this hash-specific mirror analysis, but the remaining source,
runtime and G2 gates must stay explicit. CF18-01/02 packets are ready for such
coordinator review; their native conclusions are not promoted by source tests
alone. This lane does not edit canonical files or another lane.

The private source path and analysis dependencies are runner-local. Later workers
must first verify disk/access or reacquire from the observed locator with fresh
metadata and exact hashes; a schedule is not shared storage. Once this receipt
is submitted, stop unchanged source activations quietly until phone-source
identity, historical sources or another concrete provenance question arrives.

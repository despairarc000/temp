# Hash-scoped 2018 mirror source

Coordinator reviewed base `c52243228e8d2d38dd6b4c1d85f464d9f94461f8`.
The user's explicit internet-search instruction authorized the mirror retrieval.
[CF18-04 receipt](../coordination/incoming/CF18-04/SOURCE_RESULT.md), source commit
`c52243228e8d2d38dd6b4c1d85f464d9f94461f8`, is independently rechecked here.
Canonical descriptive metadata: [MIRROR_RECEIPT.json](MIRROR_RECEIPT.json).

Observed [APKPure listing](https://apkpure.net/crossfire-legends-action/com.tencent.tmgp.cfmnac/download)
and [download entrypoint](https://d.apkpure.net/b/XAPK/com.tencent.tmgp.cfmnac?version=latest).
The endpoint is mutable. Only the following bytes are the reviewed source:

| Artifact | Bytes / SHA-256 |
|---|---|
| APK member | 30884905; `33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9` |
| lib/armeabi-v7a/libapollo.so | 5243704; `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8` |
| Assembly-CSharp.dll | 13423104; `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9` |
| Assembly-CSharp-firstpass.dll | 317440; `4ac2b58a02cc1d3ad1e345d9b21dd78c758b0077c19354862792d25bcaa8ba60` |

Embedded Android identity and the separately obtained XAPK manifest agree:
`com.tencent.tmgp.cfmnac`, versionName `1.0.11.11`, versionCode `11`.
Managed assemblies and libmono.so are present. Apollo is ELF32 little-endian ARM
DYN, EABI5; the reviewed native functions are Thumb. The extracted private
library/assemblies match these APK entries. No IL2CPP or 9.99 substitute was used.

Actual coordinator checks: APK CRCs, pinned member hashes/ISA, OpenSSL CMS over
CERT.SF, the signed complete-manifest digest and all 1212 signed payload digests
passed. Certificate SHA-256 is
`dbfc84490cc286cb3e6cfa243c8c175dab6f33862997e6b45a2973aa41a262b4`;
SHA-1 `2d1305191dfaeb11ca7fe6dc28ccabd0fc3eb8cf` matches the observed listing.
CMS uses `-noverify`: internal integrity and certificate continuity are checked;
certificate trust-chain/distribution attestation is not established.

## Offline reproduction and availability

[Original canonical verifier](../tools/verify_private_source.py) opens explicit
local paths only and prints metadata. No arguments prints its inactive state.
It pins this known APK before ZIP interpretation; the embedded Android manifest
parse was performed separately in the source receipt. Do not loosen the pin to
label a different build as verified.

```text
python tools/verify_private_source.py --apk <private-APK> --library <private-Apollo>
CF18_APK_SOURCE=<private-APK> python -m unittest discover -s tests -v
```

On this runner the originals are under coordination/incoming/CF18-04/private/;
that directory is ignored and is not uploaded. Future runs must check actual
availability/hash or reacquire through an authorized source with fresh metadata.
Scheduled workers do not imply a shared disk. The public repository contains
only descriptive metadata, original verifier/parser code and synthetic fixtures.

## Remaining provenance gaps

The full 768008878-byte XAPK and its 737048867-byte OBB member were not downloaded
or hashed. Only APK and manifest ranges were retrieved. The linked unpacked
[Drive OBB](DRIVE_MANIFEST.md) is not byte-proven to match this mirror.
The phone Original.xapk/APK/Apollo hash is not available for equality comparison.
Historical v0.1-v0.8 scripts/reports remain missing. Other same-version mirrors
may have different bytes. G0 is partial; G2 is BLOCKED.

This source makes hash-specific native analysis possible. It does not resolve
runtime path selection, historical EOF attribution, accepted ACK or gameplay.
See [receiver trace](../knowledge-system/vault/research/ACK_RECEIVER.md) and
[current assignments](../coordination/assignments.json).

# Approved scoped-trust APK preparation — offline result

2026-11-03 UTC. The owner approved the [R120 proposal](ACCOUNT_HTTPS_TRUST_AND_SCOPED_CONTROL.md) with “Go ahead”. Scope is private preparation and offline checks, not installation or phone execution. The later owner question clarifies the desired delivery is a preparation/patch script using the owner's existing APK, not a replacement XAPK download.

**OFFLINE_BUILD_AND_PAYLOAD_VERIFICATION:** two private APK copies were actually generated from exact original APK SHA256 33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9. Originals unchanged.

| Property | Signature-only control | Scoped-trust candidate |
|---|---|---|
| APK bytes | 30,952,507 | 31,190,221 |
| Original non-signature payload entries | All1,212 identical | All1,210 outside two permitted metadata files identical |
| Original payload changes | None | AndroidManifest.xml and resources.arsc only |
| Added payload files | None | Two trust XML/public-CA resources |
| Protected DLL SHA256 | Original174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9 | Same original hash |
| Signatures | v1+v2 verified | v1+v2 verified, same signer |
| ZIP alignment |4-byte check PASS |4-byte check PASS |
| Android execution | NOT PERFORMED | NOT PERFORMED |

[Machine-readable sanitized receipt](../../../experiments/receipts/scoped_trust_offline_20261103.json) includes artifact hashes. Private APKs, certificates containing original endpoint names, signing/CA/server private keys and original files have not been uploaded to the public repository. No account/provider traffic, game launch, phone install/uninstall or system trust changes occurred.

**Implementation:** [Binary-resource utility](../../../experiments/scoped_trust_resources.py) appends two isolated custom resource types, rather than round-tripping game resources through a decompiler/compiler. It preserves original resource string indices, style data and every existing type/specification/configuration chunk byte-for-byte. Independent Androguard parsing confirms all2,999 original resource IDs/configuration sets remain and exactly two IDs are added. New file references resolve correctly; Android aapt2 dumps both resource tables successfully. Custom-type acceptance on the actual Android runtime remains untested.

Manifest XML was independently parsed before/after. After removing only the added android:networkSecurityConfig attribute, canonical XML is identical. TargetSdk26, package identity, debuggable=false, component/permission metadata and all original binary resource payloads remain unchanged. Existing game code, Dex, DLL/native libraries and assets are copied unchanged into both signed outputs. Whole ZIP bytes necessarily differ due to repacking/signing; no byte-identical whole APK claim.

Trust XML keeps system trust as the base and uses only a dedicated locally generated CA for seven exact original SDK account/config hostnames, subdomains disabled. No Google/Facebook hostname configuration or blanket user-CA trust added. New roots, signing identity and two TLS leaf certificates were generated privately, not extracted from the game. Google signing-certificate registration may still reject the re-signed app; this preparation does not solve that separate gate.

**Actual checks:**8 source-free utility tests PASS, covering Unicode/long string and style preservation, malformed chunk refusal, wrong package/XML input, existing trust override refusal, invalid/unbounded host scopes and unique manifest attribute insertion. Complete original-payload assertions ran after signing both APKs. apksigner verifies v1/v2 on both with the same signer; zipalign and aapt2 parse checks pass. OpenSSL offline certificate-chain verification accepts the correct CA and rejects the same-host wrong-CA leaf. That is an offline cryptographic control, not Android TLS acceptance or a running fake server.

Tool provenance: official Android build-tools35 archive from dl.google.com; downloaded archive matched its SHA1 in official repository2-3.xml. Archive SHA256 and signer fingerprint are in the receipt. Tool artifacts are private dependencies.

**Limits / next:** Android installation, integrity-safe launch, scoped TLS acceptance/wrong-CA rejection on the phone, account callback/session, provider compatibility and gameplay remain UNKNOWN. The existing private build driver depends on workspace analysis libraries/Java tools and is not yet a standalone Termux deliverable. A phone-side preparation package would need packaging and offline checks before instructions are provided. Do not substitute a proprietary XAPK download or ask the owner to uninstall/replace their current installation yet. An eventual installation would require a separate owner decision.

Current diary is7,631 bytes, near its8KiB limit. No new entry was appended and no archive/rotation was performed; archival authorization is needed before another entry. No new R-entry ID is claimed. Knowledge-doctor historical snapshot omissions remain; new document links are checked separately.

# CF18-04 recovered-source acceptance before implementation

Base main: 56db53d81326810d5bea342b11ea4e07dc351e01. Owner CF18-04.
Use the newly authorized/recovered internet mirror's private local APK, never
substitute the excluded 9.99 APK or IL2CPP project. Preserve the earlier Drive
inventory as historical evidence; do not repeat its unchanged missing searches.

Acceptance: independently recalculate pinned APK/member hashes, read embedded
package/version and native ELF identity, reproduce internal v1 CMS/signature-file/
manifest/all-entry digest checks, and publish descriptive receipts plus original
verification code only. Keep mirror provenance distinct from Tencent distribution
attestation, full-XAPK/OBB checks, and equality with the historical phone build.

Verifier must open only explicit local paths, enforce the pinned APK before
interpreting members, reject mismatched extracted originals and produce sanitized
metadata only. No downloads, listeners, original modification, uploads or game
execution. CLI without paths must print its inactive state. Native/managed/source
availability on this runner does not establish future-run shared disk.

Negative controls: wrong APK hash/size, mismatched extracted library, ELF class/
endianness/machine mismatch, modified manifest, modified signed member, unsigned
extra member, duplicate ZIP entry, duplicate manifest attributes/names and folded
entry names. Physical synthetic fixture contents must be independently created.
Internal cryptographic checks must actually execute on the recovered file;
parser-only controls must never be reported as a signature verification.

Failure modes: mutable mirror URL; same version with different bytes; partial
ZIP/range retrieval; an intact self-signed certificate mistaken for external
trust; omitted members; partial Drive listings mistaken for absence; libraries
available only on one runner. Report exact missing prerequisites without filling
unknown hashes, historical source URLs or phone equivalence by assumption.

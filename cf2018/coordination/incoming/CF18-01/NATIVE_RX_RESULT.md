# CF18-01 — recovered mirror receiver trace and framing proposal

Base main: `925ecc3489b330dc9c6cf7738d6241450e4f24fe`.
Date: 2026-10-30 UTC. SUBMITTED; no active claim remains after submission.
Evidence classes: MIRROR_SOURCE_PROVENANCE, ORIGINAL_NATIVE_STATIC,
NATIVE_EMULATION_WITH_STUBS, ORIGINAL_CODE + LOCAL_SYNTHETIC.
G2 remains BLOCKED. No phone packet, accepted ACK, login or gameplay is claimed.

## Source recovered after the user's explicit internet-search instruction

The user explicitly asked to find the APK on the internet after connected Drive
and local checks did not obtain it. This source was downloaded from the web, not
Drive. No original was uploaded to GitHub or Drive.

Observed source page:
[APKPure exact package listing](https://apkpure.net/crossfire-legends-action/com.tencent.tmgp.cfmnac/download).
Observed download entrypoint:
[APKPure XAPK endpoint](https://d.apkpure.net/b/XAPK/com.tencent.tmgp.cfmnac?version=latest).
That URL is mutable; **the following hashes identify the analyzed bytes**.

The server returned HTTP 206 with an archive total of 768008878 bytes. The ZIP
central directory identified the APK, icon, OBB and XAPK manifest. Only the APK
and manifest were retrieved using validated byte ranges; the 737048867-byte OBB
and icon were not downloaded. APK member CRC32 `974cadd8` matched; the local
APK ZIP CRC check found no failing entry. The complete XAPK was not hashed.

| Artifact | Actually calculated size / SHA-256 |
|---|---|
| APK member | 30884905 bytes; `33045335685284385866e8b0e2df55285009399c285294c2f428b451ee00d3d9` |
| lib/armeabi-v7a/libapollo.so | 5243704 bytes; `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8` |
| assets/bin/Data/Managed/Assembly-CSharp.dll | 13423104 bytes; `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9` |
| Assembly-CSharp-firstpass.dll | 317440 bytes; `4ac2b58a02cc1d3ad1e345d9b21dd78c758b0077c19354862792d25bcaa8ba60` |

Androguard 4.1.4 read the embedded Android manifest: package
`com.tencent.tmgp.cfmnac`, versionName `1.0.11.11`, versionCode `11`.
The XAPK manifest independently gives the same identity. libmono.so and managed
assemblies exist. readelf identifies Apollo as ELF32 little-endian ARM EABI5
shared object; relevant symbol values have the Thumb bit set.

The v1 signing certificate's calculated SHA-1 is
`2d1305191dfaeb11ca7fe6dc28ccabd0fc3eb8cf`, matching the source listing;
certificate SHA-256 is
`dbfc84490cc286cb3e6cfa243c8c175dab6f33862997e6b45a2973aa41a262b4`.
OpenSSL CMS verified CERT.RSA against CERT.SF with `-noverify -binary`;
the signed SHA1-Digest-Manifest matched and all 1212 signed-entry digests matched.
`-noverify` disables certificate trust-chain validation; these checks establish
internal signature integrity and certificate continuity with the listing, not an
independent Tencent distribution attestation.

[Softonic](https://crossfire-legends.en.softonic.com/android) reports a different
APK SHA-256 (`8bd2fe304d9abbe2aab25d51578d0a3b6820447e05e1c6ad15a8bab2d04cb55f`).
That APK was not obtained or compared. Do not collapse same-version mirrors into
one byte identity. Exact equality with the historical phone's Original.xapk/APK
remains unverified. Historical v0.1-v0.8 scripts/reports remain unavailable.

Current runner's ignored private originals are under
`coordination/incoming/CF18-04/private/`; analysis dependencies are under
`private/analysis_deps/`. These paths are **local to this runner**, not guaranteed
shared disk for later scheduled workers. Reacquire using the source pointer and
require the pinned hash on another runner. Never publish those directories.

## Receiver trace: the marker comparison is on decoded state

All addresses below are virtual code addresses in the fingerprinted library,
Thumb bit cleared. No raw instructions or proprietary decompilation are included.
Capstone 5.0.9 and pyelftools 0.33 were used for bounded static examination.

| Code address | Observed operation / implication |
|---|---|
| `0x3ac0b8` | `gcloud_tgcpapi_recv_ack_msg`; direct call at `0x3ac0d2` to the GCloud receive/decrypt routine. This establishes a concrete ACK receive call chain; runtime selection on the user's phone is not established. |
| `0x3abe34` / call `0x3abe4c` | GCloud receive/decrypt calls its own splitter at `0x3ab5ec`. The unrelated legacy splitter at `0x1c0c50` is a distinct overload and must not be conflated. |
| `0x3ab5fa`–`0x3ab628` | Requires a non-null receive buffer/capacity; checks cursor, count and their sum against capacity before calculating free space. This does not establish comprehensive integer-overflow defenses. |
| `0x3ab630`–`0x3ab658` | Promotes cached lookahead when no current frame is pending; copies its decoded header and resets lookahead. |
| `0x3ab66a`–`0x3ab698` | Reads into buffer + cursor + count, bounded by available capacity, via `tgcpapi_net_recv` at `0x284fcc`; adds positive read length to buffered count. Receive -2/-4 set remembered error -9/-10; -3 leaves buffered data available. |
| `0x3ab69c`–`0x3ab6ba` | Fewer than 32 buffered bytes: compact remaining bytes; return remembered receive error if present, otherwise -12 (need more data in these controls). |
| `0x3ab6c4`–`0x3ab6e6` | If no frame pending, pass the raw buffer at the cursor to header helper `0x3aab44`. On decode success, pending length becomes decoded header length + body length. |
| `0x3aab5a`–`0x3aab96` | Header helper requires more than four bytes, accepts first byte AA or 99, obtains a big-endian 32-bit declared header length from bytes 1–4, rejects a negative signed length, and waits (-12) for a zero/unavailable length. It calls the real TLV header decoder at `0x3b7340`. |
| `0x3b7340` | Reads AA/99 and the header length, then dispatches to varint/non-varint header decoding. Header decoding dispatches nested base and extension blocks. |
| `0x3af4cc` | Varint base decoder reads base field 1 into the decoded structure's uint16 at offset zero. Base field 9 populates body length at offset 0x18. |
| `0x3ab6ea`–`0x3ab6f4` | Wait/compact when buffered bytes are fewer than pending header+body length. |
| `0x3ab6f6`–`0x3ab700` | Loads uint16 from **handle + 0x720, the decoded header structure**, compares to 0x4366; mismatch returns -13 at `0x3ab74a`. This is not a raw socket-prefix load. |
| `0x3ab702`–`0x3ab73a` | When at least another 32 bytes follow the current frame, decode the next header and cache its header+body length. Lookahead -12 is tolerated, other parse errors propagate. A malformed next header can therefore reject a currently complete frame in this path. |
| `0x3ac03c`–`0x3ac056` | After receive/decrypt, the caller advances cursor by the current pending length, subtracts it from count and clears pending. The splitter alone does not consume the frame. |

The `tgcpapi_net_recv` wrapper calls the imported `recv` at `0x285056` with the
supplied buffer and length. That wrapper performs no two-byte prefix stripping.
The exact incoming boundary used in this call chain is thus significant.

### Independent client TX cross-check

GCloud TX at `0x3ab430` explicitly prepares bytes 43 and 66 at
`0x3ab4c8`–`0x3ab4d0`, copies those two raw bytes to its output buffer at
`0x3ab4e0`–`0x3ab4ec`, and calls TGCPHead::packTLV at `0x3ab50a` with output
pointer advanced by two. This supports an outbound prefix + TLV layout in this
mirror. It does not establish an identical inbound envelope.

**Conclusion for this mirror/path:** the old argument "little-endian comparison
to 0x4366 implies raw receive bytes 66 43" confuses decoded storage with wire
format. The public frame_gate.py remains a historical hypothesis model; it is
not evidence for the decoded-marker rule, TLV envelope or an accepted ACK.
Do not deploy another prefix-only reply variant based on that argument.

## Native controls and actual scope

[Controls](native_rx_controls.py) require the exact library size/hash and ELF ISA,
then execute the real Thumb splitter plus its header/base/varint code in Unicorn
2.1.4. Budget: 100000 instructions and one second per call; input at most 64 KiB.
The network function is stubbed to return -3 (no new bytes); libc memset,
memcpy/memmove are implemented by bounded host memory operations; error-string
lookup is stubbed without altering its error code. PLT relocation names were
checked for the libc addresses. The splitter/decoder/comparison are not stubbed.
This is isolated native emulation with synthetic inputs, not a native Android
socket run, phone capture or full loader/relocation/runtime validation.

Actual controls in [tests](test_native_rx_controls.py):

- Both raw prefix orders fail with -18 before entering the TLV decoder.
- AA synthetic TLV with decoded 0x4366 reaches splitter return 0; swapped decoded
  0x6643 reaches the distinct -13 comparison branch.
- Short buffers and unavailable declared header/body return -12.
- Two synthetic coalesced frames cache lookahead without consuming the current
  cursor; a malformed next envelope returns -18.
- A wrong library fingerprint is refused before execution.

The first exploratory control used 32 trailing zero bytes, causing native
lookahead to parse those as another header and return -18. Restricting the suffix
below the 32-byte lookahead threshold isolated the marker comparison. Final tests
use explicit independent header/body lengths and test lookahead separately.

## Original strict parser proposal

[Proposal](native_rx_envelope.py) handles only AA/varint framing, big-endian nested
lengths, decoded base marker and declared body size, with fragmented/coalesced
stream tests. It has no listener, connector, reply serializer or ACK validator.
Message type is reported only when supplied by the decoded base; opaque extension
bytes are not validated, so this result cannot mean accepted ACK/type/session.

Resource cap (default 64 KiB), mandatory base/body-length fields, rejection of
unknown/duplicate fields, unsupported 99 mode and terminal parser failure are
**strict proposal policies**, not claims of native parity. It deliberately does
not imitate native's 32-byte read threshold, lookahead or error timing.

Fifteen proposal tests cover every fragment boundary, bytewise/coalesced frames,
both raw prefixes, swapped decoded marker, each EOF truncation, invalid header
and nested sizes, oversized declared body, duplicate/unknown fields, unsupported
99, uint16/uint32 overflow, opaque extension limits and terminal resource failure.
One initial size-cap fixture accidentally duplicated the body-size tag; it was
corrected to change the existing declared size, then all proposal tests passed.

## Reproduction, limitations and integration recipe

Acceptance and controls: [NATIVE_RX_ACCEPTANCE.md](NATIVE_RX_ACCEPTANCE.md).
Only CF18-01 incoming files are submitted; canonical files and other lane packets
are unchanged. The prior model-limit audit is preserved.

Actual final checks from cf2018: knowledge route completed (sources 1, tgcp 1);
knowledge doctor PASS; canonical suite **52 PASS**; complete CF18-01 suite with
the private fingerprinted library **32 PASS**, comprising nine native-emulation
controls, fifteen strict-parser tests and eight earlier model-audit tests.
The separate strict-parser command also passed all fifteen tests. No test was
skipped in the 32-test run. Without CF18_APOLLO_LIBRARY the nine native controls
are explicitly skipped, not reported as passing original-code execution.

The local source snapshot matched all 40 tracked CF2018 blobs against live main
before edits; git status returned exit 128 (no git checkout). Dependencies were
installed only in the ignored private analysis directory. Exact commands:

```text
python tools/knowledge.py route 'native gcloud receive framing marker source provenance'
python tools/knowledge.py doctor
python -m unittest discover -s tests -v
python -m unittest discover -s coordination/incoming/CF18-01 -p test_native_rx_envelope.py -v
CF18_APOLLO_LIBRARY=<private pinned library path> PYTHONPATH=<analysis dependencies> \
  python -m unittest discover -s coordination/incoming/CF18-01 -p test_native_rx_controls.py -v
```

Coordinator should independently check source/signature receipts and rerun the
native controls before changing canonical Q-01/E-09. Preserve the mirror-vs-phone
distinction and G2 BLOCKED. Integrate source pointers/hashes and the corrected
decoded-field interpretation; do not overwrite historical captures with a new
wire-format claim. Review the strict parser only as an offline framing subset.

Next bounded work: CF18-02 can trace this hash's ACK extension/session/key-mode
rules; CF18-01 can extend boundary/error analysis or compare the phone library
hash. Historical relay sources, actual failing ACK bytes, runtime path selection
and a real post-ACK client packet remain missing. No device A/B/C execution or
deployable valid ACK is supplied.

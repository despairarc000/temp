# R037 — SYN field 14 route encoder and narrower nested-route probe

Date: 2026-11-01. Sources: the user's uploaded sanitized R036 SYN-length report; privately retained exact original Apollo ELF (5,243,704 bytes; SHA256 4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8); and independent synthetic test fixtures. **Do not confuse phone observation, native STATIC verification, and synthetic controls.**

## Real phone observation from R036

Following one locally sent 169-byte 0x4013 candidate response (not proof of application acceptance), the next three phone connections delivered 131-byte 0x1001 SYN-family frames. Each retained all base and nested-SYN field tags and kinds. Relative to the exact reference 133-byte SYN, the only modified SYN field was **field14, kind5, encoded length −2**. Base structure and base byte length unchanged; other same-length SYN field values unchanged according to the R036 observer's bounded in-memory comparison. All three attempts were refused by the test's strict reference-SYN gate without ACK/auth. The previous R034 no-response phone control had four exact 133-byte reference SYNs, establishing a repeatable *association* with the R033/R035/R036 active response, **not causal proof or actual client reply acceptance**.

## Verified original-native semantics

The original `gcloud_gcp::TGCPSynHead::packTLVWithVarint` symbol begins at 0x3b2826. At 0x3b2a36 it writes TLV key `0xe5`, equal to field number14 / kind5; at 0x3b2a56 it calls original `gcloud_gcp::TGCPRouteInfo::packTLVWithVarint` (0x3b2222). Therefore SYN field14 is **nested route information**, not an unclassified variable-length authentication field. Original `TGCPRouteInfo` has separate route union variants; a named-route (variant4) invokes the `SpecifyNameRouteInfo` structure. This is a read-only, exact-source native **static** observation, not real phone code execution.

In the original owner's exact 133-byte reference SYN, field14 contains **one variant4 kind5** route; inside it is **one field1 kind5** length-delimited name of 12 bytes. That reference name length is grounded locally and no original bytes or identifying route values are exported. The R036 phone report does NOT show whether the later shorter field14 retains variant4, whether its inner field1 stays kind5, or which specific name or route is used.

A simpler explanation consistent with the observed change is a **10-byte name in the same nested-route structure**, but a **different route union or nested shape** might also reduce the total by2. This is a hypothesis pending the next discriminating observation.

## R037 source-only diagnostic (not phone tested)

Owner attachment: `CF2018_R037_ROUTE_DELTA_Kit.zip`, **35,193 bytes**, SHA256 `c9837375ed0d5b37606e9619d1597c544d60de8d2684c3e8ea6eb657378fc380`, ZIP-integrity verified, **24 source-only paths**. The original V3.8 source/binary/captures are not included and stay outside GitHub.

R037 is a separate private-copy preparer on top of the exact hash-pinned original 60-file V3.8 sources and R033/R035/R036 scripts. It changes only first-frame observation and adds `R037_ROUTE` category-only lines (route variant tag/kind, equality to reference, nested name-field shape, relative name byte-length change, name-changed boolean). The synthetic 169-byte response is unchanged; there is still at most one reply for up to four sessions, and non-golden first frames are still rejected before ACK. No raw or decoded route values, account info, sequences or hashes are saved.

Fresh-extraction verification: **113/113 original V3.8 tests PASS** and **30/30 focused R033–R037 tests PASS**, including a local loopback TCP exchange with a synthesized route name exactly two bytes shorter and one-reply-only control. The positive synthetic classification is `NAMED_ROUTE_STRING_SHORTER name_delta=-2`; changing the route union is classified separately as `ROUTE_VARIANT_CHANGED`. Neither claims acceptance of a real server response.

**Next:** the owner may run a single opt-in R037 phone test, `CF2018_R037_LIVE_REPLY=YES bash START_R037.sh`, and provide only `~/storage/downloads/CF2018_R037_ROUTE_Result.txt`. If the real client consistently shortens named-route string length by2, examine how that route is selected by native post-address-reply code. If the variant changes instead, trace that alternate route. Do not auto-ACK unmatched SYN or claim 0x4013 blocker broken. Neither accepted service reply nor login/lobby/gameplay has been verified.

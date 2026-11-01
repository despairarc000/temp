# R036 — same-shape shorter SYNs after the experimental 0x4013 reply

2026-11-01. Evidence: owner-provided sanitized R035 phone report, plus independently synthetic offline tests. The original game has **not** accepted the experimental reply or reached a lobby.

## What R035 confirmed

With a single R033-style experimental 169-byte response, phone run R035 saw a qualified real 0x4013 request from session1, then three new connections on local port8085. Each presented a complete 131-byte initial TGCP frame (header129, body0). All carried the **same 0x1001 extension** and the **same outer base field-number/type pairs** as the 133-byte reference SYN, but differed in serialized bytes. The previous R033 active-reply run also saw three 131-byte first frames (without recording the type). A no-reply R034 passive phone run had four exact 133-byte reference SYNs and two qualified requests. This is a repeatable **association**, not proof of causality or successful RPC/session acceptance. A local sendall and later read EOF are not receiver acceptance signals.

## Correcting the old synthetic control

R034/R035 tests produced a synthetic 131-byte frame by **removing TGCP Base field5**, making a shorter but structurally different base. The REAL phone's 131-byte frames retained Base field5, and indeed retained *all* reference base field number/type pairs. So that synthetic fixture is **not representative** of the observed 131-byte class. Do not use it to infer a missing field, handshake success or invalid client requests.

## R036 narrow structural discriminator

A separate source-only R036 kit adds only in-RAM nested SYN field serialization-length comparison against the hash-pinned original local 133-byte golden SYN. No private original files are in the kit; the owner must supply the existing original V3.8 ZIP. The reply bytes, send count (max1), ACK/auth/Bingo sequence, 4-session cap and rejection of non-reference first frames are exactly the same as R035.

The R036_DELTA output records only relative byte-length changes to base, extension and SYN portions; changed SYN field *numbers* and signed encoded-length deltas; and counts of modified same-length fields. It records **no field values, exact variable-length user data, RPC sequences, raw frames, hashes, device identifiers or credentials**. Two independently synthetic 131-byte variants with all base fields intact—one shrinking an encoded SYN bytestring by2, the other shrinking a SYN varint by2—pass the classifier with distinguishable field-number labels. Unlike the old fixture, these preserve the observed base field shape. The diagnostic itself never sends a packet, and the protocol server remains unverified.

Original V3.8 regression tests **113 PASS**; focused R033/R034/R035/R036 tests **23 PASS**, including a local TCP one-reply + same-base-shape 131-byte SYN test. R036 has **not** yet been run against the phone.

**Next phone test:** run R036 once after force-stopping CrossFire and stopping other probes, supply only CF2018_R036_SYNLENGTH_Result.txt. If the real client shortens one specific SYN field, trace that original native encoder and its handshake/session semantics before modifying ACK acceptance. Do not automatically send the same ACK to an unknown 131-byte variant; do not claim login/0x4013 response acceptance.

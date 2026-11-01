# R038 — route switch after a 0x4013 reply: no-reply immediate-close control

Date 2026-11-01. **Status:** R037 real-phone evidence analyzed; R038 synthetic socket and original V3.8 tests PASS. **R038 NOT run on phone.**

## Phone observation, R037

The owner uploaded a sanitized R037 report. Its first connection had reference `0x1001` SYN, normal synthetic ACK/auth/Bingo and a qualified real `0x4013` request. The local relay wrote the experimental 169-byte response, then read EOF. The three subsequent connections were 131-byte SYN-family frames with identical outer base and nested-SYN field numbers/kinds. All three were classified `NAMED_ROUTE_STRING_SHORTER`: nested route union field4, named-route inner field1, and a name-length difference of **-2 bytes**. No changes were observed in the other SYN fields under the length/identity-delta diagnostic. Their route strings were not retained, so the shorter name **cannot be identified from the report**.

An independent local check of the owner-provided original 133-byte reference SYN confirms its 12-byte named route is exactly `QueryAddrSvr`. The post-response 10-byte name is not known. The original Apollo native `TGCPSynHead::packTLVWithVarint` encodes SYN TLV14 as `TGCPRouteInfo` (R037 native evidence). Thus the client **attempted a differently named route** in three subsequent SYNs, but the exact destination and acceptance of the earlier 169-byte reply are unproven.

## Competing explanations

A downstream service-connection attempt after processing the experimental address reply is one plausible explanation. Another is failure/recovery triggered by closing the socket or a transient client state transition. Prior control R034 had no experimental reply and all four SYNs were exact original 133-byte reference; however, that passive control kept the routed-data socket open for an observation window. The active R033/R035/R036/R037 runs instead ended the first session shortly after a local reply was written. These differing closure conditions are a **confounder**; do not infer native acceptance from the association.

## R038 experiment designed to separate them

Source-only, owner-downloadable `CF2018_R038_CLOSE_CONTROL_Kit.zip`: **39,392 bytes**, SHA-256 **06ea8a44a6ede007a26d9444c9eb935a9a9bb1a17780cbbeccc5fe1baebc258a**, **26 file entries**; validated ZIP integrity. It includes the public R033-R037 observer preparation code and baseline tests but **excludes all private original V3.8 files, native libraries, game files, RPC values, route strings and captures**. Original V3.8 ZIP must be supplied separately by owner.

R038 prepares a fresh private copy through the same exact original 60-file hash-pin preflight. The only control change to R037's server behavior is: after the **first complete structurally qualified client 0x4013 request**, the local handler **closes that session without ever generating or sending an experimental 0x4013 response**. It preserves the old synthetic 63-byte ACK, 54-byte auth and 91-byte Bingo replies for the *exact* reference SYN; max four sessions, one early close only; does NOT acknowledge non-reference 131-byte SYNs. All subsequent first frames are classified using the existing R035 first-frame, R036 field-length and R037 route-delta reporters. The report adds a fixed `R038_CONTROL` label identifying the one deliberate no-reply close. No field values or content are exported.

Fresh ZIP extraction, original source hash preflight, **113/113 original V3.8 regressions PASS**, **3/3 R038 socket/control tests PASS**, including first qualifying route close with **zero additional 4013 reply bytes**, unchanged baseline synthetic handshake, no second deliberate close, and a synthetic 131-byte same-variant shorter named route that is *classified but not acknowledged*.

Owner opt-in only: `CF2018_R038_LIVE_CLOSE=YES bash START_R038.sh`, PCAPdroid CrossFire-only SOCKS5 localhost1080; report `~/storage/downloads/CF2018_R038_CLOSE_CONTROL_Result.txt`. Force-stop CrossFire before run. **No phone run yet.**

### Interpretation of next phone result

- If the no-reply immediate-close trial produces the **same 131-byte, shorter named-route SYN** pattern, early connection termination or a retry/state transition is a viable explanation independent of a successfully processed address RPC response. Do not advance to synthetic ACK for a new route.
- If it instead produces only exact **133-byte QueryAddrSvr SYNs**, the hypothesis that the experimental 169-byte reply influences the transition gains support, but still does **not prove** native reply parsing or authenticated service access.
- If a different first-frame family occurs, analyze category-only labels before making further changes.

This is a **timing/close control, not a perfect randomized experiment**. No valid game login, native address-reply acceptance, lobby or playable bots have been demonstrated.

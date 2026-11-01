# R035 — One-reply experiment with complete first-frame labels

**2026-11-01. Evidence status: R034 PHONE PASSIVE CONTROL + R035 OFFLINE TESTED. R035 has NOT run on the owner's phone.**

## What the R034 phone test established

Owner uploaded sanitized CF2018_R034_FirstFrame_Result.txt. All **four** sessions began with the exact golden **133-byte** `0x1001` SYN, with base/extension field shapes matching the golden reference. All four produced `0x2001` auth requests and the baseline synthetic ACK/auth/Bingo sequence. Two later routed `0x4013` requests were observed (frame161/body80, frame166/body85), both `qualified_address_request=COMPLETE_STRUCTURAL_CANDIDATE`. There were **no** 131-byte first frames during the passive R034 run, and no experimental address reply was sent.

Previous R033 live phone result was different: first slot had a qualified 0x4013 and the server locally sent 169-byte synthetic response; the three later first frames were 131 bytes and labeled unexpected by the exact 133-byte hash gate. Because R033 failed to emit first-frame extension/field-shape metadata on mismatch, their actual type/meaning is **unknown**, and comparison across launches does not prove reply causation, native response acceptance or server-side authentication.

## One-variable diagnostic

Prepared a source-only R035 kit that combines **R033 exact one-reply code** and **R034 first-frame structural reporting**. It changes no response bytes, route selection or original ACK/auth/Bingo logic. The R035 probe includes the same one-shot `self.request.sendall(candidate)` and same `r033_reply_claimed` guard; it additionally emits `R035_FIRST` on every fully parsed first frame, including rejected candidates. It deliberately **continues to refuse** non-golden SYNs instead of attempting to authenticate them.

Source-only owner download: `CF2018_R035_Reply_FirstFrame_Kit.zip`; 22,761 bytes; SHA-256 `a67e3b1fbfeb5a0d3bd3fce77d82a5c28281675a8d84a5f6042005813fb67c93`; 16 ZIP files; integrity verified. It contains no private original V3.8 source, original Apollo library, APK, packet data or user secrets. The original hash-pinned V3.8 ZIP must be supplied separately. This GitHub report records the handoff; the binary ZIP is a conversation attachment and not committed to GitHub.

## Evidence and strict limits

- The pinned **60-file original source** was verified before a fresh private-copy R035 build. No original source was modified.
- **113/113** original offline V3.8 tests passed.
- **15/15** focused R033, R034 and R035 tests passed from fresh extraction.
- Synthetic localhost experiment created normal 133-byte, shortened synthetic 131-byte and normal 133-byte first frames; all three received their expected fixed-label first-frame classification. The single qualified response was delivered only to the first session. The synthetic 131-byte variant received **no ACK**, and a later exact SYN received **no second experimental reply**.
- No live R035 phone run or original-client response acceptance has been observed.
- Explicit live opt-in only: `CF2018_R035_LIVE_REPLY=YES bash START_R035.sh` from prepared private directory. Four sessions max; at most one additional candidate response in total; report file `~/storage/downloads/CF2018_R035_ReplyFirstFrame_Result.txt`. Original baseline remains synthetic, not authentic login.
- Report labels only; never commit original code, route strings, packet dumps, RPC sequence values, accounts or identifiers.

**Next owner action:** force-stop and relaunch CrossFire after setting PCAPdroid and run R035 ONCE, then upload only the result TXT. If 131-byte frames recur, read their extension and base *shapes* to decide whether they are the known SYN family, a new route type or something else. If all first frames remain 133 bytes, the R033 difference may reflect transient process/session/phone state. Neither outcome proves the 169-byte candidate was consumed by the real native RPC receiver; that requires an additional independent acceptance signal.

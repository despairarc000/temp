# R039 — R038 phone no-reply close control and one-bit RPC64 negative control

Date 2026-11-01. **Evidence:** actual owner-uploaded `CF2018_R038_CLOSE_CONTROL_Result.txt`, prior R037 phone report, original Apollo static receive-path audit, and source-only R039 offline synthetic controls. **No R039 phone test has happened.**

## R038 actual phone outcome: early close without a reply does not reproduce rerouting

The owner's R038 result shows **four sessions**. Session1 sent original 133-byte reference 0x1001 SYN, auth0x2001, and a structurally complete qualified 0x4013 `QueryAddrSvr:QueryAddrInfo` request (161-byte frame, 80-byte body). The R038 local handler then recorded `closed_without_4013_reply reply_sent=False`; NO response to that request was sent. Sessions2–4 all opened with the **exact reference 133-byte 0x1001 SYN**, identical reference base+extension structures, no nested SYN name or field-length changes, and proceeded through the same synthetic ACK/auth/Bingo sequence. Session4 independently emitted a second qualified 0x4013 (166-byte frame, 85-byte body). Four auth requests and two later 0x4013 requests were observed; all four reference SYNs matched.

R037 active-reply phone test instead sent one 169-byte experimental reply in session1 and observed three 131-byte SYNs routed by a name two bytes shorter; R033/R035/R036 had consistent shorter SYN patterns, while passive R034 and early-close-only R038 did NOT. This is **repeatable experimental association supporting that the reply or its delivery matters**, rather than socket closure alone. It is not formal causality, a native QuerySession callback trace, authenticated login, or proven server acceptance.

R038 was not a randomized matched-timing trial and downstream client state was not captured. The exact 10-byte route name remained unobserved. Do NOT automatically acknowledge the alternate named route or infer its identity from name length.

## Why R039 tests RPC64 next

Original static Apollo path: `AddressService::ProcessResponse` calls binary `readMessageBegin`, searches a pending `QuerySession` by 64-bit RPC sequence, and only then can dispatch a type2 result to `Recv_QueryAddrInfo`. If the experimental reply's RPC64 is crucial, deliberately changing it while keeping every other byte identical should suppress a session-correlated transition.

R039 modifies R037's structurally validated 169-byte uncompressed AA/TGCP 0x4013 candidate **at exactly ONE byte**: it flips bit62 (XOR `0x40` of the first big-endian byte) in the 64-bit RPC sequence. It verifies the mutated message is still a complete type2 qualified reply, fields and length identical, original packet sequence unchanged, correct independent incoming request shape and only a single bit differing. This is intentionally the **wrong pending RPC64**, never an accepted/valid response. No account/identity/route contents are logged. Same four-session cap, one additional reply cap, same synthetic ACK/auth/Bingo, same loopback endpoint, same R034–R037 first-frame/nested-route structural reports. It does not auto-ACK nonreference SYNs.

## Delivered source-only kit and validation

`CF2018_R039_RPC64_NEGATIVE_Kit.zip`, **40,540 bytes**, SHA256 **2821fd111c7e1bcabc86b53918b45c1059f049de14aa9489a3e90bf494b0afdb**, 28 source-only files, ZIP integrity verified. **Not committed to GitHub as code; delivered in chat.** It contains no original private V3.8 files, original APK, native library, captured phone packets or previous private prepared workspaces. The existing owner V3.8 source ZIP is a separate input. Source preparation fails closed unless 60 original files pass exact hash checks, and creates a fresh private `qualified_r039` copy. No listener starts without explicit owner opt-in.

From **fresh extraction**, original V3.8 regression suite **113/113 PASS**; focused structural/negative tests **29/29 PASS**, and six synthetic socket/integration tests PASS individually (R033 1, R035 2, R036 1, R037 1, R039 1) — **35/35 focused PASS**. One combined runner hit a wall-time limit, so the package executes the focused socket modules individually after static tests; each completed and passed. One-shot write is guarded by original R037 code. The synthetic socket test confirms one intentionally wrong-sequence response sent and classification of a synthetic 131-byte following SYN; it is not real-game behavior.

## R039 decision outcomes

- If real phone following R039 again switches to the shorter named-route 131-byte SYNs, the rerouting may occur before RPC64 matching, via transport receipt or other side effects. Neither proves native application acceptance.
- If R039 produces only original 133-byte QueryAddrSvr SYNs, the native RPC64 pending-session check or downstream correlated-result processing becomes a much stronger explanation; still not proof of full result acceptance.
- If first-frame or route behavior is mixed, investigate specific category and timing; do not force interpretations.

**Next:** single consented R039 phone run after stopping old probes and force-stopping game; `CF2018_R039_LIVE_NEGATIVE=YES bash START_R039.sh` from the prepared folder; report `~/storage/downloads/CF2018_R039_RPC64_Negative_Result.txt`. No need to redo R027/R038. The fake server is NOT playable: no authenticated account, validated service response, lobby or bots.

# R033 — one bounded 0x4013 response experiment ready

Date: 2026-11-01. **Status: source-only kit prepared and offline tested; phone response has NOT been sent.**

R027 confirmed two real phone qualified QueryAddrSvr:QueryAddrInfo request structures. R028–R032 source-pinned the receiver, pending 64-bit RPC sequence, original result+reason reader, inbound 0x4013/DataHead, explicit TGCP Base field6 inbound decrypt selector, DataHead compression0, and conditional unprefixed Thrift application buffer. This justifies a narrowly scoped reply **test**, not another broad request-identifier research cycle.

## Owner-delivered attachment

CF2018_R033_One_Reply_Kit.zip — 18,307 bytes; SHA-256 e3767f7082b6dce72a8df74879ce3d7d301c8840bd545b1bb78be5ee3ffc825f, validated ZIP integrity, 12 source-only entries. The user receives the kit as a conversation attachment, NOT as committed code in GitHub. The private original V3.8 ZIP (SHA-256 e3bbc31f7b93e738aff0d4205dd0d1418c7abd55b7c17b332ca5d426eb619df2) is required separately and must not be committed.

The R033 preparer validates all 60 original V3.8 source hashes before creating a fresh private qualified_r033 folder. The original source, passive R026 probe and original V3.8 probe remain unchanged. The prepared copy has a distinct routed_probe_r033.py and START_R033.sh. It preserves original synthetic ACK63, auth54, Bingo91, restricts to loopback and caps at four sessions and at most ONE experimental 0x4013 response per run. Exact native-qualified request, named route and independent TGCP packet sequence are required. It uses the request's *64-bit RPC sequence*, not TGCP32, for an in-memory type2 response with required result+reason and one IPv4 loopback address 127.0.0.1:8085. Provisional AA Base field6=0, 0x4013 DataHead compression0 and named-route envelope is structurally tested but **NOT established as native-accepted server framing**.

Original private V3.8 regression suite: **113/113 PASS**. R033 focused synthetic tests: **8/8 PASS**, including full local TCP socket exchange and one-reply-only control, after fresh ZIP extraction. No game, login, original-native dynamic execution or phone response was exercised by these tests.

Live requires explicit CF2018_R033_LIVE_REPLY=YES before running the prepared START_R033.sh. Report path is ~/storage/downloads/CF2018_R033_OneReply_Result.txt. R033_RESPONSE status=r033_reply_sent establishes only that the local socket write completed; R033_POST_REPLY and LATER rows report subsequent client activity without raw identifiers or payload. A reader EOF is not proof of a game authentication reject.

**Next:** owner runs the prepared experiment once and supplies only the sanitized R033 TXT. Interpret whether a client follow-up occurs; if not, investigate the precise transport/framing/method/session gate indicated. No authenticated session, accepted 0x4013 response, lobby or playable bots claimed.

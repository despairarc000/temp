# CF18-05 — independent Bingo / WAIT serializer review
Date 2026-10-31. This is a bounded independent static review, NOT native emulation, session acceptance or phone test.
Original inspected: libapollo.so, 5,243,704 bytes, SHA256 4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8. LLVM 17 Thumb disassembly.

## Native serializer contract
- TGCPBody::packTLVWithVarintEx at 0x3b7ea4: 0x3002 WAIT body union writes tag 0x30025 (literal at 0x3b8128), big-endian nested length, then calls TGCPWaitBody packer at 0x3b4d16.
- Same switch at 0x3b807e: 0x6002 Bingo body union writes tag 0x60025 (literal at 0x3b8138), big-endian nested length, then calls TGCPBingoBody packer at 0x3b7564.
- TGCPWaitBody::packTLVWithVarint at 0x3b4d16 writes three varuint32 fields with tags 0x10,0x20,0x30; prior research identifies queue position, total, rough time.
- TGCPBingoBody::packTLVWithVarint at 0x3b7564 writes tag 0x15 containing nested TGCPRelay, tag 0x21 uint8 compression method, tag 0x30 varuint32 compression limit.
- TGCPRelay::packTLVWithVarint at 0x3b0c38 writes 0x10 varuint32 position, 0x25 BE length and exactly 16 identity bytes, 0x30 varuint64 server ID, 0x40 signed varint64 session ID.
- Body union requires the separately established TGCPBody AA + 4-byte big-endian total length preamble.

## Independently constructed offline check
An original strict Python body-structure preflight was written and tested locally in this conversation: 11/11 tests PASS. It checks 0x3002 or 0x6002 header/body union correlation, envelope and nested lengths, required native-writer field shapes, identity field length, truncation and duplicates. Its synthetic fixtures are not valid credentials or server sessions. This preflight is intentionally STRICT and does not reproduce native decoder tolerance; no ARM emulation here. The source/test ZIP was delivered in the conversation, not committed to public GitHub by this report.

## Next boundaries
Retain user-confirmed v1.4: corrected 54-byte 0x2002 response no longer leads to immediate local read EOF on either of two trials, but no third client packet nor authentication. Trace real Bingo/relay identity generation and QueryAddrInfo application request/response predicates. Do not promote native numeric state5, UI connected or buffer open to authentic login. Do not deploy arbitrary Bingo fixtures or reactivate schedules.

References: cf2018/knowledge-system/vault/research/BINGO_SESSION.md; cf2018/knowledge-system/vault/research/CONNECTION_CALLBACKS.md; cf2018/coordination/incoming/CF18-05/PHONE_V14_RESULT.md.

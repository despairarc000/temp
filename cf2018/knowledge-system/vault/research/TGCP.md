# TGCP handshake — factual/hypothesis split

## Client-side evidence
Real client 133-byte SYN; start `43 66 aa 00 00 00 83 15...`; 32 identical requests in v0.1 capture, 33 further v0.3; service identifier `QueryAddrSvr`; extension variant `0x1001`. Client framing observed/native TX code consistent with 2-byte prefix and TGCP header.

## Synthesized ACK failure
Earlier local reply is 65 bytes, ACK type `0x1002`, key mode 0 and copied SYN base fields. Never captured from real server. On-phone v0.5 A/B gives median passive ~7003 ms vs ACK ~11 ms; ACK-to-EOF median ~8.44 ms. No next client frame. EOF origin unresolved.

## v0.7 static audit
`TGCPAckHead::packTLVWithVarint` ACK tags 11,21,35,41,50,60 structurally supported by native serializer. `recv_ack_msg` dispatches on 0x1002. `recv_and_decrypt_pkg` branches for key modes 0,2,3. Mere syntactic parity does not show accepted state.

## v0.8 hypothesis
Native receiver compares first 16-bit incoming word to 0x4366; little-endian raw bytes `66 43` would match. Previous ACK used client outgoing `43 66`. Check whether the instruction is truly used in *server→client* RX path, whether there is byte-swapping, and whether relay byte order is preserved. Next controlled experiment must change only prefix, leave all else equal, and record post-ACK traffic. As of this checkpoint **phone acceptance unknown**.

## Next reverse-engineering target
- `tgcpapi_gather_and_split_entire_pkg` — byte-offset, length, magic, framing error.
- `gcloud_tgcpapi_recv_ack_msg` — type/session validation and ACK body parsing.
- `tgcpapi_encrypt_and_send_pkg` — compare client TX framing, don't reuse blindly.
- `TGCPHead`, `TGCPSynHead`, `TGCPAckHead` — TLV layout and state.
- Distinguish message framing from client logic and key exchange. Annotate source offsets, compiler/ISA mode, and confidence in Vault.

See [evidence](../EVIDENCE.md), [open questions](../OPEN_QUESTIONS.md), [Drive](../../../sources/DRIVE_MANIFEST.md).

# TGCP — reviewed mirror trace and historical phone boundary

**G2 BLOCKED.** Current receiver findings are in
[CF18-G2-ACK-01](ACK_RECEIVER.md), with
[hash-scoped source provenance](../../../sources/SOURCE_PROVENANCE.md).
They supersede the v0.8 raw receive-prefix inference for the recovered mirror's
GCloud call chain. Exact equality/runtime selection on the phone is unverified.

## Historical phone reports

Imported reports describe a 133-byte QueryAddrSvr SYN beginning 43 66 then TLV,
32 identical requests in v0.1 and 33 more in v0.3. The earlier 65-byte synthetic
ACK used type 0x1002, key mode 0 and copied base fields, without an authentic
server capture. v0.5 median passive duration was about 7003 ms; ACK duration
about 11 ms and ACK-to-EOF 8.44 ms; no later client packet. Originals and relay
source are unavailable, so EOF origin and precise candidate construction remain
unrevalidated. These are historical phone reports, not new device observations.

## Corrected native interpretation

The pinned mirror's ACK -> receive/decrypt -> GCloud splitter decodes an AA/99
TLV envelope. Its 0x4366 comparison is on decoded base marker storage, not a raw
socket prefix. Both raw prefix orders fail before the TLV decoder in native
controls. Independent TX code explicitly prepends raw 43 66. The historical
[frame_gate.py](../../../experiments/frame_gate.py) is retained only to reproduce
the retired hypothesis; do not use its prefix mutation as a candidate reply.

Effective header type comes from the extension selector, which replaces the base
field. ACK processing applies methods before some failures, consumes before the
ACK caller's type check, and handles optional body/auth content. Mode 0 reaches
the empty-body branch but does not establish successful later crypto/session.
No bounded receive function proves which fields a server should generate/echo.

## Canonical code and limits

[Offline AA/varint framing](../../../experiments/rx_envelope.py) has strict local
size/duplicate/unknown-field policies, opaque extension bytes, `base_type` metadata
and terminal EOF. It has no ACK serializer, networking or session validator.
Native 99 mode and gather/lookahead timing are not implemented by that subset.
[Private-source verifier](../../../tools/verify_private_source.py) checks known
APK/member fingerprints, internal signing links and ELF identity with explicit
local files. Its signature result does not establish external certificate trust.

Coordinator checks: 83 canonical tests passed with private APK selected; the
source-free suite has two explicit private-source skips. Separately, 32 framing,
25 ACK and 14 source-lane tests passed against the private originals, no skips.
All use synthetic/localhost or isolated native controls. No actual new phone
packet, accepted ACK, authenticated AddressService or gameplay is claimed.

Next: optional ACK body/embedded auth/session consumers, framing boundary review,
phone source/path identity and historical relay evidence. No device A/B/C packet
is ready. [Evidence](../EVIDENCE.md), [questions](../OPEN_QUESTIONS.md),
[relay](RELAY.md), [assignments](../../../coordination/assignments.json).

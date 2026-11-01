# R027 — phone-proven structural identification of routed 0x4013, and next receiver gate

Date: 2026-11-01. Source: user's uploaded `CF2018_v38_DataHead_Result.txt` from targeted R026 test. This document deliberately does not reproduce raw payloads, account identifiers, addresses or session values.

## Measured phone evidence

Four synthetic auth/Bingo trials:
- four auth 0x2001 requests; synthetic reply ACK63 / auth54 / stage91 kept unchanged;
- session 1, 0x4013 frame161 application body80; exact `QueryAddrSvr` route, independent TGCP packet-sequence prefix MATCH, **qualified_address_request=COMPLETE_STRUCTURAL_CANDIDATE**;
- session 4, 0x4013 frame166 application body85, same route and matching classification **COMPLETE_STRUCTURAL_CANDIDATE**;
- both 0x4013: older legacy classifier `not_identified`, legacy headers `METHOD_BYTES_POLICY`, compression flag `no`;
- session 2: no later frame in deadline; session 3: unrelated 0x5001 frame, not a 0x4013 response.

This is a **measured positive structural classification** for the original-native qualified RPC grammar. It closes the specific format-recognition blind spot caused by colon rejection in the previous observer. It does **not** establish that the client accepted a response, real account/authentication, service addresses, lobby, match, bots or server-side RPC meaning beyond shape. Both report lines explicitly state `rpc_verified=False auth_verified=False`. The synthetic ACK/auth/Bingo stage remains unverified as real authentication.

## Original-native reciprocal receive gates

Read-only source-pinned ELF Thumb path, not dynamic client execution:

- `AddressService::ProcessResponse(unsigned char const*,int)` loads incoming bytes into `MsgBuffer::setMessage` at native callsite `0x39b9a0`.
- Its virtual protocol `readMessageBegin` call at `0x39b9d4` reads the method name, kind and **64-bit RPC sequence** from the message, separate from the 32-bit TGCP packet-sequence prefix.
- At `0x39b9f2` it searches the `QuerySession` map keyed by the parsed 64-bit RPC sequence; `0x39b9fa-0x39b9fc` compares against the end sentinel. Without a pending session, the positive response path is not proven.
- At `0x39baa0` the message-type field is compared against type2 (RPC reply); the matching branch `0x39bb08` calls native `Recv_QueryAddrInfo`.
- Previous hash-pinned native result decoder execution confirmed a result I32 and a reason STRING are both mandatory, although reason may be empty. Header decoding alone never implies session acceptance or reply success.

The original native receive code should be checked further for response method-name equality and the exact route/TGCP response framing; the static evidence above does not resolve those or prove an actual response.

## Implemented offline protections

The canonical `experiments/address_response_gate.py` now accepts **only** two explicitly evidence-backed structural method spellings, bare `QueryAddrInfo` and qualified `QueryAddrSvr:QueryAddrInfo`. This **does not assert** either is native server-response policy. It still requires type2, required result+reason, strict field caps and pending-sequence consistency.

New `experiments/qualified_exchange_preflight.py` correlates a structurally recognized qualified request's **64-bit RPC sequence** against a synthetic response's 64-bit RPC sequence entirely in memory. It never logs, returns or stores the values. Its tests explicitly show that a response using the 32-bit TGCP packet sequence instead of the separate 64-bit RPC sequence is rejected even when both are individually well-formed. Neither module sends replies or connects to devices. Existing in-progress game remains NOT PLAYABLE.

## Next distinct test

Offline first: establish expected native response method and route/TGCP framing from source, then validate the callback and pending session with a synthetic original-reader test. Only when those pass should the local relay attempt one bounded correlated response while keeping both sequences in memory and never publishing live identifiers. No repeat of the now-successful R026 request-identification phone test.

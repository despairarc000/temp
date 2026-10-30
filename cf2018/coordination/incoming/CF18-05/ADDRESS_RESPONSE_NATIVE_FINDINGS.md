# CF18-05 — AddressService QueryAddrInfo response gate (offline v0.2)

Independent native **STATIC** review, 2026-10-31; original local Apollo 5,243,704 bytes SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, ARM Thumb disassembled with LLVM 17. No native emulation, phone, original client response, or service connection.

## New original native findings

- `AddressService::Recv_QueryAddrInfo` at `0x399a98` calls generated `QueryAddrSvr_QueryAddrInfo_presult::read` (`0x39eebc`). At `0x399af4–0x399b04`, it checks the **generated success-field presence bit**. If present, return 0; if absent, the exception path starts at `0x399b06`. This is distinct from the numeric response result.
- `AddressService::ProcessResponse(unsigned char const*,int)` at `0x39b90c` sets a received message into MsgBuffer at `0x39b9a0`. At `0x39b9de–0x39b9fc` it finds the 64-bit response sequence in its pending `QuerySession` map. Only a matching entry reaches the recognized-session branch.
- At `0x39ba9e–0x39bae0`, it checks **RPC message type 2** (Thrift reply); other types follow an error callback/cache-clear branch. The type-2 path calls `Recv_QueryAddrInfo` at `0x39bb08`.
- At `0x39bb10–0x39bb14`, after decoding, it compares `RspQueryAddrInfo.result` stored at offset +4 against **zero**. Nonzero follows an error callback, while zero progresses to address-list processing. Thus `result == 0` is now a **native observed branch condition**, replacing the older pure hypothesis, but it is not proof of a usable service address.
- At `0x39bbc0–0x39bc7c` it iterates address entries, using domain/numeric IPv4 classification. Later callback/cache logic occurs at `0x39bd58–0x39bd9a`. No real reply or downstream success has been observed.

## Original implementation and tests

- [addr_response_gate.py](addr_response_gate.py): small bounded strict subset reader for synthetic *unversioned TBinaryProtocol* method `QueryAddrInfo`, message type 2, 64-bit sequence, success wrapper field `0:STRUCT`, nested response fields and address list. `assess_response` uses caller-supplied pending IDs, native-zero result and conservative endpoint policy. It neither opens a socket nor models the GCloud connector envelope.
- [test_addr_response_gate.py](test_addr_response_gate.py): **14 local tests PASS**, including every truncation offset; unmatched sequence; nonzero result; missing wrapper; malformed list; duplicate/trailing fields; invalid port; wrong type/method. These tests do NOT execute native Apollo code; the parser is intentionally stricter than the native Thrift decoder.

Run from repository root `cf2018` using `python -m unittest discover -s coordination/incoming/CF18-05 -p test_addr_response_gate.py -v`.

## Scope / next meaningful gate

The pending QueryAddrInfo request's 64-bit sequence must match the reply. Reply type 2 and result code 0 are independently required for the examined success branch. Yet we still have **no observed real QueryAddrInfo request**, its connector envelope, authenticated Bingo relay or accepted account. A handcrafted status=0 reply is not enough. Avoid synthetic Bingo/session guesses and remote endpoint contact.

Phone v1.4 has already shown AA_DIRECT ACK63 -> client 0x2001/117 -> corrected 0x2002/54 no immediate EOF in two trials, but no third client packet; this test is unrelated and does not advance phone acceptance. Schedules remain paused. CF18-00 may integrate the strict checker as a preflight after review; keep native/phone evidence separate.

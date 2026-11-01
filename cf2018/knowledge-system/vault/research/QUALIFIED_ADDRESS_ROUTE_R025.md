# R025 — Original qualified address RPC and observer false-negative

**Evidence:** Original Apollo ELF SHA-256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, original V3.8 source ZIP SHA-256 `e3bbc31f7b93e738aff0d4205dd0d1418c7abd55b7c17b332ca5d426eb619df2`; verified privately. Neither original file is committed. Native disassembly is static, not original-code emulation or a phone capture.

## Recovered native request-owner connection

The direct original `AddressService::Send_QueryAddrInfo` function constructs a non-strict message name from literal **`QueryAddrSvr:QueryAddrInfo`**, not the previously modeled bare `QueryAddrInfo`. Its original `0x3998e2` literal load and `0x3998e8` PC add resolve to `0x4a81f2`; message begin is the virtual call at `0x399904`. Generated arguments are written by the original call at `0x39991c` to `0x39ed4c`.

A *separate* `0x399940` literal load and `0x399948` PC add resolve to the exact transport route name **`QueryAddrSvr`** at `0x4a820d`. The virtual transport method loaded at `0x39994c` and called at `0x399958` resolves through the original `MsgBuffer` vtable to `MsgBuffer::setServiceName` at `0x3c149a`. This writes field `+0x7c`; `MsgBuffer::writeEnd` loads that same field at `0x3c1f22` and forwards the message pointer/length to the connector callback at `0x3c1f42–0x3c1f46`. This is a concrete *possible* producer of the exact phone route. The phone's actual runtime owner is **not** demonstrated.

16/16 pinned original Thumb instruction checks, both name-literal resolutions and both vtable slots passed in a new local read-only audit. No private disassembly published.

## Correcting the old recognizer assumption

The recovered original message name is 26 bytes and **contains a colon**. Both the public bounded header diagnostic and the exact original V3.8 `legacy_thrift_v37._header_at` reject that colon under a name-character whitelist. In contrast the recovered V3.8 `apollo_wire._parse_rpc_at` parses this qualified legacy-binary message fully.

Two independently synthetic requests using the original grammar, service string sizes 3 and 8, and independently chosen unit IDs, yield **body80/85**, packet sequence MATCH, two METHOD_BYTES_POLICY labels, dedicated legacy classifier not_identified, shared prefix64 and suffix2. Both fully decode from offset4 with the recovered parser, ending at their respective body lengths. All observed *metadata bands* therefore fit without any inserted wrapper. The synthetic values are **not observed phone values**; the phone payload is still withheld.

**Supersedes R017/R021/R023's broad exclusion of unchanged legacy RPC.** Those controls incorrectly used a bare `QueryAddrInfo` method name. Their narrower statement only excludes that bare-name model. The later R023 original parser was functioning according to its own restrictive policy, but that policy was not suitable for all original-native method names.

## Implementation and next falsifier

New [strict exact-qualified parser](../../../experiments/qualified_address_request.py) exports only fixed labels, with [synthetic regression tests](../../../tests/test_qualified_address_request.py); it is not an account/session proof, reply generator, packet capture or server integration.

Next: classify the *existing private routed request* against this exact known qualified message grammar (or obtain a narrowly scoped local-only diagnostic only if no retained request exists). Then verify matching AddressService QuerySession/sequence and its result+reason required decoder fields before any synthetic reply. Until the real phone output is positively recognized, no valid correlated server response or client acceptance is claimed.

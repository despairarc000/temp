# R041 — Exact original QueryAddrInfo positive-path callback trace

Date: 2026-11-01. **Evidence class: ORIGINAL_NATIVE_STATIC, hash-pinned read-only Apollo + offline controls.** Cross-check context: owner's **actual R039 phone negative-control** previously showed that a one-bit-wrong Thrift RPC64 reply no longer precedes 131-byte alternate named-route SYNs. R041 adds **no phone traffic**. No lobby or account authentication is claimed.

## Native artifact and reproducible checks

Original ARM ELF libapollo.so exact SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`; size 5,243,704. Read-only disassembly with `llvm-objdump --triple=thumbv7a-linux-gnueabihf`. Native instruction audit **34/34 original exact Thumb pins PASS**; **8/8 focused tests PASS**, including all mutation negative controls and the private original-file gate. No user captures or private binary in GitHub.

[Audit script](../../../experiments/native_address_callback_audit.py) and [unit tests](../../../tests/test_native_address_callback_audit.py). Optional command in private environment: `CF18_APOLLO_LIBRARY=/path/to/private/libapollo.so python -m unittest -v cf2018/tests/test_native_address_callback_audit.py`. A missing original is intentionally SKIPPED in public source-free testing; fake files cannot pass the original hash gate.

## Stage 1 — receive and queue successful response

Exact symbol `pebble::rpc::AddressService::ProcessResponse(unsigned char const*,int)`, Thumb address `0x39b90c`:

1. `0x39b9f2` calls a `std::map<uint64,QuerySession>::find` and `0x39b9fa` compares to the end sentinel. `0x39b9fc` branches into the session-found path. This establishes **64-bit pending RPC session lookup** at entry, separate from TGCP32.
2. `0x39ba9e–0x39baa2` checks message type `2` and dispatches type-2 response parsing.
3. `0x39bb08` calls `AddressService::Recv_QueryAddrInfo` at `0x399a98`. `0x39bb0e` handles a nonzero parse-error return. `0x39bb10–0x39bb14` specifically checks parsed response `result==0` and branches to the successful-result path at `0x39bb94`. **RPC64 match alone is NOT sufficient** to conclude that the result was valid.
4. The successful branch iterates returned `addr_svr::AddressInfo` records (read at `0x39bbc0–0x39bbc2`). At `0x39bbee` it calls `IsDomainName`; at `0x39bc08` a service-instance configuration byte `[this+0x7d]` gates special numeric-IP handling, including original `NTX::IsNumericIPv4Notation` at `0x39bc12`. Thus numeric 127.0.0.1 address behavior is **conditional**, and this code does not establish the runtime setting of that flag.
5. At `0x39bd6a`, the empty-address branch can directly invoke a stored callback and clean the pending entry (`0x39bd7e`, `0x39bd90`). The nonempty-address path creates `ResponseInfo` and enqueues it in `[this+0x68]` at `0x39bde4–0x39bdea`. **The callback timing/path differs depending on returned address content.**

## Stage 2 — deferred DNS and waiting-caller callback

Exact `AddressService::ProcessResponse()`, Thumb address `0x39c164`, is a **different overload** from the buffer-receive method. It walks pending `ResponseInfo` objects stored at offsets `[this+0x68]/[this+0x6c]`:

1. `0x39c1b4` re-finds the original QuerySession by RPC64, comparing result to pending-map end at `0x39c1bc`.
2. `0x39c1fc` starts an address/result-list loop. When needed, it invokes `AddressService::DNS` at `0x39c21c` to turn domain-style addresses into endpoint strings.
3. `0x39c2c2` invokes the saved `std::tr1::function<void(int,std::vector<std::string>*)>` callback (through the shared operator at `0x3997b8`), then `0x39c2ca` erases the pending QuerySession and `0x39c2d0` updates the address-service cache.
4. `AddressService::Update(long long)` calls this deferred processor at **`0x39da20`**, following `ProcessRequest()` at `0x39da0c` and `ProcessTimeout` at `0x39da16`. This proves how the queued result is drained, not that the game Update loop actually reached the call in R037.

## Caller-facing API and the unknown ten-byte route

`AddressService::GetServiceAddress(std::string const&, std::tr1::function<...>)` at `0x39d18c` explicitly accepts **a caller-supplied service string and callback**. It distinguishes direct name/address versus lookup, and `0x39d22a–0x39d232` can construct a service address list when needed. These are library services, not application-specific assertions. The GCloud/NApollo connector uses named-route data, but **the 10-byte destination name observed on the owner's phone is still unknown**. The Apollo address-library code alone does NOT prove which caller selected it or which service it denotes. Don't invent a service name from length.

This is a more specific, source-verified explanation of the R037/R039 A/B observation: a correct Thrift RPC64 **can find the waiting QuerySession and reach the successful-result processor**, while the deliberately wrong RPC64 cannot match that pending QuerySession. However, neither branch was actually instrumented inside the running phone. A matched sequence is **necessary but not sufficient** for complete real-game reply acceptance. R037 behavior is strong indirect evidence, not a demonstrated callback trace.

## Next highest-value work

1. Locate the application-side caller of `GetServiceAddress(serviceName,callback)` and identify the 10-byte route from its actual configuration or original application binaries. Do not infer service identity from 10-byte length alone.
2. Establish the return address endpoint and native route-specific SYN/ACK contract before acknowledging the 131-byte SYN. Current 63-byte ACK is golden-QueryAddrSvr specific.
3. Only if native/application evidence cannot resolve this, prepare a privacy-preserving, **single** phone report comparing known static service-name candidates; no raw route names, auth tokens or arbitrary packet dumps.
4. Do not rerun R039 or claim successful game authentication, service acceptance, lobby, TDM or bots.

**State: R041 original static callback path verified; downstream application caller and real runtime callback still unverified.**

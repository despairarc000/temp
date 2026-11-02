# R083 — Conditional per-handle GCloud DH state and ACK key dependency

**2026-11-02. EXACT OWNER-ORIGINAL STATIC CALLGRAPH + SOURCE-FREE CI.** Continues R082's verified IConnector Connect path. No second-service ACK was generated or sent.

## Connect creates and initializes a CTGcp transport object

In original `CGCloudConnector::connectTConnd`:
- `0x3c6950` allocates a CTGcp-sized object (`operator new`); `0x3c6956` calls its constructor.
- It has two branch-specific `CTGcp::Initialize` callsites: `0x3c6a70` and `0x3c6bd4`.
- It applies the named route through `CTGcp::SetRouteInfo` at `0x3c6c4a`, then calls `CTGcp::Start` at `0x3c6c86`.
- `CTGcp::Initialize` creates a GCloud TGCP handle and calls `gcloud_tgcpapi_init`.

Thus a Connect invocation builds a new CTGcp transport object and enters the GCloud handle initialization path. The two Initialize sites are alternative branches, not evidence of two independent successful sessions.

## DH setup is conditional on a nonempty parameter string

Original `gcloud_tgcpapi_init` calls `gcloud_tgcpapi_set_dh` at `0x3a7fca`. This small wrapper has pointer/first-byte gates and a Thumb **B.W tail branch** at `0x3a7e3c` to `gcloud_tgcpapi_set_dh_info` at `0x3ac4b0`. If the supplied string is empty, the wrapper takes its clear/no-DH path instead of entering that setup routine.

On the nonempty path, `gcloud_tgcpapi_set_dh_info`:
- allocates a DH object (`DH_new`);
- creates/parses the group parameters (BN operations including `BN_hex2bn`);
- calls **`DH_generate_key`** at `0x3ac5e6`.

The SYN sender calls `tgcpapi_generate_dh` at `0x3abaa0`. That helper constructs the RawDH request and serializes the local DH public component using the BN bit-length/byte-conversion calls. The actual keypair generation is earlier, during DH setup, not in the serialization helper.

## ACK key mode uses the current handle's DH context

The original receive path is:
1. `OnStateKeySyning` calls `gcloud_tgcpapi_recv_ack_msg` at `0x3a9fb0`.
2. The ACK receiver enters `gcloud_tgcpapi_recv_and_decrypt_pkg`.
3. Its mode-3 key-response branch calls `tgcpapi_compute_k` at `0x3abef2`, then `tgcpapi_set_key` at `0x3abefe`.
4. `tgcpapi_compute_k` parses the ACK's RawDH response, calls `DH_compute_key` at `0x3abdc8`, then MD5 at `0x3abdf4`.
5. When ACK processing succeeds, `OnStateKeySyning` calls the auth-request sender at `0x3a9fd8`.

The other ACK key modes are not interchangeable with mode 3: the existing R060/R061 receiver analysis documents mode 0 (no key setup), mode 2 (direct key material), and mode 3 (DH-derived key). Which mode the owner's observed second service actually uses is **not established**.

## Practical consequence for the second service

If the second service's active CTGcp configuration supplies a nonempty DH parameter string **and** its ACK selects mode 3, the ACK's RawDH response must compute against the current handle's local DH state. A 63-byte ACK from the first service cannot be assumed reusable for that connection. If the parameter string is empty or the ACK uses another mode, the dependency is different; this report does not guess which applies to the phone.

The R077 route-name equality (3/3) is not key-exchange evidence. The sanitized phone comparison did not establish the second SYN's DH parameter configuration or ACK key mode. **Do not send the reference ACK again yet.**

## Verification

- [R083 original-binary auditor](../../../experiments/r083_gcloud_dh_ack_dependency.py) verifies exact original SHA/size, the conditional B.W wrapper, 12 function identities, and 17 direct-call target groups across Connect, CTGcp initialization, DH generation, SYN, ACK and auth transition.
- [R083 tests](../../../tests/test_r083_gcloud_dh_ack_dependency.py) cover branch mutation, missing DH/key/SYN/ACK/auth edges, function identity, owner and no-network controls.
- CI [41390159104](https://github.com/despairarc000/temp/actions/runs/41390159104): **SUCCESS — 690 tests, 154 skipped**. The private-original Python audit is skipped in public CI; the exact owner-original binary was inspected in memory during this investigation.

## Still unknown

- Whether the owner's actual second-service CTGcp initialization supplies a nonempty DH parameter string.
- Which ACK key mode the second service expects.
- Whether Android actually executed this original Connect path for the R077 SYN.
- Whether any valid second-service ACK is accepted, and whether authentication/lobby/gameplay follow.

Next offline discriminator: trace the `CTGcp::Initialize` arguments back to the connector's initialization/auth-info structure and establish the actual DH-string source and key-mode configuration. No new phone scan is required for that step.

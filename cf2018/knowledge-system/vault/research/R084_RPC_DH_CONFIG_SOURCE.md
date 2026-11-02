# R084 — RPC's default empty string reaches GCloud's conditional DH setter

**2026-11-02. EXACT OWNER-ORIGINAL STATIC CODE REVIEW + SOURCE-FREE REGRESSION CONTROLS.** Continues R083. No live phone or fake-server test, ACK generation/transmission, client modification, account login or bot gameplay.

## The newly resolved configuration-source gap

The previous [R083](R083_GCLOUD_DH_ACK_DEPENDENCY.md) proved that GCloud's `gcloud_tgcpapi_set_dh` only enters DH keypair setup for a nonempty string, and that mode-3 ACK processing uses the current connection's DH context. R083 did not know the source of that string.

For the **particular** original `pebble::rpc::RpcConnector::CreateConnection` -> `GCloud::CGCloudConnector` path verified in R080–R082, original ARM Thumb instructions now establish:

1. `RpcConnector::CreateConnection` constructs local `_tagConnectorInitInfo` storage. At `0x3c5020`, `r0` is set to local init-info base **+0x10**; at `0x3c5032`, it calls `AString::AString()`, the **default string constructor**. At `0x3c511c/0x3c5122`, the constructed init-info is handed to the connector's virtual `Initialize`.
2. `CGCloudConnector::Initialize` loads the input's **+0x10** string, addresses its own string at **+0x3c**, and invokes `AString::operator=(AString const&)` at `0x3c6148`. Thus the initialized config string is copied into the connector's owned field.
3. Each of the two alternative `CGCloudConnector::connectTConnd` branches addresses connector **+0x3c**, calls `AString::c_str()` at `0x3c6a52` / `0x3c6bb6`, saves its pointer at **[sp+0x14]** (`0x3c6a5c` / `0x3c6bc0`), and calls `CTGcp::Initialize` (`0x3c6a70` / `0x3c6bd4`).
4. `CTGcp::Initialize` calls `gcloud_tgcpapi_init` at `0x3a3ef6`; the latter loads its DH string argument at `0x3a7fc8` and calls `gcloud_tgcpapi_set_dh` at **`0x3a7fca`**. R083 pins the latter's nonempty-parameter gate.

The source chain therefore has a **default-empty DH configuration** in this specific RPC constructor. It is materially stronger than only showing that a DH setter exists. It makes a DH mode-3 requirement on this specific unchanged constructor path **unsupported**, not logically impossible in every runtime configuration.

## Important conditional limits

- The source audits identify the default-constructed `AString` and its propagation. They are **not an exhaustive run-time alias/mutation proof**: another path, configuration override, or mutation before `Connect` can still be investigated. The exact Android second connection has not been instrumented to prove the complete object instance and argument value.
- A nonempty actual DH string would still activate the R083 keypair generation path.
- The received **ACK itself** carries the mode selector. Modes 0 and 2 are distinct; a client-side default string does not tell us which mode a server will select, whether its key material is acceptable, or whether later encrypted auth/account responses are valid.
- R077's three phone 10-byte route names matched the CTDir native literal, and all three changed SYN field 5 (unit ID); they all received **zero second ACK** because the observer was intentionally `HOLD_NO_ACK`. `REFUSED` was local comparison policy, not a native phone/server rejection.
- We have **not** demonstrated that the original 63-byte first-service ACK is safe or valid on the second service. It must not be replayed based solely on string configuration or static route equality.

## Tests and independent evidence

[Audit code](../../../experiments/r084_rpc_dh_config_source.py) verifies the exact private-original SHA/size, a fixed set of original instruction halfwords for initialization/copy/two call branches/DH handoff, six original function identities and nine exact direct callsites. It outputs only static boolean/enum labels, never route bytes, keys, credentials or original code.

[Source-free tests](../../../tests/test_r084_rpc_dh_config_source.py) exercise all instruction-pin mutations, function-identity mismatch, missing string-constructor/copy/both branches/DH setter, wrong caller owner, safe extra callers, invalid original, and no networking/ACK generation. The exact-original audit remains **explicit opt-in**, skipped on GitHub CI unless `CF18_APOLLO_LIBRARY` is set; there is no proprietary game binary in the repository.

An in-memory read of the owner's connected original `libapollo.so` (5,243,704 bytes, original file identity unchanged from R083) independently matched **24** selected instruction halfwords in this investigation. This is a subset check, distinct from public source-free tests and the optional full hash-gated Python audit.

## Next falsifiable offline action

Trace the **full SYN RawDH request presence/absence** when the GCloud handle has no DH object, and the **mode-0 versus mode-2 receiver predicates** using bounded, synthetic native emulation with sends suppressed. That can determine which ACK strategies remain structurally possible, **not** establish what an actual second-service server expects. Keep any phone ACK experiment separately user-authorized, limited and disabled by default. No new phone run is justified by R084 alone.

**State: configuration source on a specific native path = supported; actual phone DH string / ACK mode / second ACK / login / gameplay = UNKNOWN.**

# R070: ordinary application fields can explain the extra SYN change

2026-11-01 UTC. CONFIRMED_NATIVE_STATIC and original-code emulation with synthetic input and explicit stubs. No phone test, next-service ACK acceptance or login. Original private Apollo independently rehashed to `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8` (5243704 bytes).

R069 phone evidence establishes one additional same-length SYN field change, but does not identify it. This continuation tests the competing explanation that an ordinary application attribute changes while the existing ACK remains parseable.

## Original sender-to-wire mapping

Original GCloud SYN builder `0x3aba5c` copies three handle attributes into the outgoing structure beginning at handle+0x2340:

| SYN field | Original native schema name | Input handle offset | SYN object offset | Original write evidence |
|---|---|---|---|---|
|4|llGameID|+8, int64|+0x410|sender0x3abb0c–1e; serializer tag0x40 at0x3b28a6, load0x3b28b8, writeVarInt64 at0x3b28bc|
|5|iUnitID|+0x10|+0x418|sender0x3abb26–2c; serializer tag0x50 at0x3b28c8, load0x3b28d6, writeVarInt32 at0x3b28da|
|6|iClientType|+0x114|+0x41c|sender0x3abb34–3c; serializer tag0x60 at0x3b28e6, load0x3b28f4, writeVarInt32 at0x3b28f8|

Names independently resolved from original `TGCPSynHead::visualize` literals via PC-relative loads at0x3b33fe/0x3b341e/0x3b343a. These are application attributes, not the separate key-method/key-info/encryption fields1/2/3.

## Actual original-code controls

New `application_prefix` in `native_syn_ack_handoff.py` executes the original SYN builder with controlled synthetic values, then the original field1..7 serializer at0x3b2826 in a fresh identical-address context. It deliberately stops at0x3b293e before field8; no full SYN packet or real account data is generated. Independently varying one attribute from0 to1 changes exactly field4,5 or6, respectively, with unchanged encoded length. All other serialized prefix fields, including key/encryption fields, remain identical.

The existing whole ACK/key-sync control is then run on each separately prepared synthetic connection. All three application changes still consume the same63-byte synthetic ACK and reach the suppressed auth-send boundary (sentinel-77). This executes actual gathering/header/ACK logic, but does not run auth construction. **Two new test methods/six mutation cases PASS; existing three native handoff methods/seven cases PASS.** Private-source tests skip in public CI without explicitly supplied original/dependencies.

Explicit boundaries: outgoing SYN pack/encrypt/send suppressed; bounded strncpy and libc/log helpers stubbed; prepared handle transferred between fresh emulator instances; network no-new-data stub; auth send suppressed. Earlier attempt to serialize the complete SYN hit an unresolved Android library-call boundary; the bounded prefix control avoids that boundary. Full original SYN serialization is not claimed.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=cf2018/private/analysis_deps CF18_APOLLO_LIBRARY=/absolute/path/to/original/libapollo.so python -m unittest discover -s cf2018/tests -p test_native_syn_application_fields.py -v
```

## Consequence

The additional changed field in R069 is **not automatically evidence of a key/security mismatch**. At least three ordinary application changes reproduce the same-length-change pattern and are compatible with the ACK boundary in this synthetic configuration. This does not identify which field changed on the phone, establish the actual application's security settings, or justify ignoring arbitrary fields. The gate stays unchanged. Next trace who supplies these attributes to AddressService versus the next connector; use the already prepared value-free field-number diagnostic only if that source trace cannot distinguish them. No new phone test requested in this continuation.

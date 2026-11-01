# Diary — page010, current

Previous [page009 archive](diary/009.md): R064–R069. See [current status](vault/CURRENT.md).

## R070 — [FINDING] Ordinary application attributes reproduce extra SYN change (2026-11-01 UTC)

**Original-native static/emulation with stubs; synthetic inputs.** Rehashed original Apollo. SYN serializer fields4/5/6 map to llGameID/iUnitID/iClientType: tags0x40/50/60 at0x3b28a6/28c8/28e6; names independently resolved from visualize literals. Original SYN builder copies handle+8/+0x10/+0x114. Actual builder plus serializer prefix(field1..7, stop0x3b293e) shows each0→1 synthetic attribute change modifies only its corresponding field at unchanged encoded length; key/encryption fields unchanged. Each prepared context still consumes the same63-byte synthetic ACK and reaches suppressed auth-send.2 new methods/six mutation cases PASS; existing3 handoff methods/seven cases PASS. SYN pack/send, libc/log/network boundaries and auth send stubbed as documented; complete SYN serialization not claimed. R069's extra field therefore need not be a key mismatch, but actual phone field remains UNKNOWN. No gate relaxation or phone test. NEXT trace application-attribute suppliers for discovery versus next connector. [Proof/commands](../cf2018/knowledge-system/vault/research/NATIVE_SYN_APPLICATION_FIELDS.md).

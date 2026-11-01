# R069: phone context mismatch, no second-service ACK attempted

2026-11-01 UTC. Owner-uploaded `CF2018_SECOND_SERVICE_ACK_Result.txt`, SHA256 `749bbc40282fe794cf6dad915ab0db1029872318340dbba524a5f66d5b38710f`. PHONE OBSERVATION separated from source interpretation and synthetic validation. No game login/session/second-service ACK acceptance.

| Property | Slot1 | Slots2–4 |
|---|---|---|
| Client first frame |133-byte reference SYN |131-byte named-route SYN |
| ACK sent |63 bytes |0 |
| Auth requests observed |One0x2001 |None |
| Address response |One169-byte candidate written |None |
| SYN_CONTEXT |REFERENCE_EXACT |REFUSED |
| Route comparison |Reference |Named variant4, name shorter by2 |
| SYN non-route same-length modified count |0 |1 each |

All three reconnects retained base field shapes; base length changes empty and same-length modified count0. SYN length change was field14/-2; other tag/kind sets unchanged. Crucially, `syn_same_length_modified_count=1` in all three reconnects. The supplied R036 `_deltas` counts a changed value only when that field's encoded length and kind stay equal. Field14 has changed encoded length, so it cannot account for that count. At least one additional non-route SYN field differs from the private reference. Its number/type/value were not exported; the report cannot identify it.

Thus the one-ACK hypothesis was **not tested on this phone run**: the matching precondition failed and the handler held all three connections. There is no ACK_WRITTEN event for the second service. This is neither phone rejection of the63-byte ACK nor evidence of successful authentication. The report does not establish the extra opt-in's environment value, which is unnecessary to explain the observed hold because context refusal already prevents the ACK.

## Next narrowly scoped diagnostic

Standalone `tools/prepare_syn_difference.py` validates the exact one-ACK handler and gate hashes, creates a separate copy, adds only changed field-number/type lists and a fixed reason to SYN_CONTEXT, and hard-disables the second ACK even if its environment flag is YES. First-stage exchange/address response remain unchanged. New report: `CF2018_SYN_DIFFERENCE_Result.txt`; old result paths retained. The field values, names, hashes and raw frames are not exported. Output lists are bounded by the existing48-field parser.

Four source-only label tests PASS, including same-length opaque-field and base-value mutations with no canary leakage. The actual R037 two-connection loopback lifecycle test PASS with the ACK environment flag deliberately YES: the new diagnostic still sends no second ACK. All113 original prepared-copy regressions PASS; both knowledge doctors PASS. No new phone diagnostic run has happened.

Only after identifying the changed field should native source establish whether it is security material, an application attribute or ordinary per-connection state. Do not ignore that field or loosen the gate merely to obtain an ACK attempt.

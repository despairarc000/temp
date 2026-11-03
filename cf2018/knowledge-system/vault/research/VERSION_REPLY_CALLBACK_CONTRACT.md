# R103 — Version method, response schema and callback predicates

2026-11-03 (Asia/Manila). Original-source research and isolated local controls only. No server packet was constructed/sent or phone experiment run.

## What the earlier phone behavior does and does not establish

The owner reported a quicker Loading→resource-check transition, untimed; the check later errored. The settings report establishes a223B write, not an observed managed callback or successful configuration application. Original directory code also has a30s timeout→finish path. **HYPOTHESIS:** the reply shortened an earlier wait. **UNKNOWN:** timing/cause, whether this exact callback ran, or acceptance of all replies. Screenshot/code154140712 maps to the separately investigated native updater wait budget; no login/lobby/resources-complete claim follows.

## Exact source method and updater instance

**CONFIRMED_NATIVE_STATIC:** Exact Apollo5,243,704B/SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, ARM32/Thumb, reverified by each NativeControl. Generated sender `VersionUpdateClient::send_ReqUpdateVersion` **0x33e400** loads its method-name string via literal0x33e51c plusPC0x33e41a: **VersionUpdate:ReqUpdateVersion**. This is a direct source operand, not a string-scan ownership inference. It increments the connector's64-bit sequence at0x33e428/432 and passes that to writeMessageBegin0x33e440. Method1 request serialization calls pargs::write0x33dc88 at0x33e45c.

The updater builds its own RpcConnector in run0x32fbe2, initializes it at0x32fc74, constructs VersionUpdateClient at0x32e6f8 and fills ReqVersionUpdate at0x32e7ac. Init has signature `(string, ConnectCfg, int, PROTOCOL_TYPE, int)`, with observed arguments8/32/8192 at this callsite; enum meanings are not guessed. This does not identify the phone's later request, destination or actual pending registration. It is a separate service method from DirService's settings query.

## Writer schema and permissive nested reader

**ORIGINAL_NATIVE_EMULATION / SYNTHETIC_ONLY:** Actual generated `ResVersionUpdate::write` **0x33bef8** executes on a zeroed synthetic object, with protocol recursion limit64 and a synthetic vtable that records typed schema events, not bytes. With presence flags0 it emits:

| Struct | Field ID | Name | Native protocol type |
|---|---:|---|---|
| ResVersionUpdate |1|result|I32/8|
| ResVersionUpdate |2|comm_info|STRUCT/12|
| UpdateCommInfo |1–4|seq, product_id, product_type, req_type|I32/8|
| UpdateCommInfo |5–6|apk_version, res_version|I64/10|
| UpdateCommInfo |7|business_data|STRING/11|

Enabling synthetic optional flags at object+0x9c additionally emits ResVersionUpdate update_info/field3, app_id/4, region_id/5, custom_cfg/6. VersionUpdateInfo contains package_info/STRUCT1 and update_type/I32-2. VersionPackageInfo contains version/I64-1 and name/description/http_url/md5sum/custom_str STRING2–6. CustomCfg contains level/I16-1, cfg/STRING2, original_len/I32-3. These are schema labels only; no original endpoints, IDs or assets are exported. Synthetic protocol events do not establish complete wire encoding or valid semantic contents.

Actual pointer-result reader **0x33ddfc**, including nested ResVersionUpdate::read0x33caf4, executes on bounded independent component bytes. Five-byte field0 STRUCT containing an empty result is consumed completely, sets the outer success-presence bit and leaves result0/inner presence flags0. Twelve-byte component explicitly containing result/I32 field1=0 sets inner flags1; it still omits comm_info/update_info. Outer STOP only leaves success absent. Truncation is refused by the bounded input provider, not claimed as a native exception test.

Thus **fields emitted by the normal writer are not necessarily enforced as present by this nested reader**. A parsed empty object is not a complete usable version response. Full header/message dispatch, pending correlation and expected product/version contents remain separate requirements; no empty reply is proposed for the phone.

## Actual callback decision

`gcloud_version_action_imp::ResUpdateCallBack` **0x32d864** checks RPC status at0x32d886, then ResVersionUpdate.result at object+4 /0x32d8da–dc. Either nonzero sets failure byte self+0x66 at0x32d934 and does not set completion byte self+0x65. Both zero take version handling0x32d93a, response assignment0x32d9b8 and string assignment0x32d9c2, clear failure byte0x32d9b2, then set completion byte0x32d9ca.

Original callback code executes on synthetic scalar statuses. RPC1/0xffffffff with result0 fails; RPC0 with result1/0xffffffff fails. RPC0/result0 reaches the two assignment boundaries and completion. Failure cases use original branch/store/epilogue code with disabled logger state. Success substitutes version-number text conversion, ResVersionUpdate assignment, GNU string assignment and temporary destruction. The original assignment implementation, useful package contents, CreateNextAction, download/integrity decisions and Android are **not executed**. This is callback predicate proof, not full updater/phone acceptance.

## Verification and next bounded check

Ten methods PASS: public input guard, exact generated method, two writer-presence schemas, three component-reader controls, and three callback groups covering five scalar cases. Command: `CF18_APOLLO_LIBRARY=<private original> PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=cf2018/private/analysis_deps python -m unittest discover -s cf2018/tests -p test_native_version_callback.py -v`. Source-free command yields1 PASS/9 SKIP. Initial isolated fixtures lacked recursion-limit/runtime setup; those were corrected without modifying original code. No earlier server baseline was relabeled as rerun. Knowledge doctors remain blocked by local snapshot omissions; no CI success claimed.

Public [controls](../../../experiments/native_version_callback_controls.py), [tests](../../../tests/test_native_version_callback.py). A further static pass through CreateNextAction0x32f35c finds its initial configuration virtual-slot0x2c selector: values20/22 branch to0x32f3ca,21/23 to0x32f734, and other values to0x32fa5a. These numeric groups are source predicates, not identified phone modes or a no-update recipe. Configuration selection therefore remains part of interpreting a successful callback.

**Next:** trace ResVersionUpdate assignment/`CreateNextAction`0x32f35c and its version/update-type/package-presence decisions, then the generated receiver's status/pending correlation before selecting a version reply. Current transport observation remains unidentified. No new owner test is needed for this source work; unique result filenames and paused schedules remain in force.

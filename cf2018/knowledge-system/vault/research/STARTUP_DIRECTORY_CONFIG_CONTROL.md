# R097 — Correlated default startup-directory configuration control

2026-11-02. Latest phone evidence remains R095's complete legacy64 BY_ID request and R096's Loading screenshot. **No new phone run, accepted directory response, authenticated account, lobby or gameplay.**

## Managed source: empty configuration has a defined fallback

**CONFIRMED_MANAGED_STATIC.** Exact original DLL SHA256 `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9` checked before in-memory metadata inspection; no game-file write or CLR execution. R096's unresolved MethodSpec `0x2b0016a0` resolves to `WNEngine.JsonTool.Deserialize<WNLogin.VersionCustomRoot>`. ECMA table43 resolution includes the 28-byte Assembly row, coded-index widths and complete table-stream boundary (2 bytes padding); generic blob is checked as one class TypeDef argument. The existing private managed inspector is a prerequisite, not evidence of public original-binary access.

More useful than guessing JSON: `VersionCustomData.SaveData` token `0x0600aa22` initializes local7 to null at IL0xcd; calls `String.IsNullOrEmpty` at0xd2; brtrue0xd7 jumps to0x111, bypassing parser call0xde. Local7 remains null, brtrue0x113 is untaken, and constructor0x118 creates `VersionCustomRoot`, stored back into local7. Eight source predicates checked. The initial verifier guessed the wrong local slot; inspection corrected it to7 before PASS. This is source validation, not managed execution.

[R096](LOADING_DIRECTORY_CONSUMER.md) established the selected source node ID `0x01010100`, native-custom UserData→managed appAttr mapping, constructor with no explicit notice-URL assignment, and empty-notice finish branch. Another GameNoticeDownloader consumer exists. These static facts do not uniquely identify the phone callback or promise a screen transition.

## Native controls on non-sensitive synthetic data

**CONFIRMED_NATIVE_EMULATION, SYNTHETIC_ONLY inputs.** Original Apollo SHA256 `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`, ELF32 ARM/Thumb checked by NativeControl for every fresh instance. No original code patch or live socket.

- Actual `TreeNodeEntry::pack`0x36eca6 emits a 47-byte category node with ID0x01010100 and empty name/custom data. `CreateTreeNode`0x370bf4 reads it and copies the selected ID into observed wrapper+0x1c. Constructor/destructor/AString/AArray boundaries are substituted; assignments are observed and explicitly nonempty in count. Not a complete managed object conversion.
- Actual generated result writer0x369f28 emits a 97-byte component: present field0 success, result0, reason empty STRING, one SingleDirTree with node_count1/tree_bin47B/empty account_info. Independent server writer matches byte-for-byte. Ordinary0x36a7a4 and pointer0x36a860 result readers consume97B and set success presence. Missing outer success stays absent.
- Segmented full-frame control executes original GCloud receive0x3abe34, bridges its output into original binary readMessageBegin0x39c78c, then pointer result reader0x36a860. A synthetic227-byte frame preserves method/type2 and RPC sequence0x100000002, returns the selected tree and consumes the full145-byte RPC body. Size227 is this example, not a phone-size prediction. Read/string/allocation/destructor boundaries are functional/bounded substitutes. No whole MsgBuffer/std::function/Android dispatch execution.
- Separately, original RpcConnector::ProcessResponse0x3c382c performs its real one-node pending-tree lookup and both-word sequence comparisons. Exact64-bit sequence reaches callback-map access/callback/erase boundaries. Same low32/different high32, different low32 and truncated32-bit sequence skip instead. Callback invocation/erase are substituted: no actual pending registration or callback acceptance claim.

The server response has no client-side4-byte packet-sequence prefix in its RPC body. Independent transport packet sequence and full64-bit RPC sequence are echoed only in memory, never in reports. Synthetic PRIVATE!/ABC argument canaries do not appear in the reply; a packet-prefix/header mismatch refuses generation.

## Bounded owner-run test

**HYPOTHESIS:** one source-selected category with empty settings can exercise the default startup configuration path and reveal the next client action. This is an experiment, not a recovered original server directory. No invented JSON flags, endpoints, accounts or game files.

`tools/prepare_directory_config.py` copies only the exact SHA-pinned R094 prepared identifier handler and helpers into a new output; embeds the reviewed reply module so only this script needs downloading. Default source `~/cf2018_directory_identify`; `--print-library` verifies the existing private original by SHA. Preparation starts no listener.

Explicit `CF2018_R037_LIVE_REPLY=YES`, `CF2018_DIRECTORY_CONFIG=YES` and `--live-opt-in` remain necessary. Existing discovery reply, exact CTDir route/unit-only comparison, clear security checks and one-connection budget remain. Only BY_ID_COMPLETE/LEGACY64 receives one application response. Other methods, disabled flag, no prior discovery, changed security and budget reuse hold. After the first subsequent frame, only fixed metadata/classifier labels are reported and no further application answer is sent. A deadline or later deliberately closed connection is not proof of client rejection. Four-session/run and existing time limits remain.

Report: `~/storage/downloads/CF2018_DIRECTORY_CONFIG_Result.txt`. Owner should also say whether Loading changes, remains, or an error appears. The bounded falsification is whether the qualified request receives CONFIG_REPLY_WRITTEN and what frame/UI follows. No follow-up or an unchanged screen leaves callback/semantic acceptance unresolved; do not invent another response immediately.

## Verification

- 8 reply/native test methods PASS (five require private original/parser source).
- 7 actual loopback lifecycle methods PASS, including one reply then no second answer, other valid directory method refused, disabled/no-discovery/security/budget controls.
- 4 copy/preparer methods PASS; original source unchanged and edited source refused.
- 2 managed test methods PASS, including eight exact-source predicates and wrong-build refusal.
- Existing native node suite6 PASS; existing prepared baseline113 PASS. Prepared root focused suite30 PASS with one optional class SKIP (not part of113).
- Both local knowledge doctors ran but report historical files omitted from this local snapshot. All86 distinct missing targets were verified present in the complete current GitHub main tree; the seven new report links resolve locally. This is a local snapshot limitation, not a claimed doctor PASS. No new remote CI result claimed.

Reproduce locally from repository root with PYTHONDONTWRITEBYTECODE=1. Set CF18_APOLLO_LIBRARY to the exact private original and PYTHONPATH to private analysis dependencies plus cf2018/experiments for native tests; CF18_DIRECTORY_IDENTIFY_PREPARED to the pinned identifier copy; CF18_DIRECTORY_CONFIG_PREPARED to the newly prepared copy; CF18_MANAGED_LIBRARY to the exact original DLL. Run unittest discover in cf2018/tests for test_directory_config.py, test_directory_config_lifecycle.py, test_directory_config_preparer.py and test_managed_directory_config.py separately. Without explicit originals/prepared files, private cases skip and must not be reported as native PASS.

Source: [reply](../../../experiments/directory_config_reply.py), [native result](../../../experiments/native_directory_result_controls.py), [pending correlation](../../../experiments/native_directory_pending_controls.py), [segmented receive](../../../experiments/native_directory_reply_pipeline.py), [managed source checks](../../../experiments/managed_directory_config_metadata.py), [preparer](../../../tools/prepare_directory_config.py).

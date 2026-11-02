# Diary — page014, current

Previous [page013 archive](diary/013.md): R091–R095. See [current state](vault/CURRENT.md).

## R096 — [FINDING] Loading directory callback consumes startup configuration and filters platform nodes (2026-11-02)

**PHONE_VISUAL:** Owner screenshot remains at Loading; no visible login/menu advance.

**CONFIRMED_MANAGED_STATIC:** Exact original DLL SHA `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9` verified before read-only in-memory inspection. StartFlow token0x0600a7ec shows loading and binds OnDirCallback to IApolloDir.QueryDir. Callback0x0600a7f1 saves VersionCustomData, then reads HTTP/notice settings and can finish on empty notice URL. ConvertNodeList0x06009c6b maps CustomData.UserData→staticInfo.appAttr; SaveData0x0600aa22 filters source node IDs0x01010100/0x01010300. Current-platform getter0x0600aa26 selects0x01010100. Eleven source checks PASS; no managed execution or original file edits. A separate GameNoticeDownloader query path means exact phone callback remains UNKNOWN. [Proof/limits](../cf2018/knowledge-system/vault/research/LOADING_DIRECTORY_CONSUMER.md).

NEXT resolve configuration parser/defaults and native node-property mapping before preparing another directory response/test. No new phone run, invented payload, accepted directory response, authenticated account or gameplay. Page013 archived intact before exceeding8KB.

## R097 — [FINDING] Empty startup settings select defaults; correlated directory reply passes offline controls (2026-11-02)

**CONFIRMED_MANAGED_STATIC:** Original DLL hash verified. SaveData0x0600aa22: IsNullOrEmpty0xd2/brtrue0xd7 bypasses parser0xde, leaves local7 null, invokes VersionCustomRoot constructor0x118. MethodSpec0x2b0016a0 resolves JsonTool.Deserialize<VersionCustomRoot>; eight exact-source predicates PASS.

**SYNTHETIC_ONLY / ORIGINAL_NATIVE_EMULATION:** Hash-verified Apollo writer emits97B result containing47B selected node0x01010100; independent bytes match. Both result readers and segmented GCloud/RPC/result parsing pass. Original ProcessResponse0x3c382c rejects wrong64-bit high/low words; callback/runtime boundaries remain substituted.21 new test methods PASS; existing node6/baseline113 PASS. Doctors blocked by86 local snapshot omissions, all verified present on GitHub. [Proof, limits, test](../cf2018/knowledge-system/vault/research/STARTUP_DIRECTORY_CONFIG_CONTROL.md).

**HYPOTHESIS, not phone finding:** one selected category with empty settings may advance startup. Copy-only opt-in preparer permits one qualified response. NEXT owner run/report plus screen outcome. UNKNOWN actual managed callback, semantic acceptance/login/gameplay; no phone run performed.

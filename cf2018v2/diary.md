# Diary — page014, current

Previous [page013 archive](diary/013.md): R091–R095. See [current state](vault/CURRENT.md).

## R096 — [FINDING] Loading directory callback consumes startup configuration and filters platform nodes (2026-11-02)

**PHONE_VISUAL:** Owner screenshot remains at Loading; no visible login/menu advance.

**CONFIRMED_MANAGED_STATIC:** Exact original DLL SHA `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9` verified before read-only in-memory inspection. StartFlow token0x0600a7ec shows loading and binds OnDirCallback to IApolloDir.QueryDir. Callback0x0600a7f1 saves VersionCustomData, then reads HTTP/notice settings and can finish on empty notice URL. ConvertNodeList0x06009c6b maps CustomData.UserData→staticInfo.appAttr; SaveData0x0600aa22 filters source node IDs0x01010100/0x01010300. Current-platform getter0x0600aa26 selects0x01010100. Eleven source checks PASS; no managed execution or original file edits. A separate GameNoticeDownloader query path means exact phone callback remains UNKNOWN. [Proof/limits](../cf2018/knowledge-system/vault/research/LOADING_DIRECTORY_CONSUMER.md).

NEXT resolve configuration parser/defaults and native node-property mapping before preparing another directory response/test. No new phone run, invented payload, accepted directory response, authenticated account or gameplay. Page013 archived intact before exceeding8KB.

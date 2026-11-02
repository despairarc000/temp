# R096 — Loading-screen directory consumer and configuration-node filter

2026-11-02. Evidence classes: **PHONE_VISUAL** and **CONFIRMED_MANAGED_STATIC**. No managed/game execution or new directory response.

## Visual observation

Owner screenshot381290.jpg shows the original game still at its illustrated Loading screen, with Termux above it. It establishes no menu/login/lobby advance. Visible port80 PASSTHROUGH log lines do not independently identify the directory connection or explain a failure. No screenshot or private traffic is committed. R095's complete BY_ID request identification remains the latest structured phone evidence.

## Exact-original managed source

Read-only existing managed_call_trace.Metadata inspected the local authorized original Assembly-CSharp.dll. Exact SHA256 `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9` checked before in-memory decoding. No DLL/APK write, integrity patch, raw method dump, credential extraction or game launch. Original metadata contains75,087 methods. Calls were decoded with operand-aware CIL walking; method/field tokens below are build-specific.

- `WNGameBase.WNLoading.LoadingFlowLoginCheckTdirController.StartFlow` **0x0600a7ec** shows loading at IL0x73, obtains ApolloWrapper.Dir at0x78, binds its OnDirCallback at0x7e and calls IApolloDir.QueryDir at0x89. Its separate IsTclsEnable branch exists; invocation on this phone is not established by static code.
- ApolloDir.QueryTdirAsync **0x06000159** creates coroutine **0x060119b1**. MoveNext **0x060119b4** reads TclsServerConfig.ApkServerIPList/TdirChannel, calls IApolloTdir.Query atIL0x88, Recv at0xaa, GetTreeNodes at0x13c, then ApolloDir.DoCallback at0x176. This supplies a source-level route to the identified directory operation, not runtime attribution.
- GCloud.ApolloTdir's constructor **0x06009c5d** subscribes QueryTreeEvent; callback **0x06009c6e** calls ConvertNodeList atIL0x1d. Conversion **0x06009c6b** maps TreeNodeBase.Id/ParentId/Name into TdirTreeNode, and CustomData.UserData into staticInfo.appAttr (IL0x117–121). Leaf Url separately maps to dynamicInfo.connectUrl. Configuration data and connection URL have distinct source fields.
- Loading controller OnDirCallback **0x0600a7f1** calls VersionCustomData.SaveData atIL0x4c only when callback status is zero and list non-null (branches0x3f/45). It subsequently reads HTTP/tunnel settings and GetGameNoticeUrl at0x8f. An empty notice URL has a direct base.OnFlowFinish call at0xa3; other paths can invoke downloader, notice cache/parsing and completion callbacks. This is static control flow, not observed screen transition.
- `WNLogin.VersionCustomData.SaveData` **0x0600aa22** reads node.staticInfo.appAttr (IL0x41/46). Node IDs **0x01010100** and **0x01010300** are selected by constant loads at0x66/77 and branches0x6b/7c; arbitrary nodes are not retained by this branch. Configuration parsing is a generic MethodSpec call at0xde, whose target was not resolved this run; do not label its format verified JSON. A VersionCustomRoot fallback constructor is present at0x118.
- `GetVersionCustomDataForCurrentPlatform` **0x0600aa26** loads **0x01010100** atIL0x1 and calls GetData. This is a source constant, not an exported phone argument or account ID. The root constructor **0x0600a9f1** does not explicitly assign game_notice_config_url; broader default/fallback behavior remains to be validated before crafting a response.

## Competing producer remains

A separate GameNoticeDownloader.InitGCloud **0x06000345** creates ApolloTdir and starts QueryTdirAsync **0x06000346**, coroutine MoveNext **0x060119de**. That also calls IApolloTdir.Query and GetTreeNodes, then GameNoticeDownloader.OnDirCallback **0x06000348**, which handles notice URL/cache/download. Both paths can use the shared directory machinery. The loading screenshot and BY_ID method alone do not uniquely choose between them. No claimed phone callback identity.

## Validation and next check

Eleven inline read-only checks PASS: loading indicator/query, configuration-save/notice/finish callsites, both coroutine queries, bridge conversion, both node-ID filter constants and the platform selector. These are source checks, not runtime tests or a login milestone. Existing native node tests from R095 remain a separate evidence class; not rerun or relabeled as managed execution.

Next offline checks: resolve the generic configuration parser, validate default/fallback settings, and map the selected configuration node through native tree/bridge conversion. Then validate a complete correlated directory response before proposing another bounded phone run. No new phone test is needed solely to reconfirm Loading. Schedules remain paused; game unchanged.

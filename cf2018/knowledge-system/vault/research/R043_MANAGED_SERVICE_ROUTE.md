# R043 — Original Unity game-side route caller: source-only offline inspection handoff

Date 2026-11-01. **State: original managed DLL identified by prior static investigation; R043 new source-only scanner verified with synthetic tests; real original DLL NOT available to this session, no real scan / ten-byte service identity.** No new phone packet experiments, authentication or lobby.

## Why research rather than more network tests

R037 with a correctly correlated RPC64 candidate response led to three 131-byte `0x1001` reconnects; R036/R037 proved the only changed header component was nested SYN field14, and the route remained named-route variant4 with a **10-byte** name versus known reference `QueryAddrSvr` (12 bytes). R038 no-reply close and R039 one-bit-wrong RPC64 showed only reference 133-byte SYNs. R041 read-only original-native trace proved the positive `QueryAddrInfo` reply has pending-RPC lookup, result==0 and possibly **deferred** callback via `AddressService::Update`. R042 original-native 12/12 checks proved the *TGCP ACK head serializer* contains no route name but full-packet/state/key acceptance is unverified; DO NOT blindly ACK 131-byte SYNs.

The critical unknown is the **game-side caller** selecting the next service name. Apollo itself accepts a service string from its caller. This is likely in Unity managed game code, not in the generic Apollo `.so`.

## Concrete original application source

The user's earlier [CF2018 XAPK Comparison Report] identified original `Original.xapk` on their phone, containing `com.tencent.tmgp.cfmnac.apk` with `assets/bin/Data/Managed/Assembly-CSharp.dll`, original DLL SHA256 `174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9`, 13,423,104 bytes. Earlier local read-only managed analysis recovered XOR-0x87 ECMA-335 metadata: **10,238 TypeDef, 75,087 MethodDef, 22,646 MemberRef**, including `Apollo.ApolloConnector`, `WNGameBase.ApolloLoginConnector`, `GCloud.RouteInfoBase`, `WNGameBase.ZoneNetWorkEventChannel`. Managed code also has explicit standalone game and AI/bot classes; that is a separate potential gameplay path, not proof of offline launching.

In this turn the connected Drive search exposed an unpacked OBB folder but NO original `Original.xapk` nor `Assembly-CSharp.dll` file; Library retrieval contained reports/source tools but not the raw DLL. The original native Apollo ELF is available privately, **not the original game-side managed DLL**. Therefore no runtime or actual original assembly scan happened. The exact 10-byte route is **unknown**; do not guess service names from lengths.

## R043 source-only offline game-code tracer

Conversation attachment `CF2018_R043_Managed_Route_Kit.zip` SHA256 `fe79158bda6de1c07dca71b8ba0ceafd1120902488a433d4590bd170113f1c98`. It includes the **already-researched, hash-pinned read-only nested-XAPK managed DLL extractor** plus an ECMA-335 Metadata/CIL callsite inspector and a bounded compile-time `ldstr` route candidate tracer. No proprietary DLL/APK/OBB binaries included.

- Does not connect to the game/network, install or modify game files, change any replies or require PCAPdroid.
- The original XAPK defaults to `~/storage/downloads/Original.xapk`. Extracts a DLL only after SHA256 verification; keeps it in `~/.cf2018_r043_private/`; refuses wrong original hashes.
- Parses recovered metadata in memory, walks bounded methods with Apollo/network/connect/route contexts and direct service API co-occurrences, emits no raw strings by default.
- Result `~/storage/downloads/CF2018_R043_Managed_Route_Result.txt` contains owner/method names, 10-character string *length*, compile-time token and related API counts; no route literal, payload, credentials, game asset bytes or packet captures.
- **16/16** source-free tests PASS after fresh ZIP extraction: five nested-XAPK extraction integrity/refusal tests, six string/CIL source controls and five CIL call scanner tests. Negative test of missing XAPK exits status3 with `ORIGINAL_XAPK_NOT_FOUND`, no server launched.
- Script may yield zero candidates or false positives; CIL co-occurrence does NOT demonstrate the runtime service selection. A string may be built from config/resources/native code rather than `ldstr`. No original DLL test was possible here.

### Next single action

Owner can locally run `bash START_R043.sh` from the extracted kit root and upload **only** the sanitized TXT. If original `Original.xapk` has moved, set `CF2018_ORIGINAL_XAPK=/absolute/path`; do not request or upload APK/DLL. On results, trace candidate caller dataflow. If no candidates, pivot to **static named-route config/asset lookup or managed connector event handling**, not blind socket ACKs. **Current complete offline login blocker is not resolved and no real next service identity has been verified.**

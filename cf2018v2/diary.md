# Diary — page001, current

Read this page by default. Archive index: [diary/INDEX](diary/INDEX.md). These are retrospective summaries imported2026-10-31; they do not invent new experiments. Limit30 entries or8KB. Stable research IDs are separate from actual probe version labels.

## R001 — V1.2 to V1.4: why auth responses failed
The native decoder needed a TGCPBody preamble. Adding it removed immediate EOF in the later phone comparison. That did not establish a real authenticated account. [Evidence](../cf2018/knowledge-system/vault/research/AUTH_RECEIVER.md).

## R002 — V1.5 onward: Bingo changed client behavior
Synthetic Bingo elicited real4013 traffic. State5 and later traffic still did not prove login. [Evidence](../cf2018/knowledge-system/vault/research/SERVER_PATH.md).

## R003 — V3.8: compression was off; request still unknown
Two routed bodies were80/85 bytes. No4013 reply was sent, so this was not a rejected service-response test. [Evidence](../cf2018/knowledge-system/vault/research/V38_BLOCKER.md).

## R004 — Native correction: prefix means packet sequence
The four-byte prefix is dwSequence, not account UID. Native counter increment confirmed. [Evidence](../cf2018/knowledge-system/vault/research/V38_SOURCE_AUDIT.md).

## R005 — Native response: empty reason is required
A reason STRING may be empty but cannot be omitted. Corrected the canonical offline preflight. This did not fix an observed phone reply. [Evidence](../cf2018/knowledge-system/vault/research/ADDRESS_APPLICATION.md).

## R006 — V3.8.1: route and boundary narrowed
Phone reports matched sequence prefix and QueryAddrSvr route. Method-name bytes still fail policy. Trace the producer; do not repeat this test. [Evidence](../cf2018/knowledge-system/vault/research/PHONE_V381.md).

## R007 — Source check: extracted APK, not full XAPK
Verified APK/native/storedDLLs exist privately. Full XAPK/OBB absent locally. Follow Write callers upstream; existing Apollo is enough for this step. [Evidence](../cf2018/knowledge-system/vault/research/REPOSITORY_SOURCE_AUDIT.md).

## R008 — Workspace v2 established
Created selective ICM, vault, explicit graph and paged diary. Original code/evidence stays in cf2018. Workspace migration does not advance the game's acceptance gates.

## R009 — Upstream request producer chain, static native (2026-11-01)
Pinned original Apollo and traced 11 native instruction checkpoints: AddressService args writer, MsgBuffer callback binding/dispatch, concrete CGCloudConnector buffer submission and routed TGCP queue. Static trace narrows the producer boundary but does not identify the on-phone 4013 application operation. Next: bounded synthetic MsgBuffer-to-connector differential and reciprocal RX; no phone run or new reply. [Evidence](../cf2018/knowledge-system/vault/research/UPSTREAM_REQUEST_CHAIN.md).

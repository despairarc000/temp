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

## R010 — Additional producer branches verified, read-only (2026-11-01)
24/24 original-native static pins confirm the virtual protocol operations, MsgBuffer bound callback and connector's size/connection gates. Six tests PASS with private Apollo; no full message execution, phone reply, login or gameplay. Next bounded whole-message comparison remains open. [Evidence](../cf2018/knowledge-system/vault/research/UPSTREAM_REQUEST_CHAIN.md).

## R011 — Two connector bind owners found (2026-11-01)
The exact original native source has two direct callers of MsgBuffer::bind: AddressService::OnConnectProc and RpcConnector::OnConnectProc. Updated original-source audit passes 26/26 instruction pins; six tests pass with original private Apollo. This is not a phone-runtime identification. Determine which bound connector and response handler owns the QueryAddrSvr request before proposing a reply. [Evidence](../cf2018/knowledge-system/vault/research/UPSTREAM_REQUEST_CHAIN.md).

## R012 — Distinct receive paths traced (2026-11-01)
Pinned native instructions link AddressService receive callback to its response parser and QuerySession lookup, versus RpcConnector receive callback to its message parser and typed response handler. Verifier now 33/33 static pins PASS, six local tests with original Apollo PASS; no on-phone receipt, server reply or authenticated session proven. Next decide which connector owns the observed 4013 and establish pending-correlation predicates. [Evidence](../cf2018/knowledge-system/vault/research/UPSTREAM_REQUEST_CHAIN.md).

## R013 — [FINDING] Route-name origin distinguishes owners, not runtime identity (2026-11-01)
CONFIRMED_NATIVE_STATIC: rehashed original Apollo (4812396e…9169d8), verified ELF32LE ARM. AddressService::CreateConnection constructs name-route info at0x39d7e6; literal load0x39d7ea/add0x39d7f0 resolves through0x39d9a4 to string0x4a820d, exactly QueryAddrSvr, assigned at0x39d7f2. RpcConnector::CreateConnection instead loads its route-name source from[r4,+0x28] at0x3c5012 and assigns it at0x3c5014. This is a new route-association distinction beyond the33-pin bind audit. SYNTHETIC_ONLY equality controls distinguish same-name versus other-name input; they do not establish permitted runtime configuration. UNKNOWN: the phone's concrete connector/configuration; route MATCH alone does not exclude RpcConnector using the same name. Next bounded check: trace writes to RpcConnector's name member and registration/init callers to determine whether QueryAddrSvr can actually reach that path. [Context](../cf2018/knowledge-system/vault/research/UPSTREAM_REQUEST_CHAIN.md).

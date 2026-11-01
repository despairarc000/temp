# R047 — Original GCloud connector owns route object before TGCP SYN

Date 2026-11-01. Evidence: exact original SHA256-pinned Apollo ELF, ARM Thumb static disassembly only. **14/14 original instruction pins PASS, 7/7 tests PASS locally**, including pin-mutants, wrong binary rejection and private original gate. No new phone test, accepted login or lobby.

## Followed direct caller beyond R046

Whole-original ELF disassembly finds a direct BL at address 0x3c6c4a from **GCloud::CGCloudConnector::connectTConnd(bool)** (symbol start 0x3c68e0) to **GCloud::CTGcp::SetRouteInfo** (0x3a33a0). This resolves R046's immediate *native* SetRouteInfo caller. It does not identify the external/app caller that supplied the route string.

**GCloud::CGCloudConnector::SetRouteInfo(GCloud::_tagRouteInfoBase const&)** at 0x3c5b18: at 0x3c5b1c retrieves previous route pointer from connector+0x19c; releases previous value if present; at 0x3c5b32–0x3c5b38 invokes virtual Clone of newly supplied route object; at 0x3c5b3c stores that clone into connector+0x19c. This is an actual stored **owned route object**, not a route literal originating in the SYN writer. The exact object's type and string in any real phone run are unknown.

**GCloud::CGCloudConnector::connectTConnd(bool)**: constructs GCloud::CTGcp at 0x3c6956 and stores its pointer at connector+0x198 (0x3c695e). Conditional setting of name service occurs at 0x3c696a. After initializing TGCP, it loads the stored cloned route from connector+0x19c (0x3c6c0c), checks non-null at 0x3c6c10; if present, loads CTGcp pointer and calls CTGcp::SetRouteInfo at 0x3c6c4a. It subsequently calls CTGcp::Start (0x3c6c86) with the connection's stored endpoint parameters. This is a **conditional route application**, not a guaranteed route for every connection.

R046 proved the downstream native route chain: GCloud::CTGcp::SetRouteInfo recognizes route type4/name string, gcloud_tgcpapi_set_route_info copies it into handle+0x3400, and gcloud_tgcpapi_send_syn_msg serializes stored type4 route into SYN. R041 and the R037/R038/R039 phone comparisons separately support a response-associated 10-byte route transition. None of those experiments observed a native callback stack, so do not conflate stages as a proven phone execution chain.

## Exact remaining question

Who invokes **GCloud::CGCloudConnector::SetRouteInfo** with a named route after a valid RPC64 address response? That may be a virtual IConnector interface call originating in game configuration, an internal route selector or native wrapper. A whole-binary direct-BL search found **no direct call** to this concrete function, consistent with but NOT proving virtual dispatch. Need inspect vtable interface callers, initialization/route config sources, and the original managed bridge, not infer service name from its 10-byte length.

Native reproducible [14-pin R047 auditor](../../../experiments/native_gcloud_connector_source_audit.py) and [7 tests](../../../tests/test_native_gcloud_connector_source_audit.py). Exact original 5,243,704-byte binary SHA256 4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8 never committed. All source-only code; no original packet contents or credentials.

## Decision

Continue read-only caller/vtable and config provenance research. Do **not** run another broad socket trial or blindly ACK unknown 131-byte named-route SYNs. A targeted later phone experiment is justified only once the correct second-service ACK/session policy and a falsifiable route predicate are established. Game is not authenticated or playable.
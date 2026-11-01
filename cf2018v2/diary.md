# Diary — page006, current

Previous [page005 archive](diary/005.md) contains R039–R044 findings and earlier context. Current [vault status](vault/CURRENT.md). Preserve separation of phone evidence, exact original native/managed static evidence, synthetic controls and unverified state.

## R045 — [REAL GAME MANAGED + ORIGINAL NATIVE] route-init origin (2026-11-01)

Original SHA256-pinned Unity CIL shows the game login connector selects a lobby URL, calls Apollo.CreateApolloConnection and sets security and callbacks before Connect. Managed ApolloConnector.Initialize enters native apollo_connector_Initialize. Native CApolloConnector::connectTConnd scans stored route-record discriminator 4 (named route), checks nonempty name, calls CTGcp::Initialize; conditionally applies SetRouteInfo before CTGcp::Start. Exact native 17/17 Thumb pins PASS, nine local tests PASS; original managed DLL was verified from Drive and kept private. The user does **not** need another Termux extraction or live capture. The 10-byte named-route identity, exact runtime configuration origin, correct next handshake and login are still unknown. [R045 evidence](../cf2018/knowledge-system/vault/research/R045_MANAGED_NATIVE_ROUTE_ORIGIN.md); [source-only audit](../cf2018/experiments/native_connector_route_audit.py).

NEXT: inspect native name-service selection and the exact client ACK session/key checks. Avoid blind second-route ACK or completion percentages.
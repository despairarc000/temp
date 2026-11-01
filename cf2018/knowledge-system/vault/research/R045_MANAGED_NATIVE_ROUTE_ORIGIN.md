# R045 — Original game managed-to-native connector and named-route handling

Date 2026-11-01. **ORIGINAL MANAGED STATIC + ORIGINAL NATIVE STATIC**, not a phone runtime trace. Game NOT authenticated/playable. This follows R044 and supersedes R043's unavailable-assembly claim.

## Material progress

Connected Google Drive now exposes the original 13,423,104-byte Unity Assembly-CSharp.dll at https://drive.google.com/file/d/1ktt82byz3GXUQRe3bYJD1_GuUgUuhE6M/view . Verified SHA256 174a30cea9dba4f84b90a446f247cc0d212b7c83d462889d57703e7875e249e9. The exact original Apollo ELF SHA256 is 4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8, size 5,243,704. Private game/native bytes never committed.

## Verified original managed CIL path

- WNGameBase.ApolloLoginConnector.DoConnect, RID 4123, RVA 0x63c30: calls ServerListData.GetLobbyServerUrl at IL+0x10c, Apollo.IApollo.CreateApolloConnection at +0x192, registers connection/reconnection/error/receive/route-change delegates, calls ProjectSetting.get_ServerLobbyDHP then IApolloConnector.SetSecurityInfo at +0x248, then IApolloConnector.Connect at +0x2af.
- Apollo.Apollo.CreateApolloConnection, RID38463/RVA0x349de4, instantiates an ApolloConnector and calls its Initialize at IL+0x45. Other overload RID38462/RVA0x349d70 calls its Initialize at IL+0x41.
- Apollo.ApolloConnector.Initialize, RID38832/RVA0x34d628, forwards object ID, connection parameters and URL into native apollo_connector_Initialize at IL+0x36. Another overload routes through InitializeWithIps.
- ServerListData.GetLobbyServerUrl (RID4555/RVA0x679bc) selects review IP, configured server-list address or ProjectSetting fallback based on runtime state. ProjectSetting.GetLobbyUrl contains tcp://{0}:{1} formatting and a fallback literal port 65010; this is NOT an observed runtime port in R037. ProjectSetting.get_ServerLobbyDHP is fetched from localization settings, not a universally fixed key.
- A real-DLL search of direct GCloud.NameRouteInfo constructor references found the factory RouteInfoBase.CreateApolloRouteInfo and NameRouteInfo.onCopyInstance. This does not exclude native/config-generated route names, nor identify the 10-byte SYN destination.

## Original Apollo native route code now reached

- Export apollo_connector_Initialize Thumb 0x38c874 calls NApollo::IApollo::GetInstance (0x38c8d8), then delegates connection creation through a virtual method at 0x38c8e8.
- NApollo::CApolloConnector::Initialize(int,std::string const&,int,char const*) starts 0x382658, stores connection attributes and caller URL in connector state.
- NApollo::CApolloConnector::connectTConnd(bool) starts 0x382cb8: constructs NApollo::CTGcp at 0x382d24 and registers observer at 0x382d30.
- A conditional connector-kind3 branch at 0x382dd0 iterates route-record array. At 0x382df2 a record discriminator 4 selects a named-route record; at 0x382df8 the name is accessed through AString::c_str. A second pass 0x382e1e..0x382e36 checks another record discriminator 4 and verifies name pointer and nonzero string length. At 0x382ea0 this branch calls NApollo::CTGcp::Initialize. Alternate paths call other CTGcp::Initialize overloads; not every connection is equivalent.
- At 0x3831a0, optional route-info presence is checked. Only if present does 0x3831a6 call NApollo::CTGcp::SetRouteInfo. Then 0x383204 calls NApollo::CTGcp::Start. **Do not misread SetRouteInfo as unconditional.**

Original-native audit: 17/17 hash-pinned Thumb instruction pins PASS, 9/9 local unit tests PASS including mutated/missing pin negatives and exact private original. Source-only auditor: [native_connector_route_audit.py](../../../experiments/native_connector_route_audit.py). Tests: [test_native_connector_route_audit.py](../../../tests/test_native_connector_route_audit.py).

## What remains uncertain

R037 correct-RPC64 reply was followed by three 131-byte SYNs with a 10-byte named route, while no reply R038 and deliberately wrong-RPC64 R039 retained the original QueryAddrSvr route. These observations strongly support a response-correlated routing transition. The real ten-byte service name, its runtime configuration provenance, whether the inspected ApolloLoginConnector call path produced those precise phone SYNs, the next SYN/ACK state/key contract, and genuine authentication are NOT proven.

Next: trace the original native name-service configuration and connection-kind branch, and the exact client ACK state/key parser before considering any service-specific test. No more R039/redundant phone experiment. The initial 0x4013 correlation mechanism has substantially advanced, but the full lobby/gameplay blocker is not solved.
# R024 — RpcConnector protocol call sites (read-only native audit)

Evidence: original ARM ELF with previously pinned SHA-256; no phone execution.

Three direct call sites were identified for RpcConnector::Init in the examined original .text:
- dolphin version-update action at 0x32fc74
- Puffer URL/update action at 0x36175e
- CTDir initialization at 0x36f0e0

Each passes protocol-type value 0x20 through the first stack argument.
RpcConnector::Init loads that argument and saves it to instance field +0x3c.
RpcConnector::InitProtocol reloads +0x3c and passes it to ProtocolFactory.

RpcConnector::InitAddressService constructs and initializes an AddressService
object at instance field +0x94, so the AddressService and RpcConnector
structures are nested in this path rather than necessarily competing producers.

Local original-native bounded disassembly verified 22/22 fixed instruction
checks. Five tests passed, with one private original-source static test.
No original runtime message, complete receiver, phone packet, credentials or
client-accepted response was executed.

Interpretation: although the general connector supports a configured protocol,
all three identified direct callers choose binary type 0x20. This weakens the
hypothesis of a different protocol *at these call sites*. Other indirect
callers, runtime substitutions, encryption, framing and the actual phone 0x4013
producer remain unverified. Do not invent a 4013 response.

Next: identify the actual runtime owner/transform and compare the matching
original writer's output at the connection boundary.

# R075 — Directory RPC is distinctive, but has no direct Update call in Apollo

**2026-11-02, CF2018 fake-server research.** Static read-only review of owner-connected original Apollo (5,243,704 bytes, original SHA-256 fingerprint from R057 pinned by the auditor). Independent direct Thumb BL scan, PC-relative data check, and source-only GitHub CI. No additional phone test, game editing, new ACK or lobby.

## Motivating real-phone finding

[R074](R074_PHONE_UNIT_FIELD_CONFIRMED.md) confirmed the original client emitted three 131-byte reconnect SYNs following a correlated synthetic address response. Compared with the 133-byte first-stage reference, each changed **only SYN field5 (iUnitID, varuint encoding kind0)** and named-route field14 (10 bytes versus 12 bytes). This supports a connection with a different unit ID but does **not** identify the unit number, source connector, route value or ACK contract. Field5's logged 0 is **encoding kind, not value**.

## Native source discrimination

The original `RpcConnector::Init` has three known **direct** calls:

| Native caller | Direct Init site | Original immediate before call | Direct `RpcConnector::Update` call? |
|---|---|---|---|
| `GCloud::CTDir::Initialize` (directory service) | `0x36f0e0` | `0x36f0de`: `movs r3,#15` | **None identified** by direct BL scan |
| Version-service action | `0x32fc74` | `0x32fc72`: `movs r3,#8` | `0x32fdf8` |
| Puffer update URL action | `0x36175e` | `0x36175c`: `movs r3,#8` | `0x3619a4` |

The `r3` values 15 and 8 are the **first integer argument after connector instance, service string and ConnectCfg** under the original native calling convention. Their application meaning was *not* established; they are **not** claimed to be the unit ID, security mode or client type. [R072](RPC_DOMAIN_UNIT_SOURCE.md) independently identified a different source for the unit value: `ConnectCfg` (or successful service-domain parsing). `CTDir` places literal1 in its temporary ConnectCfg at `0x36f0ac`/write `0x36f0ae` before the possible parse override.

The separate `GCloud::CTDir::Initialize` original routine directly constructs a `dir_cs::DirServiceClient` at `0x36f13c`, confirming this is a *directory-service client*, not direct proof of a playable game lobby. A direct BL scan finds **zero** calls to `CTDir::Initialize` and **zero direct CTDir-to-RpcConnector::Update** calls, whereas version and puffer each call `Update` directly. These are *negative direct-call results only*: virtual/indirect dispatch or other lifecycle entry points are not ruled out.

### PC-relative directory route literal verified, not printed

At `CTDir::Initialize+0x62`, Thumb `LDR r1,[PC,#0xe4]` (instruction0x4939 at `0x36f096`) loads an ELF literal from `0x36f17c`. The `ADD r1,pc` at `0x36f09e` (0x4479) resolves a constant original source C-string. Independently extracted **shape only** from owner-private ELF: **exactly 10 printable ASCII bytes and a trailing NUL**. The route bytes are not logged or committed. Matches the phone route **length**, but **not** yet phone route identity.

This supplies three useful distinctions: CTDir is a verified source-level caller with a ten-byte route; it passes an original int argument15 rather than8; and it does not show the direct `Update` lifecycle seen in the other two. The three observations together do not prove CTDir was started on the user's Android phone.

## Verification

- [Read-only original auditor](../../../experiments/r075_directory_connector_discriminator.py) pins the original SHA/size and checks **four watched target functions, six exact original direct BL callsites and eight original Thumb instruction halfwords**, plus the resolved private ten-byte literal's length and ASCII shape. It emits no route bytes, strings, packet fields or user data.
- Independent private original byte scan during this turn: **6/6 exact direct callsites**, **8/8 halfwords**, **10-byte printable NUL-terminated literal** matched. This in-memory read reused the original Drive file, but a fresh independent SHA-256 computation was not performed here. Original SHA gate exists in source auditor.
- [Positive and negative synthetic controls](../../../tests/test_r075_directory_connector_discriminator.py): **15 public methods PASS**, with **one private-original test SKIPPED** by public CI. Mutated caller graph, owner, immediate, PC-relative displacement, literal length and ASCII shape are rejected. [GitHub run 41370749621](https://github.com/despairarc000/temp/actions/runs/41370749621): SUCCESS, repository suite **563 total / 145 skipped**.
- The user R074 report remains the *only* direct live-phone source for the changed field. No Android dynamic trace has been performed in R075.

## Next strongest discriminator

Rather than guess a numeric unit ID or send a generic ACK, compare the next phone's 10-byte SYN route **privately, byte for byte** with the original `CTDir` literal and emit only a fixed `MATCH/DIFFERENT` label. Exact match substantially strengthens the CTDir route-source hypothesis; mismatch rules out that literal as the route source in this original build, but would not disprove another connector's unit-ID change. Neither result proves authenticated login or which native state machine is active.

An **offline-only draft** [`r076_private_route_equality.py`](../../../experiments/r076_private_route_equality.py) was created with SHA-pinned original-source read and a constant-time byte comparison over transient client frames, outputting only fixed labels. It has **not yet been separately regression-tested or integrated into the actual owner Termux handler**, and should **not** be deployed or claimed phone-verified. The standalone R076 test-file creation attempt was blocked; do not treat the passing repository CI on the module commit as validation of this route comparison.

Keep the existing live second-service **ACK disabled** until independently verified receiver/keys/session conditions are understood and an owner-approved bounded phone experiment is prepared.

**Current functional gate unchanged:** no accepted second-service ACK, real authenticated login, lobby, TDM or Bomb bot match.

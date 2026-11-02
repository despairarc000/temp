# R078 — Conditional CTDir-to-GCloud ACK lineage and combined route/unit controls

**2026-11-02. RESEARCH + SOURCE-FREE CI TESTED; ORIGINAL-NATIVE R078 EXECUTION NOT RUN.** Builds on the user's [R077 report](R077_ROUTE_ID_INTEGRATION.md): three out of three post-address 131-byte SYNs had `CTDIR_STATIC_ROUTE_MATCH`, but all three also had changed encoded field 5, local policy `class=REFUSED`, `HOLD_NO_ACK`, and zero second-service ACK. The local REFUSED label is **our parser/gate policy**, not a message from the original client.

## Distinct branches: what's actually pinned

Existing original native evidence from R047/R048, R057, R060/R061 and R073 gives these *conditional* direct-call segments, independently cross-checked in [R078 auditor](../../../experiments/r078_ctdir_ack_lineage.py):

1. `CTDir::Initialize` directly calls `RpcConnector::Init` (site `0x36f0e0`, target `0x3c4530`).
2. `RpcConnector::Update` directly calls `CreateConnection` (sites `0x3c52b4`, `0x3c5372`, target `0x3c4f78`).
3. The GCloud connector code separately constructs GCloud TGCP, invokes GCloud SetRouteInfo and starts GCloud transport (sites `0x3c6956`, `0x3c6c4a`, `0x3c6c86`).
4. The GCloud start/key-state code invokes `gcloud_tgcpapi_recv_ack_msg` (sites `0x3a845a`, `0x3a9fb0`).
5. That receiver's ACK path invokes the **GCloud TLV body parser** (site `0x3ac1b6`, target `0x3b8860`). Legacy NApollo ACK invokes a different parser at a different address (R061).

The R078 module checks **12 previously evidenced direct callsites across 7 watched targets**, validates caller ownership and the original size/SHA, and has explicit handling for targets that may have additional legitimate callers.

**The chain still has gaps:** original CTDir runtime Update scheduling, actual RpcConnector-to-GCloud object selection, which stack handled the *phone's* second SYN, and real ACK/key/session validation are **not observed**. A literal CTDir route match does not prove those missing links. GCloud and legacy ACK are not asserted wire-compatible or wire-incompatible without receiver tests.

## Combined controls

The [R078 tests](../../../tests/test_r078_ctdir_ack_lineage.py) add a **joint** independently synthetic 10-byte named-route + unit field5 change, as observed structurally in R077. This yields `ROUTE_AND_UNIT_FIELD5_ONLY` in the *observational classifier*, while changed security bytes, varuint width and wrong callers are refused. This is **not a second-service ACK permission**. The first-service synthetic ACK fixture has no route/unit input, but original-client session/key acceptance cannot be inferred from that fixture.

There is a separately opt-in **exact-owner-original native** test: run `native_syn_ack_handoff.probe` with `name_size=10, attribute='unit_3'`, stopping at the auth-send boundary, and negative-control wrong magic. It is deliberately **skipped in public CI** without private `libapollo.so` and native emulation dependencies, so no result from this combined original-native branch is claimed.

## Verification and next action

[GitHub Actions run 41384491376](https://github.com/despairarc000/temp/actions/runs/41384491376) **SUCCESS**, 618 repository tests /149 skipped; all 14 new source-free R078 checks passed; the one original-native R078 combined test was skipped. No packets were transmitted; no APK or original binary committed. Previous owner R077 route equality **3/3** remains the last real phone evidence.

**NEXT highest-value:** verify original dynamic connector/ACK provenance and combined alternate-unit native ACK boundary using exact owner Apollo in a bounded private offline environment. A valid synthetic native boundary would only justify designing a later separately opt-in receiver/ACK experiment; it would NOT prove live second-service authentication. Do not ask user to repeat R077, auto-enable the held second ACK, or guess an actual numeric phone unit from `[[5,0]]`. Any new owner diagnostic final TXT must go into Android Download.

## R079 extension — R078 runtime gap narrowed by original B.W tail-call
[R079](R079_CT_DIR_TAIL_UPDATE.md) independently found and checked SHA-pinned original `CTDir::UpdateByManual` **B.W** → `RpcConnector::Update`, plus the RPC `Update` → `CreateConnection` BL edges. Thus the R078 previously unverified direct source link is now *source-code verified* when the CTDir forwarding method is invoked; actual phone scheduling remains unproven. The original `CreateConnection` additionally calls GCloud named-route constructor and `CGCloud::GetInstance`. This supports prioritizing GCloud object creation/indirect dispatch next; **it does not prove a GCloud ACK was accepted**.

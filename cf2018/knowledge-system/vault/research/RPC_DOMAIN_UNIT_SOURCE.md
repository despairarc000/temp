# R072: RPC caller preserves default client type but can override unit from a domain

2026-11-02 UTC. Original native static + bounded emulation with functional string/runtime stubs; no new phone test or accepted session. Exact original Apollo fingerprint enforced by NativeControl.

## A competing explanation narrowed

The R071 client-type selector2 possibility does not come from the examined RpcConnector CreateConnection path: that method explicitly zeros init-info+0x38 at0x3c5030/0x3c5048, with the structure based at stack+0xbc. Initialize transfers this to connector+0x64; R071 showed selector0 leaves the default client type101 unchanged. This falsifies attributing a101→102 override to this specific static path. Other callers and the actual phone producer remain unresolved.

Its init-info+0x34 flag remains1 (0x3c5036/38), unlike AddressService's explicit0 at0x39d838. The flag is copied to connector+0x60. Its consumer0x3c695a–6a conditionally calls **CTGcp::SetNameService** (0x3a3374); it is name-service registration, not a demonstrated security/account-change switch.

## Concrete unit chain

RpcConnector Init loads ConnectCfg's first word into object+0x24 at0x3c45cc–d0. If IsDomainName0x399214 succeeds, ParseDomainName0x3993c8 is called at0x3c464c. On parser success,0x3c4652 loads the low word of parsed ReqQueryAddrInfo+0x10 from stack+0x20;0x3c4654 replaces object+0x24. CreateConnection loads object+0x24 at0x3c504e and stores init-info+0xc at0x3c5058. R071 follows that value into the handle and SYN field5, whereas AddressService fixes its own discovery unit to1.

The original parser splits the input service string, converts its second numeric component with atoi at0x39946e, and sign-extends/stores it at request+0x10 at0x39947c. The following numeric component goes through atoll at0x3994be into request+8. Original control flow, delimiter literals and stores execute in the controls; C++ string operations/destruction and decimal conversions are explicitly functional synthetic stubs. Full IsDomainName and RpcConnector initialization are not emulated.

Two independent synthetic names (`Example.1.12345.agcloudcs.com`, `Example.3.12345.agcloudcs.com`) produce the corresponding unit under the original parser's control flow. A malformed name returns-2. A bounded original RpcConnector store fragment transfers unit1/3 to object+0x24. Actual original SYN preparation/serializer shows unit1→3 changes only field5 at unchanged encoded length; key/encryption fields remain equal. Unit3's synthetic ACK reaches suppressed auth-send; unsupported key mode remains rejected. **Four native-gated methods PASS.** No full wire connection/auth construction is executed; R066/R070 stubs remain explicit.

## Callers and a falsifiable phone prediction

An executable-section direct Thumb BL scan finds three calls to RpcConnector::Init: version action0x32fc74, puffer update URL action0x36175e, CTDir::Initialize0x36f0e0. Owner symbols independently match those sites. CTDir initializes ConnectCfg with unit1 at0x36f0ac–ae but allows the later domain parser override. Its configured route-name literal is10 bytes (PC-relative source load0x36f096/add0x36f09e; literal pointer0x36f17c). That length matches the phone's class but **does not identify the phone route**; no route name is exported or guessed. The received service address can therefore plausibly produce a ten-byte route and a changed unit despite common game/client settings.

The prediction is now specific: **if the previously prepared field-number diagnostic identifies field5, this chain explains a plausible ordinary unit change; if it identifies field6, this particular RPC caller path is a poor fit; other fields require their own trace.** Neither outcome alone proves source ownership or accepted ACK. The gate is unchanged. The next useful phone observation is the existing value-free diagnostic, not another ACK attempt or a new kit.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=cf2018/private/analysis_deps CF18_APOLLO_LIBRARY=/absolute/path/to/original/libapollo.so python -m unittest discover -s cf2018/tests -p test_native_rpc_unit_trace.py -v
```

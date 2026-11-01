# R071: discovery defaults versus connector-selected SYN attributes

2026-11-01 UTC. Original-native static and bounded emulation; private pinned reference inspection. No phone test, next-service ACK acceptance or login. Original Apollo SHA256 independently reverified as `4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8`.

## Unit identifier: explicit discovery default and caller transfer

`AddressService::Init` stores constant1 at object+0x1c (0x39a1fe/0x39a202), independently of its two incoming integer arguments. In `CreateConnection`, 0x39d830 loads this value and0x39d840 stores it at stack+0xf0, offset+0xc of connector-init structure at stack+0xe4. `CGCloudConnector::Initialize` copies init+0xc into connector+0x38 at0x3c6140–46. Both normal connector branches read connector+0x38 at0x3c6a42/0x3c6ba6 and place it at CTGcp::Initialize's stack argument+4 before calls0x3c6a70/0x3c6bd4. CTGcp forwards that input to the API's unit argument (0x3a3ed4–d6). R070 established handle+0x10 -> SYN field5 iUnitID.

This proves discovery selects a fixed unit while generic connectors consume a caller-supplied unit. It does not establish the actual phone next connector's chosen unit.

## Client type: default and override branches

`CTGcp::Initialize` supplies enum101 to `gcloud_tgcpapi_init` via stack+8 at0x3a3edc–de. Discovery CreateConnection explicitly zeros connector-init+0x38 at0x39d828. `CGCloudConnector::Initialize` copies init+0x38 to connector+0x64 at0x3c6154–56.

After initialization `connectTConnd` dispatches on connector+0x64 at0x3c6c4e–72: selector1 calls SetClientType(101), selector2 calls SetClientType(102), selector3 calls SetClientType(0); other selectors do not invoke this override. The actual `CTGcp::SetClientType` at0x3a338c loads its handle from+0x58 then writes enum to handle+0x114 at0x3a3390. R070 independently maps that handle field to SYN field6. These are the original numeric client-type enum values; no OS/social-login/transport meaning is inferred from their numbers.

The pinned private reference agrees with discovery's defaults: decoded unit1/client-type101. The reference file's bytes are checked against V38_SOURCE_PINS before decoding; no route/account/raw packet content is exported. The R069 phone report's slot1 REFERENCE_SYN equality supports tying these defaults to that initial connection, not to its three changed reconnects.

## Shared game identifier narrows another hypothesis

Both connector initialization branches obtain llGameID from CGCloudCommon+0x30 at0x3c6a30–34 and0x3c6b94–98. CGCloud::Initialize writes that common value from initialization info+0x30 at0x3c800a–14. Thus a route change alone is not a demonstrated source of a new game identifier. Runtime common-state mutation or a different concrete stack remains unexcluded; no phone game-ID change is inferred.

## Original-code checks and discrimination

Five original-gated test methods PASS with Apollo and the pinned probe source supplied. They execute discovery Init's prefix (stop before mutex allocation/protocol/network), original SetClientType for0/101/102, actual SYN preparation/serializer prefix, and actual ACK path with auth-send suppressed. The discovery prefix string assignment is suppressed. Remaining stubs/handle transfer are documented in R066/R070. Full connector initialization or Android callbacks were not emulated.

Actual signed-varint serialization gives these conditional predictions for field6:

| Transition from discovery101 | Field6 effect | Fit to R069's same-length-only extra change |
|---|---|---|
|101→102|Value changes, encoded length unchanged|Compatible, not established on phone|
|101→0|Encoded length decreases by1|Inconsistent if field6 is the sole additional changed field under this writer|

The synthetic102 configuration still consumes the same63-byte ACK and reaches suppressed auth-send; wrong-magic negative returns-13 before auth. This is native parser compatibility, not server identity/account validity. Existing R070 application cases and R066 handoff controls pass after the added bounded enum inputs.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=cf2018/private/analysis_deps CF18_APOLLO_LIBRARY=/absolute/path/to/original/libapollo.so CF18_V38_SOURCE=/absolute/path/to/pinned/v38_source python -m unittest discover -s cf2018/tests -p test_native_syn_attribute_sources.py -v
```

Next trace the init-info selector/unit supplied by concrete downstream consumers. The phone's extra field is still unidentified; field7/account and other hypotheses are not excluded. No gate relaxation, new phone test, or inferred authentication success.

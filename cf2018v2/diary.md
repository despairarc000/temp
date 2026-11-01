# Diary — page008, current

Previous [page007 archive](diary/007.md): R052–R057. See [current status](vault/CURRENT.md).

## R058 — Original GCloud name-service wiring (2026-11-02)

**Fake-server research only.** Rechecked the original owner-connected Apollo library. Original connector construction creates a default name service, and connector startup calls `CTGcp::SetNameService`. The original method uses a virtual observer-registration slot, resolved in the default name-service vtable to `SetObserver`. The original name-service constructor initializes `AddressService`; original callback/observer entries were also verified. Three native direct-call sites, seven instruction pins and six function pointers are covered by the new [R058 auditor](../cf2018/experiments/r058_name_service_wiring.py). Public [CI 41345156313](https://github.com/despairarc000/temp/actions/runs/41345156313) PASS; 10 synthetic tests, original-only gate skipped in CI. [Full report](../cf2018/knowledge-system/vault/research/R058_NAME_SERVICE_OBSERVER_WIRING.md).

**Unverified:** which path executed on the phone, ten-byte route identity, the next ACK/session, login and bots. No game patch or live test. NEXT distinguish TGCP resolved endpoint from named route and establish appropriate second-service ACK conditions.

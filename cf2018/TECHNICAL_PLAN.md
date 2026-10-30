# TECHNICAL PLAN — evidence-bounded architecture

## Stable local path (observed)
Original re-signed CF2018 client → PCAPdroid (VpnService and app-filter) → SOCKS5 at 127.0.0.1:1080 in Termux → route old Address Service endpoints to local listener at 127.0.0.1:8080/8085. Other traffic passes through without inventing service responses.

Known old targets from PCAP + redirector tests: 45.113.69.32, 211.159.211.105 and 119.28.34.12, ports 8080/8085. Scope is specific **IP AND PORT** only. Local listener captures 133-byte TGCP `QueryAddrSvr` SYN messages. Real SYN bytes are not posted publicly.

## Components
1. **Endpoint bridge**: narrow SOCKS5 routing, stable unique connection ID, per-run audit logs, binary-safe relaying, timeout and EOF provenance; no global VPN rewriting.
2. **TGCP parser**: bounded frame splitter and TLV parser, input fuzz tests and sanitized fixtures. Read actual Apollo native receive path first.
3. **TGCP session server**: only implement ACK/session/auth semantics once native validation rules established. Do not default to guessed candidate ACK.
4. **Address Service**: after handshake, decode real on-phone `QueryAddrInfo` RPC and respond with proven fields; earlier standalone Thrift prototype is NOT integrated/accepted.
5. **Other service stubs**: research updater/config/Dolphin/Puffer, login, resources, match services incrementally; resolve DNS `cfm-na-conf.cfmna-tencent.com` NXDOMAIN separately. HTTPS/cert handling requires its own verified strategy.
6. **Offline gameplay**: map actual original menu→match engine route; use original client mode scripts/assets and bot behavior where available, no fake UI replacing the game.

## Protocol evidence
Real client packet: 133 bytes, one unique content repeated across targeted endpoints; `QueryAddrSvr` route; TGCP SYN extension 0x1001. v0.4 ACK: 65 bytes synthesized; v0.5 A/B: ACK causes EOF ~8ms median after send vs passive ~7 seconds; no client continuation. v0.6 logcat had no relevant native TGCP diagnostics. v0.7 confirms syntax but *not* semantics. v0.8 native receive gate hypothesis: server prefix likely `66 43` vs client outbound `43 66`; **on-phone experiment not yet confirmed**, never mark accepted without new capture.

## Validation discipline
- Passive SYN + no ACK is control.
- Real client ACK accepted = a *new client protocol message*, not server send().
- Distinguish relay EOF, app EOF, read timeout, app lifecycle.
- No infinite retry storms; min control, bounded experiment, app-filter.
- Preserve full context and SHA only for source files where independently verified. Original proprietary binaries remain only in Drive/local.

See [TGCP](knowledge-system/vault/research/TGCP.md), [Drive inventory](sources/DRIVE_MANIFEST.md), [acceptance](knowledge-system/vault/specs/ACCEPTANCE.md).

## Available isolated transport component — 2026-10-30

[Passive relay research](knowledge-system/vault/research/RELAY.md) documents the
original disabled-by-default loopback core and actual local tests. It is not the
historical SOCKS5 bridge or a TGCP server. A bounded SOCKS5 adapter and historical
source/capture recovery remain required before any device integration. Existing
unrelated passthrough routing must stay intact.

## SOCKS5 negotiation boundary — 2026-10-30

The [canonical handoff stage](experiments/socks5_handoff.py) now handles a bounded
NO-AUTH/CONNECT subset and preserves buffered data; [research](knowledge-system/vault/research/RELAY.md)
records 23 adapter tests. It is not a complete proxy. Historical normal CONNECT
passthrough must be recovered and verified before wiring the post-method hook,
actual loopback connector and bound reply. No live experiment is ready.

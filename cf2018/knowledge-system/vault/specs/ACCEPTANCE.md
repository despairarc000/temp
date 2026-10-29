# Acceptance — evidence gates and failure controls

| Gate | PASS must show | Not accepted |
|---|---|---|
| Bridge | Authentic client TCP 133-byte SYN captured by local Termux and specific IP/port routing, unrelated traffic passed through | proxy starts but game never connects |
| TGCP ACK | Real client sends new packet after ACK, stable socket and parsed state | `sendall` succeeds; local unit test only |
| AddressService | Parsed authentic request and accepted service response with service handoff | standalone synthetic Thrift test |
| Config/update | Original client gets past update screen with traced local services | mocked UI or bypass DLL that exits early |
| Offline game | Original client navigates and plays without Tencent live servers | demonstration webpage, recreated shooter |
| TDM bot | actual in-game bot spawning, AI, damage, score, timer, results and replay | running map with inert dummies |
| Bomb/S&D bot | bomb interaction, round teams, defend/attack AI, scoring and round end | TDM renamed to Bomb |
| Reliability | relaunch, shutdown, clean restore, bounded logs, no-root workflow | success only once, hundreds of uncontrolled retries |

Each gate: record version, device, hash or provenance, date, test command, original control, observed signal and negative result. Completed means verified on the actual game, not inferred from native static analysis or fabricated packet.

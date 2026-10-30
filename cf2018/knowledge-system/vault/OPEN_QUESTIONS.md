# OPEN QUESTIONS — bounded P0 queue

| ID | Unknown | How to falsify / resolve | State |
|---|---|---|---|
| Q-01 | Does server→client TGCP require opposite 2-byte magic from client→server? | Disassemble exact native load/compare in incoming splitter; unit-test both endian orders, compare with v0.8 phone A/B/C | HIGH-PRIORITY HYPOTHESIS |
| Q-02 | Does SOCKS5/relay or client originate early EOF? | Recover historical sources and directional evidence; new passive core has local lifecycle tests but no historical/device result | UNKNOWN |
| Q-03 | Which ACK base/session fields should be server-generated, echoed, or zeroed? | Trace `recv_ack_msg` field use and state machine; don't guess defaults | UNKNOWN |
| Q-04 | Is key mode 0 acceptable to this client's negotiated SYN? | Trace encryption branch and session constraints from native Apollo | UNKNOWN |
| Q-05 | What follows valid TGCP ACK? | Record real next client message in bounded on-device test | UNKNOWN |
| Q-06 | How to resolve discontinued config DNS safely? | Research narrow DNS remap and local TLS/HTTP after G2 | BLOCKED ON PRIORITY |
| Q-07 | What authoritative 2018 game client binaries are accessible in connected Drive? | Need a verified private target locator; bounded inventory failed a search positive control, so empty results do not prove absence | PARTIAL / BLOCKED_SOURCE |
| Q-08 | What original bot modes, scripts and assets are present? | Native/managed/OBB inventory after source access and provenance | UNKNOWN |

Do not schedule repeated 1000-connection retries. Each experimental run needs controls and a separate uniquely scoped report.

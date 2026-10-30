# CF18-G1-SOCKS5-01 acceptance — 2026-10-30

Defined before new adapter code. Base main:
`6a10445c21720b509f0023a804021cd47428d85e`. The previous local passive-core
draft was integrated by CF18-00; this packet does not re-submit it.

Authority: RFC 1928 sections 3-6, fetched from
https://www.rfc-editor.org/rfc/rfc1928.txt during this run. This is a bounded
NO-AUTH/CONNECT subset, not a claim of full RFC conformance (including GSSAPI).

- No listener/connector on import or direct execution. Disabled negotiation must
  leave streams untouched. Enabled calls accept connected loopback TCP only.
- Four to sixteen attempts per run, including malformed handshakes. One absolute
  handshake deadline, finite wire lengths, unique UUID run/connection IDs.
- Fragmented greeting/CONNECT fields work; bad version/reserved fields, empty
  method sets, unsupported authentication, commands and address types fail
  explicitly. IPv4/IPv6 addresses and opaque domain bytes remain distinct.
- Exact known IPv4 IP AND port pairs alone select a loopback redirect. Other
  IPv4, IPv6, domains (including IP-looking domains) and ports are handed back
  for normal CONNECT dispatch, without a failure reply, drop, DNS or redirect.
- Read exactly the negotiation fields so pipelined payload remains in the same
  reader. Never replay the greeting after METHOD=00 has already been sent.
- A handoff is not CONNECT success: the caller must actually establish a target
  before issuing a correctly bound SOCKS reply and invoking the canonical core.
- Test parsing, failures, byte preservation, cap/deadline and real localhost TCP
  fragmentation/handoff with independent synthetic bytes. Watchdog/clean up all
  test sockets. No phone, game IP connection, TGCP reply or ACK experiment.
- Logs contain only lifecycle status/IDs, never addresses, domain bytes, payload
  or raw exception messages. Never infer protocol/game advancement from tests.

Historical v0.1-v0.8 bridge sources and directional raw reports remain unavailable
to audit. A source-compatible post-negotiation hook must be verified before
integrating the proposal with PCAPdroid/Termux or claiming unchanged passthrough.

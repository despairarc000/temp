# Passive relay core — LOCAL_TEST_ONLY

2026-10-30: coordinator integrated original [relay code](../../../experiments/passive_relay.py)
and [19 transport tests](../../../tests/test_passive_relay.py). This is a
transport diagnostic core, not the missing historical v0.1-v0.8 probe or a
SOCKS5 server. Historical Q-02 remains UNKNOWN.

`DiagnosticRun()` is disabled by default. Importing or directly running the
module starts no listener or connector. An explicitly enabled caller must supply
two already-connected TCP stream pairs whose local and peer addresses are numeric
loopback addresses. The helper never connects to Tencent or a phone, parses TGCP,
constructs an ACK or changes game files. `local_target(ip, port)` returns a local
target only for the exact documented known-IP/8080-or-8085 pairs; None means no
redirect, not permission to block unrelated traffic.

Successful validation transfers both stream pairs to the core. Disabled/refused
calls retain caller ownership. One run holds at most 16 connection reports (four
by default), with distinct UUID connection IDs and one UUID run ID. Default
limits: ten seconds plus bounded close cleanup and 131072 queued bytes combined
across both directions. Configuration caps are 30 seconds and 1048576 bytes.
Metadata events are per lifecycle transition, not per payload chunk.

## Observation semantics

- `read_eof` names the local stream reader that returned empty bytes. It does not
  identify the original client process, packet-level FIN sender or causal error.
- `read_error`, `write_error` and `half_close_error` name the operation and side;
  reset is not rewritten as EOF. Only exception class is recorded, not messages.
- On EOF, write-half-close is propagated to the destination while the reverse
  direction stays alive. Unsupported/failed half-close is explicitly recorded.
- `deadline`, `byte_limit`, `local_stop`, `local_cancel` and cleanup `local_close`
  are distinct from peer EOF. Near-simultaneous events must not be interpreted as
  a verified network causal ordering; seq records this event loop's observations.
- Counts distinguish read, queued and drain-completed bytes. Even a completed
  drain is not peer application receipt or protocol acceptance. No payload bytes,
  raw exception text, endpoint addresses or session tokens are logged.

## Actual checks and remaining adapter work

From cf2018: `python -m unittest discover -s tests -v` passed 29 tests, including
19 relay tests. Five relay cases use real 127.0.0.1 TCP peers: both first-EOF
directions with binary traffic after half-close, silent timeout, explicit local
stop and caller cancellation. Other cases inject read/write/drain failures,
unsupported half-close, backpressure, combined byte caps and invalid scope/budgets.
All payloads are independent synthetic fixtures; no phone/device test occurred.

A bounded SOCKS5 negotiation/handoff stage is now available (see below).
A deployed adapter is still missing: actual target connection, correctly bound
CONNECT reply and the historical bridge's normal passthrough hook must be wired
and verified with a single 4-16-connection run budget before a device proposal.
The core alone cannot establish PCAPdroid/Termux compatibility or historical EOF
provenance. It has only been executed here with Python 3.12 on Linux; Android and
Termux execution remain unverified. Recover the historical source and directional
reports before attributing the old ~8 ms EOF.

No on-phone A/B/C packet is ready: exact native framing/session rules, the
historical candidate and relay provenance are prerequisites. See [questions](../OPEN_QUESTIONS.md),
[technical plan](../../../TECHNICAL_PLAN.md) and [integration record](../../../coordination/INTEGRATION.md).

## Integrated SOCKS5 handoff stage — 2026-10-30

Coordinator reviewed [CF18-03 packet](../../../coordination/incoming/CF18-03/RESULT.md)
from commit `9f77b2cbf9f0249b566c75e8a4e42666cb44c292` and integrated original
[NO-AUTH/CONNECT negotiation code](../../../experiments/socks5_handoff.py) plus
[23 canonical adapter tests](../../../tests/test_socks5_handoff.py). RFC 1928
sections 3-6 were the packet's protocol source; this subset does not implement
GSSAPI, authenticated subnegotiation, BIND or UDP and is not full RFC conformance.

NegotiationRun is disabled by default, opens no listener/connector and accepts
only already-connected loopback TCP. Four to sixteen attempts include malformed
handshakes; one absolute deadline bounds reads and METHOD-reply drain. Reports
contain IDs/status only. IPv4, IPv6 and opaque domain requests are parsed without
DNS; only exact known numeric IPv4 IP AND port pairs select a loopback target.
All others return a normal-dispatch handoff without CONNECT rejection or close.
Exact reads leave pipelined bytes in the original reader.

A valid handoff sent METHOD=00 but **has not sent CONNECT success**. A dispatcher
must connect first, issue the correct bound SOCKS reply and attach the passive
core without replaying the greeting or losing buffered bytes. Disabled None
retains caller ownership; rejection None has closed owned streams. Check enabled
state before dispatch so disabled behavior never drops existing bridge traffic.
Normal passthrough must run at the recovered post-method/parsed-CONNECT interface;
that historical interface is not verified. The module alone is not a functioning
SOCKS proxy, a replacement for the old probe or a ready phone experiment.

Actual coordinator checks: canonical suite 52 PASS, including 23 handoff and 19
relay tests; eight framing-audit tests also PASS. Adapter controls include one
real localhost fragmentation/pipelining handoff and a synthetic core-attachment
case; no real upstream target connection or complete proxy/device flow was tested.
Two coordinator controls add transport-reset message privacy and declared-domain
truncation. Direct module invocation printed the disabled message. G2 and Q-02
remain unchanged. No new native/library/historical source receipt was obtained.

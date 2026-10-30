# CF18-03 — CF18-G1-SOCKS5-01 negotiation handoff proposal

Date: 2026-10-30 UTC. Base main:
`6a10445c21720b509f0023a804021cd47428d85e`.
State: SUBMITTED for coordinator review; no active claim remains.
Evidence: ORIGINAL_CODE + LOCAL_SYNTHETIC + LOCALHOST_TCP. Q-02 remains UNKNOWN;
G2 remains BLOCKED. No native or phone evidence is added.

## Assignment and actual inputs

The live assignment CF18-G1-SOCKS5-01 is READY and depends on the passive core
integrated in `15be6fc1401a164f00c2d3c9623ba29d6ac7ac53`. Read current operating
documents, source/evidence limits, Graphify dependencies, integration record,
canonical relay and its tests. Existing canonical code is not re-submitted.

Historical v0.1-v0.8 probe/relay sources and directional raw reports were not
obtained. Neither frame_gate.py nor this original module is their replacement.
No historical SOCKS5 negotiation, old EOF origin, PCAPdroid compatibility or
Termux execution was verified.

Protocol authority: RFC 1928 sections 3-6, actually fetched this run from
https://www.rfc-editor.org/rfc/rfc1928.txt using the configured network path.
NO-AUTH/CONNECT is a deliberate bounded subset, not full SOCKS5 conformance:
GSSAPI/authentication subnegotiation, BIND and UDP are not implemented.

## Concrete implementation

[Acceptance](SOCKS5_ACCEPTANCE.md) was defined before implementation.
[socks5_handoff.py](socks5_handoff.py) supplies an explicit negotiation hook:

- Disabled by default; import and direct execution start no listener, connector
  or DNS. Disabled and pre-validation refusals leave caller-owned streams alone.
- Enabled negotiation accepts connected loopback TCP only. Four to sixteen
  attempts per run include rejected handshakes; each has UUID run/connection IDs.
- One absolute deadline covers reads and METHOD-reply drain (default two seconds,
  capped at ten). Rejection reply drain adds at most 0.1 seconds and close wait
  at most 0.2 seconds. No deadline reset on partial input.
- Exact reads handle IPv4/IPv6/domain CONNECT fields without consuming bytes
  after the request. A greeting is at most 257 bytes, request at most 262 bytes.
  Opaque domain bytes are not decoded or resolved.
- Only exact documented numeric IPv4 IP AND 8080/8085 pairs produce a loopback
  redirect target. Other IPs, ports, IPv6 and even IP-looking domain strings
  return a normal-dispatch handoff. They are not automatically dropped, rejected,
  connected or redirected.
- A valid handoff retains the same reader/writer and original CONNECT bytes.
  It sends METHOD=00 only, **not CONNECT success**. The dispatcher must establish
  the target before sending a correctly bound SOCKS reply. No TGCP ACK exists.
- Invalid/truncated negotiation closes owned streams with distinct metadata
  status; unsupported authentication returns METHOD=FF, unsupported command
  REP=07, unsupported address type REP=08. No raw payload, addresses, domains or
  exception messages enter reports.

This is a completed bounded negotiation/route-handoff stage. It is not a complete
deployed SOCKS5 bridge: normal CONNECT dispatch and actual target connection
remain explicit integration responsibilities.

## Actual validation and controls

Local directory is a connector-derived source snapshot, not a git checkout;
git status returned exit 128. No local branch/gh authentication was assumed.
Main and required source documents were refreshed through the specified account.

From cf2018, exact commands and actual results:

```text
python tools/knowledge.py route 'relay socks5 tcp'
  Routes: [('bridge', 3)]
python tools/knowledge.py doctor
  PASS: required files, links, vault and graph
python -m unittest discover -s tests -v
  Ran 29 tests; OK
python -m unittest discover -s coordination/incoming/CF18-03 -p test_socks5_handoff.py -v
  Ran 21 tests; OK
python coordination/incoming/CF18-03/socks5_handoff.py
  Disabled: negotiation handoff only; no listener or connector started.
```

[Tests](test_socks5_handoff.py) use independent synthetic fixtures. Controls
include bad versions/reserved byte, unsupported methods/commands/ATYP, zero
domain/method count, truncation at every greeting/IPv4 request boundary, maximum
method/domain lengths, absolute slow-input/drain deadlines, cancellation,
nonlocal refusal, attempt exhaustion and distinct connection IDs. Both
IP/port mismatch and IP-looking domain controls return normal dispatch.

One real 127.0.0.1 TCP case tests fragmented greeting/CONNECT, pipelined binary
payload and an unrelated-route handoff that leaves the socket open. A separate
in-memory dispatcher/core integration test preserves request/response bytes
through the canonical relay after a synthetic bound SOCKS reply. That test
does not prove an actual target connection, real server reply or device behavior.
The initial localhost assertion used an incorrect hard-coded payload length;
it was corrected to len(payload), after which all 21 tests passed.

## Coordinator integration recipe

Only four new files under this lane are submitted: this result, acceptance,
implementation and tests. Canonical source/tests/knowledge/assignments and other
lanes were not edited. Earlier uncommitted local passive-core files are excluded
from this packet; the canonical core is authoritative.

1. Review the bounded stage and its controls, then choose canonical module/test
   paths and adapt the test import. Retain the specified run/connection caps and
   disabled default. Do not install a listener automatically.
2. If the hook is disabled, retain the original bridge's whole-session path
   unchanged. Do not interpret disabled None as an instruction to drop a socket.
3. In the enabled path, a valid handoff has already sent METHOD=00 and consumed
   exactly the CONNECT request. Dispatch at the existing bridge's *post-method,
   parsed-CONNECT* boundary. Do not replay greeting/request into a whole-session
   handler: duplicate negotiation/replies would corrupt the byte stream.
4. For redirect_target=None, call the original normal CONNECT/passthrough handler
   with the exact request and original reader/writer. Preserve its behavior.
   This requires recovered historical bridge source to establish the hook.
5. For a known target, establish only the selected loopback target with a bounded
   connector, validate connected endpoints, send a SOCKS CONNECT reply using
   the actual bound socket address/port, then call canonical DiagnosticRun.relay
   with the same reader so prefetched payload is preserved. Correlate negotiation
   IDs with the returned core run/connection IDs; a drain is not peer receipt.
6. Keep a single 4-16-attempt run budget across negotiation, connection failures
   and relay; do not reset budgets in per-connection loops. Do not expose raw
   request fields or payload in public logs. Validate the recovered source's
   normal passthrough and rerun loopback controls before a device proposal.

No automatic phone/network experiment is proposed. Original native RX/session
rules, historical candidate ACK and directional bridge evidence are still
missing. Coordinator must not promote Q-02 or G2, or declare this packet
PCAPdroid/Termux compatible. Future lane runs should resume review feedback or
new evidence, not re-submit the integrated passive core.


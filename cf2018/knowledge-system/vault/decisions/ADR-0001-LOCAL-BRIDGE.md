# ADR-0001 — local network redirection first
Date: 2026-10-30. Status: ADOPTED FOR EXPERIMENTS.

## Decision
Use original-code signed 2018 client and PCAPdroid app-filtered SOCKS5 to a loopback Termux server. Reconstruct minimal discontinued service protocol progressively. Keep original resources in Drive/phone, and public GitHub workspace limited to new clean-room code/tests and analyses.

## Why
DLL modifications broke a working startup control; SOCKS5 path is proven to carry real 133-byte TGCP SYN without modifying protected DLL. This minimizes game integrity risks and allows byte-level evidence.

## Trade-offs
PCAPdroid uses the only Android VPN slot; DNS NXDOMAIN still separate; some endpoints use HTTP/TLS; Apollo TGCP ACK is unaccepted; offline gameplay may require additional client-side changes later if server-only path is insufficient. Server-only strategy is **a preferred hypothesis**, not proof all features can be unlocked this way.

Next gate in [TGCP](../research/TGCP.md) and [ACCEPTANCE](../specs/ACCEPTANCE.md).

"""Bounded, disabled-by-default SOCKS5 NO-AUTH/CONNECT handoff proposal.

No listener, connector, DNS or TGCP implementation. Python 3.10+ stdlib.
A valid handoff leaves CONNECT reply and stream ownership with the dispatcher.
"""
import asyncio
import ipaddress
import socket
import uuid
from typing import NamedTuple


KNOWN_IPS = frozenset(("45.113.69.32", "211.159.211.105", "119.28.34.12"))
KNOWN_PORTS = frozenset((8080, 8085))


class ConnectRequest(NamedTuple):
    atyp: int
    host: object  # Numeric string for IPv4/IPv6; opaque bytes for a domain.
    port: int
    raw_request: bytes  # Runtime handoff only; must never be logged/uploaded.


class Handoff(NamedTuple):
    request: ConnectRequest
    redirect_target: object  # (loopback IP, port), or None for normal dispatch.
    reader: object
    writer: object
    run_id: str
    connection_id: str


class Rejected(Exception):
    def __init__(self, reason, reply=None):
        self.reason = reason
        self.reply = reply


def failure_reply(code):
    """RFC 1928 error reply: IPv4 unspecified bound address and port."""
    return bytes((5, code, 0, 1)) + b"\x00" * 6


def require_local_stream(writer):
    sock = writer.get_extra_info("socket")
    if (sock is None or sock.family not in (socket.AF_INET, socket.AF_INET6)
            or getattr(sock, "type", 0) & 0xf != socket.SOCK_STREAM):
        raise ValueError("connected loopback TCP required")
    for key in ("peername", "sockname"):
        address = writer.get_extra_info(key)
        if not address or not ipaddress.ip_address(address[0]).is_loopback:
            raise ValueError("connected loopback TCP required")


class NegotiationRun:
    """An explicit local integration hook, not a running SOCKS5 server.

    On success the dispatcher owns the original reader/writer and must send
    CONNECT success/failure itself. METHOD=00 was already sent; do not replay
    the greeting into a legacy whole-session handler. Unknown routes are normal
    dispatch handoffs, never automatically blocked or connected by this module.
    """
    def __init__(self, *, enabled=False, max_connections=4, timeout=2.0):
        if type(max_connections) is not int or not 4 <= max_connections <= 16:
            raise ValueError("attempt budget must be 4..16")
        if not 0 < timeout <= 10:
            raise ValueError("handshake deadline must be positive and at most 10 seconds")
        self.enabled = enabled is True
        self.max_connections = max_connections
        self.timeout = timeout
        self.run_id = uuid.uuid4().hex
        self.reports = []

    async def negotiate(self, reader, writer):
        if not self.enabled:
            return None  # No ownership transfer, read, write or close.
        if len(self.reports) >= self.max_connections:
            raise ValueError("attempt budget exhausted; caller retains ownership")
        require_local_stream(writer)
        report = {"run_id": self.run_id, "connection_id": uuid.uuid4().hex,
                  "status": "negotiating"}
        self.reports.append(report)  # Claim the slot before the first await.
        phase = "greeting"

        async def exchange():
            nonlocal phase
            greeting = await reader.readexactly(2)
            if greeting[0] != 5:
                raise Rejected("bad_greeting_version")
            if not greeting[1]:
                raise Rejected("empty_methods", b"\x05\xff")
            methods = await reader.readexactly(greeting[1])
            if 0 not in methods:
                raise Rejected("no_supported_method", b"\x05\xff")
            writer.write(b"\x05\x00")
            await writer.drain()
            phase = "request"
            header = await reader.readexactly(4)
            if header[0] != 5 or header[2] != 0:
                raise Rejected("bad_request_header", failure_reply(1))
            if header[1] != 1:
                raise Rejected("unsupported_command", failure_reply(7))
            atyp = header[3]
            if atyp in (1, 4):
                address = await reader.readexactly(4 if atyp == 1 else 16)
                host = str(ipaddress.ip_address(address))
                wire_address = address
            elif atyp == 3:
                length = await reader.readexactly(1)
                if not length[0]:
                    raise Rejected("empty_domain", failure_reply(8))
                host = await reader.readexactly(length[0])
                wire_address = length + host
            else:
                raise Rejected("unsupported_address_type", failure_reply(8))
            port_bytes = await reader.readexactly(2)
            port = int.from_bytes(port_bytes, "big")
            request = ConnectRequest(atyp, host, port, header + wire_address + port_bytes)
            target = (("127.0.0.1", port)
                      if atyp == 1 and host in KNOWN_IPS and port in KNOWN_PORTS else None)
            report["status"] = "redirect_handoff" if target else "passthrough_handoff"
            return Handoff(request, target, reader, writer, self.run_id, report["connection_id"])

        try:
            # One deadline covers all reads AND the method-reply drain.
            return await asyncio.wait_for(exchange(), self.timeout)
        except Rejected as exc:
            report["status"] = exc.reason
            if exc.reply is not None:
                try:
                    writer.write(exc.reply)
                    await asyncio.wait_for(writer.drain(), 0.1)
                except (OSError, RuntimeError, asyncio.TimeoutError):
                    report["reply_write_failed"] = True
        except asyncio.IncompleteReadError:
            report["status"] = "truncated_" + phase
        except asyncio.TimeoutError:
            report["status"] = "handshake_deadline"
        except (OSError, RuntimeError) as exc:
            report["status"] = "transport_error"
            report["error_type"] = type(exc).__name__
        except asyncio.CancelledError:
            report["status"] = "local_cancel"
            raise
        finally:
            if report["status"] not in ("redirect_handoff", "passthrough_handoff"):
                writer.close()
                try:
                    await asyncio.wait_for(writer.wait_closed(), 0.2)
                except (OSError, RuntimeError, asyncio.TimeoutError):
                    report["close_failed"] = True
        return None


if __name__ == "__main__":
    print("Disabled: negotiation handoff only; no listener or connector started.")

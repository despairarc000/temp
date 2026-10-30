"""Disabled-by-default loopback TCP diagnostic core, not a SOCKS5 server.

No listener, connector, packet parser or generated ACK. Python 3.10+ stdlib.
The caller must finish SOCKS5 negotiation before transferring stream ownership.
"""
import asyncio
import ipaddress
import socket
import time
import uuid


KNOWN_IPS = frozenset(("45.113.69.32", "211.159.211.105", "119.28.34.12"))
KNOWN_PORTS = frozenset((8080, 8085))


def local_target(ip, port):
    """Return a local redirect only for a documented exact IP/port pair.

    None means no redirect; the SOCKS5 adapter must preserve its normal routing.
    This function never resolves a hostname or opens a connection.
    """
    if ip in KNOWN_IPS and type(port) is int and port in KNOWN_PORTS:
        return ("127.0.0.1", port)
    return None


def require_loopback_tcp(writer):
    sock = writer.get_extra_info("socket")
    if (sock is None or sock.family not in (socket.AF_INET, socket.AF_INET6)
            or getattr(sock, "type", 0) & 0xf != socket.SOCK_STREAM):
        raise ValueError("connected loopback TCP stream required")
    for key in ("sockname", "peername"):
        address = writer.get_extra_info(key)
        if not address or not ipaddress.ip_address(address[0]).is_loopback:
            raise ValueError("connected loopback TCP stream required")


class DiagnosticRun:
    """One finite run; explicitly enable only in a controlled local adapter.

    Successful validation transfers ownership of both stream pairs to relay().
    Disabled/refused calls leave caller-owned streams untouched. A cancellation
    propagates after cleanup; its metadata remains available in reports.
    """

    def __init__(self, *, enabled=False, max_connections=4, timeout=10.0,
                 byte_limit=131072):
        if type(max_connections) is not int or not 1 <= max_connections <= 16:
            raise ValueError("connection budget must be 1..16")
        if not 0 < timeout <= 30:
            raise ValueError("duration must be positive and at most 30 seconds")
        if type(byte_limit) is not int or not 1 <= byte_limit <= 1048576:
            raise ValueError("byte budget must be 1..1048576")
        self.enabled = enabled is True
        self.max_connections = max_connections
        self.timeout = timeout
        self.byte_limit = byte_limit
        self.run_id = uuid.uuid4().hex
        self.reports = []

    async def relay(self, client_reader, client_writer, upstream_reader,
                    upstream_writer, *, stop=None):
        if not self.enabled:
            return {"status": "disabled", "run_id": self.run_id}
        if len(self.reports) >= self.max_connections:
            raise ValueError("run connection budget exhausted")
        require_loopback_tcp(client_writer)
        require_loopback_tcp(upstream_writer)
        started = time.monotonic()
        report = {
            "run_id": self.run_id, "connection_id": uuid.uuid4().hex,
            "status": "running", "events": [],
            "read_bytes": {"client": 0, "upstream": 0},
            "queued_bytes": {"client": 0, "upstream": 0},
            "drained_bytes": {"client": 0, "upstream": 0},
        }
        self.reports.append(report)  # No await before consuming the run slot.

        def event(kind, side=None, **fields):
            # No per-chunk events. At most a fixed number of terminal/cleanup
            # events per connection; never log payload or exception messages.
            report["events"].append({
                "seq": len(report["events"]),
                "elapsed_s": time.monotonic() - started,
                "kind": kind, "side": side, **fields,
            })

        async def pump(reader, writer, side, destination):
            while True:
                remaining = self.byte_limit - sum(report["queued_bytes"].values())
                try:
                    data = await reader.read(min(4096, remaining + 1))
                except OSError as exc:
                    event("read_error", side, error_type=type(exc).__name__)
                    return "read_error"
                if not data:
                    event("read_eof", side)
                    if not writer.can_write_eof():
                        event("half_close_unavailable", destination)
                        return "half_close_unavailable"
                    try:
                        writer.write_eof()
                        await writer.drain()
                    except (OSError, RuntimeError) as exc:
                        event("half_close_error", destination,
                              error_type=type(exc).__name__)
                        return "half_close_error"
                    event("write_half_close", destination)
                    return "eof"
                report["read_bytes"][side] += len(data)
                # Recompute after read: the reverse pump may have queued bytes.
                remaining = self.byte_limit - sum(report["queued_bytes"].values())
                if len(data) > remaining:
                    event("byte_limit", side)
                    return "byte_limit"
                try:
                    writer.write(data)
                    report["queued_bytes"][side] += len(data)
                    await writer.drain()
                    report["drained_bytes"][side] += len(data)
                except (OSError, RuntimeError) as exc:
                    event("write_error", destination, source=side,
                          error_type=type(exc).__name__)
                    return "write_error"

        event("start")
        pumps = {
            asyncio.create_task(pump(client_reader, upstream_writer, "client", "upstream")),
            asyncio.create_task(pump(upstream_reader, client_writer, "upstream", "client")),
        }
        stopper = asyncio.create_task(stop.wait()) if stop is not None else None
        waiting = set(pumps)
        if stopper is not None:
            waiting.add(stopper)
        try:
            remaining_pumps = set(pumps)
            while remaining_pumps:
                left = max(0, self.timeout - (time.monotonic() - started))
                done, _ = await asyncio.wait(waiting, timeout=left,
                                             return_when=asyncio.FIRST_COMPLETED)
                if not done:
                    event("deadline")
                    report["status"] = "deadline"
                    break
                # A requested local stop is recorded independently of peer EOF.
                if stopper in done:
                    event("local_stop")
                    report["status"] = "local_stop"
                    break
                failed = False
                for task in done:
                    waiting.remove(task)
                    remaining_pumps.discard(task)
                    outcome = task.result()
                    if outcome != "eof":
                        report["status"] = outcome
                        failed = True
                if failed:
                    break
            else:
                report["status"] = "eof_both"
        except asyncio.CancelledError:
            event("local_cancel")
            report["status"] = "local_cancel"
            raise
        except Exception as exc:
            event("local_error", error_type=type(exc).__name__)
            report["status"] = "local_error"
            raise
        finally:
            all_tasks = pumps | ({stopper} if stopper is not None else set())
            for task in all_tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*all_tasks, return_exceptions=True)
            event("local_close")  # Cleanup is not a remote EOF observation.
            for writer in (client_writer, upstream_writer):
                writer.close()
            for writer, side in ((client_writer, "client"), (upstream_writer, "upstream")):
                try:
                    await asyncio.wait_for(writer.wait_closed(), timeout=0.2)
                except (OSError, asyncio.TimeoutError) as exc:
                    event("close_error", side, error_type=type(exc).__name__)
            event("end")
        return report


if __name__ == "__main__":
    print("Disabled: diagnostic core only; no listener or network traffic started.")

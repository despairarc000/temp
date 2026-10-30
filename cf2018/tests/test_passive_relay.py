"""Synthetic localhost lifecycle tests; never connect to a game or phone."""
import asyncio
import importlib.util
import json
from pathlib import Path
import socket
from types import SimpleNamespace
import unittest

spec = importlib.util.spec_from_file_location(
    "passive_relay_under_test", Path(__file__).resolve().parents[1] / "experiments/passive_relay.py"
)
relay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(relay)


class ScriptReader:
    """Finite injected reads, then wait indefinitely until the core cancels."""
    def __init__(self, *items):
        self.queue = asyncio.Queue()
        self.carry = b""
        for item in items:
            self.queue.put_nowait(item)

    async def read(self, size):
        item = self.carry or await self.queue.get()
        if isinstance(item, Exception):
            raise item
        self.carry = item[size:]
        return item[:size]


class ScriptWriter:
    def __init__(self, *, peer="127.0.0.1", local="127.0.0.1", fail=None,
                 supports_eof=True, block_drain=False, sock_type=socket.SOCK_STREAM):
        self.peer, self.local = peer, local
        self.fail = fail
        self.supports_eof = supports_eof
        self.block_drain = block_drain
        self.data = bytearray()
        self.closed = False
        self.sock_type = sock_type

    def get_extra_info(self, key):
        return {"socket": SimpleNamespace(family=socket.AF_INET, type=self.sock_type),
                "peername": (self.peer, 12345), "sockname": (self.local, 23456)}[key]

    def write(self, data):
        if self.fail == "write":
            raise BrokenPipeError("synthetic-secret-must-not-be-logged")
        self.data.extend(data)

    async def drain(self):
        if self.fail == "drain":
            raise ConnectionResetError("synthetic-secret-must-not-be-logged")
        if self.block_drain:
            await asyncio.Event().wait()

    def can_write_eof(self):
        return self.supports_eof

    def write_eof(self):
        if self.fail == "eof":
            raise BrokenPipeError("synthetic half-close failure")

    def close(self):
        self.closed = True

    async def wait_closed(self):
        return


class RelayTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.writers = []
        self.tasks = []
        self.servers = []

    async def asyncTearDown(self):
        for task in self.tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        for writer in self.writers:
            writer.close()
        await asyncio.gather(*(w.wait_closed() for w in self.writers), return_exceptions=True)
        for server in self.servers:
            server.close()
            await asyncio.wait_for(server.wait_closed(), 1)

    async def tcp_pair(self):
        accepted = asyncio.get_running_loop().create_future()

        def connected(reader, writer):
            self.writers.append(writer)
            accepted.set_result((reader, writer))

        server = await asyncio.start_server(connected, "127.0.0.1", 0)
        self.servers.append(server)
        try:
            peer = await asyncio.open_connection("127.0.0.1", server.sockets[0].getsockname()[1])
            self.writers.append(peer[1])
            local = await asyncio.wait_for(accepted, 1)
            return peer, local
        finally:
            server.close()
            # Python 3.12 wait_closed also waits for accepted connections.
            # Those streams must remain open for the test; await in teardown.

    async def real_relay(self, **options):
        client, client_local = await self.tcp_pair()
        upstream, upstream_local = await self.tcp_pair()
        run = relay.DiagnosticRun(enabled=True, timeout=1, **options)
        task = asyncio.create_task(run.relay(*client_local, *upstream_local))
        self.tasks.append(task)
        return client, upstream, task, run

    async def test_client_eof_preserves_reverse_binary_traffic(self):
        async def case():
            client, upstream, task, _ = await self.real_relay()
            data = bytes(range(256)) + b"\x00synthetic-client"
            client[1].write(data[:1])
            await client[1].drain()
            client[1].write(data[1:])
            client[1].write_eof()
            self.assertEqual(await upstream[0].read(), data)
            reply = b"synthetic-response\xff\x00"
            upstream[1].write(reply)
            upstream[1].write_eof()
            self.assertEqual(await client[0].read(), reply)
            report = await task
            self.assertEqual(report["status"], "eof_both")
            eof = [e["side"] for e in report["events"] if e["kind"] == "read_eof"]
            self.assertEqual(eof, ["client", "upstream"])
            self.assertEqual(report["drained_bytes"], {"client": len(data), "upstream": len(reply)})
        await asyncio.wait_for(case(), 3)

    async def test_upstream_eof_preserves_reverse_binary_traffic(self):
        async def case():
            client, upstream, task, _ = await self.real_relay()
            response = b"\x00synthetic-upstream\xff"
            upstream[1].write(response)
            upstream[1].write_eof()
            self.assertEqual(await client[0].read(), response)
            request = bytes(reversed(range(256)))
            client[1].write(request)
            client[1].write_eof()
            self.assertEqual(await upstream[0].read(), request)
            report = await task
            self.assertEqual(report["status"], "eof_both")
            eof = [e["side"] for e in report["events"] if e["kind"] == "read_eof"]
            self.assertEqual(eof, ["upstream", "client"])
        await asyncio.wait_for(case(), 3)

    async def test_real_silent_peers_end_as_deadline_not_remote_eof(self):
        async def case():
            client, client_local = await self.tcp_pair()
            upstream, upstream_local = await self.tcp_pair()
            run = relay.DiagnosticRun(enabled=True, timeout=0.03)
            report = await run.relay(*client_local, *upstream_local)
            kinds = [e["kind"] for e in report["events"]]
            self.assertEqual(report["status"], "deadline")
            self.assertNotIn("read_eof", kinds)
            self.assertLess(kinds.index("deadline"), kinds.index("local_close"))
        await asyncio.wait_for(case(), 3)

    async def test_explicit_stop_is_local(self):
        async def case():
            _, client_local = await self.tcp_pair()
            _, upstream_local = await self.tcp_pair()
            stop = asyncio.Event()
            stop.set()
            run = relay.DiagnosticRun(enabled=True, timeout=1)
            report = await run.relay(*client_local, *upstream_local, stop=stop)
            self.assertEqual(report["status"], "local_stop")
            self.assertFalse(any(e["kind"] == "read_eof" for e in report["events"]))
        await asyncio.wait_for(case(), 3)

    async def test_cancellation_cleans_up_and_keeps_local_attribution(self):
        async def case():
            _, _, task, run = await self.real_relay()
            await asyncio.sleep(0)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            report = run.reports[0]
            self.assertEqual(report["status"], "local_cancel")
            self.assertEqual([e["kind"] for e in report["events"]][-2:], ["local_close", "end"])
        await asyncio.wait_for(case(), 3)

    async def test_disabled_call_touches_no_stream(self):
        run = relay.DiagnosticRun()
        report = await run.relay(None, None, None, None)
        self.assertEqual(report["status"], "disabled")
        self.assertEqual(run.reports, [])

    async def test_refuses_nonloopback_without_taking_ownership(self):
        for key in ("peer", "local"):
            with self.subTest(key=key):
                bad = ScriptWriter(**{key: "192.0.2.1"})
                good = ScriptWriter()
                run = relay.DiagnosticRun(enabled=True)
                with self.assertRaises(ValueError):
                    await run.relay(ScriptReader(), bad, ScriptReader(), good)
                self.assertFalse(bad.closed or good.closed)
                self.assertEqual(run.reports, [])

    async def test_read_reset_is_read_error_not_eof(self):
        report = await relay.DiagnosticRun(enabled=True).relay(
            ScriptReader(ConnectionResetError("synthetic-secret")), ScriptWriter(),
            ScriptReader(), ScriptWriter())
        self.assertEqual(report["status"], "read_error")
        e = next(e for e in report["events"] if e["kind"] == "read_error")
        self.assertEqual(e["side"], "client")
        self.assertNotIn("synthetic-secret", json.dumps(report))

    async def test_refuses_non_tcp_socket(self):
        bad = ScriptWriter(sock_type=socket.SOCK_DGRAM)
        run = relay.DiagnosticRun(enabled=True)
        with self.assertRaises(ValueError):
            await run.relay(ScriptReader(), bad, ScriptReader(), ScriptWriter())
        self.assertFalse(bad.closed)
        self.assertEqual(run.reports, [])

    async def test_write_and_drain_failure_name_destination(self):
        for operation in ("write", "drain"):
            with self.subTest(operation=operation):
                report = await relay.DiagnosticRun(enabled=True).relay(
                    ScriptReader(b"synthetic-data"), ScriptWriter(),
                    ScriptReader(), ScriptWriter(fail=operation))
                self.assertEqual(report["status"], "write_error")
                event = next(e for e in report["events"] if e["kind"] == "write_error")
                self.assertEqual((event["source"], event["side"]), ("client", "upstream"))
                self.assertEqual(report["drained_bytes"]["client"], 0)
                self.assertNotIn("synthetic-secret", json.dumps(report))
                self.assertNotIn("synthetic-data", json.dumps(report))

    async def test_half_close_failures_are_explicit(self):
        for writer, status in ((ScriptWriter(supports_eof=False), "half_close_unavailable"),
                               (ScriptWriter(fail="eof"), "half_close_error")):
            with self.subTest(status=status):
                report = await relay.DiagnosticRun(enabled=True).relay(
                    ScriptReader(b""), ScriptWriter(), ScriptReader(), writer)
                self.assertEqual(report["status"], status)

    async def test_byte_limit_does_not_forward_over_budget_chunk(self):
        destination = ScriptWriter()
        report = await relay.DiagnosticRun(enabled=True, byte_limit=4).relay(
            ScriptReader(b"synthetic"), ScriptWriter(), ScriptReader(), destination)
        self.assertEqual(report["status"], "byte_limit")
        self.assertEqual(destination.data, b"")
        self.assertEqual(report["read_bytes"]["client"], 5)

    async def test_backpressure_timeout_does_not_claim_peer_receipt(self):
        report = await relay.DiagnosticRun(enabled=True, timeout=0.03).relay(
            ScriptReader(b"abc"), ScriptWriter(), ScriptReader(), ScriptWriter(block_drain=True))
        self.assertEqual(report["status"], "deadline")
        self.assertEqual(report["queued_bytes"]["client"], 3)
        self.assertEqual(report["drained_bytes"]["client"], 0)

    async def test_unique_ids_budget_and_event_order(self):
        run = relay.DiagnosticRun(enabled=True, max_connections=2)
        reports = []
        for _ in range(2):
            reports.append(await run.relay(ScriptReader(b""), ScriptWriter(),
                                           ScriptReader(b""), ScriptWriter()))
        self.assertNotEqual(reports[0]["connection_id"], reports[1]["connection_id"])
        self.assertEqual(reports[0]["run_id"], reports[1]["run_id"])
        self.assertNotEqual(run.run_id, relay.DiagnosticRun().run_id)
        with self.assertRaises(ValueError):
            await run.relay(None, None, None, None)
        for report in reports:
            events = report["events"]
            self.assertEqual([e["seq"] for e in events], list(range(len(events))))
            self.assertEqual([e["elapsed_s"] for e in events], sorted(e["elapsed_s"] for e in events))
            self.assertLess(len(events), 16)

    async def test_upstream_read_reset_names_upstream(self):
        report = await relay.DiagnosticRun(enabled=True).relay(
            ScriptReader(), ScriptWriter(),
            ScriptReader(ConnectionResetError("synthetic")), ScriptWriter())
        self.assertEqual(report["status"], "read_error")
        event = next(e for e in report["events"] if e["kind"] == "read_error")
        self.assertEqual(event["side"], "upstream")
        self.assertFalse(any(e["kind"] == "read_eof" for e in report["events"]))

    async def test_reverse_write_failure_names_client(self):
        report = await relay.DiagnosticRun(enabled=True).relay(
            ScriptReader(), ScriptWriter(fail="write"),
            ScriptReader(b"synthetic-response"), ScriptWriter())
        self.assertEqual(report["status"], "write_error")
        event = next(e for e in report["events"] if e["kind"] == "write_error")
        self.assertEqual((event["source"], event["side"]), ("upstream", "client"))
        self.assertEqual(report["drained_bytes"]["upstream"], 0)

    async def test_combined_bidirectional_byte_budget(self):
        report = await relay.DiagnosticRun(enabled=True, byte_limit=4).relay(
            ScriptReader(b"abc"), ScriptWriter(),
            ScriptReader(b"xyz"), ScriptWriter())
        self.assertEqual(report["status"], "byte_limit")
        self.assertLessEqual(sum(report["queued_bytes"].values()), 4)
        self.assertLessEqual(sum(report["drained_bytes"].values()), 4)


class ScopeTests(unittest.TestCase):
    def test_exact_ip_and_port_redirect_only(self):
        for ip in relay.KNOWN_IPS:
            for port in relay.KNOWN_PORTS:
                self.assertEqual(relay.local_target(ip, port), ("127.0.0.1", port))
        for ip, port in (("192.0.2.1", 8080), ("45.113.69.32", 443),
                         ("45.113.69.32.example", 8080), ("45.113.69.32", "8080")):
            self.assertIsNone(relay.local_target(ip, port))

    def test_invalid_budgets_refused(self):
        for options in ({"max_connections": 0}, {"max_connections": 17},
                        {"timeout": 0}, {"timeout": float("nan")},
                        {"timeout": 31}, {"byte_limit": 0}, {"byte_limit": 1048577}):
            with self.subTest(options=options):
                with self.assertRaises(ValueError):
                    relay.DiagnosticRun(**options)


if __name__ == "__main__":
    unittest.main()

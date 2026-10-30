"""Independent synthetic SOCKS5 fixtures, including real localhost handoff."""
import asyncio
import importlib.util
import ipaddress
import json
from pathlib import Path
import socket
from types import SimpleNamespace
import unittest

spec = importlib.util.spec_from_file_location(
    "socks5_handoff_under_test", Path(__file__).resolve().parents[1] / "experiments/socks5_handoff.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def request(host="45.113.69.32", port=8080, atyp=1, command=1, reserved=0):
    if atyp == 1:
        address = ipaddress.IPv4Address(host).packed
    elif atyp == 4:
        address = ipaddress.IPv6Address(host).packed
    elif atyp == 3:
        address = bytes((len(host),)) + host
    else:
        address = b""
    return bytes((5, command, reserved, atyp)) + address + port.to_bytes(2, "big")


class Writer:
    def __init__(self, *, peer="127.0.0.1", block=False):
        self.peer, self.block = peer, block
        self.data = bytearray()
        self.closed = False

    def get_extra_info(self, key):
        return {"socket": SimpleNamespace(family=socket.AF_INET, type=socket.SOCK_STREAM),
                "peername": (self.peer, 23456), "sockname": ("127.0.0.1", 12345)}[key]

    def write(self, data):
        self.data.extend(data)

    async def drain(self):
        if self.block:
            await asyncio.Event().wait()

    def close(self):
        self.closed = True

    async def wait_closed(self):
        return

    def can_write_eof(self):
        return True

    def write_eof(self):
        return


def reader(data=b"", eof=True):
    stream = asyncio.StreamReader()
    stream.feed_data(data)
    if eof:
        stream.feed_eof()
    return stream


class HandoffTests(unittest.IsolatedAsyncioTestCase):
    async def exchange(self, data, **options):
        stream, writer = reader(data), Writer()
        run = adapter.NegotiationRun(enabled=True, **options)
        handoff = await asyncio.wait_for(run.negotiate(stream, writer), 1)
        return handoff, stream, writer, run

    async def test_known_ipv4_requires_both_exact_ip_and_port(self):
        for host in adapter.KNOWN_IPS:
            for port in adapter.KNOWN_PORTS:
                h, _, writer, _ = await self.exchange(b"\x05\x01\x00" + request(host, port))
                self.assertEqual(h.redirect_target, ("127.0.0.1", port))
                self.assertEqual(writer.data, b"\x05\x00")
                self.assertFalse(writer.closed)  # No CONNECT success or teardown.
        for host, port in (("192.0.2.1", 8080), ("45.113.69.32", 443)):
            h, _, writer, run = await self.exchange(b"\x05\x01\x00" + request(host, port))
            self.assertIsNone(h.redirect_target)
            self.assertEqual(run.reports[0]["status"], "passthrough_handoff")
            self.assertFalse(writer.closed)

    async def test_pipelined_binary_payload_and_original_request_preserved(self):
        wire = request()
        payload = bytes(range(256)) + b"\x00synthetic"
        h, stream, writer, run = await self.exchange(b"\x05\x01\x00" + wire + payload)
        self.assertEqual(h.request.raw_request, wire)
        self.assertIs(h.reader, stream)
        self.assertIs(h.writer, writer)
        self.assertEqual(await h.reader.read(), payload)
        self.assertEqual(writer.data, b"\x05\x00")
        self.assertNotIn("synthetic", json.dumps(run.reports))
        self.assertNotIn("45.113", json.dumps(run.reports))

    async def test_domain_bytes_are_opaque_and_never_resolved_or_redirected(self):
        for host in (b"45.113.69.32", b"synthetic.invalid", b"\xff\x00opaque"):
            h, _, writer, _ = await self.exchange(b"\x05\x01\x00" + request(host, atyp=3))
            self.assertEqual(h.request.host, host)
            self.assertIsNone(h.redirect_target)
            self.assertFalse(writer.closed)

    async def test_ipv6_remains_normal_dispatch(self):
        h, _, writer, _ = await self.exchange(b"\x05\x01\x00" + request("2001:db8::1", atyp=4))
        self.assertEqual(h.request.host, "2001:db8::1")
        self.assertIsNone(h.redirect_target)
        self.assertFalse(writer.closed)

    async def test_maximum_domain_and_method_lengths_are_finite(self):
        wire = b"\x05\xff" + bytes(range(255)) + request(b"a" * 255, atyp=3)
        h, _, _, _ = await self.exchange(wire)
        self.assertEqual(len(h.request.raw_request), 262)
        self.assertEqual(len(h.request.host), 255)

    async def test_no_auth_can_be_selected_from_multiple_methods(self):
        h, _, writer, _ = await self.exchange(b"\x05\x03\x02\x00\x01" + request())
        self.assertIsNotNone(h)
        self.assertEqual(writer.data, b"\x05\x00")

    async def test_no_supported_auth_rejected(self):
        h, _, writer, run = await self.exchange(b"\x05\x02\x01\x02")
        self.assertIsNone(h)
        self.assertEqual(writer.data, b"\x05\xff")
        self.assertEqual(run.reports[0]["status"], "no_supported_method")
        self.assertTrue(writer.closed)

    async def test_bad_greeting_and_empty_method_set(self):
        for wire, expected in ((b"\x04\x01\x00", b""), (b"\x05\x00", b"\x05\xff")):
            h, _, writer, _ = await self.exchange(wire)
            self.assertIsNone(h)
            self.assertEqual(writer.data, expected)
            self.assertTrue(writer.closed)

    async def test_bad_request_header_rejected(self):
        for wire in (b"\x04\x01\x00\x01", b"\x05\x01\x01\x01"):
            h, _, writer, _ = await self.exchange(b"\x05\x01\x00" + wire)
            self.assertIsNone(h)
            self.assertEqual(writer.data, b"\x05\x00" + adapter.failure_reply(1))
            self.assertTrue(writer.closed)

    async def test_bind_and_udp_commands_rejected_explicitly(self):
        for command in (2, 3, 255):
            h, _, writer, _ = await self.exchange(b"\x05\x01\x00" + request(command=command))
            self.assertIsNone(h)
            self.assertEqual(writer.data[-10:], adapter.failure_reply(7))
            self.assertTrue(writer.closed)

    async def test_unsupported_address_and_empty_domain_rejected(self):
        for wire in (b"\x05\x01\x00\x02", b"\x05\x01\x00\x03\x00"):
            h, _, writer, _ = await self.exchange(b"\x05\x01\x00" + wire)
            self.assertIsNone(h)
            self.assertEqual(writer.data[-10:], adapter.failure_reply(8))
            self.assertTrue(writer.closed)

    async def test_truncation_at_every_greeting_ipv4_boundary(self):
        wire = b"\x05\x01\x00" + request()
        for end in range(len(wire)):
            with self.subTest(end=end):
                h, _, writer, run = await self.exchange(wire[:end])
                self.assertIsNone(h)
                self.assertTrue(run.reports[0]["status"].startswith("truncated_"))
                self.assertTrue(writer.closed)

    async def test_missing_request_hits_one_deadline(self):
        run = adapter.NegotiationRun(enabled=True, timeout=0.02)
        writer = Writer()
        h = await run.negotiate(reader(b"\x05\x01\x00", eof=False), writer)
        self.assertIsNone(h)
        self.assertEqual(run.reports[0]["status"], "handshake_deadline")
        self.assertTrue(writer.closed)

    async def test_blocked_method_reply_is_bounded(self):
        run = adapter.NegotiationRun(enabled=True, timeout=0.02)
        writer = Writer(block=True)
        self.assertIsNone(await run.negotiate(reader(b"\x05\x01\x00" + request()), writer))
        self.assertEqual(run.reports[0]["status"], "handshake_deadline")
        self.assertTrue(writer.closed)

    async def test_disabled_and_nonlocal_refusals_retain_caller_ownership(self):
        run = adapter.NegotiationRun()
        self.assertIsNone(await run.negotiate(None, None))
        self.assertEqual(run.reports, [])
        writer = Writer(peer="192.0.2.1")
        with self.assertRaises(ValueError):
            await adapter.NegotiationRun(enabled=True).negotiate(reader(), writer)
        self.assertFalse(writer.closed)

    async def test_attempt_cap_includes_rejected_connections_and_ids_are_unique(self):
        run = adapter.NegotiationRun(enabled=True, max_connections=4)
        for _ in range(4):
            await run.negotiate(reader(b"\x05\x00"), Writer())
        writer = Writer()
        with self.assertRaises(ValueError):
            await run.negotiate(reader(), writer)
        self.assertFalse(writer.closed)
        self.assertEqual(len(run.reports), 4)
        self.assertEqual(len({r["connection_id"] for r in run.reports}), 4)
        self.assertEqual({r["run_id"] for r in run.reports}, {run.run_id})

    async def test_cancellation_is_local_and_closes_owned_stream(self):
        run, writer = adapter.NegotiationRun(enabled=True), Writer()
        task = asyncio.create_task(run.negotiate(reader(eof=False), writer))
        await asyncio.sleep(0)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(run.reports[0]["status"], "local_cancel")
        self.assertTrue(writer.closed)

    async def test_handoff_attaches_to_canonical_core_without_losing_payload(self):
        root = Path(__file__).resolve().parents[1]
        core_spec = importlib.util.spec_from_file_location("canonical_core_for_handoff", root / "experiments/passive_relay.py")
        core = importlib.util.module_from_spec(core_spec)
        core_spec.loader.exec_module(core)
        payload, response = b"\x00synthetic-request\xff", b"\xffsynthetic-response\x00"
        h, _, client_writer, negotiation = await self.exchange(b"\x05\x01\x00" + request() + payload)
        upstream_writer = Writer()
        # Synthetic dispatcher step, not a real target connection or game ACK.
        bound = upstream_writer.get_extra_info("sockname")
        connect_reply = b"\x05\x00\x00\x01" + ipaddress.IPv4Address(bound[0]).packed + bound[1].to_bytes(2, "big")
        client_writer.write(connect_reply)
        await client_writer.drain()
        run = core.DiagnosticRun(enabled=True, max_connections=4)
        report = await run.relay(h.reader, h.writer, reader(response), upstream_writer)
        self.assertEqual(upstream_writer.data, payload)
        self.assertEqual(client_writer.data, b"\x05\x00" + connect_reply + response)
        self.assertEqual(report["status"], "eof_both")
        self.assertEqual(negotiation.reports[0]["connection_id"], h.connection_id)

    async def test_slow_partial_reads_do_not_restart_deadline(self):
        class SlowReader:
            async def readexactly(self, size):
                await asyncio.sleep(0.015)
                return b"\x05\x01" if size == 2 else b"\x00"
        run, writer = adapter.NegotiationRun(enabled=True, timeout=0.02), Writer()
        self.assertIsNone(await run.negotiate(SlowReader(), writer))
        self.assertEqual(run.reports[0]["status"], "handshake_deadline")
        self.assertTrue(writer.closed)

    async def test_connection_reset_is_transport_error_without_private_message(self):
        class ResetReader:
            async def readexactly(self, size):
                raise ConnectionResetError("synthetic-private-detail")
        run, writer = adapter.NegotiationRun(enabled=True), Writer()
        self.assertIsNone(await run.negotiate(ResetReader(), writer))
        self.assertEqual(run.reports[0]["status"], "transport_error")
        self.assertEqual(run.reports[0]["error_type"], "ConnectionResetError")
        self.assertNotIn("synthetic-private-detail", json.dumps(run.reports))
        self.assertTrue(writer.closed)

    async def test_declared_domain_length_with_short_data_is_rejected(self):
        wire = b"\x05\x01\x00\x05\x01\x00\x03\xffshort"
        handoff, _, writer, run = await self.exchange(wire)
        self.assertIsNone(handoff)
        self.assertEqual(run.reports[0]["status"], "truncated_request")
        self.assertEqual(writer.data, b"\x05\x00")
        self.assertTrue(writer.closed)

    async def test_fragmented_real_localhost_handshake_and_pipelined_handoff(self):
        async def case():
            accepted = asyncio.get_running_loop().create_future()
            server = await asyncio.start_server(lambda r, w: accepted.set_result((r, w)), "127.0.0.1", 0)
            client_writer = local_writer = None
            task = None
            try:
                client_reader, client_writer = await asyncio.open_connection("127.0.0.1", server.sockets[0].getsockname()[1])
                local_reader, local_writer = await accepted
                run = adapter.NegotiationRun(enabled=True)
                task = asyncio.create_task(run.negotiate(local_reader, local_writer))
                for byte in b"\x05\x01\x00":
                    client_writer.write(bytes((byte,)))
                    await client_writer.drain()
                    await asyncio.sleep(0)
                self.assertEqual(await client_reader.readexactly(2), b"\x05\x00")
                wire = request("192.0.2.1", 443)
                client_writer.write(wire[:3])
                await client_writer.drain()
                await asyncio.sleep(0)
                payload = b"\x00independent-payload\xff"
                client_writer.write(wire[3:] + payload)
                await client_writer.drain()
                h = await task
                self.assertIsNone(h.redirect_target)
                self.assertEqual(h.request.raw_request, wire)
                self.assertEqual(await h.reader.readexactly(len(payload)), payload)
                self.assertFalse(h.writer.is_closing())
            finally:
                if task is not None and not task.done():
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)
                for writer in (client_writer, local_writer):
                    if writer is not None:
                        writer.close()
                        await writer.wait_closed()
                server.close()
                await server.wait_closed()
        await asyncio.wait_for(case(), 3)


class BudgetTests(unittest.TestCase):
    def test_invalid_budgets_and_deadlines_rejected(self):
        for options in ({"max_connections": 3}, {"max_connections": 17},
                        {"max_connections": True}, {"timeout": 0},
                        {"timeout": 11}, {"timeout": float("nan")}):
            with self.subTest(options=options):
                with self.assertRaises(ValueError):
                    adapter.NegotiationRun(**options)


if __name__ == "__main__":
    unittest.main()

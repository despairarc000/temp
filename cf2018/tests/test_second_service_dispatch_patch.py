"""Copy-only dispatch patch controls. Private integration uses NO sockets/fixtures."""
import ast
import hashlib
import os
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'experiments'), str(ROOT / 'tests')]
from prepare_second_service_dispatch import patch_source, HANDLER_SHA, INSERT, REPORT_INSERT
from r056_second_service_syn import first_syn_decision
from test_r056_second_service_syn import fixture


class PublicControls(unittest.TestCase):
    def test_unknown_runtime_refused(self):
        for text in ('', 'if frames==1:', 'print("unverified deployed copy")'):
            with self.assertRaises(ValueError):
                patch_source(text)

    def test_other_route_no_ack_and_no_values(self):
        value = first_syn_decision(fixture(b'SERVICE123'))
        self.assertEqual(value, ('TEN_BYTE_NAMED_ROUTE_CANDIDATE', 'HOLD_NO_ACK'))
        self.assertNotIn('SERVICE123', repr(value))


class OriginalHandlerControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get('CF18_V38_SOURCE')
        if not source:
            raise unittest.SkipTest('explicit private V3.8 source not supplied')
        cls.text = (Path(source) / 'routed_probe_v38.py').read_text()
        if hashlib.sha256(cls.text.encode()).hexdigest() != HANDLER_SHA:
            raise ValueError('private handler fingerprint mismatch')
        cls.patched = patch_source(cls.text)

    def exercise(self, text, wire):
        # Execute the actual original handle method with in-memory IO. Supply
        # synthetic frame inspection and ACK/auth/stage bytes; no originals,
        # actual serializer, TCP stack or Android client are exercised.
        tree = ast.parse(text)
        handler = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Handler')
        fn = next(n for n in handler.body if isinstance(n, ast.FunctionDef) and n.name == 'handle')
        class FakePath:
            def __init__(self, *a): pass
            def with_name(self, name): return self
            def read_text(self): return fixture().hex()
        class Request:
            def __init__(self): self.parts = [wire, b'AUTH', b'']; self.sent = []
            def settimeout(self, value): pass
            def recv(self, n): return self.parts.pop(0)
            def sendall(self, b): self.sent.append(b)
        class Run:
            max_sessions = 4
            def __init__(self): self.events = []; self.stops = []
            def start(self, port): return 1, 'synthetic-id', 'synthetic-arm'
            def record(self, action, cid, **kw): self.events.append((action, kw))
            def stop(self, *args, **kw): self.stops.append(kw)
        def inspect(b):
            kind = 0x2001 if b == b'AUTH' else 0x1001
            return {'extension_fields': [[kind, 1 if kind == 0x2001 else 5]],
                    'sha256': hashlib.sha256(b).hexdigest(), 'frame_bytes': len(b),
                    'header_bytes': len(b), 'body_bytes': 0}, len(b)
        env = dict(__file__='synthetic_probe.py', Path=FakePath, hashlib=hashlib,
                   time=types.SimpleNamespace(monotonic=lambda: 0, sleep=lambda n: None),
                   MAX_IN=65536, PASSIVE_AFTER_ROUTE_S=1, inspect_client_frame=inspect,
                   make_candidate_ack=lambda _: b'SYNTHETIC_ACK',
                   strict_header_candidate=lambda b: b,
                   auth_candidate=lambda _: b'SYNTHETIC_AUTH',
                   candidate_stage=lambda _: b'SYNTHETIC_STAGE')
        exec(compile(ast.Module(body=[fn], type_ignores=[]), 'original-handle', 'exec'), env)
        request, run = Request(), Run()
        instance = types.SimpleNamespace(request=request, server=types.SimpleNamespace(
            run=run, server_address=('127.0.0.1', 8085)))
        env['handle'](instance)
        return request.sent, run.events, run.stops

    def test_reference_then_next_connection(self):
        before = self.exercise(self.text, fixture())[0]
        after, events, stops = self.exercise(self.patched, fixture())
        self.assertEqual(before, [b'SYNTHETIC_ACK', b'SYNTHETIC_AUTH', b'SYNTHETIC_STAGE'])
        self.assertEqual(after, before)
        self.assertTrue(any(x[0] == 'first_syn_dispatch' for x in events))
        held, events, stops = self.exercise(self.patched, fixture(b'SERVICE123'))
        self.assertEqual(held, [])
        self.assertEqual(stops[0]['reason'], 'next_route_held_no_ack')
        self.assertIn('HOLD_NO_ACK', repr(events))
        self.assertNotIn('SERVICE123', repr(events))

    def test_same_name_changed_frame_still_fails_exact_gate(self):
        changed = fixture() + b'junk'
        self.assertEqual(self.exercise(self.patched, changed)[0], [])

    def test_insertions_are_only_source_change(self):
        self.assertEqual(self.patched.replace(INSERT, '', 1).replace(REPORT_INSERT, '', 1), self.text)

    def test_private_reference_classifier(self):
        source = Path(os.environ['CF18_V38_SOURCE'])
        wire = bytes.fromhex((source / 'golden_request.hex').read_text())
        self.assertEqual(first_syn_decision(wire),
            ('REFERENCE_NAMED_ROUTE_CANDIDATE', 'DEFER_TO_PINNED_REFERENCE_GATE'))


if __name__ == '__main__':
    unittest.main()

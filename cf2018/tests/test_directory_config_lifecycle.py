"""Prepared-source loopback controls; never connect to phone/internet."""
import importlib
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = os.environ.get('CF18_DIRECTORY_CONFIG_PREPARED')
        if not folder:
            raise unittest.SkipTest('explicit private prepared source required')
        cls.folder = Path(folder).resolve()
        sys.path.insert(0, str(cls.folder))
        cls.m = importlib.import_module('test_r037_integration')
        probe=importlib.import_module('routed_probe_r037')
        from r076_private_route_equality import _original_route_name
        probe._R077_ORIGINAL_ROUTE=_original_route_name(os.environ['CF18_APOLLO_LIBRARY'])
        cls.original_route=probe._R077_ORIGINAL_ROUTE

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(str(cls.folder))

    def run_case(self, enabled, prior_reply, mutate=False, followup_type=0x2001, routed=False, request_kind='by_id'):
        m = self.m
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
                'CF2018_DIRECTORY_CONFIG': 'YES' if enabled else 'NO'}):
            run = m.Run(Path(tmp) / 'run', max_sessions=3 if prior_reply else 1)
            server = m.Server(('127.0.0.1', 0), run)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                syn = bytes.fromhex((self.folder / 'golden_request.hex').read_text())
                outer = m.fields(syn[7:])
                ext = m.require_field(outer, 2, 5)
                syn_fields = m.fields(m.require_field(m.fields(ext.value), 0x1001, 5).value)
                route = m.require_field(syn_fields, 14, 5)
                choice = m.require_field(m.fields(route.value), 4, 5)
                name = m.require_field(m.fields(choice.value), 1, 5)
                shorter = m.modify_syn(syn, 14, m.put_field(4, 5, m.put_field(1, 5, self.original_route)))
                shorter = m.modify_syn(shorter, 5, 3)
                if mutate:
                    # Change a non-route SYN scalar while retaining a complete frame.
                    scalar = next(f for f in syn_fields if f.number != 14 and f.kind == 1)
                    shorter = m.modify_syn(shorter, scalar.number, scalar.value ^ 1)
                ack = None
                if prior_reply:
                    with socket.create_connection(server.server_address, timeout=3) as c:
                        c.settimeout(5); c.sendall(syn)
                        ack = m.recv_exact(c, 63)
                        c.sendall(m.make_client_frame(0x2001, b'X' * 73))
                        self.assertEqual(m.recv_exact(c, 54), m.candidate('V14_BODY_ENVELOPED'))
                        self.assertEqual(m.recv_exact(c, 91), m.candidate_stage('CORRECTED_BINGO_SYNTHETIC'))
                        request = m.synthetic_request(); c.sendall(request)
                        self.assertEqual(m.recv_exact(c, len(m.make_candidate(request))), m.make_candidate(request))
                with socket.create_connection(server.server_address, timeout=3) as c:
                    c.settimeout(5); c.sendall(shorter)
                    if enabled and prior_reply and not mutate:
                        self.assertEqual(m.recv_exact(c, 63), ack)
                        c.sendall(m.make_client_frame(followup_type, b'Q' * 73))
                        if followup_type == 0x2001:
                            self.assertEqual(m.recv_exact(c,54),m.candidate('V14_BODY_ENVELOPED'))
                            self.assertEqual(m.recv_exact(c,91),m.candidate_stage('CORRECTED_BINGO_SYNTHETIC'))
                            from test_directory_identify import fixture
                            payload=fixture(request_kind) if routed else b'Q'*20
                            following=m.make_client_frame(0x4013 if routed else 0x5001,payload)
                            if routed:
                                base=b''.join(m.put_field(i,1 if i==6 else 0,v) for i,v in enumerate([0x4366,0,1,0x4013,0,0,0,0,len(payload)],1))
                                data=m.put_field(1,1,0)+m.put_field(2,1,0)+m.put_field(3,1,4)+m.put_field(4,5,m.put_field(4,5,m.put_field(1,5,self.original_route)))
                                h=m.put_field(1,5,base)+m.put_field(2,5,m.put_field(0x4013,5,data))
                                following=b'\x43\x66\xaa'+(5+len(h)).to_bytes(4,'big')+h+payload
                            c.sendall(following)
                            if routed and request_kind=='by_id':
                                from directory_config_reply import make_candidate
                                expected_reply=make_candidate(following)
                                self.assertEqual(m.recv_exact(c,len(expected_reply)),expected_reply)
                                c.sendall(m.make_client_frame(0x5001,b'Q'*20))
                        self.assertEqual(c.recv(1),b'')  # No response to next application frame.
                    else:
                        self.assertEqual(c.recv(1), b'')
                if prior_reply:
                    with socket.create_connection(server.server_address, timeout=3) as c:
                        c.settimeout(5); c.sendall(shorter)
                        self.assertEqual(c.recv(1), b'')  # One-shot budget cannot be reused.
                self.assertTrue(run.done.wait(3))
                events = [json.loads(x) for x in run.log.read_text().splitlines()]
                expected = int(enabled and prior_reply and not mutate)
                self.assertEqual(sum(e['action'] == 'second_service_ack_written' for e in events), expected)
                self.assertEqual(sum(e['action'] == 'synthetic_auth_reply_sent' for e in events), int(prior_reply))
                stage_expected=int(expected and followup_type==0x2001)
                self.assertEqual(sum(e['action']=='directory_auth_written' for e in events),stage_expected)
                self.assertEqual(sum(e['action']=='directory_bingo_written' for e in events),stage_expected)
                self.assertEqual(sum(e['action']=='directory_post_stage_frame' for e in events),stage_expected)
                if stage_expected:
                    event=next(e for e in events if e['action']=='directory_post_stage_frame')
                    self.assertEqual(event['status'],'DIRECTORY_REQUEST_CHECK')
                path = m.report(run, Path(tmp) / 'safe.txt')
                text = path.read_text()
                reply_expected=int(stage_expected and routed and request_kind=='by_id')
                if reply_expected:
                    self.assertIn('request=BY_ID_COMPLETE',text)
                    self.assertIn('event=directory_config_reply_written',text)
                    self.assertIn('event=directory_after_reply_frame',text)
                self.assertEqual(sum(e['action']=='directory_config_reply_written' for e in events),reply_expected)
                self.assertEqual(sum(e['action']=='directory_after_reply_frame' for e in events),reply_expected)
                self.assertNotIn('QueryAddrSvr', text)
                if expected:
                    label = 'AUTH_REQUEST_OBSERVED' if followup_type == 0x2001 else 'OTHER_FRAME_OBSERVED'
                    self.assertIn('SECOND_SERVICE slot=2 status=' + label, text)
            finally:
                server.shutdown(); server.server_close(); thread.join(timeout=3)

    def test_auth_bingo_then_other_frame_closes_without_application_reply(self):
        self.run_case(True, True)

    def test_qualified_request_gets_one_reply_and_next_frame_gets_none(self):
        self.run_case(True, True, routed=True)

    def test_other_valid_directory_method_gets_no_reply(self):
        self.run_case(True, True, routed=True, request_kind='all')

    def test_disabled_still_holds(self):
        self.run_case(False, True)

    def test_no_prior_reply_holds(self):
        self.run_case(True, False)

    def test_changed_security_holds(self):
        self.run_case(True, True, True)

    def test_other_frame_is_not_mislabeled_auth(self):
        self.run_case(True, True, followup_type=0x5001)

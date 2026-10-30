"""v1.6.1 regression: real routed extension could use kind=5, unlike prior tests.

Synthetic data only: no authentic client payloads are persisted.
"""
import json
import socket
import tempfile
import threading
import unittest
from pathlib import Path

from test_v16_route import fake_auth_request, recv_exact, rpc
from preflight_v09 import enc_vi, nested
from followup_probe_v10 import inspect_client_frame
from tgcp_body_repair_v14 import candidate
from stage_frame_v15 import candidate_stage
from route_fingerprint_v16 import inspect_routed_frame
from route_probe_v16 import Run, Server, report

ROOT = Path(__file__).resolve().parents[1]


def routed(body, kind):
    base = b''.join(enc_vi(n << 4) + (bytes([v]) if n == 6 else enc_vi(v)) for n, v in
                    ((1, 0x4366), (2, 0), (3, 1), (4, 0x4013), (5, 0),
                     (6, 0), (7, 1), (8, 42), (9, len(body))))
    ext = enc_vi((0x4013 << 4) | kind)
    if kind == 1:
        ext += b'\x00'
    elif kind == 5:
        ext += b'\x00' * 4
    elif kind == 0:
        ext += b'\x00'
    else:
        raise ValueError('unsupported test kind')
    header = nested(1, base) + nested(2, ext)
    return b'\x43\x66\xaa' + (len(header) + 5).to_bytes(4,'big') + header + body


def send_trial(sock, kind):
    sock.settimeout(2)
    sock.sendall(bytes.fromhex((ROOT / 'golden_request.hex').read_text().strip()))
    recv_exact(sock, 63)
    sock.sendall(fake_auth_request())
    assert recv_exact(sock,54) == candidate('V14_BODY_ENVELOPED')
    stage = candidate_stage('CORRECTED_BINGO_SYNTHETIC')
    assert recv_exact(sock,len(stage)) == stage
    sock.sendall(routed(rpc(b'QueryAddrInfo'),kind))
    sock.shutdown(socket.SHUT_WR)


class SelectorKindTests(unittest.TestCase):
    def test_kind_1_and_5_classify(self):
        for kind in (1,5):
            with self.subTest(kind=kind):
                wire = routed(rpc(),kind)
                metadata, used = inspect_client_frame(wire)
                self.assertEqual(len(wire),used)
                self.assertEqual(metadata['extension_fields'],[[0x4013,kind]])
                hint = inspect_routed_frame(wire,metadata)
                self.assertEqual(hint['selector_kind'],kind)
                self.assertEqual(hint['rpc_hint'],'QueryAddrInfo')
    def test_unsupported_kind_rejected_by_classifier(self):
        wire=routed(rpc(),0)
        metadata,used=inspect_client_frame(wire)
        self.assertEqual(used,len(wire))
        self.assertEqual(metadata['extension_fields'],[[0x4013,0]])
        with self.assertRaisesRegex(ValueError,'selector'):
            inspect_routed_frame(wire,metadata)
    def test_both_kinds_trigger_hint_in_real_listener(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Run(Path(tmp)/'run');server=Server(('127.0.0.1',0),run)
            thread=threading.Thread(target=server.serve_forever,daemon=True)
            thread.start()
            try:
                for kind in (1,5):
                    with socket.create_connection(server.server_address,timeout=2) as s:
                        send_trial(s,kind)
                self.assertTrue(run.done.wait(4))
                ev=[json.loads(line) for line in run.log.read_text().splitlines()]
                hints=[x for x in ev if x['action']=='routed_rpc_hint']
                self.assertEqual([x['selector_kind'] for x in hints],[1,5])
                self.assertEqual([x['rpc_hint'] for x in hints],['QueryAddrInfo']*2)
                out=report(run,Path(tmp)/'report.txt').read_text()
                self.assertIn('kind=1',out)
                self.assertIn('kind=5',out)
                self.assertNotIn('password',out)
            finally:
                server.shutdown();server.server_close();thread.join(timeout=2)

if __name__=='__main__':unittest.main()

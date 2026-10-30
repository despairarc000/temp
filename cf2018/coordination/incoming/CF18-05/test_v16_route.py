"""Offline v1.6 structural tests with synthetic frame data only."""
from __future__ import annotations
import json, os, socket, subprocess, sys, tempfile, threading, time, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# Installed folder is CF2018_TGCP_v1.5_Bingo_Stage_ABC/tests/test_v16_route.py.
sys.path.insert(0,str(ROOT))
from route_fingerprint_v16 import inspect_routed_frame
from route_probe_v16 import Run, Server, report, MAX_SLOTS
from followup_probe_v10 import inspect_client_frame
from preflight_v09 import enc_vi,nested
from tgcp_body_repair_v14 import candidate
from stage_frame_v15 import candidate_stage


def fake_auth_request():
    body=b'F'*73
    base=b''.join(enc_vi(n<<4)+(bytes([v]) if n==6 else enc_vi(v)) for n,v in
                  ((1,0x4366),(2,0),(3,1),(4,0x2001),(5,0),(6,0),(7,1),(8,42),(9,len(body))))
    head=nested(1,base)+nested(2,enc_vi(0x20011)+b'\x00')
    return b'\x43\x66\xaa'+(5+len(head)).to_bytes(4,'big')+head+body


def framed(body, subtype=0x4013):
    base=b''.join(enc_vi(n<<4)+(bytes([v]) if n==6 else enc_vi(v)) for n,v in
                  ((1,0x4366),(2,0),(3,1),(4,subtype),(5,0),(6,0),(7,1),(8,42),(9,len(body))))
    head=nested(1,base)+nested(2,enc_vi((subtype<<4)|1)+b'\x00')
    return b'\x43\x66\xaa'+(5+len(head)).to_bytes(4,'big')+head+body


def rpc(name=b'QueryAddrInfo',off=0,typ=1):
    return b'\x99'*off +len(name).to_bytes(4,'big')+name+bytes([typ])+b'\x00'*8+b'\x00'


def recv_exact(sock,n):
    buff=b''
    while len(buff)<n:
        part=sock.recv(n-len(buff))
        if not part:raise AssertionError('socket EOF before expected reply')
        buff+=part
    return buff


def serve_trial(sock,root,body):
    sock.settimeout(3)
    sock.sendall(bytes.fromhex((root/'golden_request.hex').read_text().strip()))
    recv_exact(sock,63)
    sock.sendall(fake_auth_request())
    assert recv_exact(sock,54)==candidate('V14_BODY_ENVELOPED')
    reply=candidate_stage('CORRECTED_BINGO_SYNTHETIC')
    assert recv_exact(sock,len(reply))==reply
    sock.sendall(framed(body))
    sock.shutdown(socket.SHUT_WR)


class Fingerprint(unittest.TestCase):
    def classify(self,p):
        f=framed(p)
        md,used=inspect_client_frame(f)
        self.assertEqual(used,len(f))
        return inspect_routed_frame(f,md)
    def test_positive_known_call(self):
        got=self.classify(rpc())
        self.assertEqual(got['route_type'],'0x4013')
        self.assertEqual(got['rpc_hint'],'QueryAddrInfo')
        self.assertEqual(got['rpc_type_hint'],'CALL')
        self.assertEqual(got['rpc_offset'],0)
        self.assertNotIn('seq',str(got).lower())
    def test_known_other_methods(self):
        for name in (b'GetUpdateInfo',b'ReqUpdateVersion',b'get_server_by_ids'):
            with self.subTest(name=name):
                self.assertEqual(self.classify(rpc(name,off=12))['rpc_hint'],name.decode())
    def test_wrong_type_does_not_claim_rpc(self):
        self.assertEqual(self.classify(rpc(typ=2))['rpc_hint'],'NOT_IDENTIFIED')
    def test_unanchored_string_not_accepted(self):
        self.assertEqual(self.classify(b'junk QueryAddrInfo morejunk')['rpc_hint'],'NOT_IDENTIFIED')
    def test_unrecognized_is_opaque_not_encryption(self):
        got=self.classify(b'\x9f\x12\x10\x9f'*29)
        self.assertEqual(got['body_envelope_hint'],'UNKNOWN_OR_OPAQUE')
        self.assertEqual(got['rpc_hint'],'NOT_IDENTIFIED')
    def test_aa_body_hint_only(self):
        b=b'\xaa'+(20).to_bytes(4,'big')+b'\x00'*15
        self.assertEqual(self.classify(b)['body_envelope_hint'],'AA_LENGTH_EXACT')
    def test_not_other_frame_type(self):
        f=framed(rpc(),subtype=0x2001); md,_=inspect_client_frame(f)
        with self.assertRaises(ValueError):inspect_routed_frame(f,md)
    def test_incomplete_frame_rejected(self):
        f=framed(rpc());md,_=inspect_client_frame(f)
        with self.assertRaises(ValueError):inspect_routed_frame(f[:-1],md)
    def test_no_false_positives_near_scan_limit(self):
        self.assertEqual(self.classify(rpc(off=99))['rpc_hint'],'NOT_IDENTIFIED')
        self.assertEqual(self.classify(rpc(off=95))['rpc_hint'],'QueryAddrInfo')
    def test_empty_frame(self):
        self.assertEqual(self.classify(b'')['body_envelope_hint'],'EMPTY')
    def test_multiple_matches_ambiguous(self):
        self.assertEqual(self.classify(rpc()+rpc(b'GetUpdateInfo'))['rpc_hint'],'AMBIGUOUS')
    def test_server_exact_two_bingo_arms(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Run(Path(tmp)/'run'); srv=Server(('127.0.0.1',0),run)
            t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
            try:
                self.assertEqual(MAX_SLOTS,2)
                for body in (rpc(),b'\x80\x02\x12\x13'*31):
                    with socket.create_connection(srv.server_address,timeout=3) as c:
                        serve_trial(c,ROOT,body)
                self.assertTrue(run.done.wait(4))
                log=run.log.read_text()
                events=[json.loads(x) for x in log.splitlines()]
                hints=[e for e in events if e['action']=='routed_rpc_hint']
                self.assertEqual(len(hints),2)
                self.assertEqual([x['rpc_hint'] for x in hints],['QueryAddrInfo','NOT_IDENTIFIED'])
                self.assertNotIn('raw_payload',log)
                self.assertNotIn('Account',log)
                result=report(run,Path(tmp)/'result.txt').read_text()
                self.assertIn('ROUTED_HINT slot=1',result)
                self.assertIn('NOT_IDENTIFIED',result)
                self.assertNotIn('raw_payload',result)
            finally:
                srv.shutdown();srv.server_close();t.join(2)
    def test_socks5_loopback_bingo_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Run(Path(tmp)/'run'); srv=Server(('127.0.0.1',0),run)
            thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
            with socket.socket() as free:
                free.bind(('127.0.0.1',0));proxy_port=free.getsockname()[1]
            proxy=subprocess.Popen([sys.executable,str(ROOT/'cf2018_redirector.py'),'--mode','forward',
                '--listen','127.0.0.1','--port',str(proxy_port),'--emulator-host','127.0.0.1',
                '--emulator-port-8080',str(srv.server_address[1]),'--emulator-port-8085','1',
                '--log-dir',str(Path(tmp)/'relay')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            try:
                for body in (rpc(b'QueryAddrInfo'),b'not a known RPC payload'):
                    for _ in range(80):
                        try:
                            connection=socket.create_connection(('127.0.0.1',proxy_port),timeout=.4)
                            break
                        except (ConnectionRefusedError,OSError):time.sleep(.05)
                    else:self.fail('SOCKS5 proxy unavailable')
                    with connection as c:
                        c.settimeout(3)
                        c.sendall(bytes.fromhex('050100'))
                        self.assertEqual(recv_exact(c,2),bytes.fromhex('0500'))
                        c.sendall(bytes.fromhex('05010001')+bytes([45,113,69,32])+(8080).to_bytes(2,'big'))
                        self.assertEqual(recv_exact(c,10)[:2],bytes.fromhex('0500'))
                        serve_trial(c,ROOT,body)
                self.assertTrue(run.done.wait(4))
                report_txt=report(run,Path(tmp)/'result.txt').read_text()
                self.assertIn('QueryAddrInfo',report_txt)
                self.assertIn('NOT_IDENTIFIED',report_txt)
                relay_events=[json.loads(x) for x in (Path(tmp)/'relay'/'events.jsonl').read_text().splitlines()]
                self.assertTrue(any(e.get('event')=='CONNECTED' and e.get('status')=='EMULATOR' for e in relay_events))
            finally:
                proxy.terminate()
                try:proxy.wait(timeout=3)
                except subprocess.TimeoutExpired:proxy.kill();proxy.wait()
                srv.shutdown();srv.server_close();thread.join(timeout=2)
    def test_no_network_until_opt_in(self):
        p=subprocess.run([sys.executable,str(ROOT/'route_probe_v16.py')],capture_output=True,text=True,timeout=4)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('Offline only',p.stderr+p.stdout)

if __name__=='__main__':unittest.main()

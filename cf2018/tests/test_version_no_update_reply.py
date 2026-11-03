"""Synthetic requests, original dispatch/decision and bounded loopback only."""
import os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'experiments'),str(ROOT/'tools')]
from version_no_update_reply import response
from test_version_discovery import body,frame,address_body
import test_version_discovery as discovery_tests
from version_discovery_control import METHOD
from prepare_version_reply import REPLY_SOURCE,DISCOVERY_SOURCE
from native_directory_dispatch_controls import probe
from native_version_decision_controls import exercise,VERSION

class Public(unittest.TestCase):
    def test_reviewed_sources_embedded_exactly(self):
        self.assertEqual(REPLY_SOURCE,(ROOT/'experiments/version_no_update_reply.py').read_text())
        self.assertEqual(DISCOVERY_SOURCE,(ROOT/'tools/prepare_version_discovery.py').read_text())

@unittest.skipUnless(os.environ.get('CF18_VERSION_DISCOVERY_PREPARED'),'prepared loopback source required')
class Prepared(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        discovery_tests.Prepared.setUpClass();cls.t=discovery_tests.Prepared(methodName='runTest')
    @classmethod
    def tearDownClass(cls):discovery_tests.Prepared.tearDownClass()
    def test_rpc64_and_packet_correlation_and_shape_negatives(self):
        for product in (1,2):
            a,label=response(frame(body(mode=product),route=b'VersionUpdate'))
            self.assertEqual(label,'APPLICATION' if product==1 else 'RESOURCES')
            end=int.from_bytes(a[1:5],'big');payload=a[end:]
            self.assertEqual(payload[4+len(METHOD)],2)
        for wire in (frame(body(),route=b'Other'),frame(body(),route=b'VersionUpdate',cipher=1),frame(body(mode=99),route=b'VersionUpdate'),frame(body()[:-1],route=b'VersionUpdate')):
            with self.assertRaises(ValueError):response(wire)
        # Distinct RPC64 changes the response; TGCP32 is never substituted.
        a,_=response(frame(body(rpc=0x100000002),route=b'VersionUpdate'))
        b,_=response(frame(body(rpc=0x200000002),route=b'VersionUpdate'))
        self.assertNotEqual(a,b)
        zero=body().replace(VERSION.to_bytes(8,'big'),bytes(8))
        with self.assertRaises(ValueError):response(frame(zero,route=b'VersionUpdate'))
    def test_full_app_resource_replies_and_duplicate_budget(self):
        import json
        from r033_reply import make_candidate
        from directory_config_reply import make_candidate as config
        from test_directory_identify import fixture as directory_body
        t=self.t
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'CF2018_VERSION_REPLY':'YES'}):
            run=t.m.Run(Path(tmp)/'run');server,thread=t.start(run)
            try:
                with t.connect(server,t.syn) as c:
                    wire=frame(address_body());c.sendall(wire);t.m.recv_exact(c,len(make_candidate(wire)))
                short=t.m.modify_syn(t.named(t.directory),5,3)
                with t.connect(server,short) as c:
                    wire=frame(directory_body('by_id'),route=t.directory,packet=0);c.sendall(wire);t.m.recv_exact(c,len(config(wire)))
                with t.connect(server,t.syn) as c:
                    wire=frame(address_body(b'download',1));c.sendall(wire);t.m.recv_exact(c,len(make_candidate(wire)))
                with t.connect(server,t.named(b'VersionUpdate')) as c:
                    for product,rpc in ((1,0x100000002),(2,0x100000003)):
                        wire=frame(body(mode=product,rpc=rpc),route=b'VersionUpdate');expected,label=response(wire)
                        c.sendall(wire);self.assertEqual(t.m.recv_exact(c,len(expected)),expected)
                    c.sendall(frame(body(),route=b'VersionUpdate'));self.assertEqual(c.recv(1),b'')
                events=[json.loads(x) for x in run.log.read_text().splitlines()]
                results=[e for e in events if e['action']=='version_result_written']
                self.assertEqual([e['version_mode'] for e in results],['APPLICATION','RESOURCES'])
                self.assertEqual(run.max_sessions,8);self.assertFalse(run.observation_abort.is_set())
                self.assertEqual(run.version_products_claimed,{'APPLICATION','RESOURCES'})
                report=t.m.report(run,Path(tmp)/'safe.txt').read_text()
                self.assertEqual(report.count('event=version_result_written'),2)
                self.assertNotIn('PRIVATE_CANARY',report)
            finally:server.shutdown();server.server_close();thread.join(3)
    def test_second_lookup_and_handshake_are_bounded_by_two(self):
        import socket
        from r033_reply import make_candidate
        t=self.t
        with tempfile.TemporaryDirectory() as tmp:
            run=t.m.Run(Path(tmp)/'run');run.directory_config_written=True
            run.version_products_written={'APPLICATION'};run.version_products_claimed={'APPLICATION'}
            run.version_lookup_claimed=1;run.version_ack_claimed=1;run.r033_reply_claimed=True
            server,thread=t.start(run)
            try:
                with t.connect(server,t.syn) as c:
                    wire=frame(address_body(b'download',1));c.sendall(wire);self.assertEqual(t.m.recv_exact(c,len(make_candidate(wire))),make_candidate(wire))
                with t.connect(server,t.named(b'VersionUpdate')) as c:
                    wire=frame(body(mode=2),route=b'VersionUpdate');expected,_=response(wire)
                    c.sendall(wire);self.assertEqual(t.m.recv_exact(c,len(expected)),expected)
                with t.connect(server,t.syn) as c:
                    c.sendall(frame(address_body(b'download',1)));self.assertEqual(c.recv(1),b'')
                with socket.create_connection(server.server_address,timeout=3) as c:
                    c.settimeout(3);c.sendall(t.named(b'VersionUpdate'));self.assertEqual(c.recv(1),b'')
                self.assertEqual((run.version_lookup_claimed,run.version_ack_claimed),(2,2))
            finally:server.shutdown();server.server_close();thread.join(3)

@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY') and os.environ.get('CF18_VERSION_DISCOVERY_PREPARED'),'original and prepared source required')
class Native(unittest.TestCase):
    @classmethod
    def setUpClass(cls):sys.path.insert(0,os.environ['CF18_VERSION_DISCOVERY_PREPARED'])
    @classmethod
    def tearDownClass(cls):sys.path.remove(os.environ['CF18_VERSION_DISCOVERY_PREPARED'])
    def test_actual_reply_reaches_original_typed_receiver_and_no_update_branches(self):
        lib=os.environ['CF18_APOLLO_LIBRARY']
        for product,modes in ((1,(20,22)),(2,(21,23))):
            wire,label=response(frame(body(mode=product),route=b'VersionUpdate'))
            result=probe(lib,wire=wire,service='version')
            self.assertEqual(result['pending_count'],0);callback=result['callbacks'][0]
            self.assertEqual((callback['status'],callback['result'],callback['update_type'],callback['version'],callback['product_type'],callback['request_type']),(0,0,0,VERSION,product,1))
            for mode in modes:self.assertEqual(exercise(lib,mode,0)['branch'],'NO_UPDATE_RESULT')
            wrong=probe(lib,wire=wire,pending=0x200000002,service='version')
            self.assertEqual((wrong['pending_count'],wrong['callbacks']),(1,[]))

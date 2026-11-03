"""Synthetic and optional original/loopback controls. No phone or remote I/O."""
import importlib,os,sys,tempfile,threading,time,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'experiments'),str(ROOT/'tools')]
from version_discovery_control import METHOD,classify_body,classify_frame,make_lookup_reply,version_context_matches
from native_version_request_controls import native_args,route_matches_original,fill_profile
from native_syn_ack_handoff import probe
from prepare_version_discovery import BASE_SOURCE,CONTROL_SOURCE,patch as prepare_patch
from test_address_query_target import fixture as address_body,frame

def field(kind,ident,value):return bytes([kind])+ident.to_bytes(2,'big')+value
def args(optional=False,mode=1,canary=b''):
    comm=b''.join(field(8,i,v.to_bytes(4,'big')) for i,v in enumerate((7,11,mode,1),1))
    comm+=b''.join(field(10,i,(0x1111222233334444).to_bytes(8,'big')) for i in (5,6))
    comm+=field(11,7,bytes(4))
    if optional:comm+=field(10,8,(23).to_bytes(8,'big'))+field(6,9,(2).to_bytes(2,'big'))
    req=field(12,1,comm+b'\0')+field(11,2,len(canary).to_bytes(4,'big')+canary)
    if optional:req+=field(12,3,b''.join(field(11,i,bytes(4)) for i in range(1,4))+b'\0')
    return field(12,1,req+b'\0')+b'\0'
def body(optional=False,mode=1,canary=b'',packet=7,rpc=0x100000002):
    return packet.to_bytes(4,'big')+len(METHOD).to_bytes(4,'big')+METHOD+b'\1'+rpc.to_bytes(8,'big')+args(optional,mode,canary)

class Synthetic(unittest.TestCase):
    def test_required_optional_and_mode_groups(self):
        for optional in (False,True):
            for mode,label in ((1,'APPLICATION'),(2,'RESOURCES'),(99,'OTHER')):
                r=classify_body(body(optional,mode),7)
                self.assertEqual((r['version_request'],r['version_mode']),('COMPLETE_LEGACY64',label))
    def test_truncation_trailing_duplicate_missing_and_wrong_type_refused(self):
        wire=body()
        cases=[wire[:i] for i in range(len(wire))]+[wire+b'\0',wire.replace(b'\x08\0\4',b'\x0a\0\4'),wire.replace(b'\x0b\0\7',b'\x0b\0\1')]
        for data in cases:self.assertNotEqual(classify_body(data,7)['version_request'],'COMPLETE_LEGACY64')
        self.assertNotEqual(classify_body(wire,8)['version_request'],'COMPLETE_LEGACY64')
        self.assertEqual(classify_body(body(rpc=9),7)['version_request'],'COMPLETE_LEGACY64')
    def test_fixed_label_privacy_and_exact_embedded_sources(self):
        result=repr(classify_body(body(canary=b'PRIVATE_CANARY'),7))
        for value in ('PRIVATE_CANARY','11112222','ReqUpdateVersion','4294967298'):self.assertNotIn(value,result)
        self.assertEqual(BASE_SOURCE,(ROOT/'tools/prepare_directory_config.py').read_text())
        self.assertEqual(CONTROL_SOURCE,(ROOT/'experiments/version_discovery_control.py').read_text())
    def test_unrelated_preparation_and_bad_windows_refused(self):
        for seconds in (True,0,301):
            with self.assertRaises(ValueError):prepare_patch('',seconds)
        with self.assertRaises(ValueError):prepare_patch('not the pinned source')

@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'),'explicit original Apollo required')
class Original(unittest.TestCase):
    def test_original_fill_request_translates_mode_to_product_and_request_fields(self):
        for mode,product,request in ((20,1,1),(21,2,1),(22,1,2),(23,2,2)):
            self.assertEqual(fill_profile(os.environ['CF18_APOLLO_LIBRARY'],mode),{'product_type':product,'request_type':request,'custom_fields':mode>=22})
    def test_original_request_writer_and_transport_route(self):
        lib=os.environ['CF18_APOLLO_LIBRARY']
        self.assertTrue(route_matches_original(lib))
        for optional in (False,True):self.assertEqual(native_args(lib,optional),args(optional))
    def test_original_ack_handoff_with_thirteen_byte_synthetic_route(self):
        lib=os.environ['CF18_APOLLO_LIBRARY']
        r=probe(lib,name_size=13,attribute='unit_id')
        self.assertTrue(r['syn_prepared_named_route']);self.assertTrue(r['synthetic_name_copied']);self.assertTrue(r['auth_send_boundary'])
        for variant in ('wrong_magic','bad_key','prefixed','truncated'):
            self.assertFalse(probe(lib,name_size=13,attribute='unit_id',variant=variant)['auth_send_boundary'])

@unittest.skipUnless(os.environ.get('CF18_VERSION_DISCOVERY_PREPARED'),'explicit prepared source required')
class Prepared(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=Path(os.environ['CF18_VERSION_DISCOVERY_PREPARED']).resolve();sys.path.insert(0,str(cls.folder))
        cls.m=importlib.import_module('test_r037_integration');cls.probe=importlib.import_module('routed_probe_r037')
        from r076_private_route_equality import _original_route_name
        cls.directory=_original_route_name(os.environ['CF18_APOLLO_LIBRARY']);cls.probe._R077_ORIGINAL_ROUTE=cls.directory
        cls.syn=bytes.fromhex((cls.folder/'golden_request.hex').read_text())
    @classmethod
    def tearDownClass(cls):sys.path.remove(str(cls.folder))
    def named(self,name):
        m=self.m;return m.modify_syn(self.syn,14,m.put_field(4,5,m.put_field(1,5,name)))
    def test_exact_version_context_requires_all_non_route_fields(self):
        m=self.m;good=self.named(b'VersionUpdate')
        self.assertTrue(version_context_matches(good,self.syn))
        cases=[good[:-1],good+b'X',self.named(b'SyntheticName'),m.modify_syn(good,5,3),m.modify_syn(good,6,102),m.modify_syn(good,1,8)]
        for candidate in cases:self.assertFalse(version_context_matches(candidate,self.syn))
    def test_lookup_reply_target_and_frame_guards(self):
        request=frame(address_body(b'download',1))
        from r033_reply import make_candidate
        self.assertEqual(make_lookup_reply(request),make_candidate(request))
        for bad in (frame(address_body()),frame(address_body(b'download',3)),frame(address_body(b'download',1),packet=8),request+b'X'):
            with self.assertRaises(ValueError):make_lookup_reply(bad)
        good=frame(body(),route=b'VersionUpdate')
        self.assertEqual(classify_frame(good)['version_request'],'COMPLETE_LEGACY64')
        for bad in (frame(body(),route=b'Other'),frame(body(),route=b'VersionUpdate',cipher=1),frame(body(),route=b'VersionUpdate',compression=1),good+b'X'):
            self.assertNotEqual(classify_frame(bad)['version_request'],'COMPLETE_LEGACY64')
    def start(self,run):
        server=self.m.Server(('127.0.0.1',0),run);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();return server,thread
    def connect(self,server,syn):
        import socket
        c=socket.create_connection(server.server_address,timeout=3);c.settimeout(4);c.sendall(syn)
        self.assertEqual(len(self.m.recv_exact(c,63)),63)
        c.sendall(self.m.make_client_frame(0x2001,b'Q'*73))
        self.assertEqual(self.m.recv_exact(c,54),self.m.candidate('V14_BODY_ENVELOPED'))
        self.assertEqual(self.m.recv_exact(c,91),self.m.candidate_stage('CORRECTED_BINGO_SYNTHETIC'))
        return c
    def test_full_four_session_flow_stops_at_typed_request_without_version_reply(self):
        import json
        from r033_reply import make_candidate
        from directory_config_reply import make_candidate as config
        from test_directory_identify import fixture as directory_body
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'CF2018_VERSION_DISCOVERY':'YES'}):
            run=self.m.Run(Path(tmp)/'run');server,thread=self.start(run)
            try:
                with self.connect(server,self.syn) as c:
                    wire=frame(address_body());c.sendall(wire);self.assertEqual(self.m.recv_exact(c,len(make_candidate(wire))),make_candidate(wire))
                short=self.m.modify_syn(self.named(self.directory),5,3)
                with self.connect(server,short) as c:
                    wire=frame(directory_body('by_id'),route=self.directory,packet=0);c.sendall(wire)
                    self.assertEqual(self.m.recv_exact(c,len(config(wire))),config(wire))
                with self.connect(server,self.syn) as c:
                    wire=frame(address_body(b'download',1));c.sendall(wire)
                    self.assertEqual(self.m.recv_exact(c,len(make_candidate(wire))),make_candidate(wire))
                deadline=time.monotonic()+2
                while not getattr(run,'version_lookup_reply_written',False) and time.monotonic()<deadline:time.sleep(.01)
                with self.connect(server,self.named(b'VersionUpdate')) as c:
                    c.sendall(frame(body(),route=b'VersionUpdate'));self.assertEqual(c.recv(1),b'')
                self.assertTrue(run.done.wait(3));self.assertTrue(run.version_request_observed)
                events=[json.loads(x) for x in run.log.read_text().splitlines()]
                for action in ('r033_reply_sent','directory_config_reply_written','version_lookup_reply_written','version_ack_written','version_stages_written','version_application_check'):
                    self.assertEqual(sum(e['action']==action for e in events),1,action)
                self.assertFalse(run.observation_abort.is_set());self.assertEqual(run.sessions,4)
                report=self.m.report(run,Path(tmp)/'safe.txt').read_text()
                self.assertIn('request=COMPLETE_LEGACY64 mode=APPLICATION',report)
                for private in ('download','QueryAddrSvr:','VersionUpdate:','PRIVATE_CANARY'):self.assertNotIn(private,report)
            finally:server.shutdown();server.server_close();thread.join(3)
    def test_lookup_reply_refused_without_settings_or_after_budget_used(self):
        import json
        for settings,claimed in ((False,False),(True,True)):
            with tempfile.TemporaryDirectory() as tmp:
                run=self.m.Run(Path(tmp)/'run',max_sessions=1);run.directory_config_written=settings;run.version_lookup_claimed=claimed
                server,thread=self.start(run)
                try:
                    with self.connect(server,self.syn) as c:
                        c.sendall(frame(address_body(b'download',1)));self.assertEqual(c.recv(1),b'')
                    self.assertTrue(run.done.wait(3))
                    events=[json.loads(x) for x in run.log.read_text().splitlines()]
                    self.assertFalse(any(e['action']=='version_lookup_reply_written' for e in events))
                    self.assertIn('version_lookup_order_or_budget_refused',run.log.read_text())
                finally:server.shutdown();server.server_close();thread.join(3)
    def test_version_syn_without_lookup_gets_no_ack(self):
        import socket
        for lookup,claimed,changed in ((False,False,False),(True,True,False),(True,False,True)):
            with tempfile.TemporaryDirectory() as tmp:
                run=self.m.Run(Path(tmp)/'run',max_sessions=1)
                run.version_lookup_reply_written=lookup;run.version_ack_claimed=claimed
                server,thread=self.start(run)
                try:
                    syn=self.named(b'VersionUpdate')
                    if changed:syn=self.m.modify_syn(syn,5,3)
                    with socket.create_connection(server.server_address,timeout=3) as c:
                        c.settimeout(3);c.sendall(syn);self.assertEqual(c.recv(1),b'')
                    self.assertTrue(run.done.wait(3));self.assertNotIn('version_ack_written',run.log.read_text())
                finally:server.shutdown();server.server_close();thread.join(3)

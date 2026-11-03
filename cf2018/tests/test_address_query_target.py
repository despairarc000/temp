"""Independent synthetic grammar plus optional original-code parity controls."""
import importlib.util,os,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'experiments'),str(ROOT/'tools')]
from address_query_target import classify_body,classify_frame
from native_address_producer_controls import build
from prepare_directory_config import prepare,ADDRESS_TARGET_SOURCE

def fixture(service=b'dir',unit=3,game=42,packet=7,rpc=0x100000002):
    # Independent format, never copied from native output or phone contents.
    name=b'QueryAddrSvr:QueryAddrInfo'
    return (packet.to_bytes(4,'big')+len(name).to_bytes(4,'big')+name+b'\1'+rpc.to_bytes(8,'big')+
            b'\x0c\0\1\x0a\0\1'+game.to_bytes(8,'big')+b'\x0a\0\2'+unit.to_bytes(8,'big')+
            b'\x0b\0\3'+len(service).to_bytes(4,'big')+service+b'\0\0')

def frame(body,route=b'QueryAddrSvr',cipher=0,compression=0,packet=7):
    from directory_config_reply import field
    base=b''.join(field(i,1 if i==6 else 0,v) for i,v in enumerate([0x4366,0,1,0x4013,0,cipher,packet,0,len(body)],1))
    data=field(1,1,compression)+field(2,1,0)+field(3,1,4)+field(4,5,field(4,5,field(1,5,route)))
    h=field(1,5,base)+field(2,5,field(0x4013,5,data))
    return b'\x43\x66\xaa'+(5+len(h)).to_bytes(4,'big')+h+body

class Synthetic(unittest.TestCase):
    def test_target_requires_service_and_unit(self):
        for service,unit,label in ((b'dir',3,'DIRECTORY_ADDRESS_QUERY'),(b'download',1,'VERSION_ADDRESS_QUERY'),(b'download',3,'OTHER_ADDRESS_QUERY'),(b'dir',1,'OTHER_ADDRESS_QUERY')):
            self.assertEqual(classify_body(fixture(service,unit),7)['address_target'],label)
    def test_complete_grammar_sequence_type_and_consumption_required(self):
        body=fixture(b'download',1)
        for data in [body[:i] for i in range(len(body))]+[body+b'\0',body[:34]+b'\2'+body[35:],body.replace(b'\x0a\0\2',b'\x08\0\2')]:
            self.assertNotEqual(classify_body(data,7)['address_target'],'VERSION_ADDRESS_QUERY')
        self.assertEqual(classify_body(body,8)['address_target_reason'],'PACKET_SEQUENCE_MISMATCH')
        self.assertEqual(classify_body(fixture(b'download',1,rpc=5),7)['address_target'],'VERSION_ADDRESS_QUERY')
    def test_no_input_values_exported_and_embedding_matches(self):
        result=repr(classify_body(fixture(b'PRIVATE_CANARY',19,game=123456789),7))
        for value in ('PRIVATE_CANARY','123456789','QueryAddrSvr'):
            self.assertNotIn(value,result)
        self.assertEqual(ADDRESS_TARGET_SOURCE,(ROOT/'experiments/address_query_target.py').read_text())
    def test_original_runner_refuses_non_synthetic_input_before_file_access(self):
        for domain in ('real.example.com','dir.3.42.synthetic.invalid.extra','dir.3.42.synthetic.invalid\0'):
            with self.assertRaises(ValueError):build('not-opened',domain)

@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'),'explicit original Apollo required')
class Original(unittest.TestCase):
    def test_original_domain_parser_and_whole_rpc_match_independent_grammar(self):
        for service,unit in ((b'dir',3),(b'download',1)):
            r=build(os.environ['CF18_APOLLO_LIBRARY'],service.decode()+'.'+str(unit)+'.42.synthetic.invalid')
            self.assertEqual((r['parse_return'],r['service'],r['unit'],r['game']),(0,service,unit,42))
            self.assertEqual(r['method'],[b'QueryAddrSvr:QueryAddrInfo'])
            self.assertEqual(r['body'],fixture(service,unit,packet=0,rpc=1))
            self.assertEqual(len(r['body']),77+len(service))
    def test_strict_writer_is_distinct_and_not_silently_accepted(self):
        r=build(os.environ['CF18_APOLLO_LIBRARY'],'download.1.42.synthetic.invalid',True)
        self.assertEqual(r['body'][4:8],b'\x80\1\0\1')
        self.assertEqual(classify_body(r['body'],0)['address_target'],'NOT_IDENTIFIED')

@unittest.skipUnless(os.environ.get('CF18_DIRECTORY_IDENTIFY_PREPARED'),'explicit prepared source required')
class Prepared(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Path(os.environ['CF18_DIRECTORY_IDENTIFY_PREPARED']);sys.path.insert(0,str(cls.source))
    @classmethod
    def tearDownClass(cls):sys.path.remove(str(cls.source))
    def test_frame_guards_reject_cipher_compression_wrong_route_and_size(self):
        body=fixture(b'download',1)
        self.assertEqual(classify_frame(frame(body))['address_target'],'VERSION_ADDRESS_QUERY')
        for wire in (frame(body,cipher=1),frame(body,compression=1),frame(body,route=b'Other'),frame(body,packet=8),frame(body)+b'X',frame(body)[:-1]):
            self.assertNotEqual(classify_frame(wire)['address_target'],'VERSION_ADDRESS_QUERY')
    def test_actual_handler_stops_before_any_response_to_version_address(self):
        import types
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'copy';prepare(self.source,out,180,True);sys.path.insert(0,str(out))
            try:
                spec=importlib.util.spec_from_file_location('address_target_probe',out/'routed_probe_r037.py')
                m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
                run=m.Run(Path(tmp)/'run');wire=frame(fixture(b'download',1))
                # Earlier transport stages are replaced; real application branch
                # receives a fully structured synthetic routed frame in memory.
                syn=bytes.fromhex((out/'golden_request.hex').read_text());auth=b'A'
                inputs=[syn,auth,wire,b''];sends=[]
                request=types.SimpleNamespace(settimeout=lambda n:None,recv=lambda n:inputs.pop(0),sendall=sends.append)
                def inspect(raw):
                    if raw==syn:return {'extension_fields':[[0x1001,5]],'sha256':__import__('hashlib').sha256(syn).hexdigest(),'frame_bytes':len(syn),'header_bytes':len(syn),'body_bytes':0},len(syn)
                    if raw==auth:return {'extension_fields':[[0x2001,1]],'frame_bytes':1,'header_bytes':1,'body_bytes':0},1
                    return {'extension_fields':[[0x4013,5]],'frame_bytes':len(wire),'header_bytes':len(wire)-85,'body_bytes':85},len(wire)
                handler=m.Handler.__new__(m.Handler);handler.server=types.SimpleNamespace(run=run,server_address=('127.0.0.1',8080));handler.request=request
                # Existing first-stage logging accesses detailed fields; use its
                # real SYN inspector, replacing only the tiny auth sentinel.
                original=m.inspect_client_frame
                def actual(raw):return inspect(raw) if raw==auth else original(raw)
                m.inspect_client_frame=actual
                with patch('directory_ack_gate.directory_context_matches',return_value=False):
                    handler.handle()
                self.assertTrue(run.version_address_identified)
                self.assertEqual(len(sends),3) # Established ACK/auth/Bingo only.
                events=run.log.read_text();self.assertIn('VERSION_ADDRESS_QUERY',events)
                self.assertNotIn('r033_reply_sent',events)
                self.assertNotIn('download',events)
            finally:sys.path.remove(str(out))

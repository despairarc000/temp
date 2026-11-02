"""Pending/callback controls through original native dispatcher; synthetic only."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from directory_config_reply import rpc,node,field,ROUTE
from native_directory_dispatch_controls import probe
LIB=os.environ.get('CF18_APOLLO_LIBRARY')

def wire(body,sequence=0x11223344):
    base=b''.join(field(i,1 if i==6 else 0,v) for i,v in enumerate(
        [0x4366,0,1,0x4013,0,0,sequence,0,len(body)],1))
    route=field(4,5,field(1,5,ROUTE))
    data=field(1,1,0)+field(2,1,0)+field(3,1,1)+field(4,5,route)
    header=field(1,5,base)+field(2,5,field(0x4013,5,data))
    return b'\xaa'+(5+len(header)).to_bytes(4,'big')+header+body

class Source(unittest.TestCase):
    def test_invalid_fixture_refused_before_binary_access(self):
        for kw in ({},{'body':b''},{'body':b'x'*1025},
                   {'body':b'x','wire':b'x'},{'body':b'x','pending':-1}):
            with self.assertRaises(ValueError):probe('not-a-binary',**kw)

@unittest.skipUnless(LIB,'exact original Apollo explicitly required')
class Native(unittest.TestCase):
    def test_whole_dispatch_invokes_generated_receiver_and_erases_pending(self):
        r=probe(LIB,body=rpc(0x100000002))
        self.assertEqual(r['dispatch_return'],1)
        self.assertEqual(r['protocol_flags'],(0,0))
        self.assertEqual(r['native_exception_types'],[])
        self.assertEqual(r['pending_count'],0);self.assertTrue(r['pending_root_empty'])
        self.assertEqual(r['callbacks'],[{'status':0,'result':0,'trees':1,'node_count':1,'node':node()}])
        self.assertTrue({0x399d90,0x3c180e,0x3c382c,0x3c34d8,0x3c2e70,0x36ace8,0x36c404,0x36a860}.issubset(r['visits']))
    def test_parse_success_with_wrong_sequence_is_not_callback_acceptance(self):
        for received,pending in ((0x200000002,0x100000002),
                                 (0x100000003,0x100000002),
                                 (0x100000002,2)):
            r=probe(LIB,body=rpc(received),pending=pending)
            self.assertEqual(r['dispatch_return'],1);self.assertEqual(r['callbacks'],[])
            self.assertEqual(r['pending_count'],1);self.assertFalse(r['pending_root_empty'])
            self.assertNotIn(0x36c404,r['visits'])
    def test_missing_outer_result_invokes_error_then_original_throw(self):
        r=probe(LIB,body=rpc(0x100000002)[:-97]+b'\0')
        self.assertEqual([c['status'] for c in r['callbacks']],[-11])
        self.assertEqual(r['native_exception_types'],[5])
        self.assertIsNone(r['dispatch_return']) # Stopped before C++ unwinding.
    def test_callback_status_zero_does_not_imply_directory_result_zero(self):
        b=bytearray(rpc(0x100000002));b[-97+6:-97+10]=(1).to_bytes(4,'big')
        r=probe(LIB,body=bytes(b))
        self.assertEqual((r['callbacks'][0]['status'],r['callbacks'][0]['result']),(0,1))
        self.assertEqual(r['pending_count'],0)
    def test_original_transport_output_through_whole_rpc_dispatch(self):
        r=probe(LIB,wire=wire(rpc(0x100000002)))
        self.assertEqual((r['transport_return'],r['dispatch_return']),(0,1))
        self.assertEqual(r['callbacks'][0]['node'],node());self.assertEqual(r['pending_count'],0)
        self.assertIn(0x3abe34,r['visits'])
    def test_bad_transport_marker_never_enters_rpc(self):
        w=wire(rpc(0x100000002));r=probe(LIB,wire=b'\xa5'+w[1:])
        self.assertNotEqual(r['transport_return'],0);self.assertEqual(r['callbacks'],[])
        self.assertNotIn(0x3c3a24,r['visits'])

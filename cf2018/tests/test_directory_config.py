import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from directory_config_reply import component,node,rpc,NODE_ID,METHOD
LIB=os.environ.get('CF18_APOLLO_LIBRARY');SOURCE=os.environ.get('CF18_DIRECTORY_IDENTIFY_PREPARED')
class Source(unittest.TestCase):
 def test_fixed_default_node_and_result_sizes(self):self.assertEqual((len(node()),len(component())),(47,97))
 def test_reply_method_type_and_full_u64(self):
  for seq in (1,0x100000002,0xffffffffffffffff):
   b=rpc(seq);p=4+len(METHOD);self.assertEqual(b[4:p],METHOD);self.assertEqual(b[p],2);self.assertEqual(int.from_bytes(b[p+1:p+9],'big'),seq)
 def test_invalid_rpc_sequence_refused(self):
  for x in (-1,2**64,'1',True):
   with self.assertRaises(ValueError):rpc(x)
@unittest.skipUnless(LIB and SOURCE,'explicit original Apollo and private prepared parser source required')
class Original(unittest.TestCase):
 @classmethod
 def setUpClass(cls):sys.path.insert(0,SOURCE)
 @classmethod
 def tearDownClass(cls):sys.path.remove(SOURCE)
 def test_independent_component_exactly_matches_original_writer(self):
  from native_directory_result_controls import component as original
  b,rc,_=original(LIB);self.assertEqual(component(),b);self.assertEqual(rc,97)
 def test_both_original_result_readers_accept_selected_node(self):
  from native_directory_result_controls import read_component
  from native_directory_node_controls import conversion_probe
  for ptr in (False,True):
   r=read_component(LIB,component(),ptr);self.assertTrue(r['success_present']);self.assertEqual((r['result'],r['trees'],r['node_count'],r['consumed']),(0,1,1,97))
   c=conversion_probe(LIB,r['node']);self.assertEqual(c['added_ids'],[NODE_ID]);self.assertGreater(c['assignment_count'],0);self.assertTrue(c['empty_assignments'])
 def test_missing_result_not_success(self):
  from native_directory_result_controls import component as original,read_component
  b,_,_=original(LIB,False);self.assertFalse(read_component(LIB,b,True)['success_present'])
 def test_actual_pending_map_compares_both_u64_words(self):
  from native_directory_pending_controls import probe
  key=0x100000002;self.assertEqual(probe(LIB,key)['events'],[('lookup',True),('callback',True),('erase',True)])
  for wrong in (2,0x200000002,0x100000003):self.assertEqual(probe(LIB,wrong)['events'],[('skipped',True)])
 def test_original_transport_rpc_and_result_pipeline(self):
  from directory_config_reply import field,thrift_field,make_candidate,ROUTE
  from native_directory_reply_pipeline import probe
  packet=0x11223344;seq=0x100000002
  args=thrift_field(10,1,b'PRIVATE!')+thrift_field(11,2,(3).to_bytes(4,'big')+b'ABC')+thrift_field(8,3,bytes(4))+thrift_field(10,4,bytes(8))+b'\0'
  body=packet.to_bytes(4,'big')+len(METHOD).to_bytes(4,'big')+METHOD+b'\x01'+seq.to_bytes(8,'big')+args
  base=b''.join(field(i,1 if i==6 else 0,v) for i,v in enumerate([0x4366,0,1,0x4013,0,0,packet,0,len(body)],1))
  data=field(1,1,0)+field(2,1,0)+field(3,1,4)+field(4,5,field(4,5,field(1,5,ROUTE)));h=field(1,5,base)+field(2,5,field(0x4013,5,data))
  request=b'\x43\x66\xaa'+(5+len(h)).to_bytes(4,'big')+h+body
  reply=make_candidate(request);self.assertNotIn(b'PRIVATE!',reply);self.assertNotIn(b'ABC',reply)
  r=probe(LIB,reply);self.assertEqual((r['transport_return'],r['message_type'],r['method'],r['rpc_sequence']),(0,2,METHOD,seq));self.assertTrue(r['success_present']);self.assertEqual(r['node'],node());self.assertEqual(r['consumed'],r['payload_length'])
  # Alter only body packet-sequence prefix, keeping independent header unchanged.
  bad=request[:-len(body)]+b'\0'*4+body[4:]
  with self.assertRaises(ValueError):make_candidate(bad)

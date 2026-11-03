import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_directory_dispatch_controls import probe
from native_version_reply_controls import component,body,wire,native_component,native_header
from native_version_decision_controls import exercise,VERSION
class Guard(unittest.TestCase):
 def test_invalid_profile_and_fixtures_refused(self):
  with self.assertRaises(ValueError):probe('not-opened',body=b'x',service='unknown')
  for call in (lambda:body(-1),lambda:component(update_type=4),lambda:wire(b'')):
   with self.assertRaises(ValueError):call()
@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'),'explicit original Apollo required')
class Original(unittest.TestCase):
 def setUp(self):self.lib=os.environ['CF18_APOLLO_LIBRARY']
 def check_success(self,r):
  self.assertEqual(r['dispatch_return'],1);self.assertEqual(r['pending_count'],0);self.assertTrue(r['pending_root_empty'])
  self.assertEqual(r['native_exception_types'],[])
  self.assertEqual(r['callbacks'],[{'status':0,'result':0,'presence_flags':7,'update_type':0,'version':VERSION,'comm_sequence':7,'product_id':11,'product_type':12,'request_type':20,'apk_version':VERSION,'res_version':VERSION}])
  self.assertTrue({0x3c382c,0x33e1b0,0x33ea9c,0x33ddfc}.issubset(r['visits']))
 def test_original_writer_matches_independent_complete_component_and_header(self):
  for result,kind in ((0,0),(0,1),(0,2),(1,0)):
   actual,strings=native_component(self.lib,result,kind)
   self.assertEqual(actual,component(result,kind));self.assertEqual(strings,[48,96,100,104,108,112])
  self.assertEqual(native_header(self.lib)+component(),body())
 def test_complete_dispatch_and_typed_result(self):
  self.check_success(probe(self.lib,body=body(),service='version'))
 def test_transport_and_packet_sequence_are_distinct_from_rpc_pending(self):
  for packet in (0x11223344,0x55667788):
   r=probe(self.lib,wire=wire(body(),packet),service='version');self.check_success(r);self.assertEqual(r['transport_return'],0)
 def test_wrong_full_rpc_sequence_does_not_deliver_or_erase(self):
  for sequence,pending in ((0x200000002,0x100000002),(0x100000003,0x100000002),(0x100000002,2)):
   r=probe(self.lib,body=body(sequence),pending=pending,service='version')
   self.assertEqual((r['dispatch_return'],r['callbacks'],r['pending_count']),(1,[],1));self.assertNotIn(0x33ea9c,r['visits'])
 def test_method_label_alone_does_not_validate_this_pending_receiver(self):
  self.check_success(probe(self.lib,body=body(method='Synthetic:Other'),service='version'))
 def test_comm_sequence_is_carried_without_being_the_rpc_lookup_key(self):
  r=probe(self.lib,body=body(comm_sequence=8),service='version')
  self.assertEqual((r['callbacks'][0]['comm_sequence'],r['pending_count']),(8,0))
 def test_missing_success_calls_error_and_original_throw_without_unwinding(self):
  r=probe(self.lib,body=body()[:-len(component())]+b'\0',service='version')
  self.assertEqual(r['callbacks'][0]['status'],-11);self.assertEqual(r['native_exception_types'],[5]);self.assertIsNone(r['dispatch_return']);self.assertEqual(r['pending_count'],1)
 def test_empty_nested_result_is_not_qualified_update_information(self):
  r=probe(self.lib,body=body()[:-len(component())]+b'\x0c\0\0\0\0',service='version')
  self.assertEqual((r['callbacks'][0]['presence_flags'],r['callbacks'][0]['version'],r['pending_count']),(0,0,0))
 def test_rpc_success_does_not_override_failed_result(self):
  r=probe(self.lib,body=body(result=1),service='version');callback=r['callbacks'][0]
  self.assertEqual((callback['status'],callback['result']),(0,1))
  self.assertEqual(exercise(self.lib,20,callback['update_type'],callback['status'],callback['result'])['family'],'NOT_ENTERED')
 def test_typed_success_feeds_separate_original_no_update_control(self):
  callback=probe(self.lib,body=body(),service='version')['callbacks'][0]
  self.assertEqual(callback['version'],VERSION)
  for mode in (20,21):
   r=exercise(self.lib,mode,callback['update_type'],callback['status'],callback['result'])
   self.assertEqual((r['branch'],r['delegate_calls']),('NO_UPDATE_RESULT',1))
 def test_bad_transport_never_reaches_rpc_dispatch(self):
  frame=wire(body());r=probe(self.lib,wire=b'\xa5'+frame[1:],service='version')
  self.assertNotEqual(r['transport_return'],0);self.assertEqual(r['callbacks'],[]);self.assertNotIn(0x3c3a24,r['visits'])

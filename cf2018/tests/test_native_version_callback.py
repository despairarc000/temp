import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_version_callback_controls import callback,method_name,writer_schema,read_component
class Guard(unittest.TestCase):
 def test_invalid_synthetic_status_refused(self):
  for status,result in ((-1,0),(0,2**32),(True,0)):
   with self.assertRaises(ValueError):callback('not-opened',status,result)
@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'),'explicit original Apollo required')
class Original(unittest.TestCase):
 def test_base_writer_includes_result_and_comm_info(self):
  schema=writer_schema(os.environ['CF18_APOLLO_LIBRARY'])
  self.assertEqual(schema[:4],[('struct','ResVersionUpdate'),('field','result',8,1),('field','comm_info',12,2),('struct','UpdateCommInfo')])
  self.assertNotIn(('field','update_info',12,3),schema)
 def test_optional_writer_defines_package_and_configuration_fields(self):
  schema=writer_schema(os.environ['CF18_APOLLO_LIBRARY'],True)
  for field in [('field','update_info',12,3),('field','http_url',11,4),('field','md5sum',11,5),('field','custom_cfg',12,6)]:self.assertIn(field,schema)
 def test_nested_empty_result_parses_without_proving_usable_update_data(self):
  result=read_component(os.environ['CF18_APOLLO_LIBRARY'],b'\x0c\x00\x00\x00\x00')
  self.assertEqual(result,{'consumed':5,'success_present':True,'result':0,'presence_flags':0})
 def test_explicit_zero_result_sets_only_that_presence_bit(self):
  wire=b'\x0c\x00\x00\x08\x00\x01'+bytes(4)+bytes(2)
  self.assertEqual(read_component(os.environ['CF18_APOLLO_LIBRARY'],wire),{'consumed':12,'success_present':True,'result':0,'presence_flags':1})
 def test_missing_success_and_truncated_components_are_distinct(self):
  self.assertFalse(read_component(os.environ['CF18_APOLLO_LIBRARY'],bytes(1))['success_present'])
  with self.assertRaises(ValueError):read_component(os.environ['CF18_APOLLO_LIBRARY'],b'\x0c\x00\x00')
 def test_generated_method_identity(self):
  self.assertEqual(method_name(os.environ['CF18_APOLLO_LIBRARY']),'VersionUpdate:ReqUpdateVersion')
 def test_rpc_failure_cannot_be_success_even_with_zero_result(self):
  for status in (1,0xffffffff):
   self.assertEqual(callback(os.environ['CF18_APOLLO_LIBRARY'],status,0),{'completed':False,'failed':True,'copy_boundaries':[]})
 def test_nonzero_result_cannot_be_success_even_with_zero_rpc_status(self):
  for result in (1,0xffffffff):
   self.assertEqual(callback(os.environ['CF18_APOLLO_LIBRARY'],0,result),{'completed':False,'failed':True,'copy_boundaries':[]})
 def test_both_zero_reach_completion_and_copy_boundaries(self):
  self.assertEqual(callback(os.environ['CF18_APOLLO_LIBRARY'],0,0),{'completed':True,'failed':False,'copy_boundaries':['response','version']})

import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_version_decision_controls import exercise,VERSION
class Guard(unittest.TestCase):
 def test_invalid_synthetic_cases_refused(self):
  for mode,kind in ((True,0),(33,0),(20,-1),(20,4)):
   with self.assertRaises(ValueError):exercise('not-opened',mode,kind)
@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'),'explicit original Apollo required')
class Original(unittest.TestCase):
 def run_case(self,mode,kind):
  result=exercise(os.environ['CF18_APOLLO_LIBRARY'],mode,kind)
  self.assertEqual(result['callback'],{'completed':True,'failed':False,'copied_update_type':kind,'copied_version':VERSION})
  self.assertEqual(result['version_parts'],(0x1111,0x2222,0x3333,0x4444))
  self.assertEqual(result['delegate_calls'],1)
  return result
 def test_both_app_modes_no_update(self):
  for mode in (20,22):
   result=self.run_case(mode,0);self.assertEqual((result['family'],result['branch'],result['flags']),('APP','NO_UPDATE_RESULT',(1,0,0)))
 def test_both_resource_modes_no_update(self):
  for mode in (21,23):
   result=self.run_case(mode,0);self.assertEqual((result['family'],result['branch'],result['flags']),('RESOURCE','NO_UPDATE_RESULT',(0,0,0)))
 def test_optional_update_is_a_different_branch(self):
  for mode in (20,21,22,23):
   result=self.run_case(mode,1);self.assertEqual(result['branch'],'UPDATE_HANDLING');self.assertEqual(result['flags'],(int(mode in (20,22)),1,0))
 def test_forced_update_is_a_different_branch(self):
  for mode in (20,21,22,23):
   result=self.run_case(mode,2);self.assertEqual(result['branch'],'UPDATE_HANDLING');self.assertEqual(result['flags'],(int(mode in (20,22)),1,1))
 def test_unknown_update_kind_is_not_the_no_update_branch(self):
  for mode in (20,21):
   result=self.run_case(mode,3);self.assertEqual(result['branch'],'UPDATE_HANDLING');self.assertEqual(result['flags'],(0,0,0))
 def test_other_manager_mode_does_not_enter_these_families(self):
  self.assertEqual(exercise(os.environ['CF18_APOLLO_LIBRARY'],0,0)['family'],'OTHER_MODE')
 def test_callback_failures_do_not_enter_decision_pipeline(self):
  for status,result in ((1,0),(0,1)):
   output=exercise(os.environ['CF18_APOLLO_LIBRARY'],20,0,status,result)
   self.assertEqual(output['family'],'NOT_ENTERED');self.assertTrue(output['callback']['failed'])

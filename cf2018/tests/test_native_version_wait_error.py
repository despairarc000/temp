import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_version_wait_error import control,source_checks
@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'),'explicit exact original Apollo required')
class Original(unittest.TestCase):
 def test_source_predicates(self):
  self.assertTrue(all(source_checks(os.environ['CF18_APOLLO_LIBRARY']).values()))
 def test_exact_wait_threshold_and_negative_controls(self):
  library=os.environ['CF18_APOLLO_LIBRARY']
  self.assertEqual(control(library,1000),(17,154140712))
  self.assertEqual(control(library,999),(34,0))
  self.assertEqual(control(library,1001),(34,0))
 def test_update_failure_is_a_different_error(self):
  library=os.environ['CF18_APOLLO_LIBRARY']
  self.assertEqual(control(library,update_result=1),(17,154140708))
  self.assertEqual(control(library,update_result=0),(34,0))

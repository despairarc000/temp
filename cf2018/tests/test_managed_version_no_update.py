import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from managed_version_no_update_source import check
class Guard(unittest.TestCase):
 def test_wrong_source_refused(self):
  class Wrong:sha='wrong'
  with self.assertRaises(ValueError):check(Wrong(),None)
@unittest.skipUnless(os.environ.get('CF18_MANAGED_LIBRARY') and os.environ.get('CF18_DIRECTORY_IDENTIFY_PREPARED'),'explicit original managed source/inspector required')
class Original(unittest.TestCase):
 def test_original_no_update_state_and_branch_predicates(self):
  folder=os.environ['CF18_DIRECTORY_IDENTIFY_PREPARED'];sys.path.insert(0,folder)
  try:
   from managed_call_trace import Metadata,decode_calls
   self.assertTrue(all(check(Metadata(os.environ['CF18_MANAGED_LIBRARY']),decode_calls).values()))
  finally:sys.path.remove(folder)

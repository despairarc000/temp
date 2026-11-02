"""Original managed static checks; no CLR or game execution."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from managed_directory_config_metadata import check
class Source(unittest.TestCase):
 def test_wrong_build_refused_before_metadata_access(self):
  class Wrong:sha='wrong'
  with self.assertRaises(ValueError):check(Wrong(),None)
@unittest.skipUnless(os.environ.get('CF18_DIRECTORY_IDENTIFY_PREPARED') and os.environ.get('CF18_MANAGED_LIBRARY'),'explicit original DLL and private inspector required')
class Original(unittest.TestCase):
 def test_empty_selected_settings_skip_parser_and_construct_defaults(self):
  source=os.environ['CF18_DIRECTORY_IDENTIFY_PREPARED'];sys.path.insert(0,source)
  try:
   from managed_call_trace import Metadata,decode_calls
   result=check(Metadata(os.environ['CF18_MANAGED_LIBRARY']),decode_calls)
   self.assertEqual(len(result),8);self.assertTrue(all(result.values()))
  finally:sys.path.remove(source)

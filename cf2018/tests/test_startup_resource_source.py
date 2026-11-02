"""Exact original source validation; never starts a server or managed game."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from startup_resource_source import managed_checks,native_checks

class Source(unittest.TestCase):
 def test_wrong_managed_build_refused_before_access(self):
  class Wrong:sha='other build'
  with self.assertRaises(ValueError):managed_checks(Wrong(),None)

@unittest.skipUnless(os.environ.get('CF18_MANAGED_LIBRARY') and os.environ.get('CF18_DIRECTORY_IDENTIFY_PREPARED'),'explicit original managed DLL and inspector required')
class Managed(unittest.TestCase):
 def test_timeout_alternative_and_separate_resource_checker(self):
  source=os.environ['CF18_DIRECTORY_IDENTIFY_PREPARED'];sys.path.insert(0,source)
  try:
   from managed_call_trace import Metadata,decode_calls
   result=managed_checks(Metadata(os.environ['CF18_MANAGED_LIBRARY']),decode_calls)
   self.assertEqual(len(result),23)
  finally:sys.path.remove(source)

@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'),'explicit original Apollo required')
class Native(unittest.TestCase):
 def test_gcloud_updater_uses_its_own_rpc_connector(self):
  self.assertEqual(len(native_checks(os.environ['CF18_APOLLO_LIBRARY'])),6)

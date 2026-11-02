"""Optional exact-original resource index decode, no asset extraction."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from original_resource_reference import locate

@unittest.skipUnless(os.environ.get('CF18_ORIGINAL_APK'),'explicit original APK and optional UnityPy required')
class Original(unittest.TestCase):
    def test_configuration_pointer_resolves_to_specific_external_file(self):
        r=locate(os.environ['CF18_ORIGINAL_APK'])
        self.assertEqual((r['file_id'],r['path_id'],r['index_entries']),(518,1,8344))
        self.assertEqual(r['external_file'],'7346236864af94314bae0701e3cddcd2')
        self.assertEqual(r['resource'],'config/system/gcloudsetting_')

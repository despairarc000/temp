"""Optional original manifest source check; never exports keys/asset contents."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from original_bundle_manifest import summarize
class Source(unittest.TestCase):
    def test_wrong_source_refused_before_metadata_or_crypto(self):
        class Wrong:sha='wrong'
        with self.assertRaises(ValueError):summarize(Wrong(),b'')
@unittest.skipUnless(all(os.environ.get(k) for k in ('CF18_MANAGED_LIBRARY','CF18_CONFIG_BUNDLE','CF18_DIRECTORY_IDENTIFY_PREPARED')),'explicit original managed inspector/configuration entry required')
class Original(unittest.TestCase):
    def test_source_parameters_decode_seven_complete_manifests(self):
        folder=os.environ['CF18_DIRECTORY_IDENTIFY_PREPARED'];sys.path.insert(0,folder)
        try:
            from managed_call_trace import Metadata
            r=summarize(Metadata(os.environ['CF18_MANAGED_LIBRARY']),Path(os.environ['CF18_CONFIG_BUNDLE']).read_bytes())
        finally:sys.path.remove(folder)
        self.assertEqual((r['bundle_objects'],len(r['manifests']),r['asset_records'],r['local_bundle_records']),(9,7,7973,195))
        self.assertTrue(all(v['full_consumption'] for v in r['manifests']))
        self.assertEqual(sum(v['gcloud_name_matches'] for v in r['manifests']),0)

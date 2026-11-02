"""No source assets/settings/key fixtures in this public test file."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from original_gcloud_settings import audit,evaluate_get_value
class Guard(unittest.TestCase):
    def test_wrong_source_refused(self):
        class Wrong:sha='wrong'
        with self.assertRaises(ValueError):audit(Wrong(),b'',None)
        with self.assertRaises(ValueError):evaluate_get_value(Wrong(),'synthetic.test','')
@unittest.skipUnless(all(os.environ.get(k) for k in ('CF18_MANAGED_LIBRARY','CF18_GCLOUD_RESOURCE','CF18_DIRECTORY_IDENTIFY_PREPARED')),'explicit original managed source/resource required')
class Original(unittest.TestCase):
    def setUp(self):
        folder=os.environ['CF18_DIRECTORY_IDENTIFY_PREPARED'];sys.path.insert(0,folder)
        from managed_call_trace import Metadata,decode_calls
        self.metadata=Metadata(os.environ['CF18_MANAGED_LIBRARY']);self.decode=decode_calls
        self.addCleanup(lambda:sys.path.remove(folder))
    def test_complete_original_settings_and_source_checks(self):
        result=audit(self.metadata,Path(os.environ['CF18_GCLOUD_RESOURCE']).read_bytes(),self.decode)
        self.assertEqual((result['resource_objects'],result['payload_bytes'],result['plaintext_bytes'],result['csv_rows'],result['csv_columns'],result['setting_rows'],result['regional_columns']),(1,6416,6408,24,20,22,17))
        self.assertTrue(result['tversion_default_empty'])
        self.assertEqual((result['tversion_regional_dns_raw'],result['tversion_regional_dns_after_strip']),(3,17))
        self.assertTrue(all(result['source_checks'].values()))
    def test_original_selector_rejects_default_only_inference(self):
        # Actual source method, synthetic fields. Blank Default is insufficient.
        self.assertEqual(evaluate_get_value(self.metadata,'','synthetic.invalid'),'synthetic.invalid')
        self.assertEqual(evaluate_get_value(self.metadata,'synthetic.invalid',''),'synthetic.invalid')
        self.assertEqual(evaluate_get_value(self.metadata,'synthetic.invalid',None),'synthetic.invalid')
        # IsNullOrEmpty is not IsNullOrWhiteSpace; CSV trimming is separate.
        self.assertEqual(evaluate_get_value(self.metadata,'synthetic.invalid',' '),' ')

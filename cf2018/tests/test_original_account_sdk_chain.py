import os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from original_account_sdk_chain import audit

class Public(unittest.TestCase):
    def test_unrelated_apk_rejected_before_optional_dex_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'synthetic.apk';p.write_bytes(b'non-sensitive synthetic negative')
            with self.assertRaisesRegex(ValueError,'exact original APK'):audit(p)

@unittest.skipUnless(os.environ.get('CF18_ORIGINAL_APK'),'explicit original APK required')
class Original(unittest.TestCase):
    def test_original_provider_and_separate_account_server_chain(self):
        checks=audit(os.environ['CF18_ORIGINAL_APK'])
        self.assertEqual(len(checks),13);self.assertTrue(all(checks.values()))

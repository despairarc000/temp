import os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from original_account_config_priority import original_method, evaluate


class Public(unittest.TestCase):
    def test_unrelated_apk_rejected_before_optional_dependency(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'synthetic.apk'
            path.write_bytes(b'synthetic non-sensitive negative control')
            with self.assertRaisesRegex(ValueError, 'exact original APK'):
                original_method(path)


@unittest.skipUnless(os.environ.get('CF18_ORIGINAL_APK'), 'explicit original APK required')
class Original(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.method = original_method(os.environ['CF18_ORIGINAL_APK'])

    def test_source_selector_with_synthetic_maps(self):
        key = 'synthetic_setting'
        cases = [
            ({key: 'REGIONAL'}, {key: 'DOWNLOADED'}, 'REGIONAL'),
            ({}, {key: 'DOWNLOADED'}, 'DOWNLOADED'),
            ({}, {}, 'SYNTHETIC_DEFAULT'),
            (None, {key: 'DOWNLOADED'}, 'DOWNLOADED'),
            ({key: ''}, {key: 'DOWNLOADED'}, ''),
            ({key: None}, {key: 'DOWNLOADED'}, None),
        ]
        for user, downloaded, expected in cases:
            with self.subTest(user=user, downloaded=downloaded):
                self.assertEqual(evaluate(self.method, user, downloaded), expected)

    def test_downloaded_replacement_cannot_override_populated_user_key(self):
        for number in range(16):
            with self.subTest(number=number):
                self.assertEqual(evaluate(self.method,
                    {'synthetic_setting': 'REGIONAL'},
                    {'synthetic_setting': 'DOWNLOADED_' + str(number)}), 'REGIONAL')

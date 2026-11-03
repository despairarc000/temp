import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,MagicMock

P=Path(__file__).resolve().parents[1]/'tools/prepare_scoped_trust_apks.py'
spec=importlib.util.spec_from_file_location('phone_builder',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class PhonePreparer(unittest.TestCase):
    def test_embedded_utility_matches_reviewed_source(self):
        self.assertEqual(m.RESOURCE_SOURCE,(P.parents[1]/'experiments/scoped_trust_resources.py').read_text())

    def test_original_scope_normalized_exact_match_only(self):
        with patch.object(m,'HOST_FINGERPRINTS',{m.digest(b'synthetic.invalid')}):
            self.assertEqual(m.allowed_hosts(['SYNTHETIC.INVALID.']),['synthetic.invalid'])
            for values in [[],['sub.synthetic.invalid'],['https://synthetic.invalid'],['*.synthetic.invalid']]:
                with self.subTest(values=values),self.assertRaises(ValueError):m.allowed_hosts(values)

    def test_unrelated_apk_refused_before_modification(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'synthetic.apk';path.write_bytes(b'not the original')
            with self.assertRaises((ValueError,m.zipfile.BadZipFile)):m.source_bytes(path)
            self.assertEqual(path.read_bytes(),b'not the original')

    def test_installed_source_path_cannot_select_other_files(self):
        with patch.object(m,'run',return_value=b'package:/data/data/other/secret.apk\n') as command:
            with self.assertRaises(ValueError):m.source_bytes(None)
            self.assertEqual(command.call_count,1)
            self.assertEqual(command.call_args.args[0],['adb','shell','pm','path',m.PACKAGE])

    def test_adb_hostname_read_is_game_pid_scoped_and_whitelisted(self):
        fake=b'D/iMSDK(123): Unable to resolve host "synthetic.invalid"\nD/Other(123): Unable to resolve host "other.invalid"\n'
        with patch.object(m,'HOST_FINGERPRINTS',{m.digest(b'synthetic.invalid')}),patch.object(m,'run',side_effect=[b'123\n',fake]) as command:
            self.assertEqual(m.hosts_from_adb(),['synthetic.invalid'])
            self.assertEqual(command.call_args.args[0],['adb','logcat','-d','-t','1500','--pid=123','-v','brief'])

    def test_forged_signer_refused(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);path=out/'wrong.jar';path.write_bytes(b'synthetic')
            with self.assertRaisesRegex(ValueError,'fingerprint'):m.signer_jar(out,path)
            self.assertFalse((out/'apksigner.jar').exists())

    def test_range_refusal_does_not_download_full_sdk(self):
        response=MagicMock();response.status=200
        context=MagicMock();context.__enter__.return_value=response
        with tempfile.TemporaryDirectory() as d,patch.object(m.urllib.request,'urlopen',return_value=context):
            with self.assertRaisesRegex(ValueError,'bounded'):m.signer_jar(Path(d))
        response.read.assert_not_called()

    def test_payload_change_refused(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'synthetic.apk'
            with m.zipfile.ZipFile(path,'w') as z:z.writestr('classes.dex',b'changed')
            with self.assertRaisesRegex(ValueError,'payload mismatch'):m.verify_payload(path,{'classes.dex':b'original'})

if __name__=='__main__':unittest.main()

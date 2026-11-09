import os,struct,sys,tempfile,unittest,zlib
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from original_package_integrity import signature,parse_records,audit

class Public(unittest.TestCase):
    def test_signature_includes_name_size_and_crc_in_documented_order(self):
        name='synthetic/file';crc=123;size=456
        self.assertEqual(signature(name,crc,size),zlib.crc32(name.encode()+struct.pack('<II',size,crc)))
        self.assertNotEqual(signature(name,crc,size),signature(name,crc^1,size))

    def test_record_parser_bounds_and_name_validation(self):
        name=b'synthetic/file\0';raw=struct.pack('<HHII',12+len(name),0,123,456)+name
        def parsed(data,length=None):
            n=SimpleNamespace(u=SimpleNamespace(mem_read=lambda a,k:data[a:a+k]))
            return parse_records(n,0,len(data)if length is None else length)
        self.assertEqual(parsed(raw),[('synthetic/file',123,456)])
        for bad in [b'x',struct.pack('<H',65535)+bytes(20),raw+raw]:
            with self.subTest(bad_size=len(bad)),self.assertRaises(ValueError):parsed(bad)
        with self.assertRaises(ValueError):parsed(raw,0x20001)

    def test_wrong_original_refused_before_optional_native_dependencies(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'synthetic.apk';p.write_bytes(b'synthetic non-game negative')
            with self.assertRaisesRegex(ValueError,'exact original APK'):audit('missing-library',p,{})

    def test_unrecognized_output_role_rejected_before_private_sources(self):
        with self.assertRaisesRegex(ValueError,'fixed comparison labels'):audit('absent','absent',{'private-value':'absent'})

@unittest.skipUnless(all(os.environ.get(k)for k in ['CF18_TPRT_LIBRARY','CF18_ORIGINAL_APK','CF18_CONTROL_APK','CF18_SCOPED_APK']),'explicit private original and both prepared APKs required')
class Original(unittest.TestCase):
    def test_original_metadata_distinguishes_scoped_changes_and_unlisted_addition(self):
        result=audit(os.environ['CF18_TPRT_LIBRARY'],os.environ['CF18_ORIGINAL_APK'],
                     {'signature_control':os.environ['CF18_CONTROL_APK'],'scoped_trust':os.environ['CF18_SCOPED_APK']})
        self.assertEqual(result['protected_record_count'],1210)
        self.assertTrue(result['comparisons']['original']['native_count_gate_passed'])
        self.assertTrue(result['comparisons']['signature_control']['native_count_gate_passed'])
        self.assertFalse(result['comparisons']['scoped_trust']['native_count_gate_passed'])
        self.assertEqual(result['comparisons']['scoped_trust']['mismatched_members'],['AndroidManifest.xml','resources.arsc'])
        self.assertTrue(all(result['synthetic_negative_controls'].values()))
        self.assertTrue(all(result['native_metadata_verification_controls'].values()))
        self.assertFalse(result['phone_call_stack_observed']);self.assertFalse(result['game_files_modified'])

if __name__=='__main__':unittest.main()

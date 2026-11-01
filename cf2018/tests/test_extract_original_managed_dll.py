"""Source-free tests for safe original CF2018 DLL extractor."""
import hashlib,sys,tempfile,unittest,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from extract_original_managed_dll import extract,INNER_DLL,INNER_APK
class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.xapk=self.root/'original.xapk'
        self.sample=b'unit-test synthetic mono assembly bytes'
        self.sha=hashlib.sha256(self.sample).hexdigest()
    def fixture(self,payload=None,member=INNER_DLL):
        apk=self.root/'inner.apk'
        with zipfile.ZipFile(apk,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr(member,self.sample if payload is None else payload)
        with zipfile.ZipFile(self.xapk,'w',zipfile.ZIP_DEFLATED) as z:z.write(apk,INNER_APK)
    def test_success_preserves_original(self):
        self.fixture();before=hashlib.sha256(self.xapk.read_bytes()).hexdigest()
        dest=self.root/'private'/'Assembly-CSharp.dll'
        result=extract(self.xapk,dest,self.sha)
        self.assertTrue(result['verified']);self.assertEqual(dest.read_bytes(),self.sample)
        self.assertEqual(before,hashlib.sha256(self.xapk.read_bytes()).hexdigest())
    def test_modified_binary_refused_and_not_written(self):
        self.fixture(payload=self.sample+b'!');dest=self.root/'out.dll'
        with self.assertRaises(ValueError):extract(self.xapk,dest,self.sha)
        self.assertFalse(dest.exists());self.assertFalse((self.root/'out.dll.incomplete').exists())
    def test_missing_original_refused(self):
        with self.assertRaises(FileNotFoundError):extract(self.xapk,self.root/'out.dll',self.sha)
    def test_missing_assembly_refused(self):
        self.fixture(member='other.bin')
        with self.assertRaises(KeyError):extract(self.xapk,self.root/'out.dll',self.sha)
    def test_existing_output_never_overwritten(self):
        self.fixture();dest=self.root/'out.dll';dest.write_bytes(b'kept')
        with self.assertRaises(FileExistsError):extract(self.xapk,dest,self.sha)
        self.assertEqual(dest.read_bytes(),b'kept')
if __name__=='__main__':unittest.main()

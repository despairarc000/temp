"""Synthetic renamed-container controls; never inspect original assets here."""
import hashlib,io,os,struct,sys,tempfile,unittest,zipfile
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from inspect_resource_container import inspect,main,TARGET,MAX_INDEX

class Tests(unittest.TestCase):
    def run_input(self,data):
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'Assets.png';source.write_bytes(data)
            before=hashlib.sha256(source.read_bytes()).digest()
            result=inspect(source)
            self.assertEqual(hashlib.sha256(source.read_bytes()).digest(),before)
            self.assertEqual(list(Path(folder).iterdir()),[source])
            return result
    def archive(self,name):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:z.writestr(name,b'SYNTHETIC_PRIVATE_VALUE')
        return b.getvalue()
    def test_renamed_zip_finds_exact_config_without_content_export(self):
        r=self.run_input(self.archive('data/'+TARGET))
        self.assertEqual((r['header_kind'],r['zip_index'],r['configuration_entry']),('ZIP','PARSED','PRESENT'))
        self.assertNotIn('SYNTHETIC_PRIVATE_VALUE',str(r));self.assertNotIn(TARGET,str(r))
    def test_similar_name_is_not_exact_target(self):
        r=self.run_input(self.archive(TARGET+'.other'))
        self.assertEqual(r['configuration_entry'],'NOT_IN_THIS_ZIP')
    def test_png_signature_does_not_hide_appended_zip_index(self):
        r=self.run_input(b'\x89PNG\r\n\x1a\n'+self.archive(TARGET))
        self.assertEqual((r['header_kind'],r['configuration_entry']),('PNG','PRESENT'))
    def test_png_and_unity_are_not_declared_zip_or_config(self):
        for data,label in ((b'\x89PNG\r\n\x1a\n'+b'x'*40,'PNG'),(b'UnityFS\0'+b'x'*40,'UNITYFS')):
            r=self.run_input(data);self.assertEqual(r['header_kind'],label)
            self.assertEqual(r['configuration_entry'],'UNKNOWN')
    def test_oversized_index_rejected_before_zip_parser(self):
        eocd=struct.pack('<4s4H2LH',b'PK\x05\x06',0,0,1,1,MAX_INDEX+1,0,0)
        self.assertEqual(self.run_input(b'x'*32+eocd)['zip_index'],'METADATA_BOUND_EXCEEDED')
    def test_malformed_end_record_is_not_validated(self):
        eocd=struct.pack('<4s4H2LH',b'PK\x05\x06',0,0,0,0,0,0,8)
        self.assertEqual(self.run_input(eocd)['zip_index'],'END_RECORD_INCONSISTENT')
    def test_report_alias_cannot_overwrite_source(self):
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'Assets.png';source.write_bytes(b'original')
            output=Path(folder)/'report.txt';os.link(source,output)
            with patch.object(sys,'argv',['inspect','--source',str(source),'--output',str(output)]):
                with self.assertRaises(ValueError):main()
            self.assertEqual(source.read_bytes(),b'original')

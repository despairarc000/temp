"""R047 original GCloud connector source audit: mutation tests and private gated check."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from native_gcloud_connector_source_audit import PINS,WINDOWS,failures,parse,audit
class Controls(unittest.TestCase):
    def setUp(self):self.insns={a:(op,args) for _,a,op,args in PINS}
    def test_unique_and_window_coverage(self):
        self.assertEqual((len(PINS),len(self.insns)),(14,14))
        for _,a,_,_ in PINS:self.assertTrue(any(lo<=a<hi for lo,hi in WINDOWS),hex(a))
    def test_reference_positive(self):self.assertEqual(failures(self.insns),[])
    def test_missing_pin_rejection(self):
        for name,a,_,_ in PINS:
            with self.subTest(name=name):
                x=dict(self.insns);del x[a];self.assertEqual(failures(x),[name])
    def test_operand_mutation_rejection(self):
        for name,a,op,arg in PINS:
            with self.subTest(name=name):
                x=dict(self.insns);x[a]=(op,arg+"!");self.assertEqual(failures(x),[name])
    def test_nonoriginal_rejected(self):
        with self.assertRaises((OSError,ValueError)):audit(__file__)
    def test_duplicate_disassembly_refused(self):
        line="  3c5b3c: f8c4 019c str.w r0, [r4, #0x19c]"
        with self.assertRaises(ValueError):parse(line+"\n"+line)
    def test_exact_original_optional(self):
        lib=os.environ.get("CF18_APOLLO_LIBRARY")
        if not lib:self.skipTest("original private Apollo absent from CI")
        v=audit(lib)
        self.assertEqual((v["checks"],v["passed"],v["failed"]),(14,14,[]))
if __name__=="__main__":unittest.main()

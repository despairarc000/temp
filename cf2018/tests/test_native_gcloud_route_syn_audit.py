"""R046 original-native static route-to-SYN audit negative controls."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from native_gcloud_route_syn_audit import PINS,WINDOWS,parse,failures,audit
class NativeChecks(unittest.TestCase):
    def setUp(self):self.reference={a:(op,args) for _,a,op,args in PINS}
    def test_pins_unique_and_covered(self):
        self.assertEqual(len(PINS),26)
        self.assertEqual(len(self.reference),len(PINS))
        wins=sorted(WINDOWS)
        for i,(lo,hi) in enumerate(wins):
            self.assertLess(lo,hi)
            if i:self.assertLessEqual(wins[i-1][1],lo)
        for _,a,_,_ in PINS:self.assertTrue(any(lo<=a<hi for lo,hi in wins),hex(a))
    def test_synthetic_reference(self):self.assertEqual(failures(self.reference),[])
    def test_missing_pins_rejected(self):
        for name,addr,_,_ in PINS:
            with self.subTest(pin=name):
                changed=dict(self.reference);changed.pop(addr)
                self.assertEqual(failures(changed),[name])
    def test_wrong_opcodes_rejected(self):
        for name,addr,op,args in PINS:
            with self.subTest(pin=name):
                changed=dict(self.reference);changed[addr]=("nop",args)
                self.assertEqual(failures(changed),[name])
    def test_wrong_operands_rejected(self):
        for name,addr,op,args in PINS:
            with self.subTest(pin=name):
                changed=dict(self.reference);changed[addr]=(op,args+" altered")
                self.assertEqual(failures(changed),[name])
    def test_decode_comment(self):
        x=parse(["  3abb86: 2b04  cmp r3, #0x4 @ comment",
                 "  3abbac: 227f  movs r2, #0x7f"])
        self.assertEqual(x[0x3abb86],("cmp","r3, #0x4"))
        self.assertEqual(x[0x3abbac],("movs","r2, #0x7f"))
    def test_duplicate_refused(self):
        line="  3abb86: 2b04  cmp r3, #0x4"
        with self.assertRaises(ValueError):parse([line,line])
    def test_invalid_file_refused(self):
        with self.assertRaises((ValueError,OSError)):audit(__file__)
    def test_optional_original(self):
        original=os.environ.get("CF18_APOLLO_LIBRARY")
        if not original:self.skipTest("private original Apollo not available in public CI")
        x=audit(original)
        self.assertEqual((x["checks"],x["passed"],x["failed"]),(26,26,[]))
        self.assertEqual(x["phone_runtime_chain"],"UNPROVEN")
if __name__=="__main__":unittest.main()

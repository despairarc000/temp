"""R041 source-free mutations plus optional hash-pinned original verification."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_address_callback_audit import PINS,WINDOWS,audit,failures,parse_instruction_lines
class Tests(unittest.TestCase):
    def setUp(self):
        self.baseline={addr:(op,args) for _,addr,op,args in PINS}
    def test_unique_pins_nonoverlap(self):
        self.assertEqual(len(PINS),len(self.baseline))
        spans=sorted(WINDOWS)
        for i,(a,b) in enumerate(spans):
            self.assertLess(a,b)
            if i:self.assertLessEqual(spans[i-1][1],a)
        for _,a,_,_ in PINS:
            self.assertTrue(any(lo<=a<hi for lo,hi in WINDOWS))
    def test_positive_synthetic(self):
        self.assertEqual(failures(self.baseline),[])
    def test_each_omission_is_rejected(self):
        for name,addr,_,_ in PINS:
            with self.subTest(pin=name):
                changed=dict(self.baseline);del changed[addr]
                self.assertEqual(failures(changed),[name])
    def test_each_operand_mutation_is_rejected(self):
        for name,addr,op,args in PINS:
            with self.subTest(pin=name):
                changed=dict(self.baseline);changed[addr]=(op,args+'!')
                self.assertEqual(failures(changed),[name])
    def test_each_mnemonic_mutation_is_rejected(self):
        for name,addr,op,args in PINS:
            with self.subTest(pin=name):
                changed=dict(self.baseline);changed[addr]=('nop',args)
                self.assertEqual(failures(changed),[name])
    def test_parser(self):
        rows=['  39bb08: f7fd ffc6     bl 0x399a98 <symbol> @ imm = #-1',
              '  39bb10: 686b          ldr r3, [r5, #0x4]']
        x=parse_instruction_lines(rows)
        self.assertEqual(x[0x39bb08],('bl','0x399a98'))
        self.assertEqual(x[0x39bb10],('ldr','r3, [r5, #0x4]'))
        with self.assertRaises(ValueError):parse_instruction_lines(rows+rows[:1])
    def test_non_original_refused(self):
        with self.assertRaises((ValueError,OSError)):audit(__file__)
    def test_private_original_optional(self):
        lib=os.environ.get('CF18_APOLLO_LIBRARY')
        if not lib:self.skipTest('private original not provided')
        r=audit(lib)
        self.assertEqual((r['verified'],r['total'],r['failures']),(34,34,[]))
        self.assertFalse(r['real_phone_callback_observed'])
        self.assertFalse(r['ten_byte_service_name_identified'])
if __name__=='__main__':unittest.main()

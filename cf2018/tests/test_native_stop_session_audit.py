"""Source-free mutations plus optional exact private original, R040."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_stop_session_audit import PINS,failures,parse,audit
class Tests(unittest.TestCase):
    def test_pins_unique(self):
        self.assertEqual(len(PINS),13)
        self.assertEqual(len({a for _,a,_,_ in PINS}),13)
    def test_positive_control(self):
        self.assertEqual(failures({a:(op,args) for _,a,op,args in PINS}),[])
    def test_every_mutated_operand_is_rejected(self):
        source={a:(op,args) for _,a,op,args in PINS}
        for name,a,op,args in PINS:
            with self.subTest(name=name):
                edited=dict(source);edited[a]=(op,args+'?')
                self.assertEqual(failures(edited),[name])
    def test_each_missing_pin_is_rejected(self):
        source={a:(op,args) for _,a,op,args in PINS}
        for name,a,_,_ in PINS:
            with self.subTest(name=name):
                edited=dict(source);del edited[a]
                self.assertEqual(failures(edited),[name])
    def test_bad_binary_refused(self):
        with self.assertRaises((ValueError,OSError)):audit(__file__)
    def test_disasm_parser(self):
        lines='  3a970a: f245 0301 movw r3, #0x5001\n  3a9724: f245 0201 movw r2, #0x5001 @ note\n'
        self.assertEqual(parse(lines)[0x3a970a],('movw','r3, #0x5001'))
        self.assertEqual(parse(lines)[0x3a9724],('movw','r2, #0x5001'))
    def test_exact_private_original_optional(self):
        lib=os.environ.get('CF18_APOLLO_LIBRARY')
        if not lib:self.skipTest('private original not supplied')
        result=audit(lib)
        self.assertEqual((result['checks'],result['passed'],result['failed']),(13,13,[]))
        self.assertFalse(result['phone_5001_same_callsite_proven'])
if __name__=='__main__': unittest.main()

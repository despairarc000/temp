"""R030 exact-original private test and mutation controls."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_inbound_4013_audit import PINS,parse_instructions,check_pins,audit

class Tests(unittest.TestCase):
    def test_pins_are_unique(self):
        self.assertEqual(len(PINS),26)
        self.assertEqual(len({x[1] for x in PINS}),26)
    def test_independent_synthetic_positive(self):
        self.assertEqual(check_pins({a:(op,arg) for _,a,op,arg in PINS}),[])
    def test_each_mutated_instruction_rejected(self):
        base={a:(op,arg) for _,a,op,arg in PINS}
        for name,address,op,arg in PINS:
            with self.subTest(name=name):
                modified=dict(base);modified[address]=(op,arg+'?')
                self.assertEqual(check_pins(modified),[name])
    def test_missing_type_4013_pin_rejected(self):
        base={a:(op,arg) for _,a,op,arg in PINS}
        del base[0x3a8de4]
        self.assertEqual(check_pins(base),['peek_type_4013'])
    def test_parse_native_window(self):
        raw='  3a8de4: f244 0313 movw r3, #0x4013\n  3a8df2: d06f beq 0x3a8ed4 <L> @ imm=2\n'
        x=parse_instructions(raw)
        self.assertEqual(x[0x3a8de4],('movw','r3, #0x4013'))
        self.assertEqual(x[0x3a8df2],('beq','0x3a8ed4'))
    def test_wrong_native_fingerprint_rejected(self):
        with self.assertRaises((ValueError,OSError)):
            audit(__file__)
    def test_private_native_original_optional(self):
        p=os.getenv('CF18_APOLLO_LIBRARY')
        if not p:self.skipTest('exact private Apollo not supplied')
        r=audit(p)
        self.assertEqual((r['checks'],r['passed'],r['failed']),(26,26,[]))
        self.assertEqual(r['server_return_envelope'],'NOT_VERIFIED')
        self.assertFalse(r['accepted_phone_reply'])

if __name__=='__main__':unittest.main()

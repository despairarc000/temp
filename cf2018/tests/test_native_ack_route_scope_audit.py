"""R042 static-only mutation controls and optional original Apollo check."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_ack_route_scope_audit import PINS,parse,failures,audit
class Tests(unittest.TestCase):
    def setUp(self):self.reference={a:(op,args) for _,a,op,args in PINS}
    def test_unique_pins(self):self.assertEqual(len(PINS),len(self.reference))
    def test_source_free_positive(self):self.assertEqual(failures(self.reference),[])
    def test_all_missing_pins(self):
        for name,addr,_,_ in PINS:
            with self.subTest(name=name):
                c=dict(self.reference);del c[addr]
                self.assertEqual(failures(c),[name])
    def test_mutated_key_or_target(self):
        for name,addr,op,args in PINS:
            with self.subTest(name=name):
                c=dict(self.reference);c[addr]=(op,args+'!')
                self.assertEqual(failures(c),[name])
    def test_parser_handles_real_format(self):
        self.assertEqual(parse(['  3b58d8: 2111          movs r1, #0x11'])[0x3b58d8],
                         ('movs','r1, #0x11'))
    def test_nonoriginal_refused(self):
        with self.assertRaises(ValueError):audit(__file__)
    def test_original_optional(self):
        f=os.environ.get('CF18_APOLLO_LIBRARY')
        if not f:self.skipTest('private original absent')
        res=audit(f)
        self.assertEqual(res['failures'],[])
        self.assertEqual((res['checked'],res['passed']),(12,12))
        self.assertFalse(res['auth_or_route_acceptance_proven'])
if __name__=='__main__':unittest.main()

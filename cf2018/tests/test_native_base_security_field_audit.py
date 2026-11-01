"""R032 exact-original gated native field6 proof and source-free mutation tests."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_base_security_field_audit import PINS,failures,audit
class Tests(unittest.TestCase):
    def test_exact_native_pin_count(self):
        self.assertEqual(len(PINS),10)
        self.assertEqual(len({a for _,a,_,_ in PINS}),10)
    def test_source_free_positive(self):
        self.assertEqual(failures({a:(op,arg) for _,a,op,arg in PINS}),[])
    def test_mutation_refused_for_every_pin(self):
        original={a:(op,arg) for _,a,op,arg in PINS}
        for name,a,op,arg in PINS:
            with self.subTest(name=name):
                changed=dict(original);changed[a]=(op,'wrong')
                self.assertEqual(failures(changed),[name])
    def test_missing_instruction_refused(self):
        original={a:(op,arg) for _,a,op,arg in PINS}
        for name,a,_,_ in PINS:
            with self.subTest(name=name):
                changed=dict(original);del changed[a]
                self.assertEqual(failures(changed),[name])
    def test_wrong_source_refused(self):
        with self.assertRaises((ValueError,OSError)):audit(__file__)
    def test_original_private_if_supplied(self):
        p=os.getenv('CF18_APOLLO_LIBRARY')
        if not p:self.skipTest('private original not supplied')
        r=audit(p)
        self.assertEqual((r['checks'],r['passed'],r['failed']),(11,11,[]))
        self.assertTrue(r['tgcp_base_field6_dispatch_verified'])
        self.assertFalse(r['reply_sent'])
if __name__=='__main__':unittest.main()

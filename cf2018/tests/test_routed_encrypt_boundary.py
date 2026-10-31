import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_routed_tx import encrypt_boundary
LIB=os.environ.get('CF18_APOLLO_LIBRARY')
class BoundsTests(unittest.TestCase):
    def test_reject_before_source(self):
        with self.assertRaises(ValueError):encrypt_boundary('absent',method=999)

@unittest.skipUnless(LIB,'private pinned native Apollo required')
class NativeTests(unittest.TestCase):
    def test_mode0_copy_independent_of_compression_context(self):
        for c in (0,1):
            r=encrypt_boundary(LIB,method=0,compression=c)
            self.assertEqual(r['return'],0);self.assertTrue(r['payload_copied'])
    def test_no_compression_does_not_remove_encrypted_key_requirement(self):
        for m in (3,4):
            for c in (0,1):
                r=encrypt_boundary(LIB,method=m,compression=c)
                self.assertEqual(r['return'],-31);self.assertTrue(r['output_unchanged'])
    def test_zero_and_short_capacities_are_errors_before_copy(self):
        for cap,expected in ((0,-2),(4,-21)):
            r=encrypt_boundary(LIB,capacity=cap)
            self.assertEqual(r['return'],expected);self.assertTrue(r['output_unchanged'])

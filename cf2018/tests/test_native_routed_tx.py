import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_routed_tx import routed_tx
LIB=os.environ.get('CF18_APOLLO_LIBRARY')
class BoundsTests(unittest.TestCase):
    def test_bounds_before_source(self):
        with self.assertRaises(ValueError):routed_tx('absent',bytes(66))

@unittest.skipUnless(LIB,'private pinned Apollo/native dependencies required')
class NativeRoutedTests(unittest.TestCase):
    def test_actual_pre_encrypt_prefix_and_payload(self):
        for p in (b'X',bytes(range(64))):
            r=routed_tx(LIB,p)
            self.assertEqual(r['return'],-77)
            self.assertEqual(r['header_type'],0x4013)
            self.assertEqual(r['base_marker'],0x4366)
            self.assertEqual(r['compression_flag'],0)
            self.assertEqual(r['before_encrypt_send'],{'length':len(p)+4,
                'prefix_matches_big_endian_uid':True,'payload_preserved':True})
    def test_state4_cannot_submit(self):
        r=routed_tx(LIB,b'X',state=4);self.assertEqual(r['return'],-8);self.assertFalse(r['before_encrypt_send'])
    def test_uninitialized_cannot_submit(self):
        self.assertEqual(routed_tx(LIB,b'X',initialized=False)['return'],-4)
    def test_payload_limit_before_submission(self):
        self.assertEqual(routed_tx(LIB,bytes(65))['return'],-16)
    def test_negative_timeout_before_submission(self):
        self.assertEqual(routed_tx(LIB,b'X',timeout=-1)['return'],-2)
    def test_route_requiring_missing_pointer_before_submission(self):
        self.assertEqual(routed_tx(LIB,b'X',route_type=1)['return'],-2)

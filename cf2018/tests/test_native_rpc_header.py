import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_rpc_header import binary_header
LIB=os.environ.get('CF18_APOLLO_LIBRARY')
class BoundsTests(unittest.TestCase):
    def test_refuse_unbounded_name_before_source(self):
        with self.assertRaises(ValueError):binary_header('absent',method='unknown')

@unittest.skipUnless(LIB,'private pinned Apollo/native dependencies required')
class NativeHeaderTests(unittest.TestCase):
    def test_native_legacy_exact_bytes_and_u64_order(self):
        for method in ('QueryAddrInfo','ReqUpdateVersion','GetUpdateInfo'):
            for seq in (0,0x0102030405060708,2**64-1):
                r=binary_header(LIB,method=method,sequence=seq)
                b=method.encode('ascii')
                expected=len(b).to_bytes(4,'big')+b+b'\1'+seq.to_bytes(8,'big')
                self.assertEqual(r['wire'],expected)
                self.assertEqual(r['return'],len(expected))
    def test_actual_strict_branch_is_distinct(self):
        r=binary_header(LIB,strict=True,sequence=0)
        b=b'QueryAddrInfo'
        self.assertEqual(r['wire'],b'\x80\1\0\1'+len(b).to_bytes(4,'big')+b+bytes(8))
        self.assertEqual(r['return'],len(r['wire']))
    def test_message_type_is_a_single_byte_on_legacy_path(self):
        for typ in (1,2,4):
            r=binary_header(LIB,message_type=typ)
            self.assertEqual(r['wire'][4+len('QueryAddrInfo')],typ)

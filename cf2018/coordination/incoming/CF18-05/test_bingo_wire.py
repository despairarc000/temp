import unittest
from bingo_contract import inspect_body, BodyStructureError
from bingo_wire import (WAIT,BINGO,WaitFields,RelayFields,BingoFields,
                        BodyEncodingError,wait_body,bingo_body,varuint,varint64)

class Tests(unittest.TestCase):
    def setUp(self):
        self.wait=WaitFields(2,5,60)
        self.relay=RelayFields(0,b'A'*16,123456,-1)
        self.bingo=BingoFields(self.relay,0,4096)
    def test_native_wait_vector(self):
        p=wait_body(self.wait)
        self.assertEqual(p,b'\xaa\x00\x00\x00\x12'+bytes.fromhex('a5800c0000000610022005303c'))
        self.assertEqual(inspect_body(WAIT,p)['field_count'],3)
    def test_native_bingo_shape(self):
        p=bingo_body(self.bingo)
        self.assertEqual(p[:5],b'\xaa'+len(p).to_bytes(4,'big'))
        self.assertEqual(inspect_body(BINGO,p)['field_count'],3)
        self.assertIn(bytes.fromhex('2500000010')+b'A'*16,p)
        self.assertIn(bytes.fromhex('4001'),p)
    def test_zigzag_signed(self):
        for signed,encoded in [(0,b'\x00'),(-1,b'\x01'),(1,b'\x02'),
                               (-2,b'\x03'),(-(1<<63),b'\xff'*9+b'\x01'),
                               ((1<<63)-1,b'\xfe'+b'\xff'*8+b'\x01')]:
            self.assertEqual(varint64(signed),encoded)
    def test_header_body_mismatch_rejected(self):
        a,b=wait_body(self.wait),bingo_body(self.bingo)
        for outer,other in [(WAIT,b),(BINGO,a)]:
            with self.assertRaisesRegex(BodyStructureError,'mismatch'):
                inspect_body(outer,other)
    def test_body_length_exact(self):
        for p in (wait_body(self.wait),bingo_body(self.bingo)):
            self.assertEqual(int.from_bytes(p[1:5],'big'),len(p))
    def test_missing_relay_identity(self):
        with self.assertRaisesRegex(BodyEncodingError,'identity'):
            bingo_body(BingoFields(RelayFields(0,b'',1,1),0,0))
    def test_cannot_invent_fields(self):
        for x in (None,0,{},WaitFields(0,-1,5)):
            with self.assertRaises(BodyEncodingError):wait_body(x)
        for x in (None,0,{},BingoFields(None,0,0)):
            with self.assertRaises(BodyEncodingError):bingo_body(x)
    def test_limits_and_types(self):
        bads=[RelayFields(-1,b'A'*16,1,1),RelayFields(0,b'A'*16,-1,1),
              RelayFields(0,b'A'*16,1,1<<63),RelayFields(0,b'A'*16,1,-(1<<63)-1)]
        for r in bads:
            with self.subTest(r=r),self.assertRaises(BodyEncodingError):
                bingo_body(BingoFields(r,0,0))
        for args in [(self.relay,256,0),(self.relay,0,1<<32),(self.relay,True,0)]:
            with self.assertRaises(BodyEncodingError):bingo_body(BingoFields(*args))
    def test_varuint_bounds(self):
        for v in (-1,1<<64,True,1.2):
            with self.assertRaises(BodyEncodingError):varuint(v)
    def test_unsigned_fields(self):
        self.assertIn(bytes.fromhex('30c0c407'),bingo_body(self.bingo))
    def test_signed_extremes(self):
        for n in (-(1<<63),-1000,-1,0,1,1000,(1<<63)-1):
            p=bingo_body(BingoFields(RelayFields(0,b'A'*16,0,n),0,0))
            self.assertEqual(inspect_body(BINGO,p)['field_count'],3)
    def test_small_no_network(self):
        self.assertLess(len(bingo_body(self.bingo)),256)
        self.assertLess(len(wait_body(self.wait)),100)
    def test_no_network_dependency(self):
        import inspect,bingo_wire
        s=inspect.getsource(bingo_wire)
        for forbidden in ('import socket','sendall(', 'connect(', 'token=','password='):
            self.assertNotIn(forbidden,s)

if __name__=='__main__':
    unittest.main()

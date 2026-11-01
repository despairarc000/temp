"""R030: a TGCP packet sequence must not be blindly prepended to the RPC reader.

Synthetic offline controls ONLY. This does not establish the real server
envelope or whether native TGCP leaves a sequence word in delivered data.
"""
import hashlib,os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from address_response_gate import parse_response,ResponseError
from test_address_response_gate import fixture

class Tests(unittest.TestCase):
    def test_qualified_message_parses_as_exact_application_bytes(self):
        body=fixture(method='QueryAddrSvr:QueryAddrInfo',seq=0x100000001)
        parsed=parse_response(body)
        self.assertEqual((parsed.sequence,parsed.message_type),
                         (0x100000001,2))
    def test_prepend_tgcp_sequence_is_not_valid_rpc_at_offset_zero(self):
        for method in ('QueryAddrInfo','QueryAddrSvr:QueryAddrInfo'):
            raw=fixture(method=method,seq=0x100000001)
            for packet_sequence in (1,2,7,255):
                with self.subTest(method=method,packet_seq=packet_sequence):
                    with self.assertRaises(ResponseError):
                        parse_response(packet_sequence.to_bytes(4,'big')+raw)
    def test_rpc64_not_tgcp32_even_without_transport_word(self):
        x=parse_response(fixture(seq=0x100000001))
        self.assertNotEqual(x.sequence,1)
    def test_private_original_parser_crosscheck_if_available(self):
        root=os.getenv('CF18_V38_SOURCE')
        if not root:self.skipTest('private V3.8 original parser not supplied')
        source=Path(root)/'apollo_wire.py'
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         '9f02c98d34bf781756e04383af013f9ca1d883071ad708dd10d19f20d0032011')
        sys.path.insert(0,str(Path(root)))
        from apollo_wire import _parse_rpc_at,BadWireData,NeedMoreData
        for method in ('QueryAddrInfo','QueryAddrSvr:QueryAddrInfo'):
            body=fixture(method=method,seq=0x100000001)
            msg=_parse_rpc_at(body,0)
            self.assertEqual((msg.method,msg.message_type,msg.end),(method,2,len(body)))
            with self.assertRaises((BadWireData,NeedMoreData)):
                _parse_rpc_at(b'\0\0\0\1'+body,0)

if __name__=='__main__':unittest.main()

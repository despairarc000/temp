"""All inputs are independent synthetic offline frames; never a live reply."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from inbound_4013_reply_preflight import inspect_inbound_4013_reply
from test_address_response_gate import fixture

def vi(n):
    out=bytearray()
    while n>=128:
        out.append((n&127)|128);n>>=7
    return bytes(out)+bytes([n])

def tlv(number,kind,value):
    tag=vi(number<<4|kind)
    if kind==5:return tag+len(value).to_bytes(4,'big')+value
    if kind==1:return tag+bytes([value])
    if kind==0:return tag+vi(value)
    raise ValueError('fixture field kind')

def frame(body,*,compression=0,variant=0x4013,include_route=True):
    base=tlv(1,1,0x66) if False else b'\x11'+vi(0x4366)+b'\x91\x01'+vi(len(body))
    head=tlv(1,1,compression)+tlv(2,1,0)+tlv(3,1,1)
    if include_route:
        head+=tlv(4,5,tlv(4,5,tlv(1,5,b'QueryAddrSvr')))
    ext=tlv(variant,5,head)
    header=tlv(1,5,base)+tlv(2,5,ext)
    return b'\xaa'+(5+len(header)).to_bytes(4,'big')+header+body

class Tests(unittest.TestCase):
    def test_strict_known_4013_candidate_is_offline_only(self):
        body=fixture(method='QueryAddrSvr:QueryAddrInfo',seq=0x100000001)
        result=inspect_inbound_4013_reply(frame(body),{0x100000001})
        self.assertEqual(result,'STRUCTURAL_CANDIDATE_ONLY_NOT_GAME_ACCEPTANCE')

    def test_rpc64_must_match_pending_session_not_tgcp_seq(self):
        body=fixture(method='QueryAddrSvr:QueryAddrInfo',seq=0x100000001)
        self.assertEqual(inspect_inbound_4013_reply(frame(body),{1}),
                         'REJECT_NO_PENDING_SEQUENCE')

    def test_do_not_prepend_four_byte_sequence_to_rpc(self):
        body=fixture(method='QueryAddrSvr:QueryAddrInfo',seq=0x100000001)
        self.assertEqual(inspect_inbound_4013_reply(
            frame(b'\x00\x00\x00\x01'+body),{0x100000001}),'INVALID_RPC_RESPONSE')

    def test_unsupported_compression_refused(self):
        body=fixture(method='QueryAddrSvr:QueryAddrInfo')
        self.assertEqual(inspect_inbound_4013_reply(frame(body,compression=1),{7}),
                         'UNSUPPORTED_COMPRESSION_MODE')

    def test_other_extension_and_missing_route_rejected(self):
        body=fixture(method='QueryAddrSvr:QueryAddrInfo')
        for opts in ({'variant':0x5001},{'include_route':False}):
            with self.subTest(opts=opts):
                self.assertEqual(inspect_inbound_4013_reply(frame(body,**opts),{7}),
                                 'INBOUND_DATAHEAD_NOT_RECOGNIZED')

    def test_bad_frame_or_short_frame_is_not_positive(self):
        body=fixture(method='QueryAddrSvr:QueryAddrInfo')
        valid=frame(body)
        self.assertEqual(inspect_inbound_4013_reply(b'C'+valid[1:],{7}),
                         'INVALID_TGCP_FRAMING')
        self.assertEqual(inspect_inbound_4013_reply(valid[:-1],{7}),
                         'INVALID_TGCP_FRAMING')
        self.assertEqual(inspect_inbound_4013_reply(b'\xaa',{7}),'NOT_COMPARABLE')

    def test_no_network_and_invalid_pending_metadata(self):
        import inspect,inbound_4013_reply_preflight as module
        source=inspect.getsource(module)
        for banned in ('import socket','connect(','.send(','.listen('):
            self.assertNotIn(banned,source)
        with self.assertRaises(ValueError):
            inspect_inbound_4013_reply(frame(fixture()),{True})

if __name__=='__main__':unittest.main()

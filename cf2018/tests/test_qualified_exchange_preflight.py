"""Synthetic-only controls: never a live CrossFire response or packet."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from qualified_exchange_preflight import inspect_qualified_exchange, RPC_SEQUENCE_OFFSET
from test_qualified_address_request import candidate
from test_address_response_gate import fixture


def request_with_rpc_sequence(rpc_seq=0x100000001):
    raw=candidate(3)
    return raw[:RPC_SEQUENCE_OFFSET]+rpc_seq.to_bytes(8,'big')+raw[RPC_SEQUENCE_OFFSET+8:]


def reply(rpc_seq, method='QueryAddrSvr:QueryAddrInfo',**kwargs):
    return fixture(seq=rpc_seq,method=method,**kwargs)


class QualifiedExchangePreflightTests(unittest.TestCase):
    def test_distinguishes_rpc64_from_tgcp32(self):
        req=request_with_rpc_sequence(0x100000001)
        self.assertEqual(inspect_qualified_exchange(req,1,reply(0x100000001)),
                         'STRUCTURAL_CANDIDATE_ONLY_NOT_GAME_ACCEPTANCE')
        # Four-byte TGCP packet sequence is 1, but full RPC sequence != 1.
        self.assertEqual(inspect_qualified_exchange(req,1,reply(1)),
                         'REJECT_NO_PENDING_SEQUENCE')

    def test_bare_and_qualified_response_names_are_structural_not_accepted(self):
        req=request_with_rpc_sequence(37)
        for name in ('QueryAddrInfo','QueryAddrSvr:QueryAddrInfo'):
            with self.subTest(name=name):
                self.assertEqual(inspect_qualified_exchange(req,1,reply(37,method=name)),
                                 'STRUCTURAL_CANDIDATE_ONLY_NOT_GAME_ACCEPTANCE')

    def test_missing_native_reason_rejected(self):
        req=request_with_rpc_sequence(37)
        self.assertEqual(inspect_qualified_exchange(req,1,reply(37,reason=None)),
                         'REPLY_NOT_STRUCTURALLY_VALID')

    def test_wrong_message_type_rejected(self):
        req=request_with_rpc_sequence(37)
        self.assertEqual(inspect_qualified_exchange(req,1,reply(37,msgtype=1)),
                         'REPLY_NOT_STRUCTURALLY_VALID')

    def test_result_and_endpoint_are_not_success(self):
        req=request_with_rpc_sequence(37)
        self.assertEqual(inspect_qualified_exchange(req,1,reply(37,result=7)),
                         'REJECT_RESPONSE_RESULT')
        self.assertEqual(inspect_qualified_exchange(req,1,reply(37,addr=())),
                         'WAIT_NO_ADDRESS_CANDIDATES')

    def test_incorrect_request_or_bad_sequence_never_accepted(self):
        req=request_with_rpc_sequence(37)
        self.assertEqual(inspect_qualified_exchange(req,2,reply(37)),
                         'REQUEST_NOT_RECOGNIZED')
        self.assertEqual(inspect_qualified_exchange(req[:-1],1,reply(37)),
                         'REQUEST_NOT_RECOGNIZED')

    def test_rejects_nonbytes_and_oversized_data(self):
        req=request_with_rpc_sequence(37)
        for request,sequence,rsp in ((bytearray(req),1,reply(37)),
                                    (req,True,reply(37)),(req,-1,reply(37)),
                                    (req,1,b'A'*8193),(req,1,bytearray(reply(37)))):
            with self.assertRaises(ValueError):
                inspect_qualified_exchange(request,sequence,rsp)


if __name__=='__main__':
    unittest.main()

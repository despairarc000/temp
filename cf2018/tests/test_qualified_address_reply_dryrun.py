"""Offline synthetic controls. Deliberately no TGCP serializer or network send."""
import inspect
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
import qualified_address_reply_dryrun as dryrun
from address_response_gate import parse_response, assess_response
from qualified_exchange_preflight import inspect_qualified_exchange
from test_qualified_address_request import candidate


def request(rpc_seq=0x100000001):
    raw = candidate(3)
    offset = dryrun.RPC_SEQUENCE_OFFSET
    return raw[:offset] + rpc_seq.to_bytes(8, 'big') + raw[offset+8:]


class DryRunTests(unittest.TestCase):
    def test_full_rpc64_reply_is_structurally_correlated(self):
        req = request()
        reply = dryrun.candidate_reply(req, 1)
        parsed = parse_response(reply)
        self.assertEqual(parsed.sequence, 0x100000001)
        self.assertEqual(parsed.message_type, 2)
        self.assertEqual(parsed.method, 'QueryAddrSvr:QueryAddrInfo')
        self.assertEqual(parsed.result, 0)
        self.assertTrue(parsed.reason_present)
        self.assertEqual(parsed.addresses, (('127.0.0.1', 9080),))
        self.assertEqual(inspect_qualified_exchange(req, 1, reply),
                         'STRUCTURAL_CANDIDATE_ONLY_NOT_GAME_ACCEPTANCE')

    def test_rpc64_is_not_packet_sequence(self):
        req = request(0x100000001)
        reply = dryrun.candidate_reply(req, 1)
        self.assertNotEqual(parse_response(reply).sequence, 1)
        self.assertEqual(assess_response(parse_response(reply),
                          pending_sequences={1}), 'REJECT_NO_PENDING_SEQUENCE')

    def test_source_is_synthetic_only_without_network_operations(self):
        source = inspect.getsource(dryrun)
        self.assertNotIn('import socket', source)
        self.assertNotIn('connect(', source)
        self.assertNotIn('send(', source)
        self.assertNotIn('open(', source)

    def test_rejects_external_host(self):
        for host in ('8.8.8.8', '192.0.2.1', 'example.net', '::1'):
            with self.subTest(host=host), self.assertRaises(ValueError):
                dryrun.candidate_reply(request(), 1, host=host)

    def test_rejects_incorrect_port(self):
        for port in (-1, 0, 65536, True, '9080'):
            with self.subTest(port=port), self.assertRaises(ValueError):
                dryrun.candidate_reply(request(), 1, port=port)

    def test_rejects_wrong_request_or_sequence(self):
        with self.assertRaises(ValueError):
            dryrun.candidate_reply(request(), 2)
        with self.assertRaises(ValueError):
            dryrun.candidate_reply(request()[:-1], 1)

    def test_explicit_loopback_port_preserved(self):
        reply = dryrun.candidate_reply(request(37), 1, host='127.0.0.2', port=2080)
        self.assertEqual(parse_response(reply).addresses, (('127.0.0.2', 2080),))


if __name__ == '__main__':
    unittest.main()

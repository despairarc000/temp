import unittest
from addr_response_gate import parse_response, assess_response, ResponseError

def i16(x): return x.to_bytes(2, 'big', signed=True)
def i32(x): return x.to_bytes(4, 'big', signed=True)
def i64(x): return x.to_bytes(8, 'big', signed=False)
def field(t, n): return bytes([t]) + i16(n)
def ss(value):
    data = value.encode()
    return i32(len(data)) + data

def fixture(seq=7, result=0, addr=(('127.0.0.1', 9080),), msgtype=2,
            method='QueryAddrInfo', success=True, reason=''):
    body = b''
    if success:
        body = field(8, 1) + i32(result)
        if reason:
            body += field(11, 2) + ss(reason)
        body += field(15, 3) + bytes([12]) + i32(len(addr))
        for host, port in addr:
            body += field(11, 1) + ss(host) + field(8, 2) + i32(port) + b'\0'
        body += b'\0'
        body = field(12, 0) + body
    return ss(method) + bytes([msgtype]) + i64(seq) + body + b'\0'

class Tests(unittest.TestCase):
    def test_valid_laboratory_structure_is_only_candidate(self):
        item = parse_response(fixture())
        self.assertEqual((item.method, item.message_type, item.sequence, item.result),
                         ('QueryAddrInfo', 2, 7, 0))
        self.assertEqual(item.addresses, (('127.0.0.1', 9080),))
        self.assertEqual(assess_response(item, pending_sequences={7}),
                         'STRUCTURAL_CANDIDATE_ONLY_NOT_GAME_ACCEPTANCE')
    def test_unmatched_sequence(self):
        self.assertEqual(assess_response(parse_response(fixture()), pending_sequences={8}),
                         'REJECT_NO_PENDING_SEQUENCE')
    def test_nonzero_response_result(self):
        self.assertEqual(assess_response(parse_response(fixture(result=-3)), pending_sequences={7}),
                         'REJECT_RESPONSE_RESULT')
    def test_empty_addresses_not_proven_accepted(self):
        self.assertEqual(assess_response(parse_response(fixture(addr=())), pending_sequences={7}),
                         'WAIT_NO_ADDRESS_CANDIDATES')
    def test_message_type_invalid(self):
        with self.assertRaisesRegex(ResponseError, 'not an RPC reply'):
            parse_response(fixture(msgtype=1))
    def test_method_invalid(self):
        with self.assertRaisesRegex(ResponseError, 'unexpected method'):
            parse_response(fixture(method='Other'))
    def test_success_wrapper_absent(self):
        with self.assertRaisesRegex(ResponseError, 'missing success'):
            parse_response(fixture(success=False))
    def test_input_truncated_each_offset(self):
        payload = fixture()
        for n in range(len(payload)):
            with self.subTest(n=n), self.assertRaises(ResponseError):
                parse_response(payload[:n])
    def test_unrelated_port(self):
        item = parse_response(fixture(addr=(('127.0.0.1', 0),)))
        self.assertEqual(assess_response(item, pending_sequences={7}), 'REJECT_PORT_POLICY')
    def test_string_cap(self):
        with self.assertRaisesRegex(ResponseError, 'string exceeds'):
            parse_response(i32(999999) + b'A' * 6)
    def test_list_cap(self):
        with self.assertRaisesRegex(ResponseError, 'invalid addresses'):
            parse_response(fixture(addr=tuple(('127.0.0.1', 9080) for _ in range(33))))
    def test_extra_trailing(self):
        with self.assertRaisesRegex(ResponseError, 'trailing data'):
            parse_response(fixture() + b'\0')
    def test_duplicate_result_field(self):
        payload = fixture()
        offset = len(ss('QueryAddrInfo')) + 1 + 8 + 3
        bad = payload[:offset] + field(8, 1) + i32(0) + payload[offset:]
        with self.assertRaisesRegex(ResponseError, 'duplicate'):
            parse_response(bad)
    def test_no_network_dependency(self):
        import inspect, addr_response_gate
        source = inspect.getsource(addr_response_gate)
        self.assertNotIn('import socket', source)
        self.assertNotIn('connect(', source)

if __name__ == '__main__':
    unittest.main()

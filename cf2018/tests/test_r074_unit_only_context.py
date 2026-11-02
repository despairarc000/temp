"""R074 source-free, value-free classification controls.

All frames are synthetic and never reach a socket. Negative controls prove
non-unit changes cannot be labeled as route+unit-only.
"""
import sys
import unittest
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / "experiments")]
from r074_unit_only_context import route_unit_context_label as classify


def vi(n):
    out = bytearray()
    while n >= 128:
        out.append((n & 127) | 128)
        n >>= 7
    return bytes(out) + bytes([n])


def nest(n, payload):
    return vi((n << 4) | 5) + len(payload).to_bytes(4, "big") + payload


def mock_syn(name=b"QueryAddrSvr", *, unit=1, security=b"K"*20,
             client_type=None, base_extra=0, kind_unit=0):
    base = (b"\x10" + vi(0x4366) + b"\x40" + vi(0x1001) + b"\x61\x00"
            + vi(9 << 4) + b"\x00\x50" + vi(base_extra))
    route = nest(4, nest(1, name))
    syn = nest(1, security)
    if kind_unit == 0:
        syn += vi(5 << 4) + vi(unit)
    else:
        syn += vi((5 << 4) | 1) + bytes([unit])
    if client_type is not None:
        syn += vi((6 << 4) | 0) + vi(client_type)
    syn += nest(14, route)
    target = 121 + len(name) - 7
    used = len(nest(1, base) + nest(2, nest(0x1001, syn)))
    padding = target - used - len(nest(15, b""))
    if padding < 0:
        raise ValueError("synthetic target overflow")
    syn += nest(15, b"P" * padding)
    head = nest(1, base) + nest(2, nest(0x1001, syn))
    result = b"\x43\x66\xaa" + (5 + len(head)).to_bytes(4, "big") + head
    expected_len = 133 if name == b"QueryAddrSvr" else 131
    assert len(result) == expected_len
    return result


class Tests(unittest.TestCase):
    def setUp(self):
        self.ref = mock_syn()
        self.next_unit3 = mock_syn(b"SECOND1234", unit=3)

    def test_route_and_unit_only(self):
        self.assertEqual(classify(self.next_unit3, self.ref),
                         "ROUTE_AND_UNIT_FIELD5_ONLY")

    def test_other_one_byte_unit_value_matches(self):
        self.assertEqual(classify(mock_syn(b"SECOND1234", unit=7), self.ref),
                         "ROUTE_AND_UNIT_FIELD5_ONLY")

    def test_just_route_is_separate(self):
        self.assertEqual(classify(mock_syn(b"SECOND1234"), self.ref),
                         "ROUTE_ONLY_MATCH")

    def test_new_security_fails(self):
        self.assertEqual(classify(mock_syn(b"SECOND1234", unit=3,
                                           security=b"Z"*20), self.ref),
                         "REFUSED")

    def test_changed_base_fails(self):
        self.assertEqual(classify(mock_syn(b"SECOND1234", unit=3,
                                           base_extra=1), self.ref),
                         "REFUSED")

    def test_client_type_difference_fails(self):
        a = mock_syn(client_type=101)
        b = mock_syn(b"SECOND1234", unit=3, client_type=102)
        self.assertEqual(classify(b, a), "REFUSED")

    def test_unit_type_difference_fails(self):
        self.assertEqual(classify(mock_syn(b"SECOND1234", unit=3,
                                           kind_unit=1), self.ref),
                         "REFUSED")

    def test_different_encoded_unit_width_fails(self):
        self.assertEqual(classify(mock_syn(b"SECOND1234", unit=128), self.ref),
                         "REFUSED")

    def test_wrong_name_length_fails(self):
        self.assertEqual(classify(mock_syn(b"SECOND1234")[:-1], self.ref),
                         "REFUSED")

    def test_wrong_reference_fails(self):
        self.assertEqual(classify(self.next_unit3, self.next_unit3), "REFUSED")

    def test_wrong_types_fail(self):
        self.assertEqual(classify(None, self.ref), "REFUSED")
        self.assertEqual(classify(bytearray(self.next_unit3), self.ref), "REFUSED")

    def test_no_private_values_in_label(self):
        label = classify(self.next_unit3, self.ref)
        for secret in ("SECOND1234", "QueryAddrSvr", "unit=3", "K"*20):
            self.assertNotIn(secret, label)

    def test_no_ack_or_network_code(self):
        text = (Path(__file__).resolve().parents[1] /
                "experiments/r074_unit_only_context.py").read_text()
        for banned in ("socket.", "sendall(", "write(", "asyncio", "create_server"):
            self.assertNotIn(banned, text)


if __name__ == "__main__":
    unittest.main()

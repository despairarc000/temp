"""R056 fail-closed next-service dispatch: synthetic fixtures only."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from r056_second_service_syn import first_syn_decision


def varuint(value):
    out = bytearray()
    while True:
        b = value & 127
        value >>= 7
        out.append(b | (128 if value else 0))
        if not value:
            return bytes(out)


def nested(field, payload):
    return varuint((field << 4) | 5) + len(payload).to_bytes(4, "big") + payload


def scalar(field, value):
    return varuint((field << 4) | 1) + varuint(value)


def fixture(name=b"QueryAddrSvr", *, syn_type=0x1001, route_kind=4,
            add_second_route=False, have_route=True, body=b""):
    base = scalar(1, 0x4366) + scalar(9, len(body))
    # Synthetic minimal nested route shape: this is NOT an original SYN.
    syn = scalar(1, 1)
    if have_route:
        data = nested(route_kind, nested(1, name))
        syn += nested(14, data)
        if add_second_route:
            syn += nested(14, data)
    outer = nested(1, base) + nested(2, nested(syn_type, syn))
    h = b"\xaa" + (5 + len(outer)).to_bytes(4, "big") + outer
    return b"\x43\x66" + h + body


class Tests(unittest.TestCase):
    def test_known_reference_must_still_pass_existing_exact_gate(self):
        self.assertEqual(first_syn_decision(fixture()),
            ("REFERENCE_NAMED_ROUTE_CANDIDATE", "DEFER_TO_PINNED_REFERENCE_GATE"))

    def test_different_ten_byte_route_never_auto_acks(self):
        self.assertEqual(first_syn_decision(fixture(b"SERVICE123")),
            ("TEN_BYTE_NAMED_ROUTE_CANDIDATE", "HOLD_NO_ACK"))

    def test_other_name_is_not_second_service_proof(self):
        self.assertEqual(first_syn_decision(fixture(b"ABCDE")),
                         ("OTHER_NAMED_ROUTE", "HOLD_NO_ACK"))

    def test_other_12_byte_name_not_reference(self):
        self.assertEqual(first_syn_decision(fixture(b"OTHERROUTE12")),
                         ("OTHER_NAMED_ROUTE", "HOLD_NO_ACK"))

    def test_malformed_and_wrong_extension_fail_closed(self):
        examples = [
            fixture(syn_type=0x1002), fixture(have_route=False),
            fixture(route_kind=1), fixture(add_second_route=True),
            fixture()[:-1], fixture() + b"TRAILING",
            b"\x43\x66" + fixture()[2:6],
            fixture().replace(b"\x43\x66", b"\x00\x00", 1),
            fixture(b""),
        ]
        for wire in examples:
            with self.subTest(length=len(wire)):
                self.assertEqual(first_syn_decision(wire),
                         ("UNRECOGNIZED_OR_INCOMPLETE_SYN", "NO_ACK"))

    def test_route_with_body_is_not_syn_only(self):
        self.assertEqual(first_syn_decision(fixture(body=b"test")),
                         ("UNRECOGNIZED_OR_INCOMPLETE_SYN", "NO_ACK"))

    def test_input_type_and_size_budget(self):
        for sample in (None, 8, bytearray(fixture()), b"x" * 1025):
            with self.subTest(sample_type=type(sample).__name__):
                self.assertEqual(first_syn_decision(sample),
                         ("UNRECOGNIZED_OR_INCOMPLETE_SYN", "NO_ACK"))

    def test_no_identifier_route_or_raw_bytes_in_labels(self):
        private = b"SECRET1234"
        output = first_syn_decision(fixture(private))
        self.assertEqual(output[1], "HOLD_NO_ACK")
        for token in ("SECRET", "1234", "QueryAddrSvr"):
            self.assertNotIn(token, repr(output))

    def test_original_reference_is_not_inferred_from_size_alone(self):
        fake = b"\x43\x66\xaa" + b"\x00" * (133 - 3)
        self.assertEqual(first_syn_decision(fake)[1], "NO_ACK")

    def test_source_only_no_listener_or_side_effects(self):
        wire = fixture(b"SERVICE123")
        before = bytes(wire)
        for _ in range(10):
            self.assertEqual(first_syn_decision(wire)[1], "HOLD_NO_ACK")
        self.assertEqual(wire, before)


if __name__ == "__main__":
    unittest.main()

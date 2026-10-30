"""Offline characterization of the existing hypothesis model's limits.

These tests deliberately show what a two-byte predicate cannot establish.
No fixture is an authentic packet or a proposed TGCP ACK.
Run from cf2018: python -m unittest discover -s coordination/incoming/CF18-01 -v
"""
from pathlib import Path
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "cf18_prefix_model_under_audit", ROOT / "experiments/frame_gate.py"
)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class PrefixModelLimits(unittest.TestCase):
    def test_entire_two_byte_domain_accepts_only_candidate(self):
        accepted = [
            n.to_bytes(2, "big").hex()
            for n in range(65536)
            if gate.first_native_gate(n.to_bytes(2, "big"))["passes"]
        ]
        self.assertEqual(accepted, ["6643"])

    def test_all_inputs_shorter_than_two_bytes_fail(self):
        self.assertFalse(gate.first_native_gate(b"")["passes"])
        for byte in range(256):
            with self.subTest(byte=byte):
                self.assertFalse(gate.first_native_gate(bytes([byte]))["passes"])

    def test_prefix_alone_passes_without_header_or_body(self):
        self.assertTrue(gate.first_native_gate(b"\x66\x43")["passes"])

    def test_suffix_content_and_size_cannot_affect_result(self):
        baseline = gate.first_native_gate(b"\x66\x43")
        # Independent arbitrary data; no assumed TGCP length-field layout.
        suffixes = [b"\x00", b"\xff", b"not-a-header", bytes(range(256))]
        suffixes += [b"\x00" * n for n in (2, 5, 63, 64, 65, 4096)]
        for suffix in suffixes:
            with self.subTest(size=len(suffix)):
                self.assertEqual(gate.first_native_gate(b"\x66\x43" + suffix), baseline)

    def test_fragmented_prefix_has_no_reassembly_state(self):
        self.assertFalse(gate.first_native_gate(b"\x66")["passes"])
        self.assertFalse(gate.first_native_gate(b"\x43")["passes"])
        self.assertTrue(gate.first_native_gate(b"\x66" + b"\x43")["passes"])

    def test_coalesced_data_yields_no_boundary_decision(self):
        first = b"\x66\x43" + b"synthetic-first"
        trailing = b"\x43\x66" + b"synthetic-second"
        self.assertEqual(gate.first_native_gate(first + trailing), gate.first_native_gate(first))
        self.assertFalse(gate.first_native_gate(trailing)["passes"])
        self.assertNotIn("consumed", gate.first_native_gate(first + trailing))

    def test_mutator_preserves_even_arbitrary_nonframe_suffixes(self):
        for suffix in (b"hello", b"\x00" * 63, b"\xff" * 4096):
            with self.subTest(size=len(suffix)):
                old = b"\x43\x66" + suffix
                changed = gate.prefix_only_candidate(old)
                self.assertEqual(changed, b"\x66\x43" + suffix)
                self.assertEqual(len(changed), len(old))
                self.assertTrue(gate.first_native_gate(changed)["passes"])

    def test_mutator_rejects_short_and_wrong_prefix_controls(self):
        for size in range(2, 7):
            with self.subTest(size=size):
                with self.assertRaises(ValueError):
                    gate.prefix_only_candidate(b"\x43\x66" + b"\x00" * (size - 2))
        for data in (b"", b"\x43", b"\x66\x43hello", b"\x00\x00hello"):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    gate.prefix_only_candidate(data)


if __name__ == "__main__":
    unittest.main()

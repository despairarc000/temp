"""Offline synthetic checks for the R076 fixed-label route comparison."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"experiments"), str(ROOT/"tests")]
from test_second_service_syn_gate import make
from r076_private_route_equality import classify_transient_frame, classify_against_original


class Tests(unittest.TestCase):
    def test_exact_equal_label(self):
        self.assertEqual(classify_transient_frame(make(b"ALPHA12345"), b"ALPHA12345"),
                         "CTDIR_STATIC_ROUTE_MATCH")

    def test_one_byte_difference_label(self):
        self.assertEqual(classify_transient_frame(make(b"ALPHA12346"), b"ALPHA12345"),
                         "CTDIR_STATIC_ROUTE_DIFFERENT")

    def test_reference_frame_refused(self):
        self.assertEqual(classify_transient_frame(make(), b"ALPHA12345"), "REFUSED")

    def test_short_expected_route_refused(self):
        self.assertEqual(classify_transient_frame(make(b"ALPHA12345"), b"SHORT"), "REFUSED")

    def test_truncated_frame_refused(self):
        self.assertEqual(classify_transient_frame(make(b"ALPHA12345")[:-1], b"ALPHA12345"),
                         "REFUSED")

    def test_invalid_frame_type_refused(self):
        self.assertEqual(classify_transient_frame(bytearray(make(b"ALPHA12345")), b"ALPHA12345"),
                         "REFUSED")

    def test_invalid_expected_type_refused(self):
        self.assertEqual(classify_transient_frame(make(b"ALPHA12345"), "ALPHA12345"),
                         "REFUSED")

    def test_labels_hide_comparison_data(self):
        for name in (b"ALPHA12345", b"ALPHA12346"):
            label = classify_transient_frame(make(name), b"ALPHA12345")
            self.assertNotIn("ALPHA12345", label)
            self.assertNotIn("ALPHA12346", label)

    def test_nonexistent_original_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(classify_against_original(make(b"ALPHA12345"),
                             Path(tmp)/"not_found.so"), "REFUSED")

    def test_wrong_original_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"test.so"
            p.write_bytes(b"test")
            self.assertEqual(classify_against_original(make(b"ALPHA12345"), p), "REFUSED")


if __name__ == "__main__":
    unittest.main()

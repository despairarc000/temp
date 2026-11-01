"""Synthetic full-shape counterexamples for the historical V3.8 report.

Historical metadata: body lengths 80/85, first change band 64..71,
shared suffix band 1..3, sequence-boundary and two method-policy labels.
Tests do NOT imply candidate structures were generated on a real phone.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from routed_body_diagnostic import diagnose_body, header_reason
from test_routed_nested_header_model import wrapped_candidate
from test_routed_label_implications import candidate_body


def shared_prefix(a, b):
    return next((i for i, (x, y) in enumerate(zip(a, b)) if x != y),
                min(len(a), len(b)))


def shared_suffix(a, b):
    return next((i for i, (x, y) in enumerate(zip(a[::-1], b[::-1])) if x != y),
                min(len(a), len(b)))


def change_last_service_character(b):
    """Synthetic STRING length stays fixed; only final character changes."""
    assert b[-2:] == b'\x00\x00' and b[-3] == 65
    return b[:-3] + b'B' + b[-2:]


def alternate_opaque_format(size):
    """Distinct opaque/wrapped layout, not legitimate native Thrift output."""
    src = candidate_body(size)
    # Invalid first method byte; separate fixed word inside argument payload,
    # not between packet sequence and method-length field.
    return src[:8] + b'\xff' + src[9:45] + b'\x00'*4 + src[45:]


class FullShapeEvidenceLimits(unittest.TestCase):
    def test_repeated_string_old_model_fails_short_suffix_band(self):
        a, b = (wrapped_candidate(n, 1) for n in (12, 17))
        self.assertEqual((len(a), len(b)), (80, 85))
        self.assertEqual(shared_prefix(a, b), 65)
        self.assertEqual(shared_suffix(a, b), 14)
        self.assertNotIn(shared_suffix(a, b), (1, 2, 3))

    def test_distinct_string_tail_repairs_suffix_without_changing_labels(self):
        a = wrapped_candidate(12, 1)
        b = change_last_service_character(wrapped_candidate(17, 1))
        self.assertEqual((len(a), len(b)), (80, 85))
        self.assertEqual((shared_prefix(a, b), shared_suffix(a, b)), (65, 2))
        for body in (a, b):
            d = diagnose_body(body, 1)
            self.assertEqual(d['sequence_prefix'], 'MATCH')
            self.assertEqual(d['legacy_at_start'], 'METHOD_BYTES_POLICY')
            self.assertEqual(d['legacy_after_sequence'], 'METHOD_BYTES_POLICY')
            self.assertEqual(header_reason(body, 8), 'LEGACY_HEADER_PLAUSIBLE')

    def test_distinct_opaque_layout_also_fits_all_old_bands(self):
        a = alternate_opaque_format(12)
        b = change_last_service_character(alternate_opaque_format(17))
        self.assertEqual((len(a), len(b)), (80, 85))
        self.assertEqual((shared_prefix(a, b), shared_suffix(a, b)), (65, 2))
        for body in (a, b):
            d = diagnose_body(body, 1)
            self.assertEqual(d['sequence_prefix'], 'MATCH')
            self.assertEqual(d['legacy_at_start'], 'METHOD_BYTES_POLICY')
            self.assertEqual(d['legacy_after_sequence'], 'METHOD_BYTES_POLICY')
            self.assertEqual(header_reason(body, 8), 'NAME_LENGTH_POLICY')

    def test_bad_field_word_is_not_new_observed_data(self):
        # The classifier never validates a whole message. These are only labels.
        a = alternate_opaque_format(12)
        self.assertEqual(diagnose_body(a[:-2] + b'\xff\xff', 1)['legacy_after_sequence'],
                         'METHOD_BYTES_POLICY')
        self.assertEqual(diagnose_body(a, 2)['sequence_prefix'], 'MISMATCH')


if __name__ == '__main__':
    unittest.main()

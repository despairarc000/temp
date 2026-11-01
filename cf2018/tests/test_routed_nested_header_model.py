"""Test a falsifiable extra-word hypothesis for the routed 0x4013 body.

All input is independently synthetic; no captured packets, credentials, game
binaries or client acceptance. A matching shape is not producer identification.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from routed_body_diagnostic import diagnose_body, header_reason
from test_routed_label_implications import candidate_body


def wrapped_candidate(service_size: int, word: int = 1) -> bytes:
    """Preserve sequence and RPC body; insert one unknown BE32 word between."""
    if type(word) is not int or not 0 <= word < 2**32:
        raise ValueError('synthetic uint32 only')
    base = candidate_body(service_size, strict=False)
    return base[:4] + word.to_bytes(4, 'big') + base[4:]


class ExtraWordModelTests(unittest.TestCase):
    def test_four_byte_shift_matches_all_reported_shape_labels(self):
        for word in (1, 3, 16, 64):
            bodies = [wrapped_candidate(n, word) for n in (12, 17)]
            self.assertEqual([len(b) for b in bodies], [80, 85])
            first_diff = next(i for i, pair in enumerate(zip(*bodies)) if pair[0] != pair[1])
            self.assertEqual(first_diff, 65)
            self.assertIn(first_diff, range(64, 72))
            for body in bodies:
                labels = diagnose_body(body, 1)
                self.assertEqual(labels['sequence_prefix'], 'MATCH')
                self.assertEqual(labels['legacy_at_start'], 'METHOD_BYTES_POLICY')
                self.assertEqual(labels['legacy_after_sequence'], 'METHOD_BYTES_POLICY')
                self.assertEqual(header_reason(body, 8), 'LEGACY_HEADER_PLAUSIBLE')

    def test_control_original_legacy_without_word_fails_to_match_phone_labels(self):
        unwrapped = candidate_body(16)
        self.assertEqual(len(unwrapped), 80)
        self.assertEqual(diagnose_body(unwrapped, 1)['legacy_after_sequence'],
                         'LEGACY_HEADER_PLAUSIBLE')

    def test_extra_word_must_look_like_small_name_length_to_match_phone_label(self):
        for word in (0, 65, 72, 77, 0x01020304):
            labels = diagnose_body(wrapped_candidate(12, word), 1)
            self.assertEqual(labels['legacy_after_sequence'], 'NAME_LENGTH_POLICY')
            self.assertEqual(header_reason(wrapped_candidate(12, word), 8),
                             'LEGACY_HEADER_PLAUSIBLE')

    def test_remaining_body_length_is_not_a_matching_extra_word(self):
        # For an 80/85-byte routed body, after the 4-byte sequence and proposed
        # 4-byte field there are 72/77 bytes. Both exceed the classifier's 64.
        for length, service_size in ((80, 12), (85, 17)):
            word = length - 8
            body = wrapped_candidate(service_size, word)
            self.assertEqual(len(body), length)
            self.assertEqual(diagnose_body(body, 1)['legacy_after_sequence'],
                             'NAME_LENGTH_POLICY')

    def test_mutating_extra_word_causes_early_difference(self):
        bodies = (wrapped_candidate(12, 1), wrapped_candidate(17, 2))
        first_diff = next(i for i, pair in enumerate(zip(*bodies)) if pair[0] != pair[1])
        self.assertEqual(first_diff, 7)
        # The observed long shared prefix is only modeled if this word is stable.

    def test_no_unvalidated_word_or_real_capture_required(self):
        for value in (-1, 2**32, True, 1.0):
            with self.assertRaises(ValueError):
                wrapped_candidate(12, value)


if __name__ == '__main__':
    unittest.main()

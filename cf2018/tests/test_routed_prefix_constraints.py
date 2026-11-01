"""Only independent synthetic bodies; no captured phone bytes or native execution."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from routed_prefix_constraints import fixed_classes
from routed_body_diagnostic import diagnose_body


def body_with_word(word, *, valid_header=False, length=80):
    seq = (1).to_bytes(4, 'big')
    if valid_header:
        # Independent header grammar; the body itself is NOT real phone data.
        header = len(b'QueryAddrInfo').to_bytes(4, 'big') + b'QueryAddrInfo' + b'\x01' + (1).to_bytes(8, 'big')
        prefix = seq + word.to_bytes(4, 'big') + header
    else:
        prefix = seq + word.to_bytes(4, 'big') + b'\xff'
    return prefix + bytes(length-len(prefix))


class ConstraintTests(unittest.TestCase):
    def test_all_64_small_words_require_exactly_three_leading_zero_bytes(self):
        for length in (80, 85):
            for n in range(1, 65):
                body = body_with_word(n, length=length)
                self.assertEqual(body[4:7], b'\0\0\0')
                labels = diagnose_body(body, 1)
                self.assertEqual(labels['legacy_after_sequence'], 'METHOD_BYTES_POLICY')
                self.assertEqual(labels['legacy_at_start'], 'METHOD_BYTES_POLICY')
                self.assertEqual(fixed_classes(body, 1)['word_after_sequence'], 'SMALL_BE32_1_TO_64')

    def test_8_offset_discriminates_a_four_byte_prefix_from_simple_wrong_width(self):
        raw = body_with_word(1, valid_header=True)
        self.assertEqual(fixed_classes(raw, 1)['original_after_sequence'], 'METHOD_BYTES_POLICY')
        self.assertEqual(fixed_classes(raw, 1)['header_after_sequence_word'], 'LEGACY_HEADER_PLAUSIBLE')
        other = raw[:8] + b'\x00' + raw[8:-1]
        self.assertEqual(fixed_classes(other, 1)['original_after_sequence'], 'METHOD_BYTES_POLICY')
        self.assertEqual(fixed_classes(other, 1)['header_after_sequence_word'], 'NAME_LENGTH_POLICY')

    def test_no_reply_recognition_or_plaintext_claim_from_header_only(self):
        raw = body_with_word(1, valid_header=True)
        changed = raw[:-2] + b'\xfd\xfa'
        self.assertEqual(fixed_classes(raw, 1), fixed_classes(changed, 1))
        self.assertEqual(fixed_classes(raw, 1)['interpretation'], 'STRUCTURAL_CLASSIFICATION_NOT_NATIVE_PRODUCER')

    def test_boundary_and_type_negatives(self):
        for n in (0, 65, 77, 0x80010001, 2**32-1):
            self.assertEqual(fixed_classes(body_with_word(n), 1)['word_after_sequence'], 'OTHER')
        self.assertEqual(fixed_classes(bytes(7), 1)['word_after_sequence'], 'SHORT')
        for body, seq in ((bytearray(9), 1), (b'A'*8193, 1), (b'A', True), (b'A', -1), (b'A', 2**32)):
            with self.assertRaises(ValueError):
                fixed_classes(body, seq)

    def test_uniform_ciphertext_null_three_prefix_is_rare_but_not_proof(self):
        # Exactly 64 allowed 32-bit values / 2^32 possible values.
        p = 64 / 2**32
        self.assertEqual(p, 1/67108864)
        # Shared long prefix between reported samples prevents assuming two
        # independent uniform draws; do NOT square the probability.
        self.assertGreater(p, 0)


if __name__ == '__main__':
    unittest.main()

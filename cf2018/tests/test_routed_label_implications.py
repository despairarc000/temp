"""Source-free, synthetic deductions from V3.8.1's bounded label semantics.

No actual phone payload, account, session, network access, or private game source.
This confirms what an observer LABEL implies; not the unseen underlying bytes.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from routed_body_diagnostic import diagnose_body


def query_args(service_size):
    """Independent synthetic grammar documented by original-native controls."""
    return (b'\x0c\x00\x01\x0a\x00\x01' + (1).to_bytes(8, 'big')
            + b'\x0a\x00\x02' + (2).to_bytes(8, 'big')
            + b'\x0b\x00\x03' + service_size.to_bytes(4, 'big')
            + b'A' * service_size + b'\x00\x00')


def candidate_body(service_size, strict=False):
    method = b'QueryAddrInfo'
    seq = 1
    if strict:
        header = b'\x80\x01\x00\x01' + len(method).to_bytes(4, 'big') + method + seq.to_bytes(8, 'big')
    else:
        header = len(method).to_bytes(4, 'big') + method + b'\x01' + seq.to_bytes(8, 'big')
    return seq.to_bytes(4, 'big') + header + query_args(service_size)


class LabelImplicationTests(unittest.TestCase):
    def test_dual_policy_failures_are_dependent_in_eighteen_synthetic_cases(self):
        checked = 0
        for length in (80, 85):
            for seq in (1, 2, 64):
                for name_length in (1, 8, 64):
                    # Deliberately invalid first method byte at offset 8.
                    body = (seq.to_bytes(4, 'big') + name_length.to_bytes(4, 'big')
                            + b'\xff' + b'A' * (name_length - 1))
                    body += bytes(length - len(body))
                    result = diagnose_body(body, seq)
                    self.assertEqual(len(body), length)
                    self.assertEqual(result['sequence_prefix'], 'MATCH')
                    self.assertEqual(result['legacy_after_sequence'], 'METHOD_BYTES_POLICY')
                    # First supposed character at offset 4 is zero: hence dependency.
                    self.assertEqual(body[4], 0)
                    self.assertEqual(result['legacy_at_start'], 'METHOD_BYTES_POLICY')
                    checked += 1
        self.assertEqual(checked, 18)

    def test_unmodified_native_legacy_candidate_classifies_at_offset_four(self):
        for service_size in (16, 21):
            body = candidate_body(service_size)
            self.assertIn(len(body), (80, 85))
            result = diagnose_body(body, 1)
            self.assertEqual(result['sequence_prefix'], 'MATCH')
            self.assertEqual(result['legacy_after_sequence'], 'LEGACY_HEADER_PLAUSIBLE')

    def test_unmodified_native_strict_candidate_gets_versioned_not_method_failure(self):
        for service_size in (13, 18):
            body = candidate_body(service_size, strict=True)
            self.assertIn(len(body), (80, 85))
            result = diagnose_body(body, 1)
            self.assertEqual(result['sequence_prefix'], 'MATCH')
            self.assertEqual(result['legacy_after_sequence'], 'VERSIONED_PREFIX_CANDIDATE')

    def test_length_bound_is_a_precondition_for_offset_zero_failure(self):
        # Offset 0 is not guaranteed to say METHOD_BYTES_POLICY if sequence
        # falls outside the observer's accepted method-name length window.
        for seq in (0, 65, 0x01020304):
            body = seq.to_bytes(4, 'big') + (8).to_bytes(4, 'big') + b'\xff' + bytes(76)
            result = diagnose_body(body, seq)
            self.assertEqual(result['sequence_prefix'], 'MATCH')
            self.assertEqual(result['legacy_after_sequence'], 'METHOD_BYTES_POLICY')
            self.assertEqual(result['legacy_at_start'], 'NAME_LENGTH_POLICY')

    def test_negative_controls_do_not_conflate_header_and_application_recognition(self):
        b = candidate_body(16)
        # Header-only classifier does not validate full arguments or auth.
        tampered = b[:-1] + b'\xff'
        self.assertEqual(diagnose_body(tampered, 1)['legacy_after_sequence'],
                         'LEGACY_HEADER_PLAUSIBLE')
        self.assertNotEqual(diagnose_body(b, 2)['sequence_prefix'], 'MATCH')


if __name__ == '__main__':
    unittest.main()

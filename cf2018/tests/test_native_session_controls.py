"""Independent decoded-state/component tests, not valid ACK/auth replies."""
import hashlib
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from native_control import NativeControl
import os
import unittest
from native_session_controls import (ack_body_probe, ack_presence_state_probe,
    auth_response_probe, timestamp_prefix_probe)

LIBRARY = os.environ.get('CF18_APOLLO_LIBRARY')


@unittest.skipUnless(LIBRARY, 'private fingerprinted library and native dependencies required')
class NativeBodyControls(unittest.TestCase):
    def test_absent_embedded_auth_does_not_set_presence(self):
        for fragment in (b'', b'\x11\0'):
            with self.subTest(fragment=fragment):
                r = ack_body_probe(LIBRARY, fragment)
                self.assertEqual((r['return'], r['presence']), (0, 0))
                self.assertNotIn(0x3b39c0, r['branches'])

    def test_empty_nested_auth_component_sets_presence_without_an_account(self):
        r = ack_body_probe(LIBRARY, b'\x25\0\0\0\0')
        self.assertEqual((r['return'], r['presence'], r['consumed']), (0, 1, 5))
        self.assertEqual(r['embedded_account_prefix_sha256'], hashlib.sha256(bytes(0x114)).hexdigest())
        self.assertIn(0x3b39c0, r['branches'])
        self.assertIn(0x3b4a32, r['branches'])

    def test_missing_presence_field_retains_existing_presence_in_component_decoder(self):
        r = ack_body_probe(LIBRARY, b'', initial_presence=1)
        self.assertEqual((r['return'], r['presence']), (0, 1))

    def test_explicit_zero_presence_can_clear_component_storage(self):
        r = ack_body_probe(LIBRARY, b'\x11\0', initial_presence=1)
        self.assertEqual((r['return'], r['presence']), (0, 0))

    def test_truncated_nested_auth_does_not_set_presence(self):
        for fragment in (b'\x25\0\0\0\1', b'\x25\0\0\0\1\x11'):
            with self.subTest(fragment=fragment):
                r = ack_body_probe(LIBRARY, fragment)
                self.assertEqual((r['return'], r['presence']), (-2, 0))

    def test_declared_component_overrun_is_distinct_from_truncation(self):
        r = ack_body_probe(LIBRARY, b'\x11\0', declared_length=1)
        self.assertEqual((r['return'], r['consumed']), (-34, 2))

    def test_both_presence_values_still_reach_suppressed_auth_send(self):
        for presence in (0, 1):
            with self.subTest(presence=presence):
                r = ack_presence_state_probe(LIBRARY, presence)
                self.assertEqual((r['return'], r['presence'], r['state']), (-77, presence, 2))
                self.assertTrue(r['account_unchanged'])
                self.assertIn('auth send suppressed', r['calls'])

    def test_auth_header_type_checked_before_body_or_account_copy(self):
        for header_type in (0x1002, 0x2001, 0):
            with self.subTest(header_type=header_type):
                r = auth_response_probe(LIBRARY, header_type=header_type, parser_result=0)
                self.assertEqual((r['return'], r['state'], r['diagnostic_type']), (-14, 3, header_type))
                self.assertTrue(r['account_unchanged'])
                self.assertNotIn('body parser supplied-result stub', r['calls'])

    def test_auth_receive_error_mapping_and_waiting(self):
        for result, expected in ((-10, -7), (-12, -12), (-9, -9)):
            with self.subTest(result=result):
                r = auth_response_probe(LIBRARY, receive_result=result)
                self.assertEqual((r['return'], r['state']), (expected, 3))
                self.assertTrue(r['account_unchanged'])

    def test_real_malformed_body_parser_prevents_account_copy(self):
        for body in (b'', b'\0', bytes(32)):
            with self.subTest(length=len(body)):
                r = auth_response_probe(LIBRARY, body=body)
                self.assertEqual((r['return'], r['state']), (-18, 3))
                self.assertTrue(r['account_unchanged'])
                self.assertNotIn('body parser supplied-result stub', r['calls'])

    def test_supplied_parser_failure_prevents_account_copy(self):
        r = auth_response_probe(LIBRARY, parser_result=-2)
        self.assertEqual((r['return'], r['state']), (-18, 3))
        self.assertTrue(r['account_unchanged'])

    def test_supplied_parser_zero_only_proves_native_copy_and_stage4_branch(self):
        r = auth_response_probe(LIBRARY, parser_result=0)
        self.assertEqual((r['return'], r['state']), (0, 4))
        self.assertTrue(r['account_copy_matches_synthetic_source'])
        self.assertIn('body parser supplied-result stub', r['calls'])
        self.assertIn(0x3ac37e, r['branches'])
        self.assertIn(0x3ac390, r['branches'])

    def test_auth_state_waits_without_bingo_receive(self):
        r = auth_response_probe(LIBRARY, state_handler=True, receive_result=-12)
        self.assertEqual((r['return'], r['state']), (0, 3))
        self.assertNotIn('bingo receive suppressed', r['calls'])

    def test_stage4_branch_still_reaches_bingo_receive_boundary(self):
        r = auth_response_probe(LIBRARY, state_handler=True, parser_result=0)
        self.assertEqual((r['return'], r['state']), (0, 4))
        self.assertIn('bingo receive suppressed', r['calls'])
        self.assertIn(0x3aa024, r['branches'])

    def test_ack_timestamp_copied_before_token_build_for_multiple_inputs(self):
        for timestamp in (0, 7, 0x12345678, 0xffffffff):
            with self.subTest(timestamp=timestamp):
                r = timestamp_prefix_probe(LIBRARY, timestamp)
                self.assertEqual((r['stop_code'], r['outgoing_timestamp']), (-77, timestamp))
                self.assertTrue(r['stopped_before_account_token_hash'])
                self.assertIn(0x3ab808, r['branches'])
                self.assertIn(0x3ab80c, r['branches'])


    def test_fresh_context_does_not_inherit_prior_component_presence(self):
        first = ack_body_probe(LIBRARY, b'', initial_presence=1)
        second = ack_body_probe(LIBRARY, b'')
        self.assertEqual((first['presence'], second['presence']), (1, 0))

    def test_state_receive_failure_never_copies_or_calls_bingo(self):
        r = auth_response_probe(LIBRARY, state_handler=True, receive_result=-10,
                                parser_result=0)
        self.assertEqual((r['return'], r['state']), (-7, 3))
        self.assertTrue(r['account_unchanged'])
        self.assertNotIn('body parser supplied-result stub', r['calls'])
        self.assertNotIn('bingo receive suppressed', r['calls'])


class NativeSourceGuard(unittest.TestCase):
    def test_wrong_source_refused_before_optional_dependencies(self):
        private = Path(__file__).resolve().parents[1] / 'private'
        private.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private) as directory:
            p = Path(directory) / 'synthetic-source'
            p.write_bytes(bytes(5243704))
            with self.assertRaisesRegex(ValueError, 'fingerprint'):
                NativeControl(p)


if __name__ == '__main__':
    unittest.main()

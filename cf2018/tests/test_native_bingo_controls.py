"""Negative/native branch controls; none establishes an authenticated session."""
import os
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from native_bingo_controls import (component_probe, decoded_probe, mismatched_auth_wire,
                            relay_reuse_prefix, wire_probe)

LIBRARY = os.environ.get('CF18_APOLLO_LIBRARY')


class BoundsTests(unittest.TestCase):
    def test_invalid_configuration_refused_before_source_or_dependencies(self):
        with self.assertRaises(ValueError):
            wire_probe('absent', bytes(513))
        with self.assertRaises(ValueError):
            wire_probe('absent', b'', ready=1)
        with self.assertRaises(ValueError):
            component_probe('absent', b'', component='unknown')
        with self.assertRaises(ValueError):
            component_probe('absent', b'', component='relay', declared=513)
        with self.assertRaises(ValueError):
            decoded_probe('absent', decoded_selector=123)

    def test_negative_wire_preserves_auth_body_and_has_no_bingo_component(self):
        from auth_fixture_repair import corrected_v12_fixture
        original = corrected_v12_fixture('V12_BODY_EMPTY')
        for header in (0x3002, 0x6002):
            with self.subTest(header=header):
                wire = mismatched_auth_wire(header)
                self.assertEqual(len(wire), len(original))
                self.assertEqual(wire[42:], original[42:])
                self.assertNotEqual(wire[:42], original[:42])
        with self.assertRaises(ValueError):
            mismatched_auth_wire(0x2002)


@unittest.skipUnless(LIBRARY, 'private pinned Apollo and native dependencies required')
class NativeBingoTests(unittest.TestCase):
    def test_bingo_without_data_waits_and_ready_converts_only_wait_to_zero(self):
        raw = wire_probe(LIBRARY)
        ready = wire_probe(LIBRARY, ready=True)
        self.assertEqual((raw['return'], ready['return'], ready['state']), (-12, 0, 4))
        self.assertTrue(raw['relay_unchanged'] and ready['relay_unchanged'])

    def test_eof_like_wrapper_status_is_not_a_successful_wait(self):
        for ready in (False, True):
            r = wire_probe(LIBRARY, ready=ready, network_result=-4)
            self.assertEqual((r['return'], r['state']), (-10, 4))
            self.assertTrue(r['relay_unchanged'])

    def test_ready_rejects_invalid_context_before_receive(self):
        for config, expected in (({'state': 3}, -19),
                                 ({'initialized': False}, -4),
                                 ({'descriptor': -1}, -1)):
            with self.subTest(config=config):
                r = wire_probe(LIBRARY, ready=True, **config)
                self.assertEqual(r['return'], expected)
                self.assertTrue(r['relay_unchanged'])
                self.assertFalse(any(stage == 'bingo_receive' for stage, _ in r['events']))

    def test_receive_errors_propagate_before_any_body_decode(self):
        for code in (-12, -10, -31):
            with self.subTest(code=code):
                r = decoded_probe(LIBRARY, receive_result=code)
                self.assertEqual((r['return'], r['state']), (code, 4))
                self.assertTrue(r['relay_unchanged'])
                self.assertFalse(any(stage == 'body' for stage, _ in r['events']))

    def test_wrong_header_type_fails_before_body_and_records_type(self):
        r = decoded_probe(LIBRARY, header_type=0x2002)
        self.assertEqual((r['return'], r['state'], r['diagnostic_type']), (-14, 4, 0x2002))
        self.assertTrue(r['relay_unchanged'])
        self.assertFalse(any(stage == 'body' for stage, _ in r['events']))

    def test_real_truncated_body_error_maps_to_minus18_without_session_copy(self):
        r = decoded_probe(LIBRARY)
        self.assertIn(('body', -2), r['events'])
        self.assertEqual((r['return'], r['state']), (-18, 4))
        self.assertTrue(r['relay_unchanged'])
        self.assertEqual(r['compression'], [7, 99])
        self.assertFalse(any('PARSER RESULT' in stub for stub in r['stubs']))

    def test_stubbed_parser_failure_prevents_copy(self):
        r = decoded_probe(LIBRARY, parser_result=-32)
        self.assertEqual((r['return'], r['state']), (-18, 4))
        self.assertTrue(r['relay_unchanged'])

    def test_wait_type_is_queue_metadata_and_state4_not_stop_or_login(self):
        r = decoded_probe(LIBRARY, header_type=0x3002, parser_result=0)
        self.assertEqual((r['return'], r['state']), (-28, 4))
        self.assertEqual(r['queue'], [1, 17, 34, 51])
        self.assertEqual(r['compression'], [7, 99])
        self.assertTrue(r['relay_unchanged'])
        self.assertTrue(any('PARSER RESULT/STORAGE STUB' in stub for stub in r['stubs']))

    def test_parser_stub_zero_only_proves_copy_and_compression_branch(self):
        r = decoded_probe(LIBRARY, parser_result=0)
        self.assertEqual((r['return'], r['state']), (0, 5))
        self.assertEqual(r['compression'], [3, 4096])
        self.assertFalse(r['relay_unchanged'])
        self.assertTrue(r['relay_matches_decoded_prefix'])
        self.assertTrue(any('PARSER RESULT/STORAGE STUB' in stub for stub in r['stubs']))

    def test_decoded_selector_controls_branch_after_original_header_check(self):
        queue = decoded_probe(LIBRARY, header_type=0x6002, parser_result=0, decoded_selector=0x3002)
        other = decoded_probe(LIBRARY, header_type=0x3002, parser_result=0, decoded_selector=0x2002)
        self.assertEqual((queue['return'], queue['state']), (-28, 4))
        self.assertEqual((other['return'], other['state']), (0, 5))
        self.assertEqual(other['post_body_selectors'], [0x2002])

    def test_full_native_mismatched_auth_body_reaches_state5_without_bingo_component(self):
        # Deliberately invalid correlation; never a successful Bingo/session fixture.
        for header in (0x3002, 0x6002):
            with self.subTest(header=header):
                r = wire_probe(LIBRARY, mismatched_auth_wire(header))
                self.assertEqual((r['return'], r['state'], r['header_type']), (0, 5, header))
                self.assertEqual(r['post_body_selectors'], [0x2002])
                self.assertTrue(r['relay_matches_decoded_prefix'])
                self.assertIn(('auth_component', 0), r['events'])
                self.assertIn(('body', 0), r['events'])
                self.assertFalse(any(stage == 'bingo_component' for stage, _ in r['events']))
                self.assertFalse(any('PARSER' in stub or 'RECEIVE STUB' in stub for stub in r['stubs']))

    def test_fresh_context_does_not_inherit_previous_numeric_state5(self):
        wire_probe(LIBRARY, mismatched_auth_wire())
        r = wire_probe(LIBRARY)
        self.assertEqual((r['return'], r['state']), (-12, 4))
        self.assertTrue(r['relay_unchanged'])

    def test_empty_components_return_zero_without_identity_or_presence(self):
        for component in ('bingo', 'relay'):
            r = component_probe(LIBRARY, b'', component=component)
            self.assertEqual((r['return'], r['consumed'], r['presence']), (0, 0, 0))
            self.assertTrue(r['relay_payload_unchanged'])

    def test_empty_nested_relay_marks_bingo_presence_but_keeps_prior_fields(self):
        r = component_probe(LIBRARY, b'\x15\0\0\0\0', component='bingo')
        self.assertEqual((r['return'], r['consumed'], r['presence']), (0, 5, 1))
        self.assertTrue(r['relay_payload_unchanged'])

    def test_bingo_compression_fields_decode_independently_of_relay_identity(self):
        r = component_probe(LIBRARY, b'\x21\x03\x31\x80\x20', component='bingo')
        self.assertEqual((r['return'], r['consumed'], r['presence']), (0, 5, 6))
        self.assertEqual(r['compression'], [3, 4096])
        self.assertTrue(r['relay_payload_unchanged'])

    def test_relay_zero_identity_length_fails_minus37(self):
        r = component_probe(LIBRARY, b'\x25\0\0\0\0', component='relay')
        self.assertEqual((r['return'], r['consumed']), (-37, 5))

    def test_component_declared_overrun_and_physical_truncation_are_distinct(self):
        overrun = component_probe(LIBRARY, b'\x11\x01', component='relay', declared=1)
        truncated = component_probe(LIBRARY, b'\x11\x80', component='relay')
        self.assertEqual((overrun['return'], overrun['consumed']), (-34, 2))
        self.assertEqual((truncated['return'], truncated['consumed']), (-2, 1))

    def test_exact_overlong_identity_control_is_not_promoted_to_general_size_rule(self):
        r = component_probe(LIBRARY, b'\x25\0\0\0\x11'+b'Z'*17, component='relay')
        self.assertEqual((r['return'], r['consumed']), (-35, 22))

    def test_subsequent_syn_prefix_reuses_received_relay_block_without_sending(self):
        r = relay_reuse_prefix(LIBRARY)
        self.assertEqual(r['stop_code'], -77)
        self.assertTrue(r['stopped_before_send'] and r['copied_44_bytes'])
        self.assertEqual(r['stubs'], [])


if __name__ == '__main__':
    unittest.main()

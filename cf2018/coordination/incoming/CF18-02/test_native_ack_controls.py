"""Independent decoded-state/component controls; never a complete server ACK."""
import os
from pathlib import Path
import tempfile
import unittest
from native_ack_controls import NativeControl, decoded_probe, ack_probe, ack_tlv_probe

LIBRARY = os.environ.get('CF18_APOLLO_LIBRARY')


class SourceGuards(unittest.TestCase):
    def test_wrong_fingerprint_refused_before_dependencies_or_execution(self):
        private = Path(__file__).parent / 'private'
        private.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private) as directory:
            p = Path(directory) / 'synthetic.bin'
            p.write_bytes(b'x')
            with self.assertRaisesRegex(ValueError, 'size'):
                NativeControl(p)
            with p.open('wb') as f:
                f.truncate(5243704)
            with self.assertRaisesRegex(ValueError, 'fingerprint'):
                NativeControl(p)


@unittest.skipUnless(LIBRARY, 'private hash-pinned source and native dependencies required')
class NativeAckControls(unittest.TestCase):
    def test_empty_mode0_consumes_and_saves_base_word_without_key_setup(self):
        for word in (0, 7, 0xdeadbeef):
            with self.subTest(word=word):
                r = decoded_probe(LIBRARY, base_word=word)
                self.assertEqual((r['return'], r['cursor'], r['buffered'], r['pending']), (0, 32, 0, 0))
                self.assertEqual(r['saved_base_word'], word)
                self.assertNotIn(0x3ab24a, r['branches'])

    def test_splitter_error_prevents_ack_key_changes(self):
        r = decoded_probe(LIBRARY, key_mode=1, method=4, splitter_result=-12)
        self.assertEqual((r['return'], r['method'], r['key_mode']), (-12, 0, 0))
        self.assertEqual(r['calls'], ['splitter decoded-boundary stub'])

    def test_unsupported_key_modes_reject_after_method_mode_copy(self):
        for mode in (1, 4, 255):
            with self.subTest(mode=mode):
                r = decoded_probe(LIBRARY, key_mode=mode, method=4)
                self.assertEqual((r['return'], r['method'], r['key_mode'], r['cursor']), (-30, 4, mode, 0))
                self.assertIn(0x3ac06c, r['branches'])

    def test_mode2_copies_synthetic_key_then_rejects_unsupported_method(self):
        for method in (1, 2, 255):
            with self.subTest(method=method):
                r = decoded_probe(LIBRARY, key_mode=2, key_length=16, method=method)
                self.assertEqual((r['return'], r['key_length'], r['cursor']), (-29, 16, 0))
                self.assertIn(0x3ab24a, r['branches'])

    def test_mode2_plain_method_does_not_need_aes(self):
        r = decoded_probe(LIBRARY, key_mode=2, key_length=16)
        self.assertEqual((r['return'], r['key_length'], r['cursor']), (0, 16, 32))

    def test_mode2_encrypted_method_without_key_rejected(self):
        for method in (3, 4):
            with self.subTest(method=method):
                r = decoded_probe(LIBRARY, key_mode=2, method=method)
                self.assertEqual((r['return'], r['cursor']), (-31, 0))

    def test_mode3_compute_failure_propagates_without_consumption(self):
        r = decoded_probe(LIBRARY, key_mode=3)
        self.assertEqual((r['return'], r['cursor']), (-40, 0))
        self.assertIn('DH compute failure-only stub', r['calls'])
        self.assertNotIn(0x3ab24a, r['branches'])
        with self.assertRaisesRegex(ValueError, 'DH stub'):
            decoded_probe(LIBRARY, key_mode=3, compute_result=0)

    def test_mode0_empty_body_can_hide_incompatible_crypto_configuration(self):
        r = decoded_probe(LIBRARY, method=4)
        self.assertEqual((r['return'], r['method'], r['key_length']), (0, 4, 0))
        r = decoded_probe(LIBRARY, method=4, encrypted=1, body=b'XY')
        self.assertEqual((r['return'], r['cursor']), (-31, 0))
        self.assertIn(0x3ab31e, r['branches'])

    def test_encrypted_flag_with_method0_uses_plaintext_copy(self):
        r = decoded_probe(LIBRARY, encrypted=1, body=b'\0\xffXY')
        self.assertEqual((r['return'], r['output_length'], r['cursor']), (0, 4, 36))
        self.assertTrue(r['output_matches_synthetic_body'])
        self.assertIn(0x3ab31e, r['branches'])

    def test_unencrypted_body_ignores_method_for_copy(self):
        r = decoded_probe(LIBRARY, method=4, body=b'\0\xffXY')
        self.assertEqual((r['return'], r['output_length']), (0, 4))
        self.assertTrue(r['output_matches_synthetic_body'])
        self.assertNotIn(0x3ab31e, r['branches'])

    def test_wrong_type_consumed_before_actual_ack_caller_rejects(self):
        r = decoded_probe(LIBRARY, message_type=0x1001, through_ack=True)
        self.assertEqual((r['return'], r['cursor'], r['pending'], r['saved_base_word']), (-14, 32, 0, 7))
        self.assertIn(0x3ac11e, r['branches'])
        self.assertNotIn('recv/decrypt decoded-boundary stub', r['calls'])

    def test_actual_ack_caller_after_actual_recv_decrypt_empty_mode0(self):
        r = decoded_probe(LIBRARY, through_ack=True)
        self.assertEqual((r['return'], r['cursor'], r['pending']), (0, 32, 0))
        self.assertIn(0x3ac126, r['branches'])
        self.assertNotIn('recv/decrypt decoded-boundary stub', r['calls'])

    def test_ack_type_is_checked_after_recv_decrypt(self):
        for message_type in (0, 0x1001, 0x2002):
            with self.subTest(message_type=message_type):
                r = ack_probe(LIBRARY, message_type=message_type)
                self.assertEqual((r['return'], r['diagnostic_type']), (-14, message_type))
                self.assertIn('recv/decrypt decoded-boundary stub', r['calls'])
                self.assertNotIn(0x3ac126, r['branches'])

    def test_ack_empty_body_copies_compression_scalars(self):
        r = ack_probe(LIBRARY, scalar4=255, scalar5=0xdeadbeef)
        self.assertEqual((r['return'], r['ack_scalar4'], r['ack_scalar5']), (0, 255, 0xdeadbeef))
        self.assertNotIn(0x3ac1a4, r['branches'])

    def test_ack_malformed_nonempty_body_uses_real_parser_and_maps_error(self):
        for length in (1, 4, 5, 32):
            with self.subTest(length=length):
                r = ack_probe(LIBRARY, body_length=length)
                self.assertEqual(r['return'], -18)
                self.assertIn(0x3ac1a4, r['branches'])
                self.assertNotIn('body parser result stub', r['calls'])

    def test_special_error_translation_requires_all_predicates(self):
        r = ack_probe(LIBRARY, receive_result=-11, error_state=1, error_detail=10001)
        self.assertEqual((r['return'], r['special_error_flag']), (-38, 1))
        for state, detail in ((0, 10001), (1, 10000)):
            with self.subTest(state=state, detail=detail):
                r = ack_probe(LIBRARY, receive_result=-11, error_state=state, error_detail=detail)
                self.assertEqual((r['return'], r['special_error_flag']), (-11, 0))

    def test_state_wait_return0_does_not_send_auth(self):
        r = ack_probe(LIBRARY, receive_result=-12, state_handler=True)
        self.assertEqual(r['return'], 0)
        self.assertNotIn('auth send suppressed', r['calls'])

    def test_state_ack_success_reaches_suppressed_auth_boundary(self):
        r = ack_probe(LIBRARY, state_handler=True)
        self.assertEqual(r['return'], -77)  # deliberate send stub failure, never network
        self.assertIn('auth send suppressed', r['calls'])
        self.assertIn(0x3a9fd6, r['branches'])

    def test_state_wrong_type_error_does_not_send_auth(self):
        r = ack_probe(LIBRARY, message_type=0x1001, state_handler=True)
        self.assertEqual(r['return'], -14)
        self.assertNotIn('auth send suppressed', r['calls'])

    def test_wrong_state_rejected_before_receive(self):
        r = ack_probe(LIBRARY, state=3, state_handler=True)
        self.assertEqual((r['return'], r['calls']), (-19, []))

    def test_ack_component_scalar_widths(self):
        fragment = bytes([0x11, 3, 0x21, 0, 0x41, 2, 0x50, 7, 0x60, 9])
        r = ack_tlv_probe(LIBRARY, fragment)
        self.assertEqual((r['return'], r['consumed'], r['method'], r['key_mode'],
                          r['scalar4'], r['scalar5'], r['scalar6']), (0, 10, 3, 0, 2, 7, 9))

    def test_ack_component_missing_and_duplicate_fields_are_not_strictly_rejected(self):
        self.assertEqual(ack_tlv_probe(LIBRARY, b'')['return'], 0)
        r = ack_tlv_probe(LIBRARY, bytes([0x11, 3, 0x11, 4]))
        self.assertEqual((r['return'], r['method']), (0, 4))
        self.assertEqual(ack_tlv_probe(LIBRARY, bytes([0x70, 7]))['return'], 0)

    def test_ack_component_truncation_and_declared_bound_overrun_differ(self):
        self.assertEqual(ack_tlv_probe(LIBRARY, b'\x11')['return'], -2)
        self.assertEqual(ack_tlv_probe(LIBRARY, b'\x60\x80')['return'], -2)
        self.assertEqual(ack_tlv_probe(LIBRARY, b'\x11\x03', declared_length=3)['return'], -2)
        r = ack_tlv_probe(LIBRARY, b'\x11\x03', declared_length=1)
        self.assertEqual((r['return'], r['consumed'], r['method']), (-34, 2, 3))

    def test_nested_key_union_can_override_scalar_key_mode(self):
        fragment = bytes([0x21, 2, 0x35, 0, 0, 0, 2, 1, 0])
        r = ack_tlv_probe(LIBRARY, fragment)
        self.assertEqual((r['return'], r['key_mode']), (0, 0))
        bad = bytes([0x35, 0, 0, 0, 1, 0, 0])
        self.assertEqual(ack_tlv_probe(LIBRARY, bad)['return'], -34)


if __name__ == '__main__':
    unittest.main()

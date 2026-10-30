"""Exact v1.2 regressions and independent malformed controls; no phone session."""
import hashlib
import os
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from auth_v12_fixtures import EXPECTED, reply, account_full_zero
from tgcp_body_envelope import encode_body_envelope
from auth_fixture_repair import corrected_v12_fixture
from native_auth_rx import trace_wire, trace_component

LIBRARY = os.environ.get('CF18_APOLLO_LIBRARY')


def codes(result, stage):
    return [event['code'] for event in result['events']
            if event['stage'] == stage and event['event'] == 'return']


class BodyEncodingTests(unittest.TestCase):
    def test_exact_historical_fixtures_are_preserved(self):
        for arm, expected in EXPECTED.items():
            with self.subTest(arm=arm):
                wire = reply(arm)
                self.assertEqual(len(wire), expected['length'])
                self.assertEqual(hashlib.sha256(wire).hexdigest(), expected['sha256'])

    def test_fix_changes_only_body_wrapper_and_declared_body_length(self):
        for arm in EXPECTED:
            with self.subTest(arm=arm):
                old, new = reply(arm), corrected_v12_fixture(arm)
                self.assertEqual(len(new), len(old)+5)
                self.assertEqual(new[:32], old[:32])
                self.assertEqual(new[33:42], old[33:42])
                self.assertEqual(new[32], old[32]+5)
                self.assertEqual(new[42], 0xaa)
                self.assertEqual(int.from_bytes(new[43:47], 'big'), len(new)-42)
                self.assertEqual(new[47:], old[42:])

    def test_body_length_includes_five_byte_preamble(self):
        self.assertEqual(encode_body_envelope(b'abc'), b'\xaa\0\0\0\x08abc')
        self.assertEqual(encode_body_envelope(b'abc', varint=False), b'\x99\0\0\0\x08abc')
        self.assertEqual(encode_body_envelope(b''), b'\xaa\0\0\0\x05')

    def test_exact_cap_and_one_byte_over(self):
        payload = bytes(65531)
        encoded = encode_body_envelope(payload)
        self.assertEqual(len(encoded), 65536)
        self.assertEqual(encoded[:5], b'\xaa\x00\x01\x00\x00')
        self.assertEqual(encoded[5:], payload)
        with self.assertRaises(ValueError):
            encode_body_envelope(payload + b'!')
        self.assertEqual(encode_body_envelope(b'', max_size=5), b'\xaa\0\0\0\x05')
        for cap in (True, 4, 65537):
            with self.assertRaises(ValueError):
                encode_body_envelope(b'', max_size=cap)

    def test_bounds_and_types_fail_closed(self):
        with self.assertRaises(TypeError):
            encode_body_envelope(bytearray(b'a'))
        with self.assertRaises(TypeError):
            encode_body_envelope(b'', varint=1)
        with self.assertRaises(ValueError):
            encode_body_envelope(bytes(65532))
        with self.assertRaises(ValueError):
            encode_body_envelope(b'abc', max_size=7)
        with self.assertRaises(ValueError):
            corrected_v12_fixture('not a historical arm')


@unittest.skipUnless(LIBRARY, 'private pinned Apollo and native dependencies required')
class ExactNativeAuthTests(unittest.TestCase):
    def test_all_originals_fail_at_body_mode_before_components(self):
        for arm in EXPECTED:
            with self.subTest(arm=arm):
                r = trace_wire(LIBRARY, reply(arm))
                for stage in ('base_varint', 'extension', 'header_unpack', 'gather', 'receive_decrypt'):
                    self.assertEqual(codes(r, stage), [0])
                self.assertEqual((r['effective_type'], r['header_length']), (0x2002, 42))
                self.assertEqual(codes(r, 'body_unpack'), [-32])
                self.assertEqual((r['return'], r['state']), (-18, 3))
                self.assertTrue(r['account_unchanged'])
                self.assertFalse(codes(r, 'auth_component'))
                self.assertFalse(codes(r, 'account_component'))
                self.assertFalse(codes(r, 'bingo_receive'))
                self.assertEqual(r['predicates'][0]['extension_selector'], 0x2002)
                predicate = next(p for p in r['predicates'] if 'observed_byte' in p)
                self.assertEqual((predicate['address'], predicate['observed_byte']), (0x3b88d8, 0xa5))
                self.assertEqual(r['predicates'][-1]['body_cursor'], 1)

    def test_isolated_original_auth_components_decode_but_full_path_never_reached_them(self):
        for arm in EXPECTED:
            with self.subTest(arm=arm):
                auth = reply(arm)[49:]
                r = trace_component(LIBRARY, auth, component='auth')
                self.assertEqual((r['return'], r['consumed']), (0, len(auth)))
                self.assertTrue(r['isolated_component_only'])

    def test_isolated_account_components_have_zero_decode_status_not_identity_proof(self):
        for account in (b'', account_full_zero()):
            with self.subTest(length=len(account)):
                r = trace_component(LIBRARY, account, component='account')
                self.assertEqual((r['return'], r['consumed']), (0, len(account)))

    def test_fixed_wrappers_reach_real_body_auth_and_account_decoders(self):
        for arm in EXPECTED:
            with self.subTest(arm=arm):
                r = trace_wire(LIBRARY, corrected_v12_fixture(arm), state_handler=False)
                self.assertEqual((r['return'], r['state']), (0, 4))
                self.assertEqual(codes(r, 'body_unpack'), [0])
                self.assertEqual(codes(r, 'body_union'), [0])
                self.assertEqual(codes(r, 'auth_component'), [0])
                expected_account = [] if arm == 'V12_BODY_EMPTY' else [0]
                self.assertEqual(codes(r, 'account_component'), expected_account)
                self.assertFalse(r['account_unchanged'])
                self.assertTrue(r['synthetic_uid_zero'])
                self.assertFalse(codes(r, 'bingo_receive'))

    def test_fixed_auth_handler_reaches_real_bingo_and_waits(self):
        for arm in EXPECTED:
            with self.subTest(arm=arm):
                r = trace_wire(LIBRARY, corrected_v12_fixture(arm))
                self.assertEqual(codes(r, 'auth_receive'), [0])
                self.assertEqual(codes(r, 'bingo_receive'), [-12])
                self.assertEqual((r['return'], r['state']), (0, 4))
                self.assertEqual(codes(r, 'gather'), [0, -12])
                self.assertFalse(any('parser' in stub or 'bingo' in stub or 'splitter' in stub for stub in r['stubs']))

    def test_adding_preamble_without_updating_outer_body_length_still_fails(self):
        p = corrected_v12_fixture('V12_BODY_EMPTY')
        p = p[:32]+bytes([7])+p[33:]
        r = trace_wire(LIBRARY, p)
        self.assertEqual(codes(r, 'body_unpack'), [-2])
        self.assertEqual((r['return'], r['state']), (-18, 3))
        self.assertTrue(r['account_unchanged'])

    def test_inner_body_length_larger_than_delivered_bytes_fails(self):
        p = corrected_v12_fixture('V12_BODY_EMPTY')
        p = p[:43]+(13).to_bytes(4, 'big')+p[47:]
        r = trace_wire(LIBRARY, p)
        self.assertEqual(codes(r, 'body_unpack'), [-2])
        self.assertFalse(codes(r, 'auth_component'))
        self.assertTrue(r['account_unchanged'])

    def test_incomplete_outer_body_waits_without_copy_or_bingo(self):
        p = corrected_v12_fixture('V12_BODY_EMPTY')[:-1]
        r = trace_wire(LIBRARY, p)
        self.assertEqual(codes(r, 'gather'), [-12])
        self.assertEqual((r['return'], r['state']), (0, 3))
        self.assertTrue(r['account_unchanged'])
        self.assertFalse(codes(r, 'body_unpack'))
        self.assertFalse(codes(r, 'bingo_receive'))

    def test_wrong_effective_type_rejects_before_body(self):
        p = corrected_v12_fixture('V12_BODY_EMPTY')
        # Remove extension and change the base command to 0x2001; native uses it.
        p = p[:1]+(33).to_bytes(4, 'big')+p[5:19]+b'\x81'+p[20:33]+p[42:]
        r = trace_wire(LIBRARY, p)
        self.assertEqual(r['effective_type'], 0x2001)
        self.assertEqual((r['return'], r['state']), (-14, 3))
        self.assertFalse(codes(r, 'body_unpack'))
        self.assertTrue(r['account_unchanged'])

    def test_encrypted_flag_without_key_fails_earlier_than_body(self):
        p = corrected_v12_fixture('V12_BODY_EMPTY')
        p = p[:24]+b'\1'+p[25:]
        r = trace_wire(LIBRARY, p, encryption_method=4)
        self.assertEqual(codes(r, 'receive_decrypt'), [-31])
        self.assertEqual((r['return'], r['state']), (-31, 3))
        self.assertFalse(codes(r, 'body_unpack'))
        self.assertTrue(r['account_unchanged'])

    def test_method_setting_does_not_force_decryption_when_wire_flag_is_zero(self):
        r = trace_wire(LIBRARY, corrected_v12_fixture('V12_BODY_EMPTY'), encryption_method=4)
        self.assertEqual((r['return'], r['state']), (0, 4))
        self.assertEqual(codes(r, 'body_unpack'), [0])
        self.assertEqual(codes(r, 'bingo_receive'), [-12])

    def test_explicit_eof_status_after_parse_is_separate_from_auth_body_failure(self):
        r = trace_wire(LIBRARY, corrected_v12_fixture('V12_BODY_EMPTY'), network_result=-4)
        self.assertEqual(codes(r, 'auth_receive'), [0])
        self.assertEqual(codes(r, 'body_unpack'), [0])
        self.assertEqual(codes(r, 'bingo_receive'), [-10])
        self.assertEqual((r['return'], r['state']), (-10, 4))

    def test_a_second_auth_response_is_not_a_successful_bingo_message(self):
        p = corrected_v12_fixture('V12_BODY_EMPTY')
        r = trace_wire(LIBRARY, p+p)
        self.assertEqual(codes(r, 'auth_receive'), [0])
        self.assertEqual(codes(r, 'bingo_receive'), [-14])
        self.assertEqual((r['return'], r['state'], r['diagnostic_type']), (-14, 4, 0x2002))

    def test_raw_transport_prefix_fails_before_body(self):
        for prefix in (b'\x43\x66', b'\x66\x43'):
            r = trace_wire(LIBRARY, prefix+reply('V12_BODY_EMPTY'))
            self.assertEqual(codes(r, 'gather'), [-18])
            self.assertFalse(codes(r, 'body_unpack'))


if __name__ == '__main__':
    unittest.main()

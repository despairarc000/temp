"""Independent framing inputs; no captured client/server/session bytes."""
import os
import unittest
from native_boundary_controls import probe

LIBRARY = os.environ.get('CF18_APOLLO_LIBRARY')


def uint(value):
    encoded = bytearray()
    while value >= 128:
        encoded.append((value & 127) | 128)
        value >>= 7
    encoded.append(value)
    return bytes(encoded)


def envelope(mode=0xaa, *, body=b'\0\xff', body_length=None, magic=0x4366,
             base_delta=0, padded_tags=False):
    if body_length is None:
        body_length = len(body)
    base = b''
    for field in range(1, 10):
        value = magic if field == 1 else body_length if field == 9 else 0
        tag = (field << 4) | 1
        base += tag.to_bytes(4, 'big') if padded_tags else uint(tag)
        if mode == 0x99:
            base += value.to_bytes(2 if field <= 4 else 1 if field == 6 else 4, 'big')
        else:
            base += bytes([value]) if field == 6 else uint(value)
    header = b'\x15' + (len(base) + base_delta).to_bytes(4, 'big') + base
    return bytes([mode]) + (len(header) + 5).to_bytes(4, 'big') + header + body


@unittest.skipUnless(LIBRARY, 'private pinned Apollo and native dependencies required')
class NativeBoundaryTests(unittest.TestCase):
    def test_99_dispatches_to_fixed_base_values_with_varint_tags(self):
        data = envelope(0x99)
        r = probe(LIBRARY, data)
        self.assertEqual((r['return'], r['decoded_magic'], r['header_length'],
                          r['body_length'], r['pending_frame_length']), (0, 0x4366, 46, 2, 48))
        self.assertIn(0x3b726e, r['branches'])
        self.assertIn(0x3af5f0, r['branches'])
        self.assertNotIn(0x3b719c, r['branches'])

    def test_99_swapped_decoded_marker_rejects(self):
        r = probe(LIBRARY, envelope(0x99, magic=0x6643))
        self.assertEqual(r['return'], -13)
        self.assertIn(0x3ab74a, r['branches'])

    def test_99_padded_fixed_width_tags_are_not_the_observed_tag_encoding(self):
        r = probe(LIBRARY, envelope(0x99, padded_tags=True))
        self.assertNotEqual(r['return'], 0)

    def test_99_u32_body_length_uses_network_byte_order(self):
        r = probe(LIBRARY, envelope(0x99, body=b'', body_length=0x01020304))
        self.assertEqual((r['return'], r['body_length'], r['pending_frame_length']),
                         (-12, 0x01020304, 46 + 0x01020304))

    def test_99_declared_header_and_body_truncations_wait(self):
        data = envelope(0x99)
        for partial in (data[:32], data[:-1]):
            with self.subTest(length=len(partial)):
                self.assertEqual(probe(LIBRARY, partial)['return'], -12)

    def test_nested_mismatch_results_depend_on_mode_and_payload(self):
        # Exact independently synthetic controls; do not generalize error timing.
        for mode in (0xaa, 0x99):
            for body in (b'\0\xff', b'XY'):
                for delta in (-1, 1):
                    expected = -18 if delta < 0 or (mode == 0xaa and body == b'XY') else -12
                    with self.subTest(mode=mode, body=body, delta=delta):
                        self.assertEqual(probe(LIBRARY, envelope(mode, body=body,
                            base_delta=delta))['return'], expected)

    def test_signed_outer_header_limit_and_zero_length(self):
        for length, expected in ((0, -12), (0x7fffffff, -12),
                                 (0x80000000, -18), (0xffffffff, -18)):
            with self.subTest(length=length):
                data = b'\x99' + length.to_bytes(4, 'big') + bytes(43)
                self.assertEqual(probe(LIBRARY, data)['return'], expected)

    def test_mixed_modes_cache_then_promote_without_redecode(self):
        for first, second in ((0xaa, 0x99), (0x99, 0xaa)):
            with self.subTest(first=first, second=second):
                a, b = envelope(first), envelope(second)
                r = probe(LIBRARY, a+b, advance_current=True)
                self.assertEqual((r['first']['return'], r['first']['lookahead_length']), (0, len(b)))
                self.assertEqual((r['return'], r['cursor'], r['buffered'], r['pending_frame_length'],
                                  r['lookahead_length']), (0, len(a), len(b), len(b), 0))
                self.assertNotIn(0x3aab44, r['branches'])
                self.assertIn('host simulated', r['between_calls'])

    def test_lookahead_wrong_marker_rejects_only_after_promotion(self):
        a, b = envelope(), envelope(0x99, magic=0x6643)
        r = probe(LIBRARY, a+b, advance_current=True)
        self.assertEqual((r['first']['return'], r['first']['lookahead_magic']), (0, 0x6643))
        self.assertEqual((r['return'], r['decoded_magic']), (-13, 0x6643))

    def test_malformed_lookahead_envelope_rejects_current_frame_eagerly(self):
        r = probe(LIBRARY, envelope()+b'\xfc'+bytes(31))
        self.assertEqual((r['return'], r['cursor']), (-18, 0))
        self.assertIn(0x3ab722, r['branches'])

    def test_partial_lookahead_body_is_cached_then_waits(self):
        a, b = envelope(), envelope(0x99, body=b'', body_length=80)
        r = probe(LIBRARY, a+b, advance_current=True)
        self.assertEqual((r['first']['return'], r['first']['lookahead_length']), (0, 126))
        self.assertEqual((r['return'], r['pending_frame_length'], r['buffered'], r['cursor']),
                         (-12, 126, 46, 0))
        self.assertNotIn(0x3aab44, r['branches'])

    def test_incomplete_lookahead_header_is_not_cached(self):
        a = envelope()
        b = b'\x99'+(80).to_bytes(4, 'big')+bytes(27)
        r = probe(LIBRARY, a+b, advance_current=True)
        self.assertEqual((r['first']['return'], r['first']['lookahead_length']), (0, 0))
        self.assertEqual(r['return'], -12)
        self.assertIn(0x3aab44, r['branches'])

    def test_partial_frame_compacts_without_changing_remaining_bytes(self):
        import hashlib
        part = envelope(0x99)[:31]
        r = probe(LIBRARY, b'xxxxx'+part, cursor=5, buffered=len(part))
        self.assertEqual((r['return'], r['cursor'], r['buffered']), (-12, 0, 31))
        self.assertEqual(r['remaining_sha256'], hashlib.sha256(part).hexdigest())
        self.assertIn(0x3aab28, r['branches'])

    def test_receive_errors_are_delayed_until_buffered_complete_frame_consumed(self):
        for raw, expected in ((-2, -9), (-4, -10)):
            with self.subTest(raw=raw):
                r = probe(LIBRARY, envelope(), network_result=raw, advance_current=True)
                self.assertEqual((r['first']['return'], r['return']), (0, expected))
                self.assertEqual(r['stubs'], [])  # remembered error prevents another recv

    def test_partial_input_returns_remembered_error_instead_of_need_more(self):
        for raw, expected in ((-2, -9), (-4, -10), (-3, -12), (0, -12)):
            with self.subTest(raw=raw):
                r = probe(LIBRARY, envelope()[:31], network_result=raw)
                self.assertEqual(r['return'], expected)

    def test_invalid_buffer_invariants_reject_before_recv(self):
        for cursor, count, cap in ((0, 0, 0), (33, 0, 32), (0, 33, 32), (20, 20, 32)):
            with self.subTest(cursor=cursor, count=count, cap=cap):
                r = probe(LIBRARY, bytes(cursor+count), cursor=cursor, buffered=count, capacity=cap)
                self.assertEqual((r['return'], r['stubs']), (-1, []))

    def test_full_capacity_skips_receive_but_checks_existing_frame(self):
        data = envelope(0x99)
        r = probe(LIBRARY, data, capacity=len(data))
        self.assertEqual(r['return'], 0)
        self.assertNotIn('net_recv result stub; no network', r['stubs'])

    def test_header_plus_body_sum_wraps_in_native_gather(self):
        for mode, size in ((0xaa, 36), (0x99, 46)):
            with self.subTest(mode=mode):
                r = probe(LIBRARY, envelope(mode, body=b'', body_length=0xffffffff))
                self.assertEqual((r['return'], r['header_length'], r['body_length'],
                                  r['pending_frame_length']), (0, size, 0xffffffff, size-1))
                self.assertIn(0x3ab6e4, r['branches'])

    def test_exact_wrapped_zero_is_not_a_valid_frame_length(self):
        r = probe(LIBRARY, envelope(body=b'', body_length=0xffffffdc))
        self.assertEqual((r['return'], r['header_length'], r['pending_frame_length']), (0, 36, 0))
        with self.assertRaisesRegex(ValueError, 'incomplete/error'):
            probe(LIBRARY, envelope(body=b'', body_length=0xffffffdc), advance_current=True)

    def test_lookahead_sum_can_wrap_before_promotion(self):
        a = envelope()
        b = envelope(0x99, body=b'', body_length=0xffffffff)
        r = probe(LIBRARY, a+b, advance_current=True)
        self.assertEqual((r['first']['return'], r['first']['lookahead_length']), (0, 45))
        self.assertEqual((r['return'], r['header_length'], r['pending_frame_length']), (0, 46, 45))


if __name__ == '__main__':
    unittest.main()

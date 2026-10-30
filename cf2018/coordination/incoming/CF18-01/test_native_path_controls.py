"""Synthetic native transport/dispatch controls, never a real handshake."""
import hashlib
import os
import unittest
from native_boundary_controls import probe
from native_path_controls import address_factory_probe
from test_native_boundary_controls import envelope

LIBRARY = os.environ.get('CF18_APOLLO_LIBRARY')


@unittest.skipUnless(LIBRARY, 'private pinned Apollo and native dependencies required')
class NativePathTests(unittest.TestCase):
    def test_address_service_dispatch_reaches_gcloud_factory_boundary(self):
        r = address_factory_probe(LIBRARY)
        self.assertEqual((r['stop_code'], r['selected_method']), (-77, 0x3c7e38))
        self.assertTrue(r['stopped_before_method'])
        self.assertEqual(r['calls'], ['CGCloud GetInstance synthetic-object stub'])

    def test_wrong_address_point_selects_different_method_not_connector(self):
        r = address_factory_probe(LIBRARY, address_point_offset=8)
        self.assertEqual(r['selected_method'], 0x3c84b0)
        self.assertTrue(r['stopped_before_method'])
        self.assertNotEqual(r['selected_method'], 0x3c7e38)

    def test_real_net_wrapper_passes_unprefixed_modes_to_native_gather(self):
        for mode in (0xaa, 0x99):
            with self.subTest(mode=mode):
                wire = envelope(mode)
                r = probe(LIBRARY, b'', socket_payload=wire)
                self.assertEqual((r['return'], r['decoded_magic'], r['buffered']),
                                 (0, 0x4366, len(wire)))
                self.assertIn('actual native net_recv wrapper; timeout zero', r['stubs'])
                self.assertIn('imported recv synthetic bytes/EOF stub; no socket', r['stubs'])
                self.assertNotIn('net_recv result stub; no network', r['stubs'])

    def test_raw_prefix_is_not_stripped_by_examined_native_net_wrapper(self):
        for prefix in (b'\x43\x66', b'\x66\x43'):
            with self.subTest(prefix=prefix):
                wire = prefix+envelope()
                r = probe(LIBRARY, b'', socket_payload=wire)
                self.assertEqual((r['return'], r['cursor'], r['buffered']), (-18, 0, len(wire)))
                self.assertEqual(r['remaining_sha256'], hashlib.sha256(wire).hexdigest())

    def test_native_read_appends_to_existing_partial_data(self):
        wire = envelope(0x99)
        r = probe(LIBRARY, wire[:7], socket_payload=wire[7:])
        self.assertEqual((r['return'], r['buffered'], r['pending_frame_length']),
                         (0, len(wire), len(wire)))
        self.assertEqual(r['remaining_sha256'], hashlib.sha256(wire).hexdigest())

    def test_native_wrapper_maps_injected_recv_zero_with_partial_data(self):
        r = probe(LIBRARY, envelope()[:10], socket_payload=b'')
        self.assertEqual(r['return'], -10)
        self.assertIn('imported recv synthetic bytes/EOF stub; no socket', r['stubs'])

    def test_buffered_complete_frame_precedes_injected_recv_zero_error(self):
        r = probe(LIBRARY, envelope(), socket_payload=b'', advance_current=True)
        self.assertEqual((r['first']['return'], r['return']), (0, -10))
        self.assertEqual(r['stubs'], [])

    def test_full_buffer_does_not_call_recv_or_native_wrapper(self):
        wire = envelope(0x99)
        r = probe(LIBRARY, wire, capacity=len(wire), socket_payload=b'')
        self.assertEqual(r['return'], 0)
        self.assertFalse(any('recv' in name for name in r['stubs']))


if __name__ == '__main__':
    unittest.main()

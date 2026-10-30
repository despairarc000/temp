"""Optional original-binary emulation, disabled unless the private source exists."""
import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from native_rx_controls import probe
from test_native_rx_envelope import uint

LIBRARY = os.environ.get('CF18_APOLLO_LIBRARY')


def synthetic(magic=0x4366, body=b'\x00\xff'):
    # All nine base fields have independent synthetic values; no real session.
    base = b'\x11'+uint(magic)
    for field in range(2, 10):
        base += uint((field << 4) | 1)
        base += uint(len(body) if field == 9 else 0)
    header = b'\x15'+len(base).to_bytes(4, 'big')+base
    return b'\xaa'+(len(header)+5).to_bytes(4, 'big')+header+body


@unittest.skipUnless(LIBRARY, 'private fingerprinted original required')
class NativeControls(unittest.TestCase):
    def test_correct_decoded_marker_reaches_zero(self):
        result = probe(LIBRARY, synthetic())
        self.assertEqual(result['return'], 0)
        self.assertEqual(result['decoded_magic'], 0x4366)
        self.assertEqual(result['body_length'], 2)
        self.assertEqual(result['pending_frame_length'], len(synthetic()))
        self.assertEqual(result['cursor'], 0)  # Caller consumes later.

    def test_raw_prefix_orders_fail_before_tlv_decoder(self):
        for prefix in [b'Cf', b'fC']:
            result = probe(LIBRARY, prefix+bytes(63))
            self.assertEqual(result['return'], -18)
            self.assertNotIn(0x3b7340, result['branches'])

    def test_swapped_decoded_marker_has_distinct_error(self):
        result = probe(LIBRARY, synthetic(magic=0x6643))
        self.assertEqual(result['return'], -13)
        self.assertIn(0x3ab74a, result['branches'])

    def test_short_buffer_waits_before_decoding(self):
        for count in [0, 1, 4, 5, 16, 31]:
            result = probe(LIBRARY, synthetic()[:count])
            self.assertEqual(result['return'], -12)
            self.assertNotIn(0x3aab44, result['branches'])

    def test_declared_header_truncation_waits(self):
        result = probe(LIBRARY, b'\xaa'+(80).to_bytes(4, 'big')+bytes(27))
        self.assertEqual(result['return'], -12)

    def test_declared_body_truncation_waits(self):
        data = bytearray(synthetic())
        header_size = int.from_bytes(data[1:5], 'big')
        data[header_size-1] = 80
        result = probe(LIBRARY, bytes(data))
        self.assertEqual(result['return'], -12)
        self.assertEqual(result['pending_frame_length'], header_size + 80)

    def test_coalesced_headers_cache_lookahead(self):
        data = synthetic()
        result = probe(LIBRARY, data+data)
        self.assertEqual(result['return'], 0)
        self.assertEqual(result['lookahead_length'], len(data))
        self.assertEqual(result['cursor'], 0)

    def test_invalid_lookahead_can_reject_current_frame(self):
        result = probe(LIBRARY, synthetic()+b'fC'+bytes(30))
        self.assertEqual(result['return'], -18)
        self.assertEqual(result['cursor'], 0)

    def test_wrong_fingerprint_refused(self):
        import tempfile
        private = Path(__file__).parent/'private'
        private.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private) as temp:
            bad = Path(temp)/'wrong.so'
            bad.write_bytes(b'not a library')
            with self.assertRaises(ValueError):
                probe(bad, synthetic())


if __name__ == '__main__':
    unittest.main()

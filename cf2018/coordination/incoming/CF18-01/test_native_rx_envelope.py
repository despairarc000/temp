"""Independent synthetic fixtures; no client packet or game source bytes."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from native_rx_envelope import Receiver, FrameError


def uint(value):
    result = bytearray()
    while value >= 128:
        result.append((value & 127) | 128)
        value >>= 7
    result.append(value)
    return bytes(result)


def frame(body=b'\x00\xff', magic=0x4366, base_extra=b'', top_extra=b''):
    base = b'\x11' + uint(magic) + b'\x91\x01' + uint(len(body)) + base_extra
    header = b'\x15' + len(base).to_bytes(4, 'big') + base + top_extra
    return b'\xaa' + (len(header) + 5).to_bytes(4, 'big') + header + body


class EnvelopeTests(unittest.TestCase):
    def test_independent_fixture_decodes_framing_only(self):
        r = Receiver()
        result = r.feed(frame())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].body, b'\x00\xff')
        self.assertIsNone(result[0].message_type)
        r.finish()

    def test_every_fragment_boundary(self):
        data = frame(b'\x01\x00\xff\x80')
        for split in range(len(data) + 1):
            r = Receiver()
            result = r.feed(data[:split]) + r.feed(data[split:])
            self.assertEqual([f.body for f in result], [b'\x01\x00\xff\x80'])
            r.finish()

    def test_bytewise_and_coalesced_frames(self):
        data = frame(b'a') + frame(b'\x00\xff')
        r = Receiver()
        result = []
        for b in data:
            result += r.feed(bytes([b]))
        self.assertEqual([f.body for f in result], [b'a', b'\x00\xff'])
        self.assertEqual([f.body for f in Receiver().feed(data)], [b'a', b'\x00\xff'])

    def test_raw_prefix_orders_are_rejected(self):
        for prefix in [b'Cf', b'fC']:
            with self.assertRaises(FrameError):
                Receiver().feed(prefix + frame())

    def test_swapped_decoded_marker_is_rejected(self):
        with self.assertRaisesRegex(FrameError, 'decoded base marker'):
            Receiver().feed(frame(magic=0x6643))

    def test_each_nonempty_truncation_fails_only_at_eof(self):
        data = frame(b'abc')
        for end in range(1, len(data)):
            r = Receiver()
            self.assertEqual(r.feed(data[:end]), [])
            with self.assertRaises(FrameError):
                r.finish()

    def test_header_size_bounds(self):
        for length in [0, 4, 65537, 0x80000000, 0xffffffff]:
            with self.assertRaises(FrameError):
                Receiver().feed(b'\xaa' + length.to_bytes(4, 'big'))

    def test_nested_size_mismatch(self):
        data = bytearray(frame())
        data[6:10] = (len(data) + 1).to_bytes(4, 'big')
        with self.assertRaisesRegex(FrameError, 'nested size'):
            Receiver().feed(bytes(data))

    def test_body_size_mismatch_and_cap(self):
        data = frame(b'ab')
        r = Receiver()
        self.assertEqual(r.feed(data[:-1]), [])
        with self.assertRaises(FrameError):
            r.finish()
        oversized = bytearray(frame(b''))
        oversized[-1] = 80
        with self.assertRaisesRegex(FrameError, 'frame size'):
            Receiver(32).feed(bytes(oversized))

    def test_duplicate_fields_fail_closed(self):
        for data in [frame(base_extra=b'\x11'+uint(0x4366)),
                     frame(top_extra=b'\x15\x00\x00\x00\x00')]:
            with self.assertRaisesRegex(FrameError, 'duplicate'):
                Receiver().feed(data)

    def test_unknown_fields_and_99_are_unsupported_policy(self):
        for data in [frame(base_extra=b'\xa1\x01\x00'),
                     frame(top_extra=b'\x31\x00'), b'\x99'+frame()[1:]]:
            with self.assertRaisesRegex(FrameError, 'unsupported'):
                Receiver().feed(data)

    def test_uint16_and_uint32_overflow(self):
        for data in [frame(magic=0x10000), frame(base_extra=b'\x51'+uint(1<<32))]:
            with self.assertRaisesRegex(FrameError, 'overflow'):
                Receiver().feed(data)

    def test_extension_is_opaque_not_accepted_ack(self):
        data = frame(top_extra=b'\x25\x00\x00\x00\x03\xff\x00\xaa')
        result = Receiver().feed(data)
        self.assertEqual(result[0].body, b'\x00\xff')
        self.assertIsNone(result[0].message_type)

    def test_missing_base_and_body_size(self):
        for header in [b'', b'\x15\x00\x00\x00\x04\x11\xe6\x86\x01']:
            with self.assertRaises(FrameError):
                Receiver().feed(b'\xaa'+(len(header)+5).to_bytes(4,'big')+header)

    def test_budget_and_terminal_failure(self):
        r = Receiver(32)
        with self.assertRaisesRegex(FrameError, 'budget'):
            r.feed(bytes(33))
        self.assertEqual(r.buffer, b'')
        with self.assertRaisesRegex(FrameError, 'failed'):
            r.feed(frame())


if __name__ == '__main__':
    unittest.main()

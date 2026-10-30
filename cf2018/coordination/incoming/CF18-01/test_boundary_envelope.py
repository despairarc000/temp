"""Independent synthetic strict-policy controls; no native serializer oracle."""
import unittest
from boundary_envelope import Receiver, FrameError


def varuint(number):
    parts = []
    while number > 127:
        parts.append((number & 127) | 128)
        number >>= 7
    return bytes(parts + [number])


def fixture(mode=0x99, body=b'\x00\xff', marker=0x4366, declared_body=None,
            base_delta=0, extension=b'', extra_base=b'', all_fields=False):
    # Independent wire recipe: varuint tags, fixed-width BE values for 99.
    fields = [(1, marker)]
    if all_fields:
        fields += [(2, 0x1234), (3, 0xabcd), (4, 0x2002), (5, 0x01020304),
                   (6, 0xfe), (7, 0xa1b2c3d4), (8, 0x11223344)]
    fields += [(9, len(body) if declared_body is None else declared_body)]
    base = b''
    for field, value in fields:
        base += varuint((field << 4) | 1)
        if mode == 0x99:
            width = {1: 2, 2: 2, 3: 2, 4: 2, 6: 1}.get(field, 4)
            base += value.to_bytes(width, 'big')
        else:
            base += bytes([value]) if field == 6 else varuint(value)
    base += extra_base
    nested = b'\x15' + (len(base)+base_delta).to_bytes(4, 'big') + base
    if extension:
        nested += b'\x25'+len(extension).to_bytes(4, 'big')+extension
    return bytes([mode])+(5+len(nested)).to_bytes(4, 'big')+nested+body


class BoundaryEnvelopeTests(unittest.TestCase):
    def test_both_modes_handle_independent_mixed_width_values(self):
        for mode in (0xaa, 0x99):
            with self.subTest(mode=mode):
                wire = fixture(mode, all_fields=True)
                receiver = Receiver()
                frames = receiver.feed(wire)
                self.assertEqual(len(frames), 1)
                self.assertEqual((frames[0].base_type, frames[0].body), (0x2002, b'\0\xff'))
                self.assertEqual(frames[0].header_size, len(wire)-2)
                receiver.finish()

    def test_every_fragment_boundary_in_each_mode(self):
        for mode in (0xaa, 0x99):
            wire = fixture(mode, all_fields=True)
            for split in range(len(wire)+1):
                with self.subTest(mode=mode, split=split):
                    receiver = Receiver()
                    frames = receiver.feed(wire[:split])+receiver.feed(wire[split:])
                    self.assertEqual([f.body for f in frames], [b'\0\xff'])
                    receiver.finish()

    def test_mixed_modes_bytewise_and_coalesced(self):
        a, b = fixture(0xaa, body=b'A'), fixture(0x99, body=b'B')
        for chunks in ([a+b], [bytes([value]) for value in a+b]):
            receiver = Receiver()
            frames = [f for chunk in chunks for f in receiver.feed(chunk)]
            self.assertEqual([f.body for f in frames], [b'A', b'B'])
            receiver.finish()

    def test_swapped_decoded_marker_in_both_modes(self):
        for mode in (0xaa, 0x99):
            with self.subTest(mode=mode), self.assertRaisesRegex(FrameError, 'marker mismatch'):
                Receiver().feed(fixture(mode, marker=0x6643))

    def test_both_raw_prefix_orders_remain_rejected(self):
        for prefix in (b'\x43\x66', b'\x66\x43'):
            with self.subTest(prefix=prefix), self.assertRaises(FrameError):
                Receiver().feed(prefix+fixture())

    def test_each_nonempty_truncation_is_rejected_at_eof(self):
        for mode in (0xaa, 0x99):
            wire = fixture(mode)
            for length in range(1, len(wire)):
                with self.subTest(mode=mode, length=length):
                    receiver = Receiver()
                    self.assertEqual(receiver.feed(wire[:length]), [])
                    with self.assertRaises(FrameError):
                        receiver.finish()

    def test_nested_declared_mismatches_are_strictly_rejected(self):
        for mode in (0xaa, 0x99):
            for delta in (-1, 1):
                with self.subTest(mode=mode, delta=delta), self.assertRaises(FrameError):
                    Receiver().feed(fixture(mode, base_delta=delta))

    def test_fixed_width_field_truncated_inside_complete_header(self):
        # Complete outer header, but uint16 marker has only one value byte.
        base = b'\x11\x43'
        wire = b'\x99'+(12).to_bytes(4, 'big')+b'\x15'+len(base).to_bytes(4, 'big')+base
        with self.assertRaisesRegex(FrameError, 'truncated fixed-width'):
            Receiver().feed(wire)

    def test_total_size_cannot_wrap_or_exceed_cap(self):
        for mode in (0xaa, 0x99):
            for declared in (0xffffffff, 0xffffffdc, 65536):
                with self.subTest(mode=mode, declared=declared), self.assertRaisesRegex(FrameError, 'cap'):
                    Receiver().feed(fixture(mode, body=b'', declared_body=declared))

    def test_body_size_mismatch_waits_then_eof_fails(self):
        for mode in (0xaa, 0x99):
            receiver = Receiver()
            self.assertEqual(receiver.feed(fixture(mode, declared_body=3)), [])
            with self.assertRaises(FrameError):
                receiver.finish()

    def test_duplicate_and_unknown_base_fields_are_proposal_policy(self):
        for extra in (b'\x11\x43\x66', b'\xa1\x01\0\0\0\1'):
            with self.subTest(extra=extra), self.assertRaises(FrameError):
                Receiver().feed(fixture(extra_base=extra))

    def test_extension_stays_opaque_and_base_type_is_not_effective_type(self):
        frame = Receiver().feed(fixture(extension=b'opaque', all_fields=True))[0]
        self.assertEqual(frame.base_type, 0x2002)
        self.assertFalse(hasattr(frame, 'accepted_ack'))

    def test_failure_and_successful_finish_are_terminal(self):
        receiver = Receiver()
        with self.assertRaises(FrameError):
            receiver.feed(b'\xfc')
        self.assertEqual(receiver.buffer, b'')
        with self.assertRaises(FrameError):
            receiver.feed(fixture())
        finished = Receiver()
        finished.feed(fixture())
        finished.finish()
        with self.assertRaisesRegex(FrameError, 'finished'):
            finished.feed(b'')

    def test_padded_fixed_width_tags_are_unsupported(self):
        # Tags are varuint even in 99; four-byte padded tag starts with zero.
        base = b'\0\0\0\x11\x43\x66'
        wire = b'\x99'+(10+len(base)).to_bytes(4, 'big')+b'\x15'+len(base).to_bytes(4, 'big')+base
        with self.assertRaises(FrameError):
            Receiver().feed(wire)


if __name__ == '__main__':
    unittest.main()

"""Necessary conditions for an unchanged original QueryAddrInfo request.

Reference: hash-pinned separately executed native binary header and argument
serializers (ADDRESS_APPLICATION.md), and V3.8.1 diagnostic labels. Source-free
synthetic grammar checks ONLY; no private binary, packet, login, or runtime proof.
"""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from routed_body_diagnostic import diagnose_body


def original_control(service, *, strict=False, sequence=1, game_id=1, unit_id=2):
    """Independently synthesize the native-confirmed format with bounded fields."""
    if type(service) is not bytes or len(service)>32:
        raise ValueError('bounded synthetic service bytes required')
    if any(type(n) is not int or not 0 <= n < 2**64
           for n in (sequence, game_id, unit_id)):
        raise ValueError('synthetic uint64 fields only')
    method=b'QueryAddrInfo'
    header=(b'\x80\x01\x00\x01'+len(method).to_bytes(4,'big')+method+
            sequence.to_bytes(8,'big') if strict else
            len(method).to_bytes(4,'big')+method+b'\x01'+sequence.to_bytes(8,'big'))
    arguments=(b'\x0c\x00\x01' + b'\x0a\x00\x01' + game_id.to_bytes(8,'big')+
               b'\x0a\x00\x02' + unit_id.to_bytes(8,'big')+
               b'\x0b\x00\x03' + len(service).to_bytes(4,'big')+
               service+b'\x00\x00')
    return sequence.to_bytes(4,'big')+header+arguments


def first_change(a,b):
    return next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),
                min(len(a),len(b)))


class NativeSourceBranchNecessaryConditions(unittest.TestCase):
    def test_legacy_length_variation_first_changes_at_61_for_all_service_contents(self):
        for a in (b'A',b'B',b'\xff',b'\x00'):
            for b in (b'A',b'C',b'\x01',b'\xff'):
                small,large=original_control(a*16),original_control(b*21)
                self.assertEqual((len(small),len(large)),(80,85))
                self.assertEqual(first_change(small,large),61)
                for item in (small,large):
                    label=diagnose_body(item,1)
                    self.assertEqual(label['legacy_after_sequence'],
                                     'LEGACY_HEADER_PLAUSIBLE')

    def test_changing_original_request_ids_can_only_move_difference_earlier(self):
        small=original_control(b'A'*16)
        self.assertLessEqual(first_change(small,original_control(b'B'*21,game_id=42)),61)
        self.assertLessEqual(first_change(small,original_control(b'B'*21,unit_id=42)),61)

    def test_strict_size_and_prefix_can_fit_first_difference_but_not_method_failure(self):
        small=original_control(b'A'*13,strict=True)
        large=original_control(b'C'*18,strict=True)
        self.assertEqual((len(small),len(large)),(80,85))
        self.assertEqual(first_change(small,large),64)
        for item in (small,large):
            self.assertEqual(item[4:8],b'\x80\x01\x00\x01')
            self.assertEqual(diagnose_body(item,1)['legacy_after_sequence'],
                             'VERSIONED_PREFIX_CANDIDATE')

    def test_original_legacy_name_start_is_fixed_ascii_and_length_13(self):
        for raw in (b'A'*16,b'\xff'*21):
            item=original_control(raw)
            self.assertEqual(int.from_bytes(item[4:8],'big'),13)
            self.assertEqual(item[8:21],b'QueryAddrInfo')
            self.assertEqual(diagnose_body(item,1)['legacy_after_sequence'],
                             'LEGACY_HEADER_PLAUSIBLE')

    def test_input_negative_controls_are_bounded(self):
        for raw in (bytearray(b'A'),b'A'*33,'invalid'):
            with self.assertRaises(ValueError):original_control(raw)
        for id_value in (True,-1,2**64,1.5):
            with self.assertRaises(ValueError):original_control(b'A',game_id=id_value)


if __name__=='__main__':
    unittest.main()

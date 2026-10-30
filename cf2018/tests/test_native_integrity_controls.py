"""Synthetic predicates, not the cause of a historical phone exit."""
import os
from pathlib import Path
import sys
import unittest
import zlib
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from native_integrity_controls import (classify_branch, native_crc,
                                      postload_comparison, mono_handoff)
TPRT, MONO = os.environ.get('CF18_TPRT_LIBRARY'), os.environ.get('CF18_MONO_LIBRARY')


class BoundsTests(unittest.TestCase):
    def test_invalid_controls_rejected_before_source_access(self):
        for call in (lambda: classify_branch('absent', b'A', 10),
                     lambda: classify_branch('absent', b'ABCD', 3),
                     lambda: native_crc('absent', bytes(4097)),
                     lambda: postload_comparison('absent', -1, 0)):
            with self.assertRaises(ValueError): call()


@unittest.skipUnless(TPRT, 'private pinned libtprt and native dependencies required')
class NativeIntegrityTests(unittest.TestCase):
    def test_real_crc_matches_independent_standard_vectors(self):
        for b in (b'', b'123456789', bytes(range(256)), bytes(4096)):
            with self.subTest(size=len(b)):
                self.assertEqual(native_crc(TPRT, b), zlib.crc32(b))

    def test_non_pe_signature_selects_transform_before_loader(self):
        r=classify_branch(TPRT,b'ABCD',8192)
        self.assertEqual(r['events'],[{'site':0x3512,'transform_mode':6,'input_offset':0}])
        self.assertTrue(r['input_unchanged'])

    def test_mz_takes_distinct_branch_not_proven_loadable(self):
        r=classify_branch(TPRT,b'MZ00',8192)
        self.assertEqual(r['events'][0]['site'],0x351e)
        self.assertIsNone(r['events'][0]['transform_mode'])

    def test_txp_size_classes_and_prefix_copy_are_native(self):
        for length,mode in ((4096,7),(8192,8)):
            r=classify_branch(TPRT,b'TXP0',length)
            self.assertEqual(r['events'][0]['transform_mode'],mode)
            self.assertEqual(r['events'][0]['input_offset'],4)
            self.assertFalse(r['input_unchanged'])
            self.assertEqual(r['stubs'],['bounded four-byte memcpy'])

    def test_equal_supplied_checksums_take_normal_boundary(self):
        r=postload_comparison(TPRT,123,123)
        self.assertEqual(r['events'][-1][0],'normal_return_boundary')

    def test_nonzero_mismatch_requests_termination18_before_syscall(self):
        r=postload_comparison(TPRT,123,124)
        self.assertIn(['native_site',0x3616],r['events'])
        self.assertEqual(r['events'][-1],['termination_requested',18])
        self.assertEqual(len(r['stubs']),2)

    def test_missing_zero_checksum_is_not_mismatch_termination(self):
        for pair in ((0,124),(123,0),(0,0)):
            self.assertEqual(postload_comparison(TPRT,*pair)['events'][-1][0],
                             'normal_return_boundary')


@unittest.skipUnless(TPRT and MONO, 'both private pinned native libraries required')
class NativeHandoffTests(unittest.TestCase):
    def test_original_mono_entry_routes_to_tprt_slot26(self):
        r=mono_handoff(MONO,TPRT)
        self.assertEqual(r['sites'],[0x196c38,0x14da4,0x3d5fec,0x5033fc])
        self.assertEqual(r['target_rva'],0x33fc)
        self.assertTrue(r['arguments_preserved'])
        self.assertEqual(len(r['relocations']),2)

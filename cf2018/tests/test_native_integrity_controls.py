"""Synthetic predicates, not the cause of a historical phone exit."""
import os
from pathlib import Path
import sys
import unittest
import zlib
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from native_integrity_controls import (classify_branch, native_crc,
                                      postload_comparison, mono_handoff,
                                      startup_status_predicate, startup_exit_boundary,
                                      simple_rtti_name, startup_checker_identity, rtti_name)
TPRT, MONO = os.environ.get('CF18_TPRT_LIBRARY'), os.environ.get('CF18_MONO_LIBRARY')


class BoundsTests(unittest.TestCase):
    def test_nested_rtti_names_preserve_namespace_and_reject_bad_lengths(self):
        self.assertEqual(rtti_name(b'N7tpshell8TPThreadE'),'tpshell::TPThread')
        self.assertEqual(rtti_name(b'N10__cxxabiv120__si_class_type_infoE'),'__cxxabiv1::__si_class_type_info')
        self.assertEqual(rtti_name(b'9OtherType'),'OtherType')
        for raw in [b'N7tpshell7TPThreadE',b'N7tpshell8TPThread',b'N7tpshellE',b'N0E',b'N7tpshell8TPThreadESECRET']:
            with self.subTest(raw=raw),self.assertRaises(ValueError):rtti_name(raw)

    def test_rtti_simple_name_lengths_and_unrelated_names(self):
        self.assertEqual(simple_rtti_name(b'11FileChecker'),'FileChecker')
        self.assertEqual(simple_rtti_name(b'9OtherType'),'OtherType')
        for raw in [b'10FileChecker',b'0',b'11FileChecker\0SECRET',b'999TooLong',b'2\xff\xff']:
            with self.subTest(raw=raw),self.assertRaises(ValueError):simple_rtti_name(raw)

    def test_invalid_controls_rejected_before_source_access(self):
        for call in (lambda: classify_branch('absent', b'A', 10),
                     lambda: classify_branch('absent', b'ABCD', 3),
                     lambda: native_crc('absent', bytes(4097)),
                     lambda: postload_comparison('absent', -1, 0),
                     lambda: startup_status_predicate('absent', -1),
                     lambda: startup_exit_boundary('absent', 0, producer='other')):
            with self.assertRaises(ValueError): call()


@unittest.skipUnless(TPRT, 'private pinned libtprt and native dependencies required')
class NativeIntegrityTests(unittest.TestCase):
    def test_original_rtti_links_file_checker_to_code_four_method(self):
        result=startup_checker_identity(TPRT)
        self.assertEqual(result,{'type_name':'FileChecker','vtable':0x22478,
                                'typeinfo':0x2248c,'virtual_method':0x50fc,
                                'thumb':True,'phone_path_observed':False,
                                'typeinfo_kind':'__cxxabiv1::__si_class_type_info',
                                'base_type':'tpshell::TPThread','base_typeinfo':0x224ac})

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

    def test_actual_status_predicate_accepts_zero_or_101_through_200(self):
        for value in [0,101,150,200]:
            self.assertEqual(startup_status_predicate(TPRT,value),1)
        for value in [1,4,18,100,201,0xffffffff]:
            self.assertEqual(startup_status_predicate(TPRT,value),0)

    def test_actual_failure_landing_selects_four_and_wrapper_preserves_other_status(self):
        for supplied in [0,18]:
            self.assertEqual(startup_exit_boundary(TPRT,supplied),
                             {'exit_argument':4,'syscall_number':248,'stopped_before_syscall':True})
        self.assertEqual(startup_exit_boundary(TPRT,18,producer=False),
                         {'exit_argument':18,'syscall_number':248,'stopped_before_syscall':True})


@unittest.skipUnless(TPRT and MONO, 'both private pinned native libraries required')
class NativeHandoffTests(unittest.TestCase):
    def test_original_mono_entry_routes_to_tprt_slot26(self):
        r=mono_handoff(MONO,TPRT)
        self.assertEqual(r['sites'],[0x196c38,0x14da4,0x3d5fec,0x5033fc])
        self.assertEqual(r['target_rva'],0x33fc)
        self.assertTrue(r['arguments_preserved'])
        self.assertEqual(len(r['relocations']),2)

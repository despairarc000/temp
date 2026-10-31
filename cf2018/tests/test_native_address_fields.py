import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from native_address_fields import query_args, result_fields
from native_rpc_header import binary_header
LIB = os.environ.get('CF18_APOLLO_LIBRARY')


def response(*, result=True, reason=True, status=0):
    payload = (b'\x08\0\1' + status.to_bytes(4, 'big', signed=True)) if result else b''
    if reason:
        payload += b'\x0b\0\2' + bytes(4)  # explicitly empty STRING, no account content
    return b'\x0c\0\0' + payload + b'\0\0'


class BoundsTests(unittest.TestCase):
    def test_unbounded_service_before_source(self):
        for size in (-1, 33, True):
            with self.assertRaises(ValueError): query_args('missing', service_size=size)
    def test_unbounded_result_before_source(self):
        for wire in (b'', bytes(65), bytearray(b'A')):
            with self.assertRaises(ValueError): result_fields('missing', wire)


@unittest.skipUnless(LIB, 'private pinned Apollo/native dependencies required')
class NativeAddressTests(unittest.TestCase):
    def test_generated_query_matches_independent_field_grammar(self):
        for size in (0, 9, 16, 21, 32):
            actual = query_args(LIB, service_size=size)
            expected = b'\x0c\0\1\x0a\0\1' + (1).to_bytes(8, 'big') + b'\x0a\0\2' + (2).to_bytes(8, 'big')
            expected += b'\x0b\0\3' + size.to_bytes(4, 'big') + b'A'*size + b'\0\0'
            self.assertEqual(actual['wire'], expected)
            self.assertEqual(actual['return'], 34+size)
            self.assertEqual(actual['remaining_depth'], 0)
    def test_full_u64_fields_and_order(self):
        actual = query_args(LIB, game_id=2**64-1, unit_id=0)['wire']
        self.assertEqual(actual[6:14], bytes([255])*8)
        self.assertEqual(actual[17:25], bytes(8))
    def test_v38_sizes_in_simple_model_first_differ_at61(self):
        header = binary_header(LIB, sequence=1)['wire']
        bodies = [bytes(3)+b'\1'+header+query_args(LIB, service_size=n)['wire'] for n in (16,21)]
        self.assertEqual([len(x) for x in bodies], [80,85])
        self.assertEqual(next(i for i,(a,b) in enumerate(zip(*bodies)) if a != b), 61)
    @unittest.skipUnless(os.environ.get('CF18_V38_SOURCE'), 'exact private v38 source required')
    def test_complete_native_legacy_and_versioned_requests_are_found_by_existing_observer(self):
        import hashlib
        import json
        root = Path(__file__).resolve().parents[1]
        source = Path(os.environ['CF18_V38_SOURCE']).resolve()
        pins = json.loads((root / 'coordination/V38_SOURCE_PINS.json').read_text())
        for name, digest in pins.items():
            self.assertEqual(hashlib.sha256((source / name).read_bytes()).hexdigest(), digest)
        sys.path.insert(0, str(source))
        from routed_fingerprint_v23 import inspect_application_body
        from legacy_thrift_v37 import classify_legacy_thrift
        for strict, sizes in ((False, (16,21)), (True, (13,18))):
            bodies = [bytes(3)+b'\1'+binary_header(LIB, strict=strict, sequence=1)['wire']+
                      query_args(LIB, service_size=n)['wire'] for n in sizes]
            self.assertEqual([len(x) for x in bodies], [80,85])
            self.assertEqual(next(i for i,(a,b) in enumerate(zip(*bodies)) if a != b), 64 if strict else 61)
            for body in bodies:
                self.assertEqual(inspect_application_body(body, [])['app_rpc_offset'], 'after_4')
                legacy = classify_legacy_thrift(body)['thrift_candidate']
                self.assertEqual(legacy, 'not_identified' if strict else 'legacy_complete_candidate')
    def test_present_empty_reason_and_result_decode(self):
        r = result_fields(LIB, response())
        self.assertEqual(r['native_return'], 19)
        self.assertTrue(r['wrapper_presence'])
        self.assertIsNone(r['failed_predicate'])
    def test_missing_result_stops_at_actual_required_field_branch(self):
        r = result_fields(LIB, response(result=False))
        self.assertEqual(r['failed_predicate']['address'], '0x39eaae')
        self.assertIsNone(r['native_return'])
    def test_missing_reason_stops_at_actual_required_field_branch(self):
        r = result_fields(LIB, response(reason=False))
        self.assertEqual(r['failed_predicate']['address'], '0x39ead8')
        self.assertFalse(r['wrapper_presence'])
    def test_missing_wrapper_does_not_set_presence(self):
        r = result_fields(LIB, b'\0')
        self.assertEqual(r['native_return'], 1)
        self.assertFalse(r['wrapper_presence'])
    def test_nonzero_result_still_decodes_not_success_or_acceptance(self):
        r = result_fields(LIB, response(status=7))
        self.assertEqual(r['native_return'], 19)
        self.assertEqual(r['result'], 7)
        self.assertTrue(r['wrapper_presence'])
    def test_truncation_is_transport_refusal_not_native_error_claim(self):
        with self.assertRaisesRegex(ValueError, 'not a native decoder return'):
            result_fields(LIB, response()[:-1])

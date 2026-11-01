import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from native_syn_ack_handoff import probe


@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'), 'explicit private original required')
class OriginalControls(unittest.TestCase):
    def run_case(self, **kw):
        return probe(os.environ['CF18_APOLLO_LIBRARY'], **kw)

    def test_ten_and_twelve_byte_routes_reach_same_auth_boundary(self):
        for size in (10, 12):
            with self.subTest(size=size):
                r = self.run_case(name_size=size)
                self.assertTrue(r['syn_prepared_named_route'])
                self.assertTrue(r['synthetic_name_copied'])
                self.assertEqual(r['return'], -77)
                self.assertTrue(r['auth_send_boundary'])
                self.assertEqual(r['state'], 2)
                self.assertEqual(r['consumed'], 63)

    def test_bad_frames_do_not_reach_auth_boundary(self):
        for variant, code in [('wrong_magic', -13), ('bad_key', -30),
                              ('prefixed', -18), ('truncated', 0)]:
            with self.subTest(variant=variant):
                r = self.run_case(variant=variant)
                self.assertEqual(r['return'], code)
                self.assertFalse(r['auth_send_boundary'])

    def test_relay_does_not_construct_named_route(self):
        r = self.run_case(relay=True)
        self.assertFalse(r['syn_prepared_named_route'])
        self.assertFalse(r['synthetic_name_copied'])

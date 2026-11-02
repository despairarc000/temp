import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from native_rpc_unit_trace import parse_synthetic_unit, rpc_unit_override
from native_syn_ack_handoff import application_prefix, probe


@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'), 'explicit original Apollo required')
class Tests(unittest.TestCase):
    def test_original_domain_parser_selects_synthetic_unit(self):
        for unit in (1, 3):
            r = parse_synthetic_unit(os.environ['CF18_APOLLO_LIBRARY'], unit)
            self.assertEqual(r['return'], 0)
            self.assertTrue(r['unit_matches_synthetic_input'])
            self.assertTrue(r['game_matches_synthetic_input'])

    def test_malformed_domain_fails(self):
        self.assertEqual(parse_synthetic_unit(os.environ['CF18_APOLLO_LIBRARY'], malformed=True)['return'], -2)

    def test_original_rpc_override_stores_parser_unit(self):
        for unit in (1, 3):
            self.assertTrue(rpc_unit_override(os.environ['CF18_APOLLO_LIBRARY'], unit))

    def test_unit_one_to_three_changes_only_same_length_field_five(self):
        p = os.environ['CF18_APOLLO_LIBRARY']
        a, b = application_prefix(p, 'unit_id'), application_prefix(p, 'unit_3')
        self.assertEqual([i for i in a if a[i] != b[i]], [5])
        self.assertEqual(len(a[5]), len(b[5]))
        self.assertTrue(probe(p, attribute='unit_3')['auth_send_boundary'])
        self.assertFalse(probe(p, attribute='unit_3', variant='bad_key')['auth_send_boundary'])

import os
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from native_syn_ack_handoff import application_prefix, probe


@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'), 'explicit private original required')
class Tests(unittest.TestCase):
    def test_original_serializer_maps_application_changes(self):
        p = os.environ['CF18_APOLLO_LIBRARY']; ref = application_prefix(p)
        self.assertEqual(set(ref), set(range(1, 8)))
        for name, field in [('game_id', 4), ('unit_id', 5), ('client_type', 6)]:
            with self.subTest(attribute=name):
                cur = application_prefix(p, name)
                self.assertEqual(set(cur), set(ref))
                self.assertEqual([n for n in ref if cur[n] != ref[n]], [field])
                self.assertEqual(len(cur[field]), len(ref[field]))

    def test_each_application_change_can_reach_auth_boundary(self):
        for name in ('game_id', 'unit_id', 'client_type'):
            with self.subTest(attribute=name):
                r = probe(os.environ['CF18_APOLLO_LIBRARY'], attribute=name)
                self.assertEqual(r['return'], -77)
                self.assertTrue(r['auth_send_boundary'])
                self.assertEqual(r['consumed'], 63)

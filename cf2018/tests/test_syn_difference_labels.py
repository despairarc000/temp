import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'experiments'), str(ROOT/'tests')]
from prepare_syn_difference import diagnose
from test_second_service_syn_gate import make


class Tests(unittest.TestCase):
    def test_same_length_other_field_identified_without_value(self):
        r = diagnose(make(b'SECRET1234', b'Z'*20), make())
        self.assertEqual(r, dict(reason='NON_ROUTE_SYN_CHANGED', base_changed=[], syn_changed=[[1, 5]]))
        self.assertNotIn('SECRET', repr(r)); self.assertNotIn('ZZZ', repr(r))

    def test_base_change_identified(self):
        self.assertEqual(diagnose(make(b'SECRET1234', base_extra=1), make())['base_changed'], [[5, 0]])

    def test_route_only_and_reference_distinguished(self):
        self.assertEqual(diagnose(make(), make())['reason'], 'REFERENCE_EXACT')
        self.assertEqual(diagnose(make(b'SECRET1234'), make())['reason'], 'MATCH_EXCEPT_ROUTE')

    def test_malformed_is_not_comparable(self):
        for b in (None, b'', make(b'SECRET1234')[:-1]):
            self.assertEqual(diagnose(b, make())['reason'], 'NOT_COMPARABLE')

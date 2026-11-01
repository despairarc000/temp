"""Native-source gated original receive-path checks and source-free negatives."""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from native_address_rx_branch_audit import PINS, audit, compare, parse_lines


class Tests(unittest.TestCase):
    def test_distinct_expected_pins(self):
        self.assertEqual(len(PINS), 15)
        self.assertEqual(len({p[0] for p in PINS.values()}), 15)

    def test_exact_synthetic_control(self):
        self.assertEqual(compare({a: (m, s) for a, m, s in PINS.values()}), [])

    def test_every_modified_instruction_rejected(self):
        original = {a: (m, s) for a, m, s in PINS.values()}
        for name, (address, mnemonic, args) in PINS.items():
            with self.subTest(name=name):
                changed = dict(original)
                changed[address] = (mnemonic, 'invalid-operand')
                self.assertIn(name, compare(changed))

    def test_missing_instruction_rejected(self):
        present = {a: (m, s) for a, m, s in PINS.values()}
        del present[PINS['pending_find'][0]]
        self.assertEqual(compare(present), ['pending_find'])

    def test_parser_strips_symbol_comments(self):
        got = parse_lines(
            '  39baa0: 2b02 cmp r3, #0x2\n'
            '  39bdea: f7ff fcee bl 0x39b7ca <address> @ 0x999'
        )
        self.assertEqual(got[0x39baa0], ('cmp','r3, #0x2'))
        self.assertEqual(got[0x39bdea], ('bl','0x39b7ca'))

    def test_private_original_only_when_supplied(self):
        path = os.environ.get('CF18_APOLLO_LIBRARY')
        if not path:
            self.skipTest('hash-pinned private Apollo not supplied')
        result = audit(path)
        self.assertEqual((result['checks'], result['passed']), (15, 15))
        self.assertTrue(result['verified_original'])
        self.assertFalse(result['native_executed'])
        self.assertFalse(result['client_accepted_reply'])


if __name__ == '__main__':
    unittest.main()

"""Source-free negative checks; optional hash-pinned original-native audit."""
import os
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from native_address_ingress_audit import PINS, parse_instructions, compare, audit


class Tests(unittest.TestCase):
    def test_16_unique_native_pins(self):
        self.assertEqual(len(PINS), 16)
        self.assertEqual(len({item[1] for item in PINS}), 16)

    def test_source_free_positive_control(self):
        self.assertEqual(compare({addr: (op, operand)
                                  for _,addr,op,operand in PINS}), [])

    def test_each_missing_or_changed_pin_rejected(self):
        original = {addr: (op, operand)
                    for _,addr,op,operand in PINS}
        for name, addr, op, operand in PINS:
            with self.subTest(name=name):
                incomplete = dict(original)
                del incomplete[addr]
                self.assertEqual(compare(incomplete), [name])
                changed = dict(original)
                changed[addr] = (op, operand + 'x')
                self.assertEqual(compare(changed), [name])

    def test_disassembly_parser_discards_annotations(self):
        code = ('  3a4f4c: f003 fe7e bl 0x3a8c4c <foo> @ imm = #1\n'
                '  39baa0: 2b02 cmp r3, #0x2\n')
        ins = parse_instructions(code)
        self.assertEqual(ins[0x3a4f4c], ('bl', '0x3a8c4c'))
        self.assertEqual(ins[0x39baa0], ('cmp', 'r3, #0x2'))

    def test_non_original_source_rejected(self):
        with self.assertRaises((OSError, ValueError)):
            audit(__file__)

    def test_original_only_when_supplied(self):
        library = os.environ.get('CF18_APOLLO_LIBRARY')
        if not library:
            self.skipTest('private original Apollo not provided')
        report = audit(library)
        self.assertEqual((report['checks'], report['passed'], report['failed']),
                         (16, 16, []))
        self.assertEqual(report['server_return_framing'], 'NOT_VERIFIED')
        self.assertFalse(report['live_response_sent'])


if __name__ == '__main__':
    unittest.main()

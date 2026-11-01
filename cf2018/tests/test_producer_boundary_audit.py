"""Synthetic and private-source gated tests for the producer boundary audit."""
import contextlib
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
import producer_boundary_audit as p


class SourceFreeTests(unittest.TestCase):
    def test_pin_counts_and_unique_addresses(self):
        self.assertEqual(len(p.PINS), 24)
        self.assertEqual(len({item[1] for item in p.PINS}), 24)

    def test_parser_strips_symbol_text_and_opcode_values(self):
        sample = ('  39991c: f005 fa16     bl 0x39ed4c <private-native-symbol> @ imm=0x542c\n'
                  '  3c1f46: 47e0          blx r12\n'
                  '  3c193e: 6522          str r2, [r4, #0x50]\n')
        self.assertEqual(p.parse_instructions(sample), {
            0x39991c: ('bl', '0x39ed4c'),
            0x3c1f46: ('blx', 'r12'),
            0x3c193e: ('str', 'r2, [r4, #0x50]')})

    def test_absent_or_mismatched_pin_fails_closed(self):
        good = {addr: (mnemonic, operand) for _, addr, mnemonic, operand in p.PINS}
        passed, failed = p.audit_instructions(good)
        self.assertEqual(len(passed), 24)
        self.assertFalse(failed)
        del good[0x3c1f46]
        _, failed = p.audit_instructions(good)
        self.assertIn('write_end_invokes_bound_callback', failed)
        good[0x3c1f46] = ('blx', 'r10')
        _, failed = p.audit_instructions(good)
        self.assertIn('write_end_invokes_bound_callback', failed)

    def test_tampered_source_refused_before_execution(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'not-original.so'
            path.write_bytes(b'A' * 32)
            with self.assertRaisesRegex(ValueError, 'source size mismatch'):
                p.audit(path)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(p.main(['--lib', str(path)]), 2)

    def test_no_network_or_original_binaries_in_script(self):
        text = Path(p.__file__).read_text()
        for disallowed in ('socket.create_connection', 'requests.get',
                           'urllib.request.urlopen', 'adb shell', 'XAPK'):
            self.assertNotIn(disallowed, text)


@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'),
                     'exact owner-authorized private source required')
class OriginalNativeReadOnlyTests(unittest.TestCase):
    def test_actual_24_native_callsite_pins(self):
        result = p.audit(Path(os.environ['CF18_APOLLO_LIBRARY']))
        self.assertEqual(result['checks'], 24)
        self.assertEqual(result['passed'], 24, result['failed'])
        self.assertEqual(result['failed'], [])
        self.assertFalse(result['native_execution'])
        self.assertFalse(result['phone_test'])


if __name__ == '__main__':
    unittest.main()

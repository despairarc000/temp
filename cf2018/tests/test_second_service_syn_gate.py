import sys
import unittest
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'experiments')]
from second_service_syn_gate import compare_security_context


def vi(n):
    out = bytearray()
    while n >= 128:
        out.append((n & 127) | 128); n >>= 7
    return bytes(out) + bytes([n])


def nest(n, p):
    return vi(n << 4 | 5) + len(p).to_bytes(4, 'big') + p


def make(name=b'QueryAddrSvr', security=b'K' * 20, base_extra=0, overlong=False):
    base = b'\x10' + vi(0x4366) + b'\x40' + vi(0x1001) + b'\x61\x00' + vi(9 << 4) + b'\x00\x50' + vi(base_extra)
    route = nest(4, nest(1, name))
    if overlong:
        route = b'\xc5\x00' + route[1:]
    syn = nest(1, security) + nest(14, route)
    # Keep independent synthetic pair exactly 133/131 bytes.
    missing = 121 + len(name) - 7 - len(nest(1, base) + nest(2, nest(0x1001, syn)))
    syn += nest(15, b'P' * (missing - len(nest(15, b''))))
    head = nest(1, base) + nest(2, nest(0x1001, syn))
    return b'\x43\x66\xaa' + (5+len(head)).to_bytes(4, 'big') + head


class Tests(unittest.TestCase):
    def test_match_has_only_fixed_label(self):
        a, b = make(), make(b'SECRET1234')
        self.assertEqual((len(a), len(b)), (133, 131))
        self.assertEqual(compare_security_context(b, a), 'MATCH_EXCEPT_ROUTE')
        self.assertNotIn('SECRET', compare_security_context(b, a))

    def test_same_length_security_change_refused(self):
        self.assertEqual(compare_security_context(make(b'SECRET1234', b'Z' * 20), make()), 'REFUSED')

    def test_base_value_change_refused(self):
        self.assertEqual(compare_security_context(make(b'SECRET1234', base_extra=1), make()), 'REFUSED')

    def test_encoding_change_refused(self):
        self.assertEqual(compare_security_context(make(b'SECRET1234', overlong=True), make()), 'REFUSED')

    def test_bad_or_unrelated_input_refused(self):
        for p in (None, b'', make(b'SECRET1234')[:-1], make(b'SECRET1234')+b'x', make()):
            self.assertEqual(compare_security_context(p, make()), 'REFUSED')

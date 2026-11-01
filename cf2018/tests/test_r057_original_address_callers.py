"""Synthetic ELF32/Thumb tests + optional exact-private-source gate for R057."""
import importlib.util
import os
import struct
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "r057_original_address_callers", ROOT / "experiments/r057_original_address_callers.py")
r057 = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = r057
spec.loader.exec_module(r057)


def make_bl(site, target):
    delta = (target - site - 4) & 0x1FFFFFF
    s, i1, i2 = (delta >> 24) & 1, (delta >> 23) & 1, (delta >> 22) & 1
    j1, j2 = 1 ^ i1 ^ s, 1 ^ i2 ^ s
    return (0xF000 | (s << 10) | ((delta >> 12) & 1023),
            0xD000 | (j1 << 13) | (j2 << 11) | ((delta >> 1) & 2047))


def fixture_elf():
    raw = bytearray(1024)
    raw[:6] = b"\x7fELF\x01\x01"
    struct.pack_into("<H", raw, 18, 40)
    struct.pack_into("<I", raw, 32, 0x80)  # section header table
    struct.pack_into("<HH", raw, 46, 40, 4)
    # Section 1: executable PROGBITS at vaddr 0x1000
    struct.pack_into("<10I", raw, 0x80 + 40,
                     0, 1, 4, 0x1000, 0x200, 64, 0, 0, 2, 0)
    # Section 2: associated name string table
    strings = b"\0" + b"synthetic_foo\0"
    struct.pack_into("<10I", raw, 0x80 + 80,
                     0, 3, 0, 0, 0x260, len(strings), 0, 0, 1, 0)
    raw[0x260:0x260+len(strings)] = strings
    # Section 3: 2 symbols (null and synthetic function)
    struct.pack_into("<10I", raw, 0x80 + 120,
                     0, 2, 0, 0, 0x300, 32, 2, 0, 4, 16)
    struct.pack_into("<IIIBBH", raw, 0x310, 1, 0x1001, 64, 2, 0, 1)
    struct.pack_into("<HH", raw, 0x200 + 8, *make_bl(0x1008, 0x2200))
    return bytes(raw)


class Tests(unittest.TestCase):
    def test_thumb_bl_forward(self):
        a, b = make_bl(0x3A6890, 0x39D18C)
        self.assertEqual(r057.thumb_bl_target(a, b, 0x3A6890), 0x39D18C)

    def test_thumb_bl_backward(self):
        site, target = 0x3C334E, 0x39D18C
        a, b = make_bl(site, target)
        self.assertEqual(r057.thumb_bl_target(a, b, site), target)

    def test_known_independent_original_bl_sites(self):
        for site, target in ((0x3C6C4A, 0x3A33A0), (0x3B5926, 0x3AFEFA)):
            a, b = make_bl(site, target)
            self.assertEqual(r057.thumb_bl_target(a, b, site), target)

    def test_blx_and_other_instruction_not_claimed(self):
        a, b = make_bl(0x1008, 0x2200)
        self.assertIsNone(r057.thumb_bl_target(a, b & ~0x1000, 0x1008))
        self.assertIsNone(r057.thumb_bl_target(0x1234, b, 0x1008))

    def test_synthetic_elf_executable_symbol_and_callsite(self):
        raw = fixture_elf()
        executable, funcs = r057.parse_elf(raw)
        self.assertEqual(len(executable), 1)
        self.assertEqual(r057.containing_symbol(funcs, 0x1008), "synthetic_foo")
        self.assertEqual(r057.direct_calls(raw, executable, {0x2200})[0x2200], {0x1008})

    def test_nonmatching_target_not_found(self):
        raw = fixture_elf()
        ex, _ = r057.parse_elf(raw)
        self.assertEqual(r057.direct_calls(raw, ex, {0x1234})[0x1234], set())

    def test_elf_format_rejections(self):
        raw = fixture_elf()
        for data in (b"hello", raw[:40], raw[:18] + b"\0\0" + raw[20:],
                     raw[:46] + b"\0\0" + raw[48:]):
            with self.subTest(length=len(data)):
                with self.assertRaises((ValueError, struct.error)):
                    r057.parse_elf(data)

    def test_no_wrong_source_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            wrong = Path(tmp) / "libapollo.so"
            wrong.write_bytes(fixture_elf())
            with self.assertRaisesRegex(ValueError, "incorrect original library size"):
                r057.audit(wrong)
            self.assertEqual(wrong.read_bytes(), fixture_elf())

    def test_pinned_direct_edges_unique(self):
        self.assertEqual(sum(len(d) for d in r057.EXPECTED.values()), 6)
        self.assertEqual(set(r057.EXPECTED[r057.ADDRESS_SERVICE_GET]),
                         {0x3A6890, 0x3C334E})


    def test_callback_symbol_checks_are_distinct_from_execution(self):
        sample = [
            r057.Func(0x1000, 20, "_ZN6GCloud19CDefaultNameService19OnGetServiceAddressEiPv"),
            r057.Func(0x1100, 20, "_ZN6GCloud5CTGcp17OnQueryNameResultEiPv"),
            r057.Func(0x1200, 20, "_ZNSt3tr117_Function_handler_foo_CDefaultNameService"),
        ]
        self.assertTrue(all(r057.callback_symbol_evidence(sample).values()))
        for i in range(len(sample)):
            with self.subTest(missing_index=i):
                self.assertFalse(all(r057.callback_symbol_evidence(
                    sample[:i] + sample[i+1:]).values()))

    def test_exact_private_original_optional(self):
        original = os.environ.get("CF18_APOLLO_LIBRARY")
        if not original:
            self.skipTest("exact original private Apollo not available in CI")
        result = r057.audit(original)
        self.assertTrue(result["sha256_match"])
        self.assertEqual(result["original_direct_edges_verified"], 6)
        self.assertEqual(result["address_service_direct_caller_count"], 2)
        self.assertEqual(result["actual_ten_byte_route_name"], "NOT_IDENTIFIED")


if __name__ == "__main__":
    unittest.main()

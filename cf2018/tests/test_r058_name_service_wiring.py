"""Focused source-only tests for R058 original name-service wiring."""
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from r058_name_service_wiring import (
    EXPECTED_EDGES, EXPECTED_HALFW, EXPECTED_VTABLE,
    progbits_sections, virtual_file_offset, pinned_data_failures, audit
)


def small_elf():
    raw = bytearray(2048)
    raw[:6] = b"\x7fELF\x01\x01"
    struct.pack_into("<H", raw, 18, 40)
    struct.pack_into("<I", raw, 32, 0x80)
    struct.pack_into("<HH", raw, 46, 40, 2)
    struct.pack_into("<10I", raw, 0x80 + 40,
                     0, 1, 4, 0x1000, 0x200, 0x100, 0, 0, 4, 0)
    return bytes(raw)


class NameServiceTests(unittest.TestCase):
    def test_expected_native_edge_count(self):
        self.assertEqual(sum(map(len, EXPECTED_EDGES.values())), 3)

    def test_source_observer_pins_present(self):
        self.assertEqual(len(EXPECTED_HALFW), 7)
        self.assertEqual(len(EXPECTED_VTABLE), 6)

    def test_vtable_distinguishes_query_update_observer(self):
        self.assertEqual(len({EXPECTED_VTABLE[x] for x in (
            0x4F5088, 0x4F508C, 0x4F5090)}), 3)

    def test_elf_mapping(self):
        s = progbits_sections(small_elf())
        self.assertEqual(virtual_file_offset(s, 0x1008, 4), 0x208)

    def test_unmapped_refused(self):
        with self.assertRaises(ValueError):
            virtual_file_offset(progbits_sections(small_elf()), 0x1100, 4)

    def test_overlapping_mappings_refused(self):
        s = progbits_sections(small_elf())[0]
        with self.assertRaises(ValueError):
            virtual_file_offset([s, s], 0x1008, 4)

    def test_non_elf_refused(self):
        with self.assertRaises(ValueError):
            progbits_sections(b"not ELF")

    def test_native_halfword_and_vtable_synthetic_positive(self):
        sections = [(0x3A0000, 0, 0x100000, 4),
                    (0x4F0000, 0x100000, 0x10000, 2)]
        buf = bytearray(0x110000)
        for addr, value in EXPECTED_HALFW.items():
            struct.pack_into("<H", buf,
                virtual_file_offset(sections, addr, 2), value)
        for addr, value in EXPECTED_VTABLE.items():
            struct.pack_into("<I", buf,
                virtual_file_offset(sections, addr, 4), value)
        self.assertEqual(pinned_data_failures(buf, sections), [])
        buf[virtual_file_offset(sections, 0x4F5090, 4)] ^= 1
        self.assertEqual(pinned_data_failures(buf, sections),
                         ["native_callback_vtable_pin"])

    def test_wrong_source_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sample"
            p.write_bytes(small_elf())
            with self.assertRaises(ValueError):
                audit(p)

    def test_original_optional(self):
        path = os.getenv("CF18_APOLLO_LIBRARY")
        if not path:
            self.skipTest("exact original not included in CI")
        res = audit(path)
        self.assertTrue(res["sha256_match"])
        self.assertFalse(res["second_service_ack_accepted"])


if __name__ == "__main__":
    unittest.main()

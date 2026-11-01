"""R059 original native static query/endpoint controls (synthetic + opt-in)."""
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from r059_service_query_endpoint import (
    EXPECTED_CALLERS, EXPECTED_HALFWORDS, EXPECTED_VTABLE,
    QUERY_KEY_OFFSET, ENDPOINT_OFFSET, NAMESERVICE_OFFSET,
    static_pin_failures, audit
)


def sample():
    # Synthetic, NOT derived from proprietary source data.
    buf = bytearray(0x110000)
    sections = [(0x3A0000, 0, 0x100000, 4),
                (0x4F0000, 0x100000, 0x10000, 2)]
    for address, value in EXPECTED_HALFWORDS.items():
        struct.pack_into("<H", buf, address - 0x3A0000, value)
    for address, value in EXPECTED_VTABLE.items():
        struct.pack_into("<I", buf, 0x100000 + address - 0x4F0000, value)
    return buf, sections


class TestQueryEndpoint(unittest.TestCase):
    def test_three_distinct_storage_offsets(self):
        self.assertEqual([QUERY_KEY_OFFSET, ENDPOINT_OFFSET, NAMESERVICE_OFFSET],
                         [0x2D8, 0x2DC, 0x2E0])

    def test_caller_evidence_includes_two_producers(self):
        self.assertEqual(set(EXPECTED_CALLERS[0x39D18C]),
                         {0x3A6890, 0x3C334E})

    def test_thread_proc_calls_query_selector(self):
        self.assertEqual(set(EXPECTED_CALLERS[0x3A3C74]), {0x3A5DE6})

    def test_start_uses_resolved_endpoint(self):
        self.assertEqual(set(EXPECTED_CALLERS[0x3A9D92]), {0x3A4A80})
        self.assertEqual(EXPECTED_HALFWORDS[0x3A4A7E], 0x12DC)

    def test_query_and_update_vtable_slots_are_distinct(self):
        self.assertNotEqual(EXPECTED_VTABLE[0x4F5088],
                            EXPECTED_VTABLE[0x4F508C])

    def test_positive_synthetic_pins(self):
        raw, sections = sample()
        self.assertEqual(static_pin_failures(raw, sections), [])

    def test_mutate_query_virtual_instruction(self):
        raw, sections = sample()
        raw[0x3A3C9A - 0x3A0000] ^= 1
        self.assertEqual(static_pin_failures(raw, sections),
                         ["instruction_mismatch"])

    def test_mutate_endpoint_register_load(self):
        raw, sections = sample()
        raw[0x3A4A7E - 0x3A0000] ^= 1
        self.assertEqual(static_pin_failures(raw, sections),
                         ["instruction_mismatch"])

    def test_mutate_query_vtable_pointer(self):
        raw, sections = sample()
        raw[0x100000 + 0x4F5088 - 0x4F0000] ^= 1
        self.assertEqual(static_pin_failures(raw, sections),
                         ["virtual_dispatch_mismatch"])

    def test_wrong_private_source_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "original.so"
            p.write_bytes(b"example only")
            with self.assertRaises(ValueError):
                audit(p)

    def test_private_original_optional(self):
        private = os.getenv("CF18_APOLLO_LIBRARY")
        if not private:
            self.skipTest("exact original not distributed to public CI")
        result = audit(private)
        self.assertEqual(result["direct_edges_checked"], 4)
        self.assertTrue(result["query_key_and_endpoint_distinct_offsets"])
        self.assertEqual(result["second_service_ack_or_login"], "NOT_VERIFIED")


if __name__ == "__main__":
    unittest.main()

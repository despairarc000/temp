"""Source-free negative controls for R075's original directory discriminators."""
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from r057_original_address_callers import Func
from r075_directory_connector_discriminator import (
    EXPECTED_CALLS, PARAM_R3, OTHER_PINS, verify_calls,
    verify_instruction_pins, route_literal_shape, audit
)


def dummy_symbols():
    pairs = {}
    for entries in EXPECTED_CALLS.values():
        pairs.update(entries)
    return [Func(site, 2, "synthetic::" + name)
            for site, name in pairs.items()]


def dummy_callers():
    return {target: set(calls) for target, calls in EXPECTED_CALLS.items()}


def dummy_native_layout():
    mem = bytearray(0x400)
    sec = [(0x36F000, 0, 0x300, 4),
           (0x4A1200, 0x300, 0x100, 2)]
    struct.pack_into("<H", mem, 0x96, 0x4939)
    struct.pack_into("<H", mem, 0x9E, 0x4479)
    struct.pack_into("<I", mem, 0x17C, 0x132192)
    mem[0x334:0x33F] = b"ROUTE12345\0"
    return mem, sec


class Tests(unittest.TestCase):
    def test_three_distinct_rpc_init_callers(self):
        self.assertEqual(len(EXPECTED_CALLS[0x3C4530]), 3)
        self.assertEqual(len(EXPECTED_CALLS[0x3C5248]), 2)

    def test_dir_constructor_has_direct_owner(self):
        self.assertEqual(EXPECTED_CALLS[0x36CE4C], {0x36F13C: "CTDir10Initialize"})

    def test_no_direct_ctdir_initialize_reference(self):
        self.assertEqual(EXPECTED_CALLS[0x36F034], {})

    def test_real_callsite_owner_synthetic_reference(self):
        verify_calls(dummy_callers(), dummy_symbols())

    def test_added_direct_update_call_refused(self):
        callers = dummy_callers()
        callers[0x3C5248].add(0x36F123)
        with self.assertRaises(ValueError):
            verify_calls(callers, dummy_symbols())

    def test_removed_version_update_refused(self):
        callers = dummy_callers()
        callers[0x3C5248].remove(0x32FDF8)
        with self.assertRaises(ValueError):
            verify_calls(callers, dummy_symbols())

    def test_wrong_caller_identity_refused(self):
        syms = [Func(f.address, f.size,
                     "wrong" if f.address == 0x36F0E0 else f.name)
                for f in dummy_symbols()]
        with self.assertRaises(ValueError):
            verify_calls(dummy_callers(), syms)

    def test_original_rpc_parameter_pins_different(self):
        self.assertEqual(PARAM_R3[0x36F0DE], 0x230F)
        self.assertEqual(PARAM_R3[0x32FC72], 0x2308)
        self.assertEqual(PARAM_R3[0x36175C], 0x2308)
        self.assertEqual(OTHER_PINS[0x36F0AC], 0x2301)

    def test_ten_byte_ascii_route_shape_from_pc_relative_pointer(self):
        raw, sections = dummy_native_layout()
        self.assertEqual(route_literal_shape(raw, sections),
                         {"route_literal_ascii_length": 10,
                          "route_bytes_exported": False})

    def test_short_route_name_rejected(self):
        raw, sections = dummy_native_layout()
        raw[0x334:0x33F] = b"SHORT\0xxxxx"
        with self.assertRaises(ValueError):
            route_literal_shape(raw, sections)

    def test_non_ascii_route_rejected(self):
        raw, sections = dummy_native_layout()
        raw[0x334] = 0xff
        with self.assertRaises(ValueError):
            route_literal_shape(raw, sections)

    def test_pc_relative_displacement_mutation_rejected(self):
        raw, sections = dummy_native_layout()
        raw[0x17C] ^= 2
        with self.assertRaises(ValueError):
            route_literal_shape(raw, sections)

    def test_thumb_literal_add_instruction_mutation_rejected(self):
        raw, sections = dummy_native_layout()
        raw[0x9E] ^= 1
        with self.assertRaises(ValueError):
            route_literal_shape(raw, sections)

    def test_instruction_pin_refuses_mutation(self):
        raw, sections = dummy_native_layout()
        pins = {0x36F096: 0x4939, 0x36F09E: 0x4479}
        verify_instruction_pins(raw, sections, pins=pins)
        raw[0x96] ^= 1
        with self.assertRaises(ValueError):
            verify_instruction_pins(raw, sections, pins=pins)

    def test_absent_original_source_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"lib.so"
            p.write_bytes(b"fake")
            with self.assertRaises(ValueError):
                audit(p)

    def test_private_original_gate(self):
        path = os.getenv("CF18_APOLLO_LIBRARY")
        if not path:
            self.skipTest("private original Apollo unavailable in GitHub CI")
        out = audit(path)
        self.assertEqual(out["watched_native_direct_edges"], 6)
        self.assertEqual(out["route_literal_ascii_length"], 10)
        self.assertFalse(out["directory_direct_rpc_update"])
        self.assertEqual(out["runtime_connector_selected"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()

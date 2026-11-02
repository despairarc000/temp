"""Source-free negative tests for R073; private original test is opt-in."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from r057_original_address_callers import Func
from r073_rpc_initialization_order import (
    EDGES, INIT_START, INIT_STEPS, INIT_SIZE,
    validate_edges, verify_init_order, audit
)


def fake_functions():
    by_site = {}
    for sites in EDGES.values():
        by_site.update(sites)
    return [Func(site, 2, "mock::" + name)
            for site, name in by_site.items()]


def fake_calls():
    return {target: set(sites) for target, sites in EDGES.items()}


class Tests(unittest.TestCase):
    def test_original_graph_has_exact_targets_and_call_count(self):
        self.assertEqual(len(EDGES), 7)
        self.assertEqual(sum(map(len, EDGES.values())), 14)

    def test_synthetic_grounded_callers_pass(self):
        validate_edges(fake_calls(), fake_functions())

    def test_order_domain_then_parse_then_lb(self):
        verify_init_order(fake_functions())
        self.assertEqual(INIT_STEPS, (0x3C4622, 0x3C464C, 0x3C474C))
        self.assertTrue(all(INIT_START <= s < INIT_START + INIT_SIZE for s in INIT_STEPS))

    def test_swapped_parser_and_lookup_refused(self):
        s = list(INIT_STEPS)
        s[1], s[2] = s[2], s[1]
        with self.assertRaises(ValueError):
            verify_init_order(fake_functions(), tuple(s))

    def test_false_caller_symbol_refused(self):
        functions = fake_functions()
        functions = [Func(x.address, x.size,
                          "mock::wrong" if x.address == 0x36F0E0 else x.name)
                     for x in functions]
        with self.assertRaises(ValueError):
            validate_edges(fake_calls(), functions)

    def test_missing_ctdir_to_rpc_edge_refused(self):
        calls = fake_calls()
        calls[0x3C4530].remove(0x36F0E0)
        with self.assertRaises(ValueError):
            validate_edges(calls, fake_functions())

    def test_fabricated_ctdir_to_update_edge_refused(self):
        calls = fake_calls()
        calls[0x3C4F78].add(0x36F08A)
        with self.assertRaises(ValueError):
            validate_edges(calls, fake_functions())

    def test_missing_update_to_create_edge_refused(self):
        calls = fake_calls()
        calls[0x3C4F78].remove(0x3C52B4)
        with self.assertRaises(ValueError):
            validate_edges(calls, fake_functions())

    def test_altered_lookup_producer_refused(self):
        calls = fake_calls()
        calls[0x39D18C].remove(0x3C334E)
        with self.assertRaises(ValueError):
            validate_edges(calls, fake_functions())

    def test_callsite_outside_rpc_init_refused(self):
        fake = (INIT_STEPS[0], INIT_STEPS[1], INIT_START+INIT_SIZE)
        with self.assertRaises(ValueError):
            verify_init_order(fake_functions(), fake)

    def test_absent_source_refused_before_parsing(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.so"
            path.write_bytes(b"mock")
            with self.assertRaises(ValueError):
                audit(path)

    def test_private_original_optional(self):
        source = os.getenv("CF18_APOLLO_LIBRARY")
        if not source:
            self.skipTest("private original Apollo missing in public CI")
        result = audit(source)
        self.assertEqual(result["native_direct_calls_verified"], 14)
        self.assertTrue(result["rpc_init_domain_check_then_parser_then_lookup"])
        self.assertEqual(result["on_phone_changed_field"], "NOT_OBSERVED")


if __name__ == "__main__":
    unittest.main()

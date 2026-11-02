"""R084 source-only negative/positive controls for GCloud DH config provenance."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from r057_original_address_callers import Func
from r084_rpc_dh_config_source import (
    PINS, FUNCTIONS, REQUIRED_CALLS, verify_pins, verify_functions,
    verify_calls, audit,
)


def functions():
    return [Func(a, size, "Fixture::" + needle)
            for a, (size, needle) in FUNCTIONS.items()] + [
        Func(site, 4, "Fixture::" + owner)
        for required in REQUIRED_CALLS.values()
        for site, owner in required.items()
    ]


def calls():
    return {target: set(sites) for target, sites in REQUIRED_CALLS.items()}


class Tests(unittest.TestCase):
    def test_positive_original_instruction_shape(self):
        self.assertTrue(verify_pins(PINS.__getitem__))
        self.assertEqual(PINS[0x3C5022], 0x10)
        self.assertEqual(PINS[0x3C6144], 0x3C)

    def test_every_instruction_mutation_is_refused(self):
        for address in PINS:
            changed = dict(PINS); changed[address] ^= 1
            with self.subTest(address=hex(address)), self.assertRaises(ValueError):
                verify_pins(changed.__getitem__)

    def test_original_function_identities(self):
        self.assertTrue(verify_functions(functions()))
        self.assertEqual(len(FUNCTIONS), 6)

    def test_wrong_function_identity_refused(self):
        broken = [Func(f.address, f.size + 1, f.name)
                  if f.address == 0x3C60B8 else f for f in functions()]
        with self.assertRaises(ValueError):
            verify_functions(broken)

    def test_full_config_source_direct_calls(self):
        self.assertTrue(verify_calls(calls(), functions()))
        self.assertEqual(len(REQUIRED_CALLS), 7)
        self.assertEqual(sum(map(len, REQUIRED_CALLS.values())), 9)

    def test_empty_string_constructor_edge_required(self):
        changed = calls(); changed[0x3971F0].clear()
        with self.assertRaises(ValueError):
            verify_calls(changed, functions())

    def test_connector_string_copy_edge_required(self):
        changed = calls(); changed[0x39738C].clear()
        with self.assertRaises(ValueError):
            verify_calls(changed, functions())

    def test_both_c_str_sources_required(self):
        for site in (0x3C6A52, 0x3C6BB6):
            changed = calls(); changed[0x3972F4].remove(site)
            with self.subTest(site=hex(site)), self.assertRaises(ValueError):
                verify_calls(changed, functions())

    def test_both_ctgcp_initialize_branches_required(self):
        for site in (0x3C6A70, 0x3C6BD4):
            changed = calls(); changed[0x3A3D18].remove(site)
            with self.subTest(site=hex(site)), self.assertRaises(ValueError):
                verify_calls(changed, functions())

    def test_dh_setter_edge_required(self):
        changed = calls(); changed[0x3A7E2A].clear()
        with self.assertRaises(ValueError):
            verify_calls(changed, functions())

    def test_unexpected_edge_collection_refused(self):
        changed = calls(); changed[0xDEADB0] = set()
        with self.assertRaises(ValueError):
            verify_calls(changed, functions())

    def test_extra_other_legitimate_callers_allowed(self):
        changed = calls(); changed[0x3972F4].add(0xDEADB0)
        self.assertTrue(verify_calls(changed, functions()))

    def test_wrong_caller_ownership_refused(self):
        altered = [Func(f.address, f.size, "wrong")
                   if f.address == 0x3C6A52 else f for f in functions()]
        with self.assertRaises(ValueError):
            verify_calls(calls(), altered)

    def test_invalid_original_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "apollo.so"
            p.write_bytes(b"not the owner original")
            with self.assertRaises(ValueError):
                audit(p)

    def test_no_network_server_or_ack_generation(self):
        script = (ROOT / "experiments/r084_rpc_dh_config_source.py").read_text()
        for disallowed in ("socket.", "sendall(", "listen(", "synthetic_ack(",
                           "CF2018_SECOND_SERVICE_ACK=", "subprocess.run("):
            self.assertNotIn(disallowed, script)

    @unittest.skipUnless(os.getenv("CF18_APOLLO_LIBRARY"),
                         "private original Apollo not present in public CI")
    def test_private_original_source(self):
        result = audit(os.environ["CF18_APOLLO_LIBRARY"])
        self.assertEqual(result["static_rpc_constructor_default_string"], "EMPTY")
        self.assertEqual(result["phone_runtime_string"], "NOT_OBSERVED")
        self.assertFalse(result["second_service_ack_accepted"])


if __name__ == "__main__":
    unittest.main()

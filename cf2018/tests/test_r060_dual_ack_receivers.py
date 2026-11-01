"""R060 dual TGCP pipeline tests. Public fixture only; private gate optional."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from r060_dual_ack_receivers import (
    RECEIVER_CALLS, RECEIVERS, validate_edges, validate_function_identities, audit
)
from r057_original_address_callers import Func


def symbols():
    objs = [Func(addr, size, "Fake::" + stem) for addr, size, stem
            in RECEIVERS.values()]
    # Every direct caller belongs to a separate mock method of size two.
    seen = {}
    for target, entries in RECEIVER_CALLS.items():
        for site, part in entries.items():
            seen.setdefault(site, part)
    objs += [Func(site, 4, "Fake::" + part) for site, part in seen.items()]
    return objs


def sets():
    return {target: set(paths) for target, paths in RECEIVER_CALLS.items()}


class Tests(unittest.TestCase):
    def test_all_six_receivers_have_expected_callers(self):
        self.assertEqual(len(RECEIVER_CALLS), 6)
        self.assertEqual(sum(map(len, RECEIVER_CALLS.values())), 14)

    def test_distinct_ack_symbols(self):
        self.assertNotEqual(RECEIVERS["legacy_ack"][0],
                            RECEIVERS["gcloud_ack"][0])

    def test_distinct_auth_symbols(self):
        self.assertNotEqual(RECEIVERS["legacy_auth"][0],
                            RECEIVERS["gcloud_auth"][0])

    def test_original_symbol_fixture_pass(self):
        validate_function_identities(symbols())

    def test_original_symbol_mutation_rejected(self):
        x = symbols()
        x[0] = Func(x[0].address, x[0].size+2, x[0].name)
        with self.assertRaises(ValueError):
            validate_function_identities(x)

    def test_all_mock_caller_symbols_pass(self):
        validate_edges(sets(), symbols())

    def test_missing_direct_call_rejected(self):
        x = sets()
        x[0x1C195C].remove(0x1BEB6A)
        with self.assertRaises(ValueError):
            validate_edges(x, symbols())

    def test_wrong_call_owner_rejected(self):
        x = symbols()
        for i, f in enumerate(x):
            if f.address == 0x3A845A:
                x[i] = Func(f.address, f.size, "wrong_owner")
                break
        with self.assertRaises(ValueError):
            validate_edges(sets(), x)

    def test_cross_stack_call_injection_rejected(self):
        x = sets()
        x[0x1C195C].add(0x3A845A)
        with self.assertRaises(ValueError):
            validate_edges(x, symbols())

    def test_missing_receiver_rejected(self):
        x = sets()
        del x[0x3AB5EC]
        with self.assertRaises(ValueError):
            validate_edges(x, symbols())

    def test_fake_source_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "original.so"
            p.write_bytes(b"synthetic")
            with self.assertRaises(ValueError):
                audit(p)

    def test_original_library_opt_in(self):
        path = os.getenv("CF18_APOLLO_LIBRARY")
        if not path:
            self.skipTest("private original Apollo not present in public CI")
        result = audit(path)
        self.assertEqual(result["direct_receiver_calls_checked"], 14)
        self.assertFalse(result["second_service_handshake_accepted"])


if __name__ == "__main__":
    unittest.main()

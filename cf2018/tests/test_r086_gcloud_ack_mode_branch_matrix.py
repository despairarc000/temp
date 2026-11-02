"""R086: only bounded symbolic ACK branch tests and no-network source controls."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from r057_original_address_callers import Func
from r086_gcloud_ack_mode_branch_matrix import (
    PINS, EXPECTED_FUNCTIONS, EXPECTED_CALLS,
    thumb_cond_target, thumb_b_target, verify_static,
    classify_source_branch, audit,
)

def fixture_functions():
    return [Func(addr, size, "Fixture::" + name)
            for addr, (size, name) in EXPECTED_FUNCTIONS.items()]

def fixture_calls():
    return {dest: set(sites) for dest, sites in EXPECTED_CALLS.items()}

def decide(mode, dh=False, key=False, body=False, method=0):
    return classify_source_branch(
        mode, has_dh=dh, key_present=key,
        encrypted_body=body, encryption_method=method
    )

class Tests(unittest.TestCase):
    def test_original_source_branch_pins(self):
        self.assertTrue(verify_static(PINS.__getitem__, fixture_functions(), fixture_calls()))

    def test_mode0_bypasses_set_key(self):
        self.assertEqual(thumb_b_target(0xE01E, 0x3ABEC8), 0x3ABF08)
        self.assertEqual(decide(0), "MODE0_NO_KEY_SETUP_SOURCE_ONLY")

    def test_mode2_enters_copy_and_set_key(self):
        self.assertEqual(thumb_cond_target(0xD007, 0x3ABEB8, 0), 0x3ABECA)
        self.assertEqual(thumb_b_target(0xE008, 0x3ABEE8), 0x3ABEFC)
        self.assertEqual(decide(2, key=True, method=3), "MODE2_SET_KEY_SOURCE_ONLY")
        self.assertEqual(decide(2, key=True, method=4), "MODE2_SET_KEY_SOURCE_ONLY")

    def test_mode3_computes_using_dh(self):
        self.assertEqual(thumb_cond_target(0xD015, 0x3ABEBC, 0), 0x3ABEEA)
        self.assertEqual(decide(3, dh=True), "MODE3_DH_COMPUTE_KEY_SOURCE_ONLY")
        self.assertEqual(decide(3, dh=False), "MODE3_ABSENT_DH_CONTEXT_REJECT_EXPECTED")

    def test_unknown_modes_do_not_pass(self):
        for m in (-1, 1, 4, 255, 256):
            self.assertEqual(decide(m), "OTHER_MODE_NATIVE_REJECT_BRANCH")

    def test_mode0_encrypted_body_remains_a_risk(self):
        self.assertEqual(decide(0, body=True, method=4),
                         "NO_KEY_ENCRYPTED_BODY_LATER_FAILURE_RISK")
        self.assertEqual(decide(0, body=False, method=4),
                         "MODE0_NO_KEY_SETUP_SOURCE_ONLY")

    def test_mode2_requires_key_for_nonzero_encryption(self):
        self.assertEqual(decide(2, key=False, method=4),
                         "MODE2_EMPTY_KEY_NONZERO_ENCRYPTION_REJECT")
        self.assertEqual(decide(2, key=True, method=255),
                         "MODE2_UNSUPPORTED_METHOD_REJECT")

    def test_mode2_key_presence_does_not_mean_auth(self):
        self.assertEqual(decide(2, key=True, method=0),
                         "MODE2_SET_KEY_SOURCE_ONLY")
        self.assertNotIn("ACCEPTED", decide(2, key=True, method=3))

    def test_every_native_instruction_mutation_refuses(self):
        for addr in PINS:
            changed = dict(PINS)
            changed[addr] ^= 1
            with self.subTest(addr=hex(addr)), self.assertRaises(ValueError):
                verify_static(changed.__getitem__, fixture_functions(), fixture_calls())

    def test_bad_branch_encodings_refused(self):
        with self.assertRaises(ValueError):
            thumb_cond_target(0xD107, 0x3ABEB8, 0)
        with self.assertRaises(ValueError):
            thumb_b_target(0xD01E, 0x3ABEC8)

    def test_missing_key_callsite_refused(self):
        for dest, callsite in ((0x3ABD7C, 0x3ABEF2), (0x3AB24A, 0x3ABEFE)):
            changed = fixture_calls()
            changed[dest].remove(callsite)
            with self.subTest(site=hex(callsite)), self.assertRaises(ValueError):
                verify_static(PINS.__getitem__, fixture_functions(), changed)

    def test_wrong_function_size_or_owner_refused(self):
        fs = fixture_functions()
        fs = [Func(x.address, x.size + 2, x.name) if x.address == 0x3ABE34 else x for x in fs]
        with self.assertRaises(ValueError):
            verify_static(PINS.__getitem__, fs, fixture_calls())
        fs = [Func(x.address, x.size, "Wrong") if x.address == 0x3ABE34 else x for x in fixture_functions()]
        with self.assertRaises(ValueError):
            verify_static(PINS.__getitem__, fs, fixture_calls())

    def test_unknown_untyped_symbolic_inputs_refused(self):
        for x in (True, None, "0", 0.0):
            with self.assertRaises(ValueError):
                decide(x)
        with self.assertRaises(ValueError):
            decide(2, method=-1)
        with self.assertRaises(ValueError):
            classify_source_branch(2, has_dh=1, key_present=True, encrypted_body=False, encryption_method=4)

    def test_source_binary_hash_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "libapollo.so"
            f.write_bytes(b"not actual source")
            with self.assertRaises(ValueError):
                audit(f)

    def test_no_traffic_or_ack_generation(self):
        src = (ROOT / "experiments/r086_gcloud_ack_mode_branch_matrix.py").read_text()
        for bad in ("socket.", "sendall(", "listen(", "create_server(", "synthetic_ack("):
            self.assertNotIn(bad, src)

    @unittest.skipUnless(os.getenv("CF18_APOLLO_LIBRARY"),
                         "private original Apollo unavailable in public CI")
    def test_private_original_native_source(self):
        out = audit(os.environ["CF18_APOLLO_LIBRARY"])
        self.assertTrue(out["original_verified"])
        self.assertEqual(out["phone_second_ack_mode"], "NOT_OBSERVED")
        self.assertFalse(out["second_ack_accepted"])

if __name__ == "__main__":
    unittest.main()

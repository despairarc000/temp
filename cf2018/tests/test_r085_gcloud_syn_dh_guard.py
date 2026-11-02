"""R085: source-only GCloud SYN conditional DH branch controls."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from r057_original_address_callers import Func
from r085_gcloud_syn_dh_guard import (
    PINS, FUNCTIONS, REQUIRED_CALLS, beq_target, cbz_target,
    verify_guards, verify_functions, verify_calls, audit,
)

def functions():
    return [Func(addr, size, "Fixture::" + name)
            for addr, (size, name) in FUNCTIONS.items()]

def calls():
    return {addr: set(items) for addr, items in REQUIRED_CALLS.items()}

class Tests(unittest.TestCase):
    def test_null_dh_branch_skips_helper(self):
        self.assertTrue(verify_guards(PINS.__getitem__))
        self.assertEqual(beq_target(0xD039, 0x3ABA96), 0x3ABB0C)
        self.assertGreater(0x3ABB0C, 0x3ABAA0)

    def test_helper_null_dh_branch(self):
        self.assertEqual(cbz_target(0xB1F3, 0x3AB9FC), 0x3ABA3C)
        self.assertEqual(cbz_target(0xB1E8, 0x3AB9F2), 0x3ABA30)
        self.assertEqual(cbz_target(0xB1F9, 0x3AB9F4), 0x3ABA36)

    def test_all_instruction_mutations_refused(self):
        for addr in PINS:
            broken = dict(PINS); broken[addr] ^= 1
            with self.subTest(addr=hex(addr)), self.assertRaises(ValueError):
                verify_guards(broken.__getitem__)

    def test_wrong_conditional_opcode_refused(self):
        for insn in (0xE039, 0xD139, 0xBF00):
            with self.subTest(insn=hex(insn)), self.assertRaises(ValueError):
                beq_target(insn, 0x3ABA96)
        for insn in (0xBF00, 0xE1F3):
            with self.assertRaises(ValueError):
                cbz_target(insn, 0x3AB9FC)

    def test_function_ownership_and_sizes(self):
        self.assertTrue(verify_functions(functions()))
        self.assertEqual(len(FUNCTIONS), 2)

    def test_function_identity_mutation_refused(self):
        broken = [Func(f.address, f.size + 2, f.name)
                  if f.address == 0x3AB9E0 else f for f in functions()]
        with self.assertRaises(ValueError):
            verify_functions(broken)

    def test_direct_helper_callsite(self):
        self.assertTrue(verify_calls(calls(), functions()))
        self.assertEqual(REQUIRED_CALLS[0x3AB9E0][0x3ABAA0],
                         "gcloud_tgcpapi_send_syn_msg")

    def test_direct_helper_call_removed_refused(self):
        broken = calls(); broken[0x3AB9E0].clear()
        with self.assertRaises(ValueError):
            verify_calls(broken, functions())

    def test_wrong_caller_owner_refused(self):
        broken = [Func(f.address, f.size, "Wrong") for f in functions()]
        with self.assertRaises(ValueError):
            verify_calls(calls(), broken)

    def test_extra_legitimate_calls_tolerated(self):
        broken = calls(); broken[0x3AB9E0].add(0xDEADB0)
        self.assertTrue(verify_calls(broken, functions()))

    def test_invalid_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "not-original.so"; p.write_bytes(b"bad")
            with self.assertRaises(ValueError):
                audit(p)

    def test_no_network_or_ack_in_new_script(self):
        s = (ROOT/"experiments/r085_gcloud_syn_dh_guard.py").read_text()
        for bad in ("socket.", "sendall(", "listen(", "synthetic_ack(",
                    "CF2018_SECOND_SERVICE_ACK=", "subprocess.run("):
            self.assertNotIn(bad, s)

    @unittest.skipUnless(os.getenv("CF18_APOLLO_LIBRARY"),
                         "private Apollo not present in public CI")
    def test_opt_in_private_original(self):
        r = audit(os.environ["CF18_APOLLO_LIBRARY"])
        self.assertTrue(r["sender_omits_dh_helper_if_pointer_null"])
        self.assertEqual(r["phone_ack_key_mode"], "NOT_OBSERVED")

if __name__ == "__main__":
    unittest.main()

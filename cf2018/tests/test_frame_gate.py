from pathlib import Path
import importlib.util
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("frame_gate", ROOT / "experiments/frame_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class FrameGateTests(unittest.TestCase):
    def test_old_prefix_fails(self):
        self.assertFalse(gate.first_native_gate(bytes.fromhex("4366"))["passes"])
    def test_new_prefix_passes_only_first_gate(self):
        self.assertTrue(gate.first_native_gate(bytes.fromhex("6643"))["passes"])
    def test_short(self):
        self.assertFalse(gate.first_native_gate(b"")["passes"])
    def test_rewrites_exactly_two_bytes(self):
        old = bytes.fromhex("4366aa00000004")
        fixed = gate.prefix_only_candidate(old)
        self.assertEqual(fixed, bytes.fromhex("6643aa00000004"))
        self.assertEqual(fixed[2:], old[2:])
    def test_refuses_unknown_input(self):
        with self.assertRaises(ValueError):
            gate.prefix_only_candidate(bytes.fromhex("1234aa00000004"))

if __name__ == "__main__":
    unittest.main()

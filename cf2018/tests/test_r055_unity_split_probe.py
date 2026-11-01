"""Synthetic-only R055 tests. No original CF2018 game bytes."""
from pathlib import Path
import importlib.util
import struct
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location("r055_unity_split_probe", TOOLS / "r055_unity_split_probe.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SplitProbeTests(unittest.TestCase):
    def make(self, root, pieces, basename="sharedassets0.assets"):
        for i, data in enumerate(pieces):
            (root / f"{basename}.split{i}").write_bytes(data)
        return root / f"{basename}.split0"

    def test_detect_png_across_split_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            start = self.make(root, [b"\x89PNG\r\n", b"\x1a\nrest"])
            res = module.probe_split(start)
            self.assertEqual(res["format_hint"], "png_magic")
            self.assertEqual(res["part_count"], 2)
            self.assertEqual(res["logical_size"], 12)

    def test_virtual_unity_header_uses_logical_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            header = struct.pack(">4I", 64, 256, 13, 128) + b"\0" * 112
            start = self.make(root, [header, b"x" * (256 - len(header))])
            res = module.probe_split(start)
            self.assertEqual(res["format_hint"], "unity_serialized_header_consistent")

    def test_token_crosses_part_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            start = self.make(root, [b"1234567890Config/Glo", b"balDef/GlobalMapDef.END"])
            res = module.probe_split(start)
            self.assertEqual(res["literal_offsets"]["Config/GlobalDef/GlobalMapDef"], [10])

    def test_markers_absent_does_not_assert_resource_absence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            start = self.make(root, [b"empty", b"random"])
            res = module.probe_split(start)
            self.assertEqual(res["literal_offsets"]["GlobalGameDef"], [])
            self.assertIn("NOT parsed game config", res["evidence_class"])

    def test_missing_part_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            start = self.make(root, [b"a", b"b", b"c"])
            (root / "sharedassets0.assets.split1").unlink()
            with self.assertRaisesRegex(ValueError, "gap"):
                module.find_parts(start)

    def test_zero_size_part_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            start = self.make(root, [b"yes", b""])
            with self.assertRaisesRegex(ValueError, "zero-size"):
                module.find_parts(start)

    def test_noncanonical_index_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            start = self.make(root, [b"a"])
            (root / "sharedassets0.assets.split00").write_bytes(b"alias")
            with self.assertRaisesRegex(ValueError, "noncanonical"):
                module.find_parts(start)

    def test_reject_nonsplit_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "mainData"
            p.write_bytes(b"data")
            with self.assertRaises(ValueError):
                module.find_parts(p)

    def test_read_budget_stops_before_later_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            start = self.make(root, [b"x" * 1048576, b"AITrainGame"])
            res = module.probe_split(start, 1048576)
            self.assertFalse(res["scan_complete"])
            self.assertEqual(res["scan_bytes"], 1048576)
            self.assertEqual(res["literal_offsets"]["AITrainGame"], [])

    def test_no_modifications_or_combined_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            originals = [b"AAA", b"BBB"]
            start = self.make(root, originals)
            before = set(root.iterdir())
            module.probe_split(start)
            self.assertEqual(set(root.iterdir()), before)
            self.assertEqual([p.read_bytes() for p in sorted(before)], originals)


if __name__ == "__main__":
    unittest.main()

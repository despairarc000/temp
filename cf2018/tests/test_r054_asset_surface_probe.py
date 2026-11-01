"""R054 synthetic-only checks. No original game data committed."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "tools" / "r054_asset_surface_probe.py"
spec = importlib.util.spec_from_file_location("r054_asset_surface_probe", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AssetSurfaceTests(unittest.TestCase):
    def test_png_signature_over_name(self):
        self.assertEqual(module.detect_signature(b"\x89PNG\r\n\x1a\n" + b"x" * 40, 48),
                         "png_magic")

    def test_zip_and_unity_bundle_signatures(self):
        self.assertEqual(module.detect_signature(b"PK\x03\x04" + b"a" * 30, 34),
                         "zip_magic")
        self.assertEqual(module.detect_signature(b"UnityRaw\x00" + b"a" * 30, 39),
                         "UnityRaw_magic")
        self.assertEqual(module.detect_signature(b"UnityFS\x00" + b"a" * 30, 38),
                         "UnityFS_magic")

    def test_consistent_unity_header(self):
        header = struct.pack(">4I", 64, 256, 13, 128) + b"\x00" + b"\x00" * 24
        self.assertEqual(module.detect_signature(header, 256),
                         "unity_serialized_header_consistent")
        self.assertEqual(module.detect_signature(header, 128),
                         "unity_serialized_header_size_mismatch_or_split")

    def test_bad_version_does_not_claim_unity(self):
        header = struct.pack(">4I", 64, 256, 100, 128) + b"\x00" + b"\x00" * 24
        self.assertEqual(module.detect_signature(header, 256), "unknown_header")

    def test_unknown_png_extension_is_not_magic(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Assets.png"
            path.write_bytes(b"not a real image")
            found = module.probe_file(path)
            self.assertEqual(found["kind"], "unknown_header")
            self.assertTrue(found["scan_complete"])

    def test_known_path_offset(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.bin"
            data = b"a" * 15 + b"Config/GlobalDef/GlobalGameDef" + b"z" * 5
            path.write_bytes(data)
            result = module.probe_file(path)
            self.assertEqual(result["literal_offsets"]["Config/GlobalDef/GlobalGameDef"], [15])

    def test_cross_chunk_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.bin"
            path.write_bytes(b"x" * (65536 - 7) + b"GlobalMapDef" + b"y" * 10)
            result = module.probe_file(path)
            self.assertEqual(result["literal_offsets"]["GlobalMapDef"], [65536 - 7])

    def test_bounded_scanning_marks_partial(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.bin"
            path.write_bytes(b"x" * 1048576 + b"AITrainGame")
            result = module.probe_file(path, max_scan=1048576)
            self.assertFalse(result["scan_complete"])
            self.assertEqual(result["scan_bytes"], 1048576)
            self.assertEqual(result["literal_offsets"]["AITrainGame"], [])

    def test_invalid_scan_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.bin"
            path.write_bytes(b"hello")
            with self.assertRaises(ValueError):
                module.probe_file(path, 0)

    def test_never_writes_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.bin"
            original = b"\x89PNG\r\n\x1a\nAITrainGame"
            path.write_bytes(original)
            module.probe_file(path)
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()

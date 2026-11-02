"""Validate the exact R077 source-only Termux ZIP bundle in CI."""
import base64
from io import BytesIO
from pathlib import Path
import unittest
from zipfile import ZipFile, BadZipFile

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "kits/CF2018_R077_ROUTE_ID_Kit.zip.b64"
SOURCES = (
    "cf2018/tools/prepare_r077_route_id.py",
    "cf2018/tools/prepare_syn_difference.py",
    "cf2018/experiments/r056_second_service_syn.py",
    "cf2018/experiments/second_service_syn_gate.py",
    "cf2018/experiments/rx_envelope.py",
    "cf2018/experiments/r057_original_address_callers.py",
    "cf2018/experiments/r058_name_service_wiring.py",
    "cf2018/experiments/r075_directory_connector_discriminator.py",
    "cf2018/experiments/r076_private_route_equality.py",
)


class Tests(unittest.TestCase):
    def load_zip(self):
        archive = base64.b64decode(BUNDLE.read_text().strip(), validate=True)
        self.assertGreater(len(archive), 10000)
        return ZipFile(BytesIO(archive))

    def test_bundle_integrity_and_all_files(self):
        with self.load_zip() as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(set(z.namelist()), set(SOURCES) | {"START_HERE.txt"})
            self.assertTrue(all(".." not in Path(n).parts for n in z.namelist()))

    def test_bundle_source_is_exact_current_repo(self):
        with self.load_zip() as z:
            for name in SOURCES:
                self.assertEqual(z.read(name), (ROOT.parent / name).read_bytes(), name)

    def test_readme_and_originals_not_embedded(self):
        with self.load_zip() as z:
            readme = z.read("START_HERE.txt").decode("utf-8")
            self.assertIn("cf2018_syn_difference_r073", readme)
            self.assertIn("CF2018_R077_ROUTE_ID_Result.txt", readme)
            self.assertIn("CF18_APOLLO_LIBRARY", readme)
            self.assertTrue(all(not n.endswith((".so", ".apk", ".xapk", ".obb", ".hex"))
                                for n in z.namelist()))

    def test_zip_members_are_stored_and_bounded(self):
        with self.load_zip() as z:
            self.assertTrue(all(x.compress_type == 0 for x in z.infolist()))
            self.assertLess(sum(i.file_size for i in z.infolist()), 200_000)


if __name__ == "__main__":
    unittest.main()

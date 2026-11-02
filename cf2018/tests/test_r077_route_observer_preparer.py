"""R077 preparer negative controls; full private prepared lifecycle is gated."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from prepare_r077_route_observer import patch_handler, prepare, verify_r073

class Tests(unittest.TestCase):
    def test_reject_unknown_handler(self):
        with self.assertRaises(ValueError):
            patch_handler("print('unverified')")

    def test_reject_source_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                prepare(Path(tmp)/"no",Path(tmp)/"new")

    def test_refuse_output_already_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                prepare(tmp,tmp)

    def test_refuse_output_inside_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                prepare(tmp,Path(tmp)/"nested")

    def test_declared_modules_present(self):
        from prepare_r077_route_observer import DEPENDENCIES
        for name in DEPENDENCIES:
            self.assertTrue((ROOT/"experiments"/name).is_file(),name)

    def test_preparer_is_offline_only(self):
        text=(ROOT/"tools/prepare_r077_route_observer.py").read_text()
        self.assertNotIn("socket.create_connection",text)
        self.assertNotIn("asyncio.start_server",text)
        self.assertNotIn("sendall(",text)

    def test_private_prepared_source_optional(self):
        source=os.getenv("CF18_R073_PREPARED")
        if not source:
            self.skipTest("private R073 prepared source unavailable in public CI")
        text=(Path(source)/"routed_probe_r037.py").read_text()
        self.assertTrue(verify_r073(text))
        with tempfile.TemporaryDirectory() as tmp:
            new=Path(tmp)/"r077"
            result=prepare(source,new)
            self.assertTrue(result["ack_disabled"])
            self.assertFalse(result["listener_started"])
            self.assertTrue((new/"r076_private_route_equality.py").exists())
            self.assertIn("CTDIR_ROUTE slot", (new/"routed_probe_r037.py").read_text())

if __name__=="__main__":
    unittest.main()

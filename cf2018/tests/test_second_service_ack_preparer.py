import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from prepare_second_service_ack import patch_probe, prepare_from_zip


class Tests(unittest.TestCase):
    def test_unknown_handler_refused(self):
        with self.assertRaises(ValueError):
            patch_probe('print("unverified handler")')

    def test_unpinned_source_archive_refused_before_extract(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input.zip'; path.write_bytes(b'not the original source')
            with self.assertRaises(ValueError):
                prepare_from_zip(path, 'unused-kit', Path(tmp) / 'never-created')
            self.assertFalse((Path(tmp) / 'never-created').exists())

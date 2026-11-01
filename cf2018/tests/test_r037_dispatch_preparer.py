import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from prepare_r037_dispatch import patch_probe


class Tests(unittest.TestCase):
    def test_unknown_handler_refused(self):
        for text in ('', 'print("not R037")'):
            with self.assertRaises(ValueError):
                patch_probe(text)

    def test_baseline_is_not_silently_treated_as_r037(self):
        with self.assertRaises(ValueError):
            patch_probe("                    if frames==1:\n")

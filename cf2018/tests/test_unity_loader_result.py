import os
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_integrity_controls import unity_loader_result

class BoundsTests(unittest.TestCase):
    def test_reject_before_source(self):
        with self.assertRaises(ValueError):unity_loader_result('absent',image_present=1,status=0)

@unittest.skipUnless(os.environ.get('CF18_UNITY_LIBRARY'),'private pinned Unity source required')
class NativeUnityTests(unittest.TestCase):
    def test_image_and_zero_status_reach_next_handling(self):
        self.assertEqual(unity_loader_result(os.environ['CF18_UNITY_LIBRARY'],image_present=True,status=0)['stop_site'],0x20fb28)
    def test_null_image_takes_diagnostic_even_without_error_status(self):
        self.assertEqual(unity_loader_result(os.environ['CF18_UNITY_LIBRARY'],image_present=False,status=0)['stop_site'],0x20f898)
    def test_nonzero_status_takes_diagnostic_even_with_nonnull_image(self):
        self.assertEqual(unity_loader_result(os.environ['CF18_UNITY_LIBRARY'],image_present=True,status=3)['stop_site'],0x20f898)

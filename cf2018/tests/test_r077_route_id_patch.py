"""R077 copy-only integration controls. Public tests never send packets."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"tools"), str(ROOT/"experiments")]
from prepare_r077_route_id import (
    ACK_R068, ACK_R073, RECORD_R073, REPORT_R073, ORIGINAL_MAIN,
    R077_RECORD, R077_REPORT, R077_MAIN, original_r068_sha_verified,
    patch_handler, prepare
)
from test_second_service_syn_gate import make
from r076_private_route_equality import classify_transient_frame


def synthetic_r073():
    # Valid Python with the exact R073 anchors, NOT original game source.
    return (
        "def handle():\n"
        "    if True:\n"
        "        if True:\n"
        "            if True:\n"
        "                if True:\n"
        "                    if True:\n"
        + RECORD_R073 +
        "def guarded():\n"
        "    if (assessment == 'MATCH_EXCEPT_ROUTE' and\n"
        "                            False):\n"
        "        second_service_probe=True\n"
        "def report():\n"
        "    out=[]\n"
        "    out.append(f\"SYN_CONTEXT slot={e['slot']} "
        + REPORT_R073 + "\n"
        "    return out\n"
        "RUN='cf2018_syn_difference_runs'\n"
        "FILE='CF2018_SYN_DIFFERENCE_Result.txt'\n"
        "TITLE='CF2018 SYN difference diagnostic; second-service ACK disabled'\n"
        "def main():\n"
        "    return None\n"
        + ORIGINAL_MAIN + "\n"
    )


class Tests(unittest.TestCase):
    def patch_mock(self, source=None):
        with patch("prepare_r077_route_id.original_r068_sha_verified",
                   return_value=True):
            return patch_handler(source if source is not None else synthetic_r073())

    def test_copy_patch_preserves_false_second_ack_gate(self):
        amended = self.patch_mock()
        self.assertIn(ACK_R073, amended)
        self.assertNotIn(ACK_R068, amended)
        self.assertIn("second_service_probe=True", amended)

    def test_report_includes_route_label_only(self):
        amended = self.patch_mock()
        self.assertIn(R077_RECORD, amended)
        self.assertIn(R077_REPORT, amended)
        self.assertIn("r076_private_route_equality", amended)

    def test_separate_result_name_and_metadata(self):
        amended = self.patch_mock()
        self.assertIn("CF2018_R077_ROUTE_ID_Result.txt", amended)
        self.assertIn("cf2018_r077_route_id_runs", amended)
        self.assertNotIn("CF2018_SYN_DIFFERENCE_Result.txt", amended)

    def test_explicit_original_preflight_before_server_main(self):
        amended = self.patch_mock()
        self.assertIn(R077_MAIN, amended)
        self.assertIn("CF18_APOLLO_LIBRARY", amended)
        self.assertLess(amended.index("_R077_ORIGINAL_ROUTE = _original_route_name"),
                        amended.rindex("    main()"))

    def test_patcher_rejects_wrong_ack_gate(self):
        bad = synthetic_r073().replace(ACK_R073, ACK_R073.replace("False", "True"))
        with self.assertRaises(ValueError):
            self.patch_mock(bad)

    def test_patcher_rejects_duplicate_instrumentation(self):
        bad = synthetic_r073().replace(RECORD_R073, RECORD_R073+RECORD_R073)
        with self.assertRaises(ValueError):
            self.patch_mock(bad)

    def test_patcher_rejects_missing_report_anchor(self):
        bad = synthetic_r073().replace(REPORT_R073, "unexpected report label")
        with self.assertRaises(ValueError):
            self.patch_mock(bad)

    def test_patcher_rejects_duplicate_main(self):
        bad = synthetic_r073() + "\n" + ORIGINAL_MAIN + "\n"
        with self.assertRaises(ValueError):
            self.patch_mock(bad)

    def test_patcher_rejects_unpinned_real_source(self):
        with self.assertRaises(ValueError):
            patch_handler(synthetic_r073())

    def test_original_reconstruction_rejects_unknown_input(self):
        with self.assertRaises(ValueError):
            original_r068_sha_verified("unverified random handler")

    def test_prepare_refuses_source_as_output(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                prepare(folder, folder, "/does-not-exist")

    def test_prepare_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            a = Path(folder)/"source"; b = Path(folder)/"out"
            a.mkdir(); b.mkdir()
            with self.assertRaises(ValueError):
                prepare(a, b, "/does-not-exist")

    def test_preparation_does_not_create_output_when_original_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)/"source"; source.mkdir()
            output = Path(folder)/"new"
            with self.assertRaises((ValueError, FileNotFoundError)):
                prepare(source, output, "/does-not-exist")
            self.assertFalse(output.exists())

    def test_route_comparator_is_observational_not_ack_gate(self):
        base = make(b"SECOND1234")
        self.assertEqual(classify_transient_frame(base, b"SECOND1234"),
                         "CTDIR_STATIC_ROUTE_MATCH")
        # This label is not supplied to 'second_service_probe' or an ACK.
        amended = self.patch_mock()
        guard = amended[amended.index("if (assessment == 'MATCH_EXCEPT_ROUTE'"): ]
        self.assertNotIn("route_label", guard.split("second_service_probe=True")[0])

    def test_original_gated_prepared_source_optional(self):
        import os
        source = os.environ.get("CF18_R073_PREPARED")
        original = os.environ.get("CF18_APOLLO_LIBRARY")
        if not (source and original):
            self.skipTest("owner's exact R073 directory and Apollo not mounted in CI")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)/"r077"
            result = prepare(source, target, original)
            self.assertTrue(result["second_service_ack_disabled"])
            self.assertFalse(result["listener_started"])
            output = (target/"routed_probe_r037.py").read_text()
            self.assertIn(R077_REPORT, output)
            self.assertIn(ACK_R073, output)
            self.assertNotIn(ACK_R068, output)
            self.assertFalse((target/"libapollo.so").exists())


if __name__ == "__main__":
    unittest.main()

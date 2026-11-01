"""Private-original gated regression: full V3.8 legacy recognizer vs synthetic 4013 models.

No original binary, private parser code, captured packet or key is committed.
Set CF18_V38_SOURCE to the original unpacked V3.8 ZIP root, optionally
CF18_APOLLO_LIBRARY to the original libapollo.so for a bounded static audit.
"""
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest

from test_routed_label_implications import candidate_body
from test_routed_suffix_constraints import (
    change_last_service_character, shared_prefix, shared_suffix,
    alternate_opaque_format,
)

SOURCE_FILES = {
    "legacy_thrift_v37.py": "589f03ff8d5b9ffec80d0046253e2dab2791400fa488bec08e5b8f86ccff390a",
    "apollo_wire.py": "9f02c98d34bf781756e04383af013f9ca1d883071ad708dd10d19f20d0032011",
}
APOLLO_SHA = "4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8"


def check_file(path, sha):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest() == sha


def original_parser():
    root = os.environ.get("CF18_V38_SOURCE")
    if not root:
        raise unittest.SkipTest("exact private V3.8 parser source required")
    root = Path(root)
    if not all((root / n).is_file() and check_file(root / n, sha)
               for n, sha in SOURCE_FILES.items()):
        raise AssertionError("V3.8 source fingerprint mismatch")
    sys.path.insert(0, str(root))
    from legacy_thrift_v37 import classify_legacy_thrift, MAX_PREFIX_OFFSET
    return classify_legacy_thrift, MAX_PREFIX_OFFSET


def wrapped(service_size, width):
    if type(width) is not int or not 4 <= width <= 10:
        raise ValueError("bounded preamble width")
    base = candidate_body(service_size, strict=False)
    return base[:4] + b"\x00\x00\x00\x01" + bytes(width-4) + base[4:]


class PrivateOriginalV38Tests(unittest.TestCase):
    def test_original_parser_scans_offset_8(self):
        classifier, max_offset = original_parser()
        self.assertEqual(max_offset, 48)
        self.assertEqual(classifier(wrapped(12, 4))["thrift_offset"], "8to15")

    def test_all_widths_4_through_10_would_have_been_recognized(self):
        classifier, _ = original_parser()
        for width in range(4, 11):
            a = wrapped(16 - width, width)
            b = change_last_service_character(wrapped(21 - width, width))
            with self.subTest(width=width):
                self.assertEqual((len(a), len(b)), (80, 85))
                self.assertEqual(shared_prefix(a, b), 61 + width)
                self.assertEqual(shared_suffix(a, b), 2)
                for body in (a, b):
                    result = classifier(body)
                    self.assertEqual(result["thrift_candidate"], "legacy_complete_candidate")
                    self.assertEqual(result["thrift_offset"], "8to15")
                    self.assertEqual(result["thrift_args"], "complete")

    def test_opaque_negative_control_remains_unidentified(self):
        classifier, _ = original_parser()
        for size in (12, 17):
            self.assertEqual(classifier(alternate_opaque_format(size))["thrift_candidate"],
                             "not_identified")

    def test_direct_legacy_positive_control(self):
        classifier, _ = original_parser()
        result = classifier(candidate_body(16))
        self.assertEqual(result["thrift_candidate"], "legacy_complete_candidate")
        self.assertEqual(result["thrift_offset"], "1to7")


@unittest.skipUnless(os.environ.get("CF18_APOLLO_LIBRARY"), "private original Apollo required")
class PrivateNativeStaticTests(unittest.TestCase):
    def test_original_critical_write_boundaries(self):
        path = Path(os.environ["CF18_APOLLO_LIBRARY"])
        self.assertEqual(path.stat().st_size, 5243704)
        self.assertTrue(check_file(path, APOLLO_SHA))
        objdump = shutil.which("llvm-objdump")
        if not objdump:
            self.skipTest("llvm-objdump unavailable")
        ins = {}
        ranges = [(0x3998d4,0x39992a), (0x3c1ed0,0x3c1f50),
                  (0x3c5fd0,0x3c6050), (0x39c3bc,0x39c41c)]
        for a,b in ranges:
            result = subprocess.run([objdump, "--triple=thumbv7a-linux-gnueabihf",
                "--disassemble", "--start-address="+hex(a), "--stop-address="+hex(b),
                str(path)], check=True, capture_output=True, text=True, timeout=10)
            for line in result.stdout.splitlines():
                m = re.match(r"\s*([0-9a-f]{6,8}):\s+(?:(?:[0-9a-f]{4})\s+){1,2}([a-z.]+)\s+(.*)", line)
                if m:
                    ins[int(m[1],16)] = (m[2], m[3].split("@")[0].strip())
        pins = {
            0x399904: ("blx","r3"),
            0x39991c: ("bl","0x39ed4c"),
            0x399926: ("blx","r3"),
            0x3c1f42: ("mov","r2, r11"),
            0x3c1f44: ("mov","r3, r6"),
            0x3c1f46: ("blx","r12"),
            0x3c601e: ("bl","0x397316"),
            0x3c6046: ("bl","0x3a4708"),
            0x39c3ce: ("cbz","r3, 0x39c3f8"),
        }
        for address, (opcode, operand) in pins.items():
            with self.subTest(address=hex(address)):
                actual = ins.get(address, ("", ""))
                self.assertEqual(actual[0], opcode)
                self.assertTrue(actual[1].startswith(operand), (hex(address), actual))


if __name__ == "__main__":
    unittest.main()

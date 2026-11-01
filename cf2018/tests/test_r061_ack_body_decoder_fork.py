"""R061 synthetic-only decoder-selection controls and optional native hash gate."""
import os
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from r057_original_address_callers import Func
from r061_ack_body_decoder_fork import (
    DECODER_CALLS, DECODER_IDENTITIES, GCLOUD_MARKER_PINS,
    LEGACY_DISPATCH_PINS, validate_identifiers, validate_calls,
    native_instruction_failures, audit
)

def mock_funcs():
    result = [Func(addr, size, name)
              for addr, size, name in DECODER_IDENTITIES.values()]
    # Smaller, synthetic exact-owner symbols override surrounding method.
    unique = {}
    for calls in DECODER_CALLS.values():
        unique.update(calls)
    result += [Func(site, 2, "Owner::" + name)
               for site, name in unique.items()]
    return result

def mock_calls():
    return {target: set(sites) for target, sites in DECODER_CALLS.items()}

def mock_instructions():
    sections = [(0x1F0000, 0, 0x100000, 4),
                (0x3B0000, 0x100000, 0x100000, 4)]
    source = bytearray(0x200000)
    for addr, word in {**GCLOUD_MARKER_PINS, **LEGACY_DISPATCH_PINS}.items():
        pos = addr-0x1F0000 if addr<0x300000 else 0x100000+addr-0x3B0000
        struct.pack_into("<H", source, pos, word)
    return source, sections


class DecoderForkTests(unittest.TestCase):
    def test_two_distinct_ack_auth_decoder_targets(self):
        self.assertIn(0x1F9F6A, DECODER_CALLS)
        self.assertIn(0x3B8860, DECODER_CALLS)
        self.assertNotEqual(0x1F9F6A, 0x3B8860)

    def test_ack_and_auth_both_use_legacy_decoder(self):
        self.assertEqual(set(DECODER_CALLS[0x1F9F6A]), {0x1C1B90, 0x1C1F1E})

    def test_ack_and_auth_both_use_gcloud_decoder(self):
        self.assertEqual(set(DECODER_CALLS[0x3B8860]), {0x3AC1B6, 0x3AC366})

    def test_original_gcloud_marker_checks_are_explicit(self):
        self.assertEqual(GCLOUD_MARKER_PINS[0x3B8896], 0x2BAA)
        self.assertEqual(GCLOUD_MARKER_PINS[0x3B889A], 0x2B99)
        self.assertEqual(GCLOUD_MARKER_PINS[0x3B889C], 0xD11C)

    def test_distinct_gcloud_variants(self):
        self.assertEqual(set(DECODER_CALLS[0x3B8488]), {0x3B88C0})
        self.assertEqual(set(DECODER_CALLS[0x3B8674]), {0x3B88C6})

    def test_synthetic_owners_and_identities(self):
        validate_identifiers(mock_funcs())
        validate_calls(mock_calls(), mock_funcs())

    def test_extra_generic_library_consumers_are_permitted(self):
        calls = mock_calls()
        calls[0x1F4842].add(0x123456)
        validate_calls(calls, mock_funcs())

    def test_absent_required_original_edge_is_refused(self):
        calls = mock_calls()
        calls[0x1F9F6A].remove(0x1C1B90)
        with self.assertRaises(ValueError):
            validate_calls(calls, mock_funcs())

    def test_unexpected_owner_is_refused(self):
        names = mock_funcs()
        for i, symbol in enumerate(names):
            if symbol.address == 0x3AC366:
                names[i] = Func(symbol.address, symbol.size, "WrongOwner")
                break
        with self.assertRaises(ValueError):
            validate_calls(mock_calls(), names)

    def test_missing_original_parser_identity_is_refused(self):
        names = mock_funcs()
        names = [x for x in names if x.address != 0x3B8860]
        with self.assertRaises(ValueError):
            validate_identifiers(names)

    def test_synthetic_static_bytes_and_mutation(self):
        raw, sections = mock_instructions()
        self.assertEqual(native_instruction_failures(raw, sections), [])
        raw[0x100000+0x3B889A-0x3B0000] ^= 1
        self.assertEqual(native_instruction_failures(raw, sections),
                         ["decoder_instruction"])

    def test_original_missing_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "not_original"
            path.write_bytes(b"fake")
            with self.assertRaises(ValueError):
                audit(path)

    def test_private_original_gate(self):
        path = os.getenv("CF18_APOLLO_LIBRARY")
        if not path:
            self.skipTest("2018 original private Apollo not in public CI")
        result = audit(path)
        self.assertEqual(result["original_parser_functions"], 5)
        self.assertEqual(result["gcloud_body_envelope_marker"], "AA_OR_99")
        self.assertFalse(result["accepted_second_service_ack"])


if __name__ == "__main__":
    unittest.main()

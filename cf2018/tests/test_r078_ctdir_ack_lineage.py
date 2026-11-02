"""R078: offline lineage and joint route+unit+ACK controls.

All public inputs are synthetic. Optional original native test requires the
owner's exact private Apollo and Unicorn/pyelftools, and never sends packets.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from r057_original_address_callers import Func
from r078_ctdir_ack_lineage import (
    REQUIRED_CALLS, EXACT_CALLSETS, EXPECTED_CHAIN, GAPS, audit, verify_edges,
)
from r074_unit_only_context import route_unit_context_label
from native_syn_ack_handoff import probe, synthetic_ack
from test_r074_unit_only_context import mock_syn


def fake_symbols():
    found = {}
    for callers in REQUIRED_CALLS.values():
        for site, owner in callers.items():
            found[site] = Func(site, 2, "fixture::" + owner)
    return list(found.values())


def fake_calls():
    return {target: set(callers) for target, callers in REQUIRED_CALLS.items()}


class PublicTests(unittest.TestCase):
    def test_chain_preserves_known_native_edges(self):
        self.assertEqual(len(REQUIRED_CALLS), 7)
        self.assertEqual(sum(map(len, REQUIRED_CALLS.values())), 12)
        self.assertTrue(verify_edges(fake_calls(), fake_symbols()))

    def test_missing_ctdir_init_edge_is_refused(self):
        calls = fake_calls()
        calls[0x3C4530].remove(0x36F0E0)
        with self.assertRaises(ValueError):
            verify_edges(calls, fake_symbols())

    def test_wrong_gcloud_ack_receiver_edge_is_refused(self):
        calls = fake_calls()
        calls[0x3AC0B8].remove(0x3A845A)
        with self.assertRaises(ValueError):
            verify_edges(calls, fake_symbols())

    def test_wrong_ack_body_decoder_edge_is_refused(self):
        calls = fake_calls()
        calls[0x3B8860].remove(0x3AC1B6)
        with self.assertRaises(ValueError):
            verify_edges(calls, fake_symbols())

    def test_wrong_gcloud_constructor_owner_is_refused(self):
        funcs = fake_symbols()
        funcs = [
            Func(x.address, x.size, "wrong_owner") if x.address == 0x3C6956 else x
            for x in funcs
        ]
        with self.assertRaises(ValueError):
            verify_edges(fake_calls(), funcs)

    def test_extra_unknown_caller_in_exact_pinned_set_is_refused(self):
        calls = fake_calls()
        calls[0x3AC0B8].add(0xDEADBE)
        with self.assertRaises(ValueError):
            verify_edges(calls, fake_symbols())

    def test_other_original_callers_allowed_only_in_partial_sets(self):
        calls = fake_calls()
        calls[0x3A62A0].add(0xDEADBE)
        self.assertTrue(verify_edges(calls, fake_symbols()))
        self.assertNotIn(0x3A62A0, EXACT_CALLSETS)

    def test_unknown_target_is_refused(self):
        calls = fake_calls()
        calls[0x999999] = set()
        with self.assertRaises(ValueError):
            verify_edges(calls, fake_symbols())

    def test_dynamic_handoffs_are_explicitly_unproven(self):
        self.assertEqual(len(EXPECTED_CHAIN), 7)
        self.assertIn("CTDIR_RUNTIME_UPDATE_SCHEDULING", GAPS)
        self.assertIn("PHONE_SECOND_SERVICE_RECEIVER_EXECUTION", GAPS)
        self.assertIn("SECOND_SERVICE_ACK_KEY_AND_SESSION_VALIDATION", GAPS)

    def test_joint_synthetic_ten_byte_route_and_unit_change(self):
        # Independently synthetic controls. The captured phone route is not
        # supplied and no real account, unit, token or reply is exposed.
        ref = mock_syn()
        new = mock_syn(b"SECOND1234", unit=3)
        self.assertEqual(len(ref), 133)
        self.assertEqual(len(new), 131)
        self.assertEqual(
            route_unit_context_label(new, ref), "ROUTE_AND_UNIT_FIELD5_ONLY"
        )

    def test_joint_gate_negative_controls(self):
        ref = mock_syn()
        self.assertEqual(
            route_unit_context_label(
                mock_syn(b"SECOND1234", unit=3, security=b"Z"*20), ref
            ), "REFUSED"
        )
        self.assertEqual(
            route_unit_context_label(mock_syn(b"SECOND1234", unit=128), ref),
            "REFUSED"
        )

    def test_ack_fixture_is_not_a_route_or_unit_policy(self):
        # Synthetic ACK builder does not take route or unit. This does NOT
        # prove original client's ACK acceptance under a changed context.
        frame = synthetic_ack()
        self.assertGreater(len(frame), 0)
        self.assertNotIn(b"SECOND1234", frame)
        self.assertNotIn(b"QueryAddrSvr", frame)

    def test_invalid_original_is_refused_before_elf_inspection(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "libapollo.so"
            p.write_bytes(b"synthetic")
            with self.assertRaises(ValueError):
                audit(p)

    def test_no_network_or_ack_writer_in_lineage_module(self):
        content = (ROOT / "experiments/r078_ctdir_ack_lineage.py").read_text()
        for banned in ("socket.", "sendall(", "create_server(", "listen(", "CF2018_SECOND_SERVICE_ACK"):
            self.assertNotIn(banned, content)

    @unittest.skipUnless(
        os.environ.get("CF18_APOLLO_LIBRARY"),
        "exact owner-private libapollo.so required for native original validation",
    )
    def test_original_apollo_chain_and_combined_native_ack_boundary(self):
        lib = os.environ["CF18_APOLLO_LIBRARY"]
        result = audit(lib)
        self.assertTrue(result["original_apollo_verified"])
        self.assertFalse(result["game_login_verified"])
        # Actual native SYN prep and ACK parser on a *synthetic* alternate
        # 10-byte route and unit3, auth send stopped, no connection.
        good = probe(lib, name_size=10, attribute="unit_3", variant="valid")
        self.assertTrue(good["syn_prepared_named_route"])
        self.assertTrue(good["auth_send_boundary"])
        self.assertEqual(good["consumed"], 63)
        self.assertEqual(good["return"], -77)
        bad = probe(lib, name_size=10, attribute="unit_3",
                    variant="wrong_magic")
        self.assertFalse(bad["auth_send_boundary"])
        self.assertEqual(bad["return"], -13)


if __name__ == "__main__":
    unittest.main()

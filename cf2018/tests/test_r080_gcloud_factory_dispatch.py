"""R080 original GCloud virtual factory static-dispatch regression, no sockets."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"experiments"))
from r057_original_address_callers import Func
from r080_gcloud_factory_dispatch import (
    FACTORY_DISPATCH_PINS, EXPECTED_VTABLE_WORDS,
    REQUIRED_CALLS, verify_virtual_dispatch, verify_direct_edges, audit,
)


def source_symbols():
    return [Func(site, 4, "Fixture::"+owner)
            for items in REQUIRED_CALLS.values() for site,owner in items.items()]


def call_fixture():
    return {target:set(sites) for target,sites in REQUIRED_CALLS.items()}


class Tests(unittest.TestCase):
    def test_original_factory_virtual_slot(self):
        self.assertEqual(
            verify_virtual_dispatch(FACTORY_DISPATCH_PINS.__getitem__,
                                    EXPECTED_VTABLE_WORDS.__getitem__),
            "CGCLOUD_CREATE_APOLLO_CONNECTION_STATIC_VTABLE_MATCH")

    def test_not_plain_direct_bl(self):
        self.assertEqual(FACTORY_DISPATCH_PINS[0x3C5096],0x47A8)
        self.assertEqual(EXPECTED_VTABLE_WORDS[0x4F5D74],0x3C7E39)

    def test_each_dispatch_halfword_negative(self):
        for bad in FACTORY_DISPATCH_PINS:
            values=dict(FACTORY_DISPATCH_PINS);values[bad]^=1
            with self.subTest(bad=hex(bad)),self.assertRaises(ValueError):
                verify_virtual_dispatch(values.__getitem__,
                                        EXPECTED_VTABLE_WORDS.__getitem__)

    def test_each_vtable_word_negative(self):
        for bad in EXPECTED_VTABLE_WORDS:
            values=dict(EXPECTED_VTABLE_WORDS);values[bad]^=1
            with self.subTest(bad=hex(bad)),self.assertRaises(ValueError):
                verify_virtual_dispatch(FACTORY_DISPATCH_PINS.__getitem__,
                                        values.__getitem__)

    def test_required_factory_to_connector_edge(self):
        self.assertTrue(verify_direct_edges(call_fixture(), source_symbols()))
        self.assertEqual(len(REQUIRED_CALLS),7)

    def test_missing_gcloud_connector_ctor_refused(self):
        calls=call_fixture();calls[0x3C7784].remove(0x3C7EE6)
        with self.assertRaises(ValueError):
            verify_direct_edges(calls,source_symbols())

    def test_missing_nameservice_ctor_refused(self):
        calls=call_fixture();calls[0x3A69E0].clear()
        with self.assertRaises(ValueError):
            verify_direct_edges(calls,source_symbols())

    def test_missing_gcloud_ack_receiver_refused(self):
        calls=call_fixture();calls[0x3AC0B8].remove(0x3A845A)
        with self.assertRaises(ValueError):
            verify_direct_edges(calls,source_symbols())

    def test_missing_gcloud_ack_decoder_refused(self):
        calls=call_fixture();calls[0x3B8860].clear()
        with self.assertRaises(ValueError):
            verify_direct_edges(calls,source_symbols())

    def test_unexpected_caller_owner_refused(self):
        functions=source_symbols()
        functions=[Func(f.address,f.size,"wrong")
                   if f.address==0x3C7EE6 else f for f in functions]
        with self.assertRaises(ValueError):
            verify_direct_edges(call_fixture(),functions)

    def test_extra_allowed_caller_not_assumed_exclusive(self):
        calls=call_fixture();calls[0x3C7784].add(0xDEADB0)
        self.assertTrue(verify_direct_edges(calls,source_symbols()))

    def test_invalid_source_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"apollo.so";path.write_bytes(b"not original")
            with self.assertRaises(ValueError):audit(path)

    def test_auditor_has_no_packet_or_network_logic(self):
        text=(ROOT/"experiments/r080_gcloud_factory_dispatch.py").read_text()
        for banned in ("socket.","sendall(","listen(","CF2018_SECOND_SERVICE_ACK"):
            self.assertNotIn(banned,text)

    @unittest.skipUnless(os.getenv("CF18_APOLLO_LIBRARY"),"private original not in public CI")
    def test_owner_original_full_audit(self):
        r=audit(os.environ["CF18_APOLLO_LIBRARY"])
        self.assertTrue(r["virtual_slot_resolves_create_apollo_connection"])
        self.assertFalse(r["game_login_verified"])


if __name__=="__main__":
    unittest.main()

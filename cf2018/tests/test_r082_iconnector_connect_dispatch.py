"""R082 exact-original IConnector Connect dispatch controls; no network."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"experiments"))
from r057_original_address_callers import Func
from r082_iconnector_connect_dispatch import (
    FACTORY_RETURN_ADJUST,DISPATCH_PINS,VTABLE_PINS,REQUIRED_CALLS,
    verify_virtual_dispatch,verify_direct_calls,audit,
)


def read16(addr):
    return {**FACTORY_RETURN_ADJUST,**DISPATCH_PINS}[addr]


def read32(addr):
    return VTABLE_PINS[addr]


def fixture_functions():
    return [Func(site,4,"Fixture::"+owner)
            for items in REQUIRED_CALLS.values() for site,owner in items.items()]


def fixture_calls():
    return {target:set(items) for target,items in REQUIRED_CALLS.items()}


class Tests(unittest.TestCase):
    def test_factory_returns_i_connector_subobject(self):
        self.assertEqual(verify_virtual_dispatch(read16,read32),
                         "ICONNECTOR_CONNECT_CALLSITE_AND_VTABLE_MATCH")
        self.assertEqual(FACTORY_RETURN_ADJUST[0x3C7F52],0x14)

    def test_connect_slot_is_secondary_vtable_plus_18(self):
        self.assertEqual(VTABLE_PINS[0x4F5C2C],0x3C7055)
        self.assertEqual(DISPATCH_PINS[0x3C5152],0x699B)
        self.assertEqual(DISPATCH_PINS[0x3C5154],0x4798)

    def test_initialize_and_connect_are_distinct_calls(self):
        self.assertEqual(DISPATCH_PINS[0x3C5122],0x4798)
        self.assertEqual(DISPATCH_PINS[0x3C5154],0x4798)
        self.assertNotEqual(0x3C5122,0x3C5154)

    def test_observer_and_manual_update_slots_are_not_connect(self):
        self.assertEqual(VTABLE_PINS[0x4F5C1C],0x3C5919)
        self.assertEqual(VTABLE_PINS[0x4F5C48],0x3C59E7)
        self.assertEqual(DISPATCH_PINS[0x3C5138],0x4798)
        self.assertEqual(DISPATCH_PINS[0x3C5144],0x4798)

    def test_every_factory_and_dispatch_pin_mutation_refused(self):
        for address in list(FACTORY_RETURN_ADJUST)+list(DISPATCH_PINS):
            values={**FACTORY_RETURN_ADJUST,**DISPATCH_PINS}
            values[address]^=1
            with self.subTest(address=hex(address)),self.assertRaises(ValueError):
                verify_virtual_dispatch(values.__getitem__,read32)

    def test_every_secondary_vtable_mutation_refused(self):
        for address in VTABLE_PINS:
            values=dict(VTABLE_PINS);values[address]^=1
            with self.subTest(address=hex(address)),self.assertRaises(ValueError):
                verify_virtual_dispatch(read16,values.__getitem__)

    def test_direct_connect_to_connect_tconnd_edges(self):
        self.assertTrue(verify_direct_calls(fixture_calls(),fixture_functions()))
        self.assertEqual(len(REQUIRED_CALLS),4)
        self.assertEqual(len(REQUIRED_CALLS[0x3C68E0]),2)

    def test_missing_factory_constructor_edge_refused(self):
        calls=fixture_calls();calls[0x3C7784].clear()
        with self.assertRaises(ValueError):
            verify_direct_calls(calls,fixture_functions())

    def test_missing_connect_to_transport_edge_refused(self):
        calls=fixture_calls();calls[0x3C68E0].remove(0x3C6F4A)
        with self.assertRaises(ValueError):
            verify_direct_calls(calls,fixture_functions())

    def test_missing_route_setter_edge_refused(self):
        calls=fixture_calls();calls[0x3A33A0].clear()
        with self.assertRaises(ValueError):
            verify_direct_calls(calls,fixture_functions())

    def test_missing_transport_start_edge_refused(self):
        calls=fixture_calls();calls[0x3A369C].clear()
        with self.assertRaises(ValueError):
            verify_direct_calls(calls,fixture_functions())

    def test_wrong_caller_owner_refused(self):
        functions=fixture_functions()
        functions=[Func(x.address,x.size,"wrong") if x.address==0x3C6F4A else x
                   for x in functions]
        with self.assertRaises(ValueError):
            verify_direct_calls(fixture_calls(),functions)

    def test_extra_valid_caller_does_not_fail_closed_audit(self):
        calls=fixture_calls();calls[0x3C68E0].add(0xDEADB0)
        self.assertTrue(verify_direct_calls(calls,fixture_functions()))

    def test_invalid_original_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"apollo.so";p.write_bytes(b"not original")
            with self.assertRaises(ValueError):
                audit(p)

    def test_no_network_or_ack_generation(self):
        source=(ROOT/"experiments/r082_iconnector_connect_dispatch.py").read_text()
        for banned in ("socket.","sendall(","listen(","CF2018_SECOND_SERVICE_ACK","synthetic_ack"):
            self.assertNotIn(banned,source)

    @unittest.skipUnless(os.getenv("CF18_APOLLO_LIBRARY"),"private Apollo omitted from public CI")
    def test_exact_owner_original(self):
        result=audit(os.environ["CF18_APOLLO_LIBRARY"])
        self.assertTrue(result["create_connection_calls_connect_slot_plus_0x18"])
        self.assertFalse(result["second_service_ack_accepted"])


if __name__=="__main__":
    unittest.main()

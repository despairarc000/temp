"""R081 original native IConnector dispatch; public fixtures never send traffic."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"experiments"))
from r057_original_address_callers import Func
from r081_iconnector_virtual_chain import (
    PINNED_DISPATCH,VTABLE_WORDS,REQUIRED_DIRECT,
    verify_dispatch,verify_direct_calls,audit,
)


def funcs():
    return [Func(site,4,"Fixture::"+owner)
            for sites in REQUIRED_DIRECT.values() for site,owner in sites.items()]


def calls():
    return {target:set(items) for target,items in REQUIRED_DIRECT.items()}


class Tests(unittest.TestCase):
    def test_secondary_vtable_and_indirect_init_slot(self):
        self.assertEqual(verify_dispatch(PINNED_DISPATCH.__getitem__,
                                         VTABLE_WORDS.__getitem__),
                         "ICONNECTOR_INIT_VIRTUAL_SLOT_MATCH")
        self.assertEqual(VTABLE_WORDS[0x4F5C24],0x3C61B5)
        self.assertEqual(VTABLE_WORDS[0x4F5C2C],0x3C7055)

    def test_each_dispatch_instruction_mutation_refused(self):
        for key in PINNED_DISPATCH:
            altered=dict(PINNED_DISPATCH);altered[key]^=1
            with self.subTest(site=hex(key)),self.assertRaises(ValueError):
                verify_dispatch(altered.__getitem__,VTABLE_WORDS.__getitem__)

    def test_each_interface_vtable_word_mutation_refused(self):
        for key in VTABLE_WORDS:
            altered=dict(VTABLE_WORDS);altered[key]^=1
            with self.subTest(address=hex(key)),self.assertRaises(ValueError):
                verify_dispatch(PINNED_DISPATCH.__getitem__,altered.__getitem__)

    def test_direct_connector_connection_chain(self):
        self.assertTrue(verify_direct_calls(calls(),funcs()))
        self.assertEqual(sum(len(x) for x in REQUIRED_DIRECT.values()),6)

    def test_missing_connect_tconnd_invocation_refused(self):
        v=calls();v[0x3C68E0].remove(0x3C6F4A)
        with self.assertRaises(ValueError):
            verify_direct_calls(v,funcs())

    def test_missing_set_route_refused(self):
        v=calls();v[0x3A33A0].clear()
        with self.assertRaises(ValueError):
            verify_direct_calls(v,funcs())

    def test_missing_transport_start_refused(self):
        v=calls();v[0x3A369C].clear()
        with self.assertRaises(ValueError):
            verify_direct_calls(v,funcs())

    def test_wrong_caller_refused(self):
        fake=funcs()
        fake=[Func(f.address,f.size,"wrong") if f.address==0x3C6F4A else f
              for f in fake]
        with self.assertRaises(ValueError):
            verify_direct_calls(calls(),fake)

    def test_extra_direct_caller_may_exist(self):
        c=calls();c[0x3C68E0].add(0xD0D0D0)
        self.assertTrue(verify_direct_calls(c,funcs()))

    def test_wrong_original_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"apollo.so";p.write_bytes(b"invalid")
            with self.assertRaises(ValueError):
                audit(p)

    def test_no_network_or_ack_commands(self):
        s=(ROOT/"experiments/r081_iconnector_virtual_chain.py").read_text()
        for word in ("socket.","sendall(","listen(","CF2018_SECOND_SERVICE_ACK"):
            self.assertNotIn(word,s)

    @unittest.skipUnless(os.getenv("CF18_APOLLO_LIBRARY"),"private Apollo omitted from CI")
    def test_exact_original(self):
        result=audit(os.environ["CF18_APOLLO_LIBRARY"])
        self.assertTrue(result["secondary_iconnector_initialize_thunk_identified"])
        self.assertFalse(result["login_or_gameplay_verified"])


if __name__=="__main__":
    unittest.main()

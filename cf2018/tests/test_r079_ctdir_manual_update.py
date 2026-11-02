"""R079 B.W branch regression: never invoke a live listener or send ACK."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"experiments"))
from r057_original_address_callers import Func
from r079_ctdir_manual_update import (
    WRAPPERS, EXPECTED_CALLS, decode_thumb_b_w, verify_wrappers,
    verify_call_edges, audit,
)


def symbols():
    result={}
    for _,(a,op,d,src,tgt) in WRAPPERS.items():
        result[a]="GCloud::"+src
        result[d]="pebble::rpc::"+tgt
    return result


def read_fixture(addr, n):
    assert n==10
    return next(pins for _,(a,pins,_,_,_) in WRAPPERS.items() if a==addr)


def funcs():
    by_addr={}
    for target, entries in EXPECTED_CALLS.items():
        for site,name in entries.items():
            by_addr[site]=Func(site,4,"fixture::"+name)
    return list(by_addr.values())


class Tests(unittest.TestCase):
    def test_original_thumb_bw_targets_and_guards(self):
        result=verify_wrappers(read_fixture,symbols())
        self.assertEqual(result["update_by_manual"],0x3C5248)
        self.assertEqual(result["enable_manual_update"],0x3C2580)
        self.assertEqual(result["is_connected"],0x3C27DC)

    def test_not_a_direct_bl(self):
        for _,(address,pins,dest,_,_) in WRAPPERS.items():
            self.assertEqual(pins[3]&0xD000,0x9000)
            self.assertNotEqual(pins[3]&0xD000,0xD000)
            self.assertEqual(decode_thumb_b_w(pins[2],pins[3],address+4),dest)

    def test_guard_or_return_mutation_refused(self):
        for index in (0,1,4):
            def corrupted(addr,n):
                values=list(read_fixture(addr,n))
                values[index]^=1
                return values
            with self.subTest(index=index),self.assertRaises(ValueError):
                verify_wrappers(corrupted,symbols())

    def test_tail_target_mutation_refused(self):
        def changed(addr,n):
            words=list(read_fixture(addr,n))
            words[3]^=1
            return words
        with self.assertRaises(ValueError):
            verify_wrappers(changed,symbols())

    def test_wrong_symbol_refused(self):
        obj=symbols()
        obj[0x3C5248]="wrong"
        with self.assertRaises(ValueError):
            verify_wrappers(read_fixture,obj)

    def test_no_unpinned_bw_or_bl_encodings(self):
        with self.assertRaises(ValueError):
            decode_thumb_b_w(0xf056,0xf90b,0x36f02e) # BL instead
        with self.assertRaises(ValueError):
            decode_thumb_b_w(0xf056,0xb90b,0x36f02f) # unaligned
        with self.assertRaises(ValueError):
            decode_thumb_b_w(0,0,0x36f02e)

    def test_source_call_edges(self):
        self.assertTrue(verify_call_edges({x:set(y) for x,y in EXPECTED_CALLS.items()},funcs()))
        self.assertEqual(sum(len(y) for y in EXPECTED_CALLS.values()),4)

    def test_missing_rpc_create_edge_refused(self):
        items={x:set(y) for x,y in EXPECTED_CALLS.items()}
        items[0x3C4F78].remove(0x3C52B4)
        with self.assertRaises(ValueError):
            verify_call_edges(items,funcs())

    def test_missing_gcloud_route_construction_refused(self):
        items={x:set(y) for x,y in EXPECTED_CALLS.items()}
        items[0x398CB4].clear()
        with self.assertRaises(ValueError):
            verify_call_edges(items,funcs())

    def test_missing_gcloud_instance_lookup_refused(self):
        items={x:set(y) for x,y in EXPECTED_CALLS.items()}
        items[0x3C82A0].clear()
        with self.assertRaises(ValueError):
            verify_call_edges(items,funcs())

    def test_invalid_original_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"apollo.so";p.write_bytes(b"not original")
            with self.assertRaises(ValueError):audit(p)

    def test_module_has_no_network_or_ack_work(self):
        source=(ROOT/"experiments/r079_ctdir_manual_update.py").read_text()
        for banned in ("socket.","sendall(","create_server(","CF2018_SECOND_SERVICE_ACK","subprocess"):
            self.assertNotIn(banned,source)

    @unittest.skipUnless(os.environ.get("CF18_APOLLO_LIBRARY"),"original source not present in CI")
    def test_private_original_pinned(self):
        data=audit(os.environ["CF18_APOLLO_LIBRARY"])
        self.assertTrue(data["original_apollo_verified"])
        self.assertTrue(data["ctdir_update_by_manual_tail_branches_to_rpc_update"])
        self.assertEqual(data["gcloud_connector_created_for_ctdir_at_runtime"],"NOT_PROVEN")


if __name__=="__main__":
    unittest.main()

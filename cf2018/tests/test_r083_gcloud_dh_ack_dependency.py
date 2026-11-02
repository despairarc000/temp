"""R083 source-only GCloud DH/ACK chain controls; no live protocol work."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"experiments"))
from r057_original_address_callers import Func
from r083_gcloud_dh_ack_dependency import (
    DH_WRAPPER_PINS,DH_WRAPPER_TARGET,REQUIRED_CALLS,FUNCTIONS,
    verify_wrapper,verify_functions,verify_calls,audit,
)


def read16(address):
    return DH_WRAPPER_PINS[address]


def symbols():
    return {0x3A7E2A:"gcloud_tgcpapi_set_dh",
            DH_WRAPPER_TARGET:"gcloud_tgcpapi_set_dh_info"}


def funcs():
    return [Func(a,size,"Fixture::"+name)
            for a,(size,name) in FUNCTIONS.items()]


def calls():
    return {target:set(sites) for target,sites in REQUIRED_CALLS.items()}


class Tests(unittest.TestCase):
    def test_nonempty_dh_wrapper_tail_target(self):
        self.assertTrue(verify_wrapper(read16,symbols()))

    def test_wrapper_halfword_mutations_refused(self):
        for address in DH_WRAPPER_PINS:
            altered=dict(DH_WRAPPER_PINS);altered[address]^=1
            with self.subTest(address=hex(address)),self.assertRaises(ValueError):
                verify_wrapper(altered.__getitem__,symbols())

    def test_wrong_tail_target_symbol_refused(self):
        names=symbols();names[DH_WRAPPER_TARGET]="wrong"
        with self.assertRaises(ValueError):
            verify_wrapper(read16,names)

    def test_all_gcloud_function_identities(self):
        self.assertTrue(verify_functions(funcs()))
        self.assertEqual(len(FUNCTIONS),12)

    def test_function_size_or_symbol_mutation_refused(self):
        broken=funcs()
        broken=[Func(x.address,x.size+2,x.name) if x.address==0x3AC4B0 else x
                for x in broken]
        with self.assertRaises(ValueError):
            verify_functions(broken)

    def test_full_dh_ack_source_edges(self):
        self.assertTrue(verify_calls(calls(),funcs()))
        self.assertEqual(len(REQUIRED_CALLS),17)

    def test_missing_new_ctgcp_initialization_refused(self):
        c=calls();c[0x3A3D18].remove(0x3C6A70)
        with self.assertRaises(ValueError):
            verify_calls(c,funcs())

    def test_missing_dh_key_generation_refused(self):
        c=calls();c[0x27E9DE].clear()
        with self.assertRaises(ValueError):
            verify_calls(c,funcs())

    def test_missing_syn_dh_serialization_refused(self):
        c=calls();c[0x3AB9E0].clear()
        with self.assertRaises(ValueError):
            verify_calls(c,funcs())

    def test_missing_ack_compute_k_refused(self):
        c=calls();c[0x3ABD7C].clear()
        with self.assertRaises(ValueError):
            verify_calls(c,funcs())

    def test_missing_ack_set_key_refused(self):
        c=calls();c[0x3AB24A].clear()
        with self.assertRaises(ValueError):
            verify_calls(c,funcs())

    def test_missing_auth_request_after_key_sync_refused(self):
        c=calls();c[0x3AB964].clear()
        with self.assertRaises(ValueError):
            verify_calls(c,funcs())

    def test_wrong_direct_edge_owner_refused(self):
        fs=funcs()
        fs=[Func(x.address,x.size,"wrong") if x.address==0x3AC5E6 else x
            for x in fs]
        with self.assertRaises(ValueError):
            verify_calls(calls(),fs)

    def test_extra_direct_callers_are_allowed(self):
        c=calls();c[0x3ABD7C].add(0xDEADB0)
        self.assertTrue(verify_calls(c,funcs()))

    def test_invalid_original_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"apollo.so";p.write_bytes(b"wrong source")
            with self.assertRaises(ValueError):
                audit(p)

    def test_no_network_or_ack_generation(self):
        s=(ROOT/"experiments/r083_gcloud_dh_ack_dependency.py").read_text()
        for banned in ("socket.","sendall(","listen(","synthetic_ack","CF2018_SECOND_SERVICE_ACK"):
            self.assertNotIn(banned,s)

    @unittest.skipUnless(os.getenv("CF18_APOLLO_LIBRARY"),"private Apollo omitted from public CI")
    def test_exact_original(self):
        r=audit(os.environ["CF18_APOLLO_LIBRARY"])
        self.assertTrue(r["dh_generate_key_call_verified"])
        self.assertEqual(r["phone_ack_key_mode"],"NOT_PROVEN")


if __name__=="__main__":
    unittest.main()

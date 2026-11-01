"""R048 eight tests; private exact original is optional in public CI."""
import os,sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
from native_gcloud_init_route_audit import (SIZE,PINS,WINDOWS,VTABLE_ADDRESS_POINT,
    VTABLE_SET_ROUTE_SLOT,VTABLE_SET_ROUTE_THUMB,parse,failures,vtable_pointer,audit)
class Tests(unittest.TestCase):
    def setUp(self):self.base={a:(op,args) for _,a,op,args in PINS}
    def test_count_unique_and_windows(self):
        self.assertEqual((len(PINS),len(self.base)),(23,23))
        for _,a,_,_ in PINS:
            self.assertTrue(any(lo<=a<hi for lo,hi in WINDOWS),hex(a))
    def test_reference_positive(self):
        self.assertEqual(failures(self.base),[])
    def test_each_missing_pin_negative(self):
        for name,a,_,_ in PINS:
            with self.subTest(name=name):
                c=dict(self.base);del c[a];self.assertEqual(failures(c),[name])
    def test_each_mutated_operand_negative(self):
        for name,a,op,arg in PINS:
            with self.subTest(name=name):
                c=dict(self.base);c[a]=(op,arg+" altered")
                self.assertEqual(failures(c),[name])
    def test_duplicate_disassembly_rejected(self):
        line="  3c6172: 6a1b ldr r3, [r3, #0x20]"
        with self.assertRaises(ValueError):parse([line,line])
    def test_bad_binary_refused(self):
        with self.assertRaises((ValueError,OSError)):audit(__file__)
    def test_virtual_slot_mutation_rejected(self):
        raw=bytearray(SIZE)
        offset=VTABLE_ADDRESS_POINT+VTABLE_SET_ROUTE_SLOT-0x1000
        struct.pack_into("<I",raw,offset,VTABLE_SET_ROUTE_THUMB)
        self.assertEqual(vtable_pointer(raw),VTABLE_SET_ROUTE_THUMB)
        struct.pack_into("<I",raw,offset,VTABLE_SET_ROUTE_THUMB+2)
        self.assertNotEqual(vtable_pointer(raw),VTABLE_SET_ROUTE_THUMB)
    def test_private_original_optional(self):
        lib=os.environ.get("CF18_APOLLO_LIBRARY")
        if not lib:self.skipTest("private original not in public CI")
        x=audit(lib)
        self.assertEqual((x["pins"],x["passed"],x["failed"]),(23,23,[]))
        self.assertTrue(x["vtable_slot_0x20_matches_setroute"])
        self.assertFalse(x["authenticated_login"])
if __name__=="__main__":unittest.main()

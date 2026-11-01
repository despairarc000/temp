"""R031 source-free native instruction mutations + optional exact private original."""
import os
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_rx_payload_boundary_audit import PINS,parse_instructions,failures,audit

class Tests(unittest.TestCase):
    def test_unique_pins(self):
        self.assertEqual(len(PINS),34)
        self.assertEqual(len({addr for _,addr,_,_ in PINS}),34)
    def test_positive_source_free_control(self):
        self.assertEqual(failures({addr:(op,arg) for _,addr,op,arg in PINS}),[])
    def test_each_changed_pin_is_rejected(self):
        source={addr:(op,arg) for _,addr,op,arg in PINS}
        for name,addr,op,arg in PINS:
            with self.subTest(name=name):
                modified=dict(source);modified[addr]=(op,arg+'?')
                self.assertEqual(failures(modified),[name])
    def test_each_missing_pin_is_rejected(self):
        source={addr:(op,arg) for _,addr,op,arg in PINS}
        for name,addr,_,_ in PINS:
            with self.subTest(name=name):
                modified=dict(source);del modified[addr]
                self.assertEqual(failures(modified),[name])
    def test_disassembly_parser_ignores_comments(self):
        insns=parse_instructions('  3abfe6: f5e7 ef78 blx 0x193ed8 <memcpy> @ imm = -1\n')
        self.assertEqual(insns[0x3abfe6],('blx','0x193ed8'))
    def test_wrong_source_fails_closed(self):
        with self.assertRaises((ValueError,OSError)):
            audit(__file__)
    def test_original_library_if_supplied(self):
        path=os.getenv('CF18_APOLLO_LIBRARY')
        if not path:self.skipTest('original private Apollo not supplied')
        result=audit(path)
        self.assertEqual((result['checks'],result['passed'],result['failed']),(34,34,[]))
        self.assertTrue(result['conditional_payload_preservation'])
        self.assertFalse(result['removes_four_byte_prefix'])
        self.assertFalse(result['server_envelope_verified'])

if __name__=='__main__': unittest.main()

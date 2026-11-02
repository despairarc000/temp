import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from prepare_directory_ack import directory_context_matches,patch,NEW
from test_second_service_syn_gate import vi,nest

def make(name=b'QueryAddrSvr',unit=1,security=b'K'*20,base_extra=0):
 base=b'\x10'+vi(0x4366)+b'\x40'+vi(0x1001)+b'\x61\x00'+vi(9<<4)+b'\x00\x50'+vi(base_extra)
 syn=nest(1,security)+b'\x50'+vi(unit)+nest(14,nest(4,nest(1,name)))
 missing=121+len(name)-7-len(nest(1,base)+nest(2,nest(0x1001,syn)))
 syn+=nest(15,b'P'*(missing-len(nest(15,b''))))
 h=nest(1,base)+nest(2,nest(0x1001,syn))
 return b'\x43\x66\xaa'+(5+len(h)).to_bytes(4,'big')+h
class Tests(unittest.TestCase):
 def test_only_original_named_route_and_unit_change_can_match(self):
  self.assertTrue(directory_context_matches(make(b'DIRECTORY!',3),make(),b'DIRECTORY!'))
 def test_other_route_refused(self):
  self.assertFalse(directory_context_matches(make(b'OTHERNAME!',3),make(),b'DIRECTORY!'))
 def test_unchanged_unit_refused(self):
  self.assertFalse(directory_context_matches(make(b'DIRECTORY!'),make(),b'DIRECTORY!'))
 def test_changed_security_refused(self):
  self.assertFalse(directory_context_matches(make(b'DIRECTORY!',3,b'Z'*20),make(),b'DIRECTORY!'))
 def test_changed_base_refused(self):
  self.assertFalse(directory_context_matches(make(b'DIRECTORY!',3,base_extra=1),make(),b'DIRECTORY!'))
 def test_larger_unit_encoding_refused(self):
  self.assertFalse(directory_context_matches(make(b'DIRECTORY!',128),make(),b'DIRECTORY!'))
 def test_malformed_input_refused(self):
  for x in (b'',None,make(b'DIRECTORY!',3)[:-1],make(b'DIRECTORY!',3)+b'x'):
   self.assertFalse(directory_context_matches(x,make(),b'DIRECTORY!'))
 def test_arbitrary_handler_cannot_be_patched(self):
  with self.assertRaises(ValueError):patch('pass\n')

"""R045: read-only native route audit mutants and original optional file."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_connector_route_audit import PINS,WINDOWS,parse,failures,audit
class Tests(unittest.TestCase):
 def setUp(self):self.base={a:(op,args) for _,a,op,args in PINS}
 def test_pin_count(self):
  self.assertEqual(len(PINS),17)
  self.assertEqual(len(self.base),17)
 def test_window_coverage(self):
  wins=sorted(WINDOWS)
  for i,(a,b) in enumerate(wins):
   self.assertLess(a,b)
   if i:self.assertLessEqual(wins[i-1][1],a)
  for _,a,_,_ in PINS:self.assertTrue(any(lo<=a<hi for lo,hi in wins))
 def test_synthetic_positive(self):self.assertEqual(failures(self.base),[])
 def test_each_missing_pin(self):
  for name,a,_,_ in PINS:
   with self.subTest(name=name):
    b=dict(self.base);del b[a]
    self.assertEqual(failures(b),[name])
 def test_each_wrong_opcode(self):
  for name,a,op,args in PINS:
   with self.subTest(name=name):
    b=dict(self.base);b[a]=('nop',args)
    self.assertEqual(failures(b),[name])
 def test_each_wrong_operand(self):
  for name,a,op,args in PINS:
   with self.subTest(name=name):
    b=dict(self.base);b[a]=(op,args+' altered')
    self.assertEqual(failures(b),[name])
 def test_duplicate_disassembly_address(self):
  line='  382df2: 2b04          cmp r3, #0x4\n'
  with self.assertRaises(ValueError):parse(line+line)
 def test_fake_original_rejected(self):
  with self.assertRaises((ValueError,OSError)):audit(__file__)
 def test_exact_original_optional(self):
  src=os.environ.get('CF18_APOLLO_LIBRARY')
  if not src:self.skipTest('private hash-pinned Apollo not in public CI')
  r=audit(src)
  self.assertEqual((r['pins'],r['passed'],r['failed']),(17,17,[]))
  self.assertEqual(r['route_name_value'],'NOT_OBSERVED')
if __name__=='__main__':unittest.main()

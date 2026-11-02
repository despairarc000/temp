import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_directory_node_controls import pack,unpack,conversion_probe
LIB=os.environ.get('CF18_APOLLO_LIBRARY')
@unittest.skipUnless(LIB,'exact private Apollo explicitly required')
class Native(unittest.TestCase):
 def test_category_and_leaf_real_native_round_trips(self):
  for selector,size in [(0,44),(1,52)]:
   b,_=pack(LIB,selector);r=unpack(LIB,b)
   self.assertEqual((len(b),r['return'],r['consumed'],r['selector']),(size,0,size,selector))
 def test_bad_node_envelope_rejected(self):
  for selector in (0,1):
   b,_=pack(LIB,selector);self.assertEqual(unpack(LIB,b'\xa5'+b[1:])['return'],-32)
 def test_truncated_node_rejected(self):
  for selector in (0,1):
   b,_=pack(LIB,selector);self.assertEqual(unpack(LIB,b[:-1])['return'],-2)
 def test_real_tree_conversion_loop_observes_one_category(self):
  b,_=pack(LIB,0);r=conversion_probe(LIB,b)
  self.assertEqual((r['return'],r['added_types']),(1,[0]))
 def test_conversion_rejects_bad_blob_without_adding_nodes(self):
  b,_=pack(LIB,0);r=conversion_probe(LIB,b'\xa5'+b[1:]);self.assertEqual((r['return'],r['added_types']),(0,[]))
 def test_node_count_is_not_strict_cardinality_validation(self):
  b,_=pack(LIB,0)
  r=conversion_probe(LIB,b,2);self.assertEqual((r['return'],r['added_types']),(1,[0]))
  r=conversion_probe(LIB,b,0);self.assertEqual((r['return'],r['added_types']),(1,[]))

"""Private V3.8 source-gated false-negative check. Synthetic input only."""
import hashlib
import os
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from qualified_address_request import classify_known_qualified_query
from test_qualified_address_request import candidate

SOURCE_HASHES={
 'legacy_thrift_v37.py':'589f03ff8d5b9ffec80d0046253e2dab2791400fa488bec08e5b8f86ccff390a',
 'apollo_wire.py':'9f02c98d34bf781756e04383af013f9ca1d883071ad708dd10d19f20d0032011',
}

class ExactOriginalParserTest(unittest.TestCase):
 def test_false_negative_with_native_qualified_method(self):
  root=os.environ.get('CF18_V38_SOURCE')
  if not root:self.skipTest('exact private V3.8 original source required')
  root=Path(root)
  for name,sha in SOURCE_HASHES.items():
   self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),sha)
  sys.path.insert(0,str(root))
  from legacy_thrift_v37 import classify_legacy_thrift
  from apollo_wire import _parse_rpc_at
  for size,uid in ((3,2),(8,0x1000002)):
   with self.subTest(size=size):
    data=candidate(size,unit_id=uid)
    self.assertEqual(classify_legacy_thrift(data)['thrift_candidate'],'not_identified')
    parsed=_parse_rpc_at(data,4)
    self.assertEqual(parsed.method,'QueryAddrSvr:QueryAddrInfo')
    self.assertEqual(parsed.wire_format,'legacy-binary')
    self.assertEqual(parsed.end,len(data))
    self.assertEqual(classify_known_qualified_query(data,1)[
        'qualified_address_request'],'COMPLETE_STRUCTURAL_CANDIDATE')

if __name__=='__main__':unittest.main()

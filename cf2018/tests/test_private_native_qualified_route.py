"""Private-original native source assertion: qualified method and route setter.
Hash-pinned read only; original source never enters repository/CI.
"""
import os
import hashlib
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from producer_boundary_audit import audit

SHA='4812396e98bfba9664164c14c8973eed111c5b9d177c1b575e86bc8e9f9169d8'

class NativeQualifiedRouteTest(unittest.TestCase):
 def test_original_name_route_and_msgbuffer_vtable(self):
  path=os.environ.get('CF18_APOLLO_LIBRARY')
  if not path:self.skipTest('exact private original Apollo required')
  path=Path(path)
  raw=path.read_bytes()
  self.assertEqual(len(raw),5243704)
  self.assertEqual(hashlib.sha256(raw).hexdigest(),SHA)
  self.assertEqual(raw[0x4a81f2:0x4a81f2+27],b'QueryAddrSvr:QueryAddrInfo\x00')
  self.assertEqual(raw[0x4a820d:0x4a820d+13],b'QueryAddrSvr\x00')
  def w(p):return struct.unpack_from('<I',raw,p)[0]
  self.assertEqual(0x3998ec+w(0x399a7c),0x4a81f2)
  self.assertEqual(0x39994c+w(0x399a84),0x4a820d)
  # MsgBuffer vtable (file bias 0x1000); +8 is the object vptr.
  self.assertEqual(w(0x4f5778+8+0x30-0x1000)&~1,0x3c149a)
  self.assertEqual(w(0x4f5778+8+0x28-0x1000)&~1,0x3c1ed0)
  report=audit(path)
  self.assertEqual(report['failed'],[])
  self.assertFalse(report['native_execution'])
  self.assertFalse(report['phone_test'])

if __name__=='__main__':unittest.main()

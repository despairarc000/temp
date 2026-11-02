"""Exact existing synthetic auth/Bingo pair; explicit optional original source."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_auth_rx import trace_wire
LIB=os.environ.get('CF18_APOLLO_LIBRARY');SOURCE=os.environ.get('CF18_DIRECTORY_ACK_PREPARED')
@unittest.skipUnless(LIB and SOURCE,'explicit original Apollo and prepared probe required')
class Native(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  sys.path.insert(0,SOURCE)
  from tgcp_body_repair_v14 import candidate
  from stage_frame_v15 import candidate_stage
  cls.auth=candidate('V14_BODY_ENVELOPED');cls.bingo=candidate_stage('CORRECTED_BINGO_SYNTHETIC')
 @classmethod
 def tearDownClass(cls):sys.path.remove(SOURCE)
 def test_auth_only_waits_for_bingo(self):
  r=trace_wire(LIB,self.auth);self.assertEqual(r['state'],4);self.assertTrue(r['account_zero'])
 def test_original_pair_parses_to_transport_ready(self):
  self.assertEqual((len(self.auth),len(self.bingo)),(54,91))
  r=trace_wire(LIB,self.auth+self.bingo);self.assertEqual((r['return'],r['state'],r['buffered']),(0,5,0));self.assertTrue(r['account_zero'])
  self.assertTrue(any(e['stage']=='body_unpack' and e['event']=='return' and e['code']==0 for e in r['events']))
 def test_malformed_bingo_body_blocks_ready(self):
  h=int.from_bytes(self.bingo[1:5],'big')
  r=trace_wire(LIB,self.auth+self.bingo[:h]+b'\xa5'+self.bingo[h+1:]);self.assertEqual((r['return'],r['state']),(-18,4))
 def test_truncated_bingo_waits_without_ready(self):
  r=trace_wire(LIB,self.auth+self.bingo[:-1]);self.assertEqual(r['state'],4);self.assertEqual(r['buffered'],90)

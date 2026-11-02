import os,sys,unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'tools'),str(Path(__file__).resolve().parents[1]/'experiments')]
from prepare_directory_identify import classify_body,classify_frame

def fixture(label='all',strict=False):
 name,shape={'all':(b'DirService:get_server_dirtree_all',[(1,10),(2,11),(3,10)]),'by_id':(b'DirService:get_server_dirtree_by_id',[(1,10),(2,11),(3,8),(4,10)]),'by_ids':(b'DirService:get_server_by_ids',[(1,10),(2,11),(3,8),(4,8),(5,10)])}[label]
 n=(9 if strict else 12) if label=='all' else (0 if strict else 3)
 head=(b'\x80\x01\x00\x01' if strict else b'')+len(name).to_bytes(4,'big')+name+(b'' if strict else b'\x01')+bytes(8)
 args=b''
 for field,kind in shape:args+=bytes([kind])+field.to_bytes(2,'big')+((n.to_bytes(4,'big')+b'S'*n) if kind==11 else bytes(8 if kind==10 else 4))
 return bytes(4)+head+args+b'\0'
class Tests(unittest.TestCase):
 def test_all_six_models_fit92_and_remain_distinct(self):
  for label,out in [('all','ALL_COMPLETE'),('by_id','BY_ID_COMPLETE'),('by_ids','BY_IDS_COMPLETE')]:
   for strict in [False,True]:
    b=fixture(label,strict);self.assertEqual(len(b),92);self.assertEqual(classify_body(b,0),{'directory_request':out,'directory_encoding':'STRICT64' if strict else 'LEGACY64','directory_reason':'COMPLETE'})
 def test_packet_sequence_mismatch(self):self.assertEqual(classify_body(fixture(),1)['directory_request'],'NOT_IDENTIFIED')
 def test_truncation_and_trailing_data(self):
  for x in [fixture()[:-1],fixture()+b'x',fixture()[:40]]:self.assertEqual(classify_body(x,0)['directory_request'],'NOT_IDENTIFIED')
 def test_wrong_message_type(self):
  b=bytearray(fixture());b[8+len(b'DirService:get_server_dirtree_all')]=2;self.assertEqual(classify_body(bytes(b),0)['directory_request'],'NOT_IDENTIFIED')
 def test_unknown_method(self):self.assertEqual(classify_body(fixture().replace(b'DirService:',b'OtherName!:'),0)['directory_request'],'NOT_IDENTIFIED')
 def test_wrong_field_type(self):self.assertEqual(classify_body(fixture().replace(b'\x0a\0\x01',b'\x08\0\x01',1),0)['directory_request'],'NOT_IDENTIFIED')
 def test_oversized_string(self):self.assertEqual(classify_body(fixture().replace(b'\0\0\0\x0c',b'\0\0\x01\x01',1),0)['directory_request'],'NOT_IDENTIFIED')
 def test_bad_frame_is_not_comparable(self):
  for f in [None,b'',b'Q'*171]:self.assertEqual(classify_frame(f,b'DirService')['directory_request'],'NOT_COMPARABLE')
 def test_no_payload_or_values_returned(self):
  self.assertEqual(set(classify_body(fixture(),0)),{'directory_request','directory_encoding','directory_reason'});self.assertNotIn('SSSS',str(classify_body(fixture(),0)))

@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'),'exact original Apollo explicitly required')
class Native(unittest.TestCase):
 def test_real_native_writers_all_reproduce92_and_classify(self):
  from native_directory_writer_controls import build
  for label,expect in [('all','ALL_COMPLETE'),('by_id','BY_ID_COMPLETE'),('by_ids','BY_IDS_COMPLETE')]:
   for strict in [False,True]:
    n=(9 if strict else 12) if label=='all' else (0 if strict else 3)
    body,calls=build(os.environ['CF18_APOLLO_LIBRARY'],label,n,strict)
    self.assertEqual(len(body),92);self.assertEqual(classify_body(body,0)['directory_request'],expect)
    self.assertEqual(set(calls),{'bounded synthetic memory sink'})

@unittest.skipUnless(os.environ.get('CF18_DIRECTORY_STAGE_PREPARED'),'explicit private probe parser modules required')
class Frame(unittest.TestCase):
 @classmethod
 def setUpClass(cls):sys.path.insert(0,os.environ['CF18_DIRECTORY_STAGE_PREPARED'])
 @classmethod
 def tearDownClass(cls):sys.path.remove(os.environ['CF18_DIRECTORY_STAGE_PREPARED'])
 def test_frame_route_sequence_compression_and_cipher_guards(self):
  from native_syn_ack_handoff import _field
  def make(name=b'DirService',seq=0,comp=0,enc=0):
   body=fixture();base=b''.join(_field(i,1 if i==6 else 0,v) for i,v in enumerate([0x4366,0,1,0x4013,0,enc,seq,0,len(body)],1))
   data=_field(1,1,comp)+_field(2,1,0)+_field(3,1,4)+_field(4,5,_field(4,5,_field(1,5,name)))
   h=_field(1,5,base)+_field(2,5,_field(0x4013,5,data))
   return b'\x43\x66\xaa'+(5+len(h)).to_bytes(4,'big')+h+body
  self.assertEqual(classify_frame(make(),b'DirService')['directory_request'],'ALL_COMPLETE')
  for kwargs in [dict(name=b'OtherRoute'),dict(comp=1),dict(enc=1)]:self.assertEqual(classify_frame(make(**kwargs),b'DirService')['directory_request'],'NOT_COMPARABLE')
  self.assertEqual(classify_frame(make(seq=1),b'DirService')['directory_request'],'NOT_IDENTIFIED')

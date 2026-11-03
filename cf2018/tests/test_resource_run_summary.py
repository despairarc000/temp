import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from summarize_resource_run import summarize,host_label,records,choose_run,write_summary
class Tests(unittest.TestCase):
 def fixture(self,root,name='run_20261103T000000Z_1234abcd'):
  run=root/name;run.mkdir();(run/'relay').mkdir()
  server=[{'action':'accepted','slot':1},{'action':'r033_reply_sent','slot':1},{'action':'later_client_frame','slot':1,'variant':0x4013,'qualified_address_request':'COMPLETE_STRUCTURAL_CANDIDATE'},{'action':'directory_config_reply_written','slot':1},{'action':'accepted','slot':5},{'action':'finished','slot':5,'reason':'over_cap'}]
  relay=[{'event':'CONNECTED','connection':1,'host':'version.synthetic.invalid','port':8080,'status':'EMULATOR','account':'SYNTHETIC_SECRET'},
         {'event':'RELAY_BYTES','connection':1,'direction':'client->server','bytes':31},
         {'event':'RELAY_BYTES','connection':1,'direction':'server->client','bytes':12},
         {'event':'CONNECT_FAILED','connection':2,'host':'203.0.113.5','port':443,'reason':'SYNTHETIC_SECRET'}]
  for path,data in ((run/'events.jsonl',server),(run/'relay'/'events.jsonl',relay)):path.write_text(''.join(json.dumps(e)+'\n' for e in data))
  return run
 def known(self):return {hashlib.sha256(b'version.synthetic.invalid').hexdigest():'VERSION'}
 def test_fixed_labels_counts_and_no_sensitive_field_export(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);run=self.fixture(root);before={p:p.read_bytes() for p in run.rglob('*.jsonl')}
   text=summarize(run,self.known())
   self.assertIn('over_cap=1 over_cap_after_settings=1 settings_replies=1 discovery_replies=1 address_candidates=1',text)
   self.assertIn('class=VERSION mode=EMULATOR port=8080 connected=1 connect_failed=0 client_bytes=31 server_bytes=12',text)
   for private in ('version.synthetic.invalid','203.0.113.5','SYNTHETIC_SECRET'):self.assertNotIn(private,text)
   self.assertEqual(before,{p:p.read_bytes() for p in before})
 def test_ip_is_not_assigned_a_service_even_if_mapping_supplied(self):
  host='203.0.113.5';mapping={hashlib.sha256(host.encode()).hexdigest():'VERSION'}
  self.assertEqual(host_label(host,mapping),'UNCLASSIFIED_IP')
 def test_untrusted_label_cannot_be_exported(self):
  mapping={hashlib.sha256(b'example.invalid').hexdigest():'SYNTHETIC_SECRET'}
  self.assertEqual(host_label('example.invalid',mapping),'UNCLASSIFIED_NAME')
 def test_malformed_json_is_counted_without_export(self):
  with tempfile.TemporaryDirectory() as tmp:
   run=self.fixture(Path(tmp));path=run/'events.jsonl';path.write_text(path.read_text()+'SYNTHETIC_SECRET\n')
   text=summarize(run,self.known());self.assertIn('INVALID_JSON_LINES 1',text);self.assertNotIn('SYNTHETIC_SECRET',text)
 def test_oversized_line_refused(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'events.jsonl';path.write_bytes(b'x'*8193)
   with self.assertRaises(ValueError):records(path)
 def test_latest_named_run_and_unique_deliverables(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.fixture(root);latest=self.fixture(root,'run_20261103T010000Z_abcd1234')
   self.assertEqual(choose_run(root),latest)
   a=write_summary(latest,root/'out',self.known());b=write_summary(latest,root/'out',self.known())
   self.assertNotEqual(a.name,b.name);self.assertEqual(a.read_text(),b.read_text())
   self.assertRegex(a.name,r'^CF2018_RESOURCE_RUN_SUMMARY_\d{8}T\d{6}_\d{6}Z_[0-9a-f]{8}\.txt$')
 def test_symlink_metadata_refused(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);run=self.fixture(root);p=run/'events.jsonl';p.rename(root/'original');p.symlink_to(root/'original')
   with self.assertRaises(ValueError):summarize(run,self.known())
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);run=self.fixture(root);relay=run/'relay';relay.rename(root/'other');relay.symlink_to(root/'other',target_is_directory=True)
   with self.assertRaises(ValueError):summarize(run,self.known())

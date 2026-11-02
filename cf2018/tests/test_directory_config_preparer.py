"""Source refusal and copy-only preparation controls; no listener starts."""
import ast,hashlib,json,os,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from prepare_directory_config import patch,prepare,REPLY_SOURCE,SOURCE_SHA

class Public(unittest.TestCase):
 def test_changed_or_unrelated_source_refused(self):
  for text in ('','pass\n','from directory_identify import classify_frame\n'):
   with self.assertRaises(ValueError):patch(text)
 def test_embedded_reply_matches_reviewed_module(self):
  self.assertEqual(REPLY_SOURCE,(ROOT/'experiments/directory_config_reply.py').read_text())
 def test_existing_output_refused_without_modification(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);sentinel=p/'keep';sentinel.write_text('unchanged')
   with self.assertRaises(ValueError):prepare(p/'missing',p)
   self.assertEqual(sentinel.read_text(),'unchanged')

@unittest.skipUnless(os.environ.get('CF18_DIRECTORY_IDENTIFY_PREPARED'),'explicit private prepared source required')
class Prepared(unittest.TestCase):
 def test_unique_report_names_and_existing_file_protection(self):
  source=Path(os.environ['CF18_DIRECTORY_IDENTIFY_PREPARED'])
  changed=patch((source/'routed_probe_r037.py').read_text(),180)
  self.assertIn("'CF2018_DIRECTORY_CONFIG_Result_'+run.base.name+'.txt'",changed)
  self.assertNotIn("/CF2018_DIRECTORY_CONFIG_Result.txt'",changed)
  tree=ast.parse(changed)
  report=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='report')
  module=ast.Module(body=[report],type_ignores=[]);env={'json':json,'RESOURCE_OBSERVATION_SECONDS':180}
  exec(compile(module,'report control','exec'),env)
  from types import SimpleNamespace
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder);log=p/'events.jsonl'
   log.write_text(json.dumps({'action':'accepted','slot':2,'port':8085})+'\n')
   run=SimpleNamespace(log=log,max_sessions=4,base=p/'run_20261102T000000Z_1234abcd')
   target=p/'report.txt';env['report'](run,target);before=target.read_bytes()
   self.assertIn('REPORT_ID run_20261102T000000Z_1234abcd',before.decode())
   self.assertIn('SESSION_OPEN_AT_REPORT slot=2',before.decode())
   with self.assertRaises(FileExistsError):env['report'](run,target)
   self.assertEqual(target.read_bytes(),before)
 def test_pinned_source_copied_and_mutation_refused(self):
  source=Path(os.environ['CF18_DIRECTORY_IDENTIFY_PREPARED']).resolve()
  original=(source/'routed_probe_r037.py').read_text()
  self.assertEqual(hashlib.sha256(original.encode()).hexdigest(),SOURCE_SHA)
  with tempfile.TemporaryDirectory() as tmp:
   output=Path(tmp)/'separate';prepare(source,output)
   changed=(output/'routed_probe_r037.py').read_text()
   self.assertIn('CF2018_DIRECTORY_CONFIG',changed)
   self.assertIn('directory_reply_claimed',changed)
   self.assertEqual((output/'directory_config_reply.py').read_text(),REPLY_SOURCE)
   self.assertEqual((source/'routed_probe_r037.py').read_text(),original)
  with self.assertRaises(ValueError):patch(original+'\n')

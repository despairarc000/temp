"""Source refusal and copy-only preparation controls; no listener starts."""
import hashlib,os,sys,tempfile,unittest
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

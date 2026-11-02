"""Optional original archive-header checksum controls; no asset dumps."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from native_nifs_header import verify
@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY') and os.environ.get('CF18_NIFS_ASSET'),'explicit private original Apollo/archive required')
class Native(unittest.TestCase):
    def test_original_header_and_two_mutations(self):
        with Path(os.environ['CF18_NIFS_ASSET']).open('rb') as stream:b=stream.read(172)
        library=os.environ['CF18_APOLLO_LIBRARY']
        self.assertEqual(verify(library,b),0)
        bad=bytearray(b);bad[100]^=1;self.assertEqual(verify(library,bytes(bad)),109)
        bad=bytearray(b);bad[-1]^=1;self.assertEqual(verify(library,bytes(bad)),109)

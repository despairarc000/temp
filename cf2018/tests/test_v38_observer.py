import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from prepare_v38_observer import prepare


class BoundsTests(unittest.TestCase):
    def test_original_directory_is_never_an_output(self):
        with self.assertRaises(ValueError):
            prepare(ROOT, ROOT)


@unittest.skipUnless(os.environ.get('CF18_V38_SOURCE'), 'exact private v38 source required')
class PrivateIntegrationTests(unittest.TestCase):
    def test_real_probe_integration_and_private_canary(self):
        (ROOT / 'private').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / 'private') as temp:
            output = Path(temp) / 'observer'
            self.assertFalse(prepare(os.environ['CF18_V38_SOURCE'], output)['wire_changes'])
            script = '''import json,tempfile
from pathlib import Path
from tests.test_v38 import frame
from routed_probe_v38 import Run
from apollo_wire import request_query_addr
with tempfile.TemporaryDirectory() as temp:
 r=Run(Path(temp))
 packet=frame(0,(1).to_bytes(4,'big')+request_query_addr(1,1,'PRIVATE_CANARY',1),b'QueryAddrSvr')
 value=r.compare_routed(packet,{})
 assert value['sequence_prefix']=='MATCH',value
 assert value['legacy_after_sequence']=='LEGACY_HEADER_PLAUSIBLE',value
 assert value['known_address_route']=='MATCH',value
 r.record('later_frame','synthetic-control',**value)
 assert 'PRIVATE_CANARY' not in r.log.read_text()
 assert 'QueryAddrSvr' not in r.log.read_text()
 assert value['legacy_at_start']!='LEGACY_HEADER_PLAUSIBLE'
 print(json.dumps({'integrated':True,'canary_absent':True}))
'''
            result = subprocess.run([sys.executable, '-c', script], cwd=output,
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)['canary_absent'])
            # The existing opt-in must still prevent startup in a source copy.
            result = subprocess.run([sys.executable, 'routed_probe_v38.py'], cwd=output,
                                    capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Offline only', result.stderr)

    @unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'), 'pinned Apollo required')
    def test_exact_stage_replay_matches_published_matrix(self):
        from replay_v38_stage_context import replay
        actual = replay(os.environ['CF18_APOLLO_LIBRARY'], os.environ['CF18_V38_SOURCE'])
        expected = json.loads((ROOT / 'coordination/V38_STAGE_CONTEXT_MATRIX.json').read_text())
        self.assertEqual(actual, expected)

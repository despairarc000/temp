import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments'))
sys.path.insert(0, str(ROOT / 'tools'))
from v381_termux_patch import prepare
from build_v381_patch_kit import build

ARCHIVE = os.environ.get('CF18_V38_ZIP')


class KitBoundsTests(unittest.TestCase):
    def test_kit_is_patch_only_and_deterministic(self):
        with tempfile.TemporaryDirectory() as temp:
            a, b = Path(temp) / 'a.zip', Path(temp) / 'b.zip'
            self.assertEqual(build(a)['sha256'], build(b)['sha256'])
            with zipfile.ZipFile(a) as z:
                self.assertEqual(set(z.namelist()), {'apply_v381.py', 'routed_body_diagnostic.py',
                                                   'V38_SOURCE_PINS.json', 'README.txt'})
                self.assertFalse(any(n.endswith(('.hex', '.so', '.apk', '.dll', '.obb')) for n in z.namelist()))

    def test_changed_archive_refused_without_creating_output(self):
        with tempfile.TemporaryDirectory() as temp:
            source, output = Path(temp) / 'old.zip', Path(temp) / 'new'
            source.write_bytes(b'unverified package')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                prepare(source, output)
            self.assertFalse(output.exists())

    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, 'new output'):
                prepare('missing', temp)


@unittest.skipUnless(ARCHIVE, 'exact private v38 ZIP required')
class PrivatePathTests(unittest.TestCase):
    def test_patch_and_complete_socks5_local_server_path(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'private') as temp:
            temp = Path(temp)
            kit = temp / 'kit'
            kit.mkdir()
            with zipfile.ZipFile(self._build(temp)) as z:
                z.extractall(kit)
            output = temp / 'prepared'
            result = prepare(ARCHIVE, output, kit)
            self.assertFalse(result['relay_started'])
            with zipfile.ZipFile(ARCHIVE) as z:
                original = ast.parse(z.read('CF2018_TGCP_v3.8_GCloud_DataHead_Flags/routed_probe_v38.py'))
            patched = ast.parse((output / 'routed_probe_v38.py').read_text())
            # Entire protocol handler, including send bytes/order/delay/caps, is untouched.
            get_handler = lambda tree: next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Handler')
            self.assertEqual(ast.dump(get_handler(original)), ast.dump(get_handler(patched)))
            idle = subprocess.run(['bash', 'START_V381.sh'], cwd=output, capture_output=True,
                                  text=True, timeout=30, env={**os.environ, 'CF2018_V381_LIVE': 'NO'})
            self.assertEqual(idle.returncode, 0, idle.stderr)
            self.assertIn('No listener started', idle.stdout)
            # Actual supplied NO-AUTH/CONNECT redirector -> patched server.
            script = (ROOT / 'tests/v381_socks5_control.py').read_text()
            actual = subprocess.run([sys.executable, '-c', script], cwd=output,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(actual.returncode, 0, actual.stderr)
            final = json.loads(actual.stdout.splitlines()[-1])
            self.assertEqual(final['sessions'], 4)
            self.assertTrue(final['privacy_pass'])

    @staticmethod
    def _build(temp):
        path = temp / 'patch.zip'
        build(path)
        return path

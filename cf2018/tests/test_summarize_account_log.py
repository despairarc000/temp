import importlib.util, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1] / 'tools/summarize_account_log.py'
spec = importlib.util.spec_from_file_location('account_log', PATH)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class Summary(unittest.TestCase):
    def test_fixed_status_and_exception_mentions_only(self):
        raw = b'D/iMSDK  ( 123): {"imsdkRetCode":4,"code":-111}\nD/iMSDK(123): SSLHandshakeException\n'
        result = reader.summarize(raw)
        self.assertEqual(result['mentions'], {'HTTP_NO_CONNECTION': 1, 'SDK_STATUS_4': 1, 'SSLHandshakeException': 1})
        self.assertEqual(result['stage_attribution'], 'UNKNOWN')

    def test_sensitive_text_and_arbitrary_numbers_are_not_exported(self):
        raw = b'D/iMSDK(123): {"openId":"SYNTHETIC_ID","sInnerToken":"SYNTHETIC_SECRET","code":12345678901234567890,"url":"https://synthetic.invalid"}\n'
        report = json.dumps(reader.summarize(raw))
        for forbidden in ['SYNTHETIC_ID', 'SYNTHETIC_SECRET', 'synthetic.invalid', '12345678901234567890', 'openId', 'sInnerToken']:
            self.assertNotIn(forbidden, report)
        self.assertEqual(reader.summarize(raw)['mentions'], {'UNRECOGNIZED_STATUS': 1})

    def test_unrelated_tags_and_plaintext_are_ignored(self):
        raw = b'D/Other(123): {"imsdkRetCode":4}\nSSLHandshakeException\nD/iMSDK(123): NotSSLHandshakeException\n'
        self.assertEqual(reader.summarize(raw)['mentions'], {})

    def test_no_matching_log_does_not_imply_success(self):
        result = reader.summarize(b'')
        self.assertEqual(result['sdk_lines_examined'], 0)
        self.assertEqual(result['login_acceptance'], 'NOT_ESTABLISHED')

    def test_oversize_input_refused(self):
        with self.assertRaisesRegex(ValueError, 'bounded log limit'):
            reader.summarize(b'x' * (reader.MAX_BYTES + 1))

    def test_adb_only_reads_running_game_pid_and_log_buffer(self):
        replies = [subprocess.CompletedProcess([], 0, b'123\n', b''), subprocess.CompletedProcess([], 0, b'', b'')]
        with patch.object(reader.subprocess, 'run', side_effect=replies) as call:
            self.assertEqual(reader.read_adb(), b'')
        self.assertEqual(call.call_args_list[0].args[0], ['adb', 'shell', 'pidof', '-s', reader.PACKAGE])
        self.assertEqual(call.call_args_list[1].args[0], ['adb', 'logcat', '-d', '-t', '1500', '--pid=123', '-v', 'brief'])

    def test_unique_reports_do_not_append_or_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'synthetic.log'
            source.write_bytes(b'D/iMSDK(123): {"imsdkRetCode":4}\n')
            command = [sys.executable, str(PATH), '--file', str(source), '--output-dir', folder]
            for _ in range(2):
                result = subprocess.run(command, capture_output=True, check=False)
                self.assertEqual(result.returncode, 0)
            reports = list(Path(folder).glob('CF2018_ACCOUNT_ERRORS_*.txt'))
            self.assertEqual(len(reports), 2)
            self.assertEqual(reports[0].read_text(), reports[1].read_text())

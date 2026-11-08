import datetime,importlib.util,json,subprocess,unittest
from pathlib import Path
from unittest.mock import patch

P=Path(__file__).resolve().parents[1]/'tools/summarize_startup_exit.py'
spec=importlib.util.spec_from_file_location('exit_summary',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def record(reason=4,process=m.PACKAGE,status=0):
    return f'ApplicationExitInfo #0:\n timestamp=PRIVATE pid=123 realUid=999\n process={process} reason={reason} (PRIVATE) subreason=0 (OTHER) status={status}\n description=PRIVATE_SECRET\n'

def crash(package=m.PACKAGE,pid=123,message='XmlConfigSource XmlPullParserException PRIVATE_SECRET'):
    return f'E/AndroidRuntime({pid}): FATAL EXCEPTION: main\nE/AndroidRuntime({pid}): Process: {package}, PID: {pid}\nE/AndroidRuntime({pid}): {message}\n'

class Summary(unittest.TestCase):
    def test_reason_mapping_and_self_exit_does_not_claim_integrity(self):
        for code,label in [(1,'EXIT_SELF'),(4,'JAVA_CRASH'),(5,'NATIVE_CRASH'),(7,'INITIALIZATION_FAILURE')]:
            result=m.exit_records(record(code,status=18).encode());self.assertEqual(result[0]['reason'],label)
            self.assertNotIn('PRIVATE',json.dumps(result))
        self.assertEqual(m.exit_records(record(1,status=18).encode())[0]['status'],'NONZERO')

    def test_exact_main_process_only_and_three_record_bound(self):
        self.assertEqual(m.exit_records(record(process=m.PACKAGE+':service').encode()),[])
        self.assertEqual(m.exit_records(record(process=m.PACKAGE+'other').encode()),[])
        self.assertEqual(len(m.exit_records((record()*10).encode())),3)

    def test_signal_fixed_labels_and_unknown_reason(self):
        self.assertEqual(m.exit_records(record(2,status=11).encode())[0]['signal'],'SIGSEGV')
        self.assertEqual(m.exit_records(record(99).encode())[0]['reason'],'UNRECOGNIZED_REASON')

    def test_malformed_or_absent_record_is_not_normal_exit(self):
        for raw in [b'',b'permission denied',b'ApplicationExitInfo #0:\nprocess='+m.PACKAGE.encode()+b' subreason=4 status=0']:
            self.assertEqual(m.exit_records(raw),[])

    def test_java_package_scope_fixed_markers_and_secret_suppression(self):
        result=m.crash_mentions(crash().encode());self.assertEqual(result['target_java_fatal_records'],1)
        self.assertEqual(result['fixed_mentions'],{'NETWORK_SECURITY_CONFIG':1,'XML_PARSE_ERROR':1})
        self.assertNotIn('PRIVATE',json.dumps(result));self.assertNotIn(m.PACKAGE,json.dumps(result))
        self.assertEqual(m.crash_mentions(crash('another.package').encode())['target_java_fatal_records'],0)

    def test_pid_reuse_and_missing_process_do_not_mix_crashes(self):
        raw=crash(message='java.lang.NullPointerException')+crash('another.package',message='XmlConfigSource')
        self.assertEqual(m.crash_mentions(raw.encode())['fixed_mentions'],{'NULL_POINTER':1})
        self.assertEqual(m.crash_mentions(b'E/AndroidRuntime(12): FATAL EXCEPTION: main')['target_java_fatal_records'],0)

    def test_bounds(self):
        for parser in [m.exit_records,m.crash_mentions]:
            with self.assertRaises(ValueError):parser(b'x'*(m.MAX_BYTES+1))

    def test_adb_reads_existing_records_only_and_returns_explicit_failures(self):
        with patch.object(m.subprocess,'run',side_effect=[subprocess.CompletedProcess([],0,record().encode()),FileNotFoundError()]) as run:
            raw,states=m.read_existing()
        self.assertEqual(states,{'exit_info':'READ','crash_buffer':'UNAVAILABLE'})
        self.assertEqual(run.call_args_list[0].args[0],['adb','shell','dumpsys','activity','exit-info',m.PACKAGE])
        self.assertEqual(run.call_args_list[1].args[0],['adb','logcat','-b','crash','-d','-t','256','-v','brief'])
        self.assertEqual(raw['crash_buffer'],b'')

    def test_exit_code_preserved_in_bounded_range_without_inferring_integrity(self):
        for value in [0,18,26,255]:
            result=m.exit_records(record(1,status=value).encode())[0]
            self.assertEqual(result['exit_status_code'],value)
            self.assertNotIn('integrity',json.dumps(result))
        self.assertEqual(m.exit_records(record(1,status=-1).encode())[0]['exit_status_code'],'OUT_OF_RANGE')

    def test_record_before_or_after_update_and_unknown_time(self):
        updated=datetime.datetime(2026,11,8,22,0,0)
        for text,label in [('2026-11-08 21:59:00.123','BEFORE_UPDATE'),('2026-11-08 22:01:00','AT_OR_AFTER_UPDATE'),('PRIVATE','UNKNOWN')]:
            result=m.exit_records(record().replace('timestamp=PRIVATE','timestamp='+text).encode(),updated)[0]
            self.assertEqual(result['relative_to_current_package_update'],label)
            self.assertNotIn(text,json.dumps(result))

    def test_installed_identity_reads_phone_hash_without_downloading_or_exporting_path(self):
        path='/data/app/~~synthetic/package-synthetic/base.apk';digest=next(k for k,v in m.APK_ROLES.items() if v=='SCOPED_TRUST_B')
        with patch.object(m,'adb_read',side_effect=[(b'  lastUpdateTime=2026-11-08 22:00:00\n','READ'),(('package:'+path+'\n').encode(),'READ'),((digest+'  '+path+'\n').encode(),'READ')]) as read:
            identity,updated=m.read_identity()
        self.assertEqual(identity['installed_apk'],'SCOPED_TRUST_B')
        self.assertEqual(updated,datetime.datetime(2026,11,8,22,0,0))
        self.assertEqual(read.call_args_list[-1].args[0],['shell','sha256sum',path])
        self.assertNotIn(path,json.dumps(identity));self.assertNotIn(digest,json.dumps(identity))

    def test_unsafe_path_or_multiple_apks_never_passed_to_shell(self):
        for paths in [b'package:/data/app/a/$(secret)/base.apk',b'package:/data/app/a/base.apk\npackage:/data/app/a/split.apk']:
            with patch.object(m,'adb_read',side_effect=[(b'','UNAVAILABLE'),(paths,'READ')]) as read:
                identity,updated=m.read_identity()
            self.assertEqual(read.call_count,2);self.assertEqual(identity['installed_apk'],'UNKNOWN')
            self.assertIsNone(updated)

if __name__=='__main__':unittest.main()

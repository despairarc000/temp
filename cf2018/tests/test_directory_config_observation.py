"""Timer controls use fake time/sockets; never run a phone or remote server."""
import importlib.util,os,socket,sys,tempfile,types,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from prepare_directory_config import OBSERVATION_HELPER,patch,prepare

class Clock:
 def __init__(self):self.now=0;self.sleeps=0
 def monotonic(self):return self.now
 def sleep(self,n):self.now+=n;self.sleeps+=1

class Public(unittest.TestCase):
 def helper(self,clock):
  env={'time':clock,'RESOURCE_OBSERVATION_SECONDS':180}
  exec(OBSERVATION_HELPER,env);return env['resource_observation_wait']
 def test_completed_session_budget_does_not_stop_proxy_window(self):
  clock=Clock();run=types.SimpleNamespace(done=types.SimpleNamespace(is_set=lambda:True))
  proc=types.SimpleNamespace(poll=lambda:None)
  self.helper(clock)(run,proc)
  self.assertGreaterEqual(run.observation_elapsed,180)
  self.assertLess(run.observation_elapsed,180.21)
  self.assertEqual(run.observation_stop,'window_elapsed')
  self.assertGreater(clock.sleeps,800) # Sleeps rather than spinning on a set Event.
 def test_dead_proxy_is_reported_and_does_not_claim_full_window(self):
  clock=Clock();run=types.SimpleNamespace()
  with self.assertRaises(RuntimeError):self.helper(clock)(run,types.SimpleNamespace(poll=lambda:1))
  self.assertEqual((run.observation_stop,run.observation_elapsed),('proxy_exit',0))
 def test_manual_stop_remains_available(self):
  clock=Clock()
  def stop(n):raise KeyboardInterrupt
  clock.sleep=stop;run=types.SimpleNamespace()
  with self.assertRaises(KeyboardInterrupt):self.helper(clock)(run,None)
  self.assertEqual(run.observation_stop,'manual_stop')
 def test_invalid_windows_refused(self):
  for value in (True,0,12,59,301,'180'):
   with self.assertRaises(ValueError):patch('',value)

@unittest.skipUnless(os.environ.get('CF18_DIRECTORY_IDENTIFY_PREPARED'),'explicit private prepared source required')
class Prepared(unittest.TestCase):
 def test_default_unchanged_and_long_copy_keeps_all_reply_gates(self):
  source=Path(os.environ['CF18_DIRECTORY_IDENTIFY_PREPARED']);original=(source/'routed_probe_r037.py').read_text()
  old=patch(original);new=patch(original,180)
  self.assertIn('while time.monotonic()-started<12.0:',old)
  self.assertIn('while not run.done.wait(.2):',old)
  self.assertIn('while time.monotonic()-started<180.0:',new)
  self.assertIn('resource_observation_wait(run,proc)',new)
  self.assertIn('RESOURCE_OBSERVATION configured_seconds=',new)
  for gate in ('directory_reply_claimed','second_service_ack_claimed',"!='BY_ID_COMPLETE'","!='LEGACY64'",'MAX_SLOTS=4'):
   self.assertIn(gate,new)
  self.assertEqual((source/'routed_probe_r037.py').read_text(),original)
 def test_actual_handler_crosses_old_deadline_with_fake_socket(self):
  source=Path(os.environ['CF18_DIRECTORY_IDENTIFY_PREPARED'])
  with tempfile.TemporaryDirectory() as tmp:
   output=Path(tmp)/'copy';prepare(source,output,180);sys.path.insert(0,str(output))
   try:
    spec=importlib.util.spec_from_file_location('resource_observation_probe',output/'routed_probe_r037.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    clock=Clock();module.time=clock
    class Idle:
     def settimeout(self,n):pass
     def recv(self,n):clock.now+=1;raise socket.timeout
     def sendall(self,data):raise AssertionError('idle connection must receive no replies')
    run=module.Run(Path(tmp)/'run');server=types.SimpleNamespace(run=run,server_address=('127.0.0.1',0))
    handler=module.Handler.__new__(module.Handler);handler.server=server;handler.request=Idle();handler.handle()
    self.assertEqual(clock.now,180)
    self.assertEqual((run.sessions,run.finished),(1,1))
   finally:sys.path.remove(str(output))

"""Optional original-native controls; never start listeners or use phone data."""
import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"))
import unittest
from native_ack_crypto_controls import run
LIBRARY=os.environ.get('CF18_APOLLO_LIBRARY')
@unittest.skipUnless(LIBRARY,'exact private Apollo explicitly required')
class NativeAckCrypto(unittest.TestCase):
 def test_supplied_key_reaches_real_decrypt_body_and_suppressed_auth(self):
  for method in (3,4):
   with self.subTest(method=method):
    r=run(LIBRARY,method=method)
    self.assertEqual(r['return'],-77);self.assertTrue(r['auth_boundary']);self.assertEqual(r['state'],2)
    self.assertEqual(r['key_length'],16)
    self.assertEqual(r['native_calls'],['0x3ab24a','0x2845fc','0x3ab31e','0x3b8860','0x3b49a6'])
    self.assertEqual(r['body_events'][-1]['code'],0)
 def test_wrong_synthetic_key_rejects_before_body_decode(self):
  for method in (3,4):
   r=run(LIBRARY,method=method,variant='wrong_key')
   self.assertEqual(r['return'],-33);self.assertFalse(r['auth_boundary']);self.assertEqual(r['body_events'],[])
 def test_cipher_length_rejects_before_body_decode(self):
  for method in (3,4):
   r=run(LIBRARY,method=method,variant='bad_cipher_length')
   self.assertEqual(r['return'],-33);self.assertFalse(r['auth_boundary']);self.assertEqual(r['body_events'],[])
 def test_decrypted_malformed_body_rejects_at_actual_parser(self):
  for method in (3,4):
   r=run(LIBRARY,method=method,variant='bad_body')
   self.assertEqual(r['return'],-18);self.assertFalse(r['auth_boundary']);self.assertEqual(r['body_events'][-1]['code'],-32)
 def test_truncated_key_extension_never_sets_key(self):
  for method in (3,4):
   r=run(LIBRARY,method=method,variant='bad_extension')
   self.assertEqual(r['return'],-18);self.assertFalse(r['auth_boundary']);self.assertEqual(r['native_calls'],[])
 def test_no_key_plaintext_ack_success_does_not_prove_later_cipher_ready(self):
  for method in (0,4):
   r=run(LIBRARY,method=method,mode=0,encrypted=False)
   self.assertTrue(r['auth_boundary']);self.assertEqual(r['key_length'],0);self.assertNotIn('0x3ab31e',r['native_calls'])
  r=run(LIBRARY,method=4,mode=0,encrypted=True)
  self.assertEqual(r['return'],-31);self.assertFalse(r['auth_boundary'])
 def test_plain_body_does_not_enter_decrypt_even_with_supplied_key(self):
  r=run(LIBRARY,method=3,mode=2,encrypted=False)
  self.assertTrue(r['auth_boundary']);self.assertIn('0x3ab24a',r['native_calls']);self.assertNotIn('0x3ab31e',r['native_calls'])
 def test_unsupported_encryption_method_rejects_at_key_setup(self):
  r=run(LIBRARY,method=2,mode=2,encrypted=False)
  self.assertEqual(r['return'],-29);self.assertEqual(r['native_calls'],['0x3ab24a']);self.assertFalse(r['auth_boundary'])

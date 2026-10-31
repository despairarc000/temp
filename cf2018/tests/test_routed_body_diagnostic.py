import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from routed_body_diagnostic import diagnose_body

def sample():
    name=b'QueryAddrInfo'
    return len(name).to_bytes(4,'big')+name+b'\1'+bytes(8)+b'\0'

class DiagnosticTests(unittest.TestCase):
    def test_grounded_sequence_boundary(self):
        r=diagnose_body((123).to_bytes(4,'big')+sample(),123)
        self.assertEqual(r['sequence_prefix'],'MATCH')
        self.assertEqual(r['legacy_after_sequence'],'LEGACY_HEADER_PLAUSIBLE')
    def test_wrong_prefix_is_not_encryption_proof(self):
        self.assertEqual(diagnose_body(bytes(4)+sample(),123)['sequence_prefix'],'MISMATCH')
    def test_versioned_branch_is_distinguished(self):
        self.assertEqual(diagnose_body(bytes(4)+b'\x80\1\0\1',0)['legacy_after_sequence'],'VERSIONED_PREFIX_CANDIDATE')
    def test_truncation_does_not_raise(self):
        for n in range(len(sample())):
            diagnose_body(sample()[:n],0)
    def test_no_names_sequences_or_private_contents_in_output(self):
        r=diagnose_body(b'SECRET_PRIVATE_CANARY'+sample(),0x12345678)
        for token in ('SECRET','CANARY','QueryAddrInfo','305419896'):
            self.assertNotIn(token,repr(r))
    def test_bounded_inputs(self):
        for data,seq in ((bytes(8193),0),(b'A',-1),(bytearray(b'A'),0)):
            with self.assertRaises(ValueError):diagnose_body(data,seq)

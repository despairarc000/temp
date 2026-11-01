import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from native_control import NativeControl, CTX, AUX, STOP
from native_syn_ack_handoff import application_prefix, probe


@unittest.skipUnless(os.environ.get('CF18_APOLLO_LIBRARY'), 'explicit private original required')
class Tests(unittest.TestCase):
    def test_original_discovery_init_forces_unit_one(self):
        from unicorn import UC_HOOK_CODE
        from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_PC
        n = NativeControl(os.environ['CF18_APOLLO_LIBRARY'])
        reached = []
        def boundary(u, address, size, unused):
            if address == 0x39a210:  # Stop before mutex allocation/protocol/network initialization.
                reached.append(True)
                u.reg_write(UC_ARM_REG_R0, 0); u.reg_write(UC_ARM_REG_PC, STOP | 1)
        n.uc.hook_add(UC_HOOK_CODE, boundary)
        n.execute(0x39a1e0, (CTX, 17, 23), {0x3f8f7c: ('string assignment suppressed', 0)})
        self.assertTrue(reached)
        self.assertEqual(n.read(CTX+0x1c), 1)

    def test_original_client_type_setter(self):
        for value in (0, 101, 102):
            n = NativeControl(os.environ['CF18_APOLLO_LIBRARY'])
            n.write(AUX+0x58, CTX)
            n.execute(0x3a338c, (AUX, value))
            self.assertEqual(n.read(CTX+0x114), value)

    def test_platform_transition_length_discriminator(self):
        p = os.environ['CF18_APOLLO_LIBRARY']
        a = application_prefix(p, 'platform_101')
        b = application_prefix(p, 'platform_102')
        c = application_prefix(p, 'none')
        self.assertEqual([i for i in a if a[i] != b[i]], [6])
        self.assertEqual(len(a[6]), len(b[6]))
        self.assertEqual([i for i in a if a[i] != c[i]], [6])
        self.assertEqual(len(c[6]) - len(a[6]), -1)

    def test_platform_102_still_reaches_suppressed_auth(self):
        p = os.environ['CF18_APOLLO_LIBRARY']
        good = probe(p, attribute='platform_102')
        bad = probe(p, attribute='platform_102', variant='wrong_magic')
        self.assertTrue(good['auth_send_boundary']); self.assertEqual(good['return'], -77)
        self.assertFalse(bad['auth_send_boundary']); self.assertEqual(bad['return'], -13)

    def test_pinned_reference_matches_discovery_defaults(self):
        folder = os.environ.get('CF18_V38_SOURCE')
        if not folder:
            self.skipTest('explicit original probe source required')
        import hashlib
        import json
        from second_service_syn_gate import _parts
        root = Path(__file__).resolve().parents[1]
        pins = json.loads((root/'coordination/V38_SOURCE_PINS.json').read_text())
        data = (Path(folder)/'golden_request.hex').read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), pins['golden_request.hex'])
        fields = {f[0]: f for f in _parts(bytes.fromhex(data.decode()))[2]}
        def signed(value):
            return (value >> 1) ^ -(value & 1)
        self.assertEqual(signed(fields[5][2]), 1)
        self.assertEqual(signed(fields[6][2]), 101)

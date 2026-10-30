import hashlib
import unittest
from auth_v12_fixtures import EXPECTED, account_full_zero, describe, nested, reply, scalar, varuint

class FixtureTests(unittest.TestCase):
    def test_all_exact_pinned_hashes(self):
        for name, expected in EXPECTED.items():
            with self.subTest(name=name):
                packet = reply(name)
                self.assertEqual(len(packet), expected["length"])
                self.assertEqual(hashlib.sha256(packet).hexdigest(), expected["sha256"])

    def test_header_lengths(self):
        self.assertEqual({d["header"] for d in describe()}, {42})
        self.assertEqual({d["body"] for d in describe()}, {7, 24, 37})

    def test_aa_prefix_and_extension_tags(self):
        for name in EXPECTED:
            packet = reply(name)
            self.assertEqual(packet[:5], b"\xaa\x00\x00\x00\x2a")
            self.assertIn(varuint((0x2002 << 4) | 1) + b"\x00", packet[:42])
            self.assertEqual(packet[42:45], varuint((0x2002 << 4) | 5))

    def test_body_only_difference_in_header(self):
        cases = [reply(n) for n in EXPECTED]
        header_bytes = [p[:42] for p in cases]
        changed = [i for i in range(42) if len({h[i] for h in header_bytes}) > 1]
        self.assertEqual(changed, [32])

    def test_scalar_and_nested_encoding(self):
        self.assertEqual(scalar(1, 0x4366), bytes.fromhex("11e68601"))
        self.assertEqual(nested(1, b""), bytes.fromhex("1500000000"))
        self.assertIn(bytes.fromhex("0100"), account_full_zero())

    def test_unknown_and_bounds(self):
        with self.assertRaises(ValueError):
            reply("NOT_A_REPLY")
        for value in (-1, 1 << 64, 1.1):
            with self.assertRaises(ValueError):
                varuint(value)

    def test_no_external_sources_or_network(self):
        import ast, inspect, auth_v12_fixtures
        source = inspect.getsource(auth_v12_fixtures)
        module = ast.parse(source)
        imports = [name.name for n in module.body if isinstance(n, ast.Import) for name in n.names]
        self.assertEqual(imports, ["hashlib"])
        self.assertNotIn("socket.", source)

if __name__ == "__main__":
    unittest.main()

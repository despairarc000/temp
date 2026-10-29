import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("knowledge",ROOT/"tools/knowledge.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestKnowledge(unittest.TestCase):
 def test_doctor(self):
  self.assertEqual(mod.doctor(),[])
 def test_tgcp_route(self):
  routes,paths=mod.route("tgcp ack")
  self.assertEqual(routes[0][0],"tgcp")
  self.assertIn("knowledge-system/vault/research/TGCP.md",paths)
 def test_gameplay_route(self):
  routes,paths=mod.route("offline bots tdm")
  self.assertEqual(routes[0][0],"gameplay")
  self.assertIn("knowledge-system/vault/specs/ACCEPTANCE.md",paths)
 def test_unknown(self):
  routes,paths=mod.route("unrecognized")
  self.assertEqual(routes,[])
  self.assertIn("knowledge-system/vault/INDEX.md",paths)
 def test_graph(self):
  edges=mod.edges()
  self.assertTrue(any(e[2]=="doc-link" for e in edges))
  self.assertTrue(any("blocks" in e[2] for e in edges))

if __name__=="__main__":unittest.main()

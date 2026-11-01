"""Opt-in prepared R037 lifecycle: original kit test plus dispatch assertions."""
import importlib
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


class Tests(unittest.TestCase):
    def test_two_connections_keep_reply_and_hold_second_route(self):
        folder = os.environ.get('CF18_R037_PREPARED')
        if not folder:
            self.skipTest('explicit private prepared R037 copy required')
        folder = str(Path(folder).resolve())
        sys.path.insert(0, folder)
        try:
            m = importlib.import_module('test_r037_integration')
            original = m.report
            observed = []
            def report(run, target):
                events = [json.loads(x) for x in run.log.read_text().splitlines()]
                self.assertEqual(sum(e['action'] == 'ack_sent' for e in events), 1)
                self.assertEqual(sum(e['action'] == 'r033_reply_sent' for e in events), 1)
                result = original(run, target)
                text = result.read_text()
                self.assertIn('FIRST_SYN slot=1 class=REFERENCE_NAMED_ROUTE_CANDIDATE', text)
                self.assertIn('FIRST_SYN slot=2 class=TEN_BYTE_NAMED_ROUTE_CANDIDATE disposition=HOLD_NO_ACK', text)
                self.assertIn('SYN_CONTEXT slot=1 class=REFERENCE_EXACT', text)
                self.assertIn('SYN_CONTEXT slot=2 class=MATCH_EXCEPT_ROUTE', text)
                observed.append(True)
                return result
            with patch.object(m, 'report', report):
                m.Tests('test_one_reply_then_exact_same_base_shape_131_diagnostics').test_one_reply_then_exact_same_base_shape_131_diagnostics()
            self.assertEqual(observed, [True])
        finally:
            sys.path.remove(folder)

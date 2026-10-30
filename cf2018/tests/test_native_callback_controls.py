"""Native negative callback controls; never authentication acceptance tests."""
import os
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from native_callback_controls import callback_probe

LIBRARY = os.environ.get('CF18_APOLLO_LIBRARY')


class BoundsTests(unittest.TestCase):
    def test_invalid_controls_fail_before_loading_private_source(self):
        for config in ({'stage':'socket'}, {'observer':1}, {'result':123},
                       {'state':3}, {'execute_bind':1}, {'buffer_cast':0}):
            with self.subTest(config=config), self.assertRaises(ValueError):
                callback_probe('absent', **config)


@unittest.skipUnless(LIBRARY, 'private pinned Apollo and native dependencies required')
class NativeCallbackTests(unittest.TestCase):
    def test_actual_observer_thunk_schedules_local_zero_without_account(self):
        r=callback_probe(LIBRARY)
        self.assertEqual(r['return'],1)
        self.assertEqual(r['client_connected'],1)
        self.assertEqual(r['scheduled'],[{'object_matches':True,'method':0x3c67ad,
                                          'adjust':0,'argument':0}])
        for address in (0x3c6378,0x3c6300,0x3c59fa):
            self.assertIn(['native_site',address],r['events'])
        self.assertTrue(r['connected_info_prefix_unchanged_zero'])
        self.assertFalse(any('RTTI' in s for s in r['stubs']))

    def test_state4_wait_does_not_schedule_connected(self):
        r=callback_probe(LIBRARY,state=4)
        self.assertEqual(r['scheduled'],[])
        self.assertEqual(r['client_connected'],0)

    def test_empty_transport_observer_list_does_not_run_connector(self):
        r=callback_probe(LIBRARY,observer=False)
        self.assertEqual(r['scheduled'],[])
        self.assertEqual(r['client_connected'],1)
        self.assertNotIn(['native_site',0x3c6300],r['events'])

    def test_injected_dispatch_reaches_real_service_with_zero_info(self):
        r=callback_probe(LIBRARY,stage='dispatch')
        self.assertEqual(r['return'],-77)
        self.assertIn(['service_result',0],r['events'])
        self.assertIn(['connected_info_pointer_matches',True],r['events'])
        self.assertTrue(r['reached_bind_boundary'])
        self.assertTrue(r['connected_info_prefix_unchanged_zero'])
        self.assertTrue(any('RTTI' in s for s in r['stubs']))

    def test_nonzero_result_sets_error_flag_before_buffer_lookup(self):
        r=callback_probe(LIBRARY,stage='dispatch',result=9)
        self.assertEqual(r['service_error_flag'],1)
        self.assertFalse(r['reached_bind_boundary'])
        self.assertFalse(any('GetBuffer' in s for s in r['stubs']))

    def test_no_service_connector_prevents_bind(self):
        r=callback_probe(LIBRARY,stage='dispatch',connector=False)
        self.assertFalse(r['reached_bind_boundary'])
        self.assertFalse(any('GetBuffer' in s for s in r['stubs']))

    def test_failed_observer_rtti_prevents_service_callback(self):
        r=callback_probe(LIBRARY,stage='dispatch',cast=False)
        self.assertNotIn(['native_site',0x39ca78],r['events'])

    def test_failed_buffer_rtti_prevents_bind_after_service_callback(self):
        r=callback_probe(LIBRARY,stage='dispatch',buffer_cast=False)
        self.assertIn(['native_site',0x39ca78],r['events'])
        self.assertFalse(r['reached_bind_boundary'])

    def test_real_bind_sets_function_object_and_real_open_is_noop(self):
        r=callback_probe(LIBRARY,stage='dispatch',execute_bind=True)
        self.assertTrue(r['buffer_manager_nonzero'])
        self.assertTrue(r['bound_connector_matches'])
        self.assertIn(['native_site',0x3c1498],r['events'])
        self.assertTrue(r['connected_info_prefix_unchanged_zero'])
        self.assertFalse(any('socket send' in s for s in r['stubs']))

    def test_empty_dispatch_list_prevents_service_callback(self):
        r=callback_probe(LIBRARY,stage='dispatch',observer=False)
        self.assertNotIn(['native_site',0x39ca78],r['events'])
        self.assertFalse(r['reached_bind_boundary'])


if __name__=='__main__':
    unittest.main()

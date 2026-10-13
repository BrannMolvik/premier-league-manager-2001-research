"""Source event31 branch contracts: no native window or CRT execution."""
import unittest
from original_scouting_event31_reseed import (
    OriginalManagerEvent31Error,
    SOURCE_EVENT_ID,SOURCE_WINDOW_VTABLE,SOURCE_WINDOW_RTTI,
    FIRST_RESEED_CALLER,SECOND_RESEED_CALLER,
    project_original_manager_event31_reseed_path,
)

class OriginalManagerEvent31SourceTests(unittest.TestCase):
    def args(self):
        return dict(native_event_id=31,native_window_vtable=SOURCE_WINDOW_VTABLE,
                    source_manager_list_pointer_is_null=False)

    def test_event31_first_state_xor_reseed_is_unconditional_in_branch(self):
        receipt=project_original_manager_event31_reseed_path(**self.args())
        self.assertEqual(receipt.native_event_id,SOURCE_EVENT_ID)
        self.assertEqual(receipt.source_window_rtti,SOURCE_WINDOW_RTTI)
        self.assertEqual(receipt.source_window_rtti,'.?AVPScouting2K@@')
        self.assertEqual(receipt.native_first_reseed_callsite,FIRST_RESEED_CALLER)
        self.assertIsNone(receipt.native_second_reseed_callsite)
        self.assertFalse(receipt.original_qualifying_window_event_observed)
        self.assertFalse(receipt.actual_shared_crt_seed_verified)

    def test_absent_original_manager_list_enters_second_reseed(self):
        params=self.args()
        params["source_manager_list_pointer_is_null"]=True
        receipt=project_original_manager_event31_reseed_path(**params)
        self.assertEqual(receipt.native_second_reseed_callsite,SECOND_RESEED_CALLER)

    def test_other_event_id_and_other_native_vtables_fail_closed(self):
        for bad_id in (0,1,30,32,True,None,31.0):
            with self.subTest(id=bad_id),self.assertRaises(OriginalManagerEvent31Error):
                project_original_manager_event31_reseed_path(
                    **{**self.args(),"native_event_id":bad_id})
        for bad_vft in (None,True,0,0x7C6DDC):
            with self.subTest(vft=bad_vft),self.assertRaises(OriginalManagerEvent31Error):
                project_original_manager_event31_reseed_path(
                    **{**self.args(),"native_window_vtable":bad_vft})

    def test_unobserved_manager_list_state_is_never_guessed(self):
        for bad in (None,1,0,"empty"):
            with self.subTest(flag=bad),self.assertRaises(OriginalManagerEvent31Error):
                project_original_manager_event31_reseed_path(
                    **{**self.args(),"source_manager_list_pointer_is_null":bad})

if __name__=="__main__":
    unittest.main()

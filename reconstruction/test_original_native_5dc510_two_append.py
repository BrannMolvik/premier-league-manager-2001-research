"""Source-exact optional 5DC650 then mandatory 5DC510 FIFO sequencing."""
from struct import unpack_from
from unittest import TestCase,main
from original_native_5dc510_two_append import (
    Original5DC510TwoAppendError,source_original_5dc510_optional_then_main_append,
)
from original_native_5dc650_event_tail import source_original_5dc650_reached_record_and_fifo
from test_original_native_5dc650_event_tail import fixture as inputs
from test_original_native_5dc510_event_tail import source

def joined():
    first=inputs()
    stage=source_original_5dc650_reached_record_and_fifo(**first)
    q=stage.original_source_fifo_projection
    second=source()
    second['original_owner_at_5dc5d9']=q.owner_after_append
    second['original_payload_pointer_allocated']=0xa0000
    second['original_wrapper_pointer_allocated']=0xb0000
    second['original_old_tail_pointer_if_nonempty']=q.original_new_wrapper_pointer
    second['original_old_tail_wrapper_if_nonempty']=q.new_native_wrapper_after_append
    return first,second

class TwoAppendTests(TestCase):
    def test_5dc650_early_return_still_runs_5dc510_main(self):
        result=source_original_5dc510_optional_then_main_append(
            original_5dc650_return_al_nonzero=False,
            original_5dc650_reached_inputs_if_appended=None,
            original_5dc510_main_reached_inputs=source())
        self.assertIsNone(result.optional_5dc650_first_append)
        self.assertFalse(result.live_game_state_updated)

    def test_joined_first_then_second_appends_in_native_order(self):
        first,second=joined()
        result=source_original_5dc510_optional_then_main_append(
            original_5dc650_return_al_nonzero=True,
            original_5dc650_reached_inputs_if_appended=first,
            original_5dc510_main_reached_inputs=second)
        q=result.mandatory_5dc510_second_append
        self.assertEqual(unpack_from('<I',q.owner_after_append,4)[0],0x60000)
        self.assertEqual(unpack_from('<I',q.owner_after_append,8)[0],0xb0000)
        self.assertEqual(unpack_from('<I',q.old_tail_after_append_if_reached,4)[0],0xb0000)
        self.assertFalse(result.original_true_native_call_executed)

    def test_stage_substitution_and_wrong_al_fail_closed(self):
        first,second=joined()
        for altered in (
            {'original_owner_at_5dc5d9':source()['original_owner_at_5dc5d9']},
            {'original_old_tail_pointer_if_nonempty':0x70000},
            {'original_wrapper_pointer_allocated':0x60000},
        ):
            with self.subTest(altered=altered):
                with self.assertRaises(Original5DC510TwoAppendError):
                    source_original_5dc510_optional_then_main_append(
                        original_5dc650_return_al_nonzero=True,
                        original_5dc650_reached_inputs_if_appended=first,
                        original_5dc510_main_reached_inputs=second|altered)
        for al,receipt in ((True,None),(False,first),(1,first)):
            with self.subTest(al=al):
                with self.assertRaises(Original5DC510TwoAppendError):
                    source_original_5dc510_optional_then_main_append(
                        original_5dc650_return_al_nonzero=al,
                        original_5dc650_reached_inputs_if_appended=receipt,
                        original_5dc510_main_reached_inputs=source())

if __name__=='__main__':main()

"""Original native 5127A0 row+4A optional 41A5B0 source-event ownership."""
from __future__ import annotations
from dataclasses import replace
import unittest

from test_original_native_5127a0_combined_owner import qualified,side
from test_original_native_41a5b0_extra_event import staged,player
from original_native_41a5b0_extra_event import source_original_41a5b0_optional_extra_from_reached
from original_native_5127a0_extra_event_owners import (
    Original5127A0ExtraEventOwnerError,
    source_original_5127a0_qualified_optional_extra_events,
)


def source_extra(*,pid=100,pointer=0x4000,registered=True,status=1,
                 count=None):
    value=staged(source=player(pid=pid,status=status),
                 registered=registered,count=count)
    value=replace(value,original_native_row_player_pointer=pointer)
    return source_original_41a5b0_optional_extra_from_reached(value)


class Original5127A0ExtraOwnersTests(unittest.TestCase):
    def test_original_row_plus4a_safe_noallocation_return(self):
        owner=qualified(first=side(0,extra=True))
        event=source_extra()
        x=source_original_5127a0_qualified_optional_extra_events(
            source_original_owner=owner,
            original_reached_extra_by_side=((event,),()),
        )
        self.assertEqual((x.original_first_side_extra_count,x.original_second_side_extra_count),(1,0))
        self.assertEqual(x.original_world_allocations_outstanding,0)
        self.assertTrue(x.original_extra_rows_have_no_mutating_world_effects)
        self.assertFalse(x.native_callbacks_executed)
        self.assertFalse(x.live_game_state_updated)
        self.assertFalse(x.match_finished)

    def test_original_two_team_extra_event_types_remain_separate_outstanding(self):
        owner=qualified(first=side(0,extra=True),second=side(1,extra=True))
        safe=source_extra(status=1)
        pending=source_extra(pid=110,pointer=0x4200,status=0)
        x=source_original_5127a0_qualified_optional_extra_events(
            source_original_owner=owner,
            original_reached_extra_by_side=((safe,),(pending,)),
        )
        self.assertEqual(x.original_first_side_extra_count,1)
        self.assertEqual(x.original_second_side_extra_count,1)
        self.assertEqual(x.original_world_allocations_outstanding,1)
        self.assertFalse(x.original_extra_rows_have_no_mutating_world_effects)
        self.assertFalse(x.match_finished)
        self.assertEqual(pending.original_605f90_subtype_if_allocated,1)

    def test_nonregistered_under14_skips_all_mutations(self):
        owner=qualified(first=side(0,extra=True))
        decision=source_extra(registered=False,count=13,status=0)
        x=source_original_5127a0_qualified_optional_extra_events(
            source_original_owner=owner,
            original_reached_extra_by_side=((decision,),()),
        )
        self.assertTrue(x.original_extra_rows_have_no_mutating_world_effects)
        self.assertEqual(x.original_world_allocations_outstanding,0)

    def test_missing_extra_and_extra_in_zero_flag_row_are_refused(self):
        owner=qualified(first=side(0,extra=True))
        with self.assertRaisesRegex(Original5127A0ExtraEventOwnerError,"exactly"):
            source_original_5127a0_qualified_optional_extra_events(
                source_original_owner=owner,original_reached_extra_by_side=((),()))
        owner_noextra=qualified()
        with self.assertRaisesRegex(Original5127A0ExtraEventOwnerError,"exactly"):
            source_original_5127a0_qualified_optional_extra_events(
                source_original_owner=owner_noextra,
                original_reached_extra_by_side=((source_extra(),),()))

    def test_wrong_postrow_pointer_and_native_id_are_refused(self):
        owner=qualified(first=side(0,extra=True))
        event=source_extra()
        for bad in (
            replace(event,original_native_row_player_pointer=0x9000),
            replace(event,original_player_id=900),
        ):
            with self.subTest(bad=bad),self.assertRaisesRegex(
                Original5127A0ExtraEventOwnerError,"identity/pointer mismatch"
            ):
                source_original_5127a0_qualified_optional_extra_events(
                    source_original_owner=owner,original_reached_extra_by_side=((bad,),()))

    def test_contradictory_source_receipt_rejected_without_any_world_mutation(self):
        owner=qualified(first=side(0,extra=True))
        event=source_extra()
        contradict=replace(event,source_branch_complete_without_world_effects=False)
        with self.assertRaisesRegex(Original5127A0ExtraEventOwnerError,"contradictory"):
            source_original_5127a0_qualified_optional_extra_events(
                source_original_owner=owner,
                original_reached_extra_by_side=((contradict,),()))
        with self.assertRaisesRegex(Original5127A0ExtraEventOwnerError,"source"):
            source_original_5127a0_qualified_optional_extra_events(
                source_original_owner=replace(owner,live_game_state_updated=True),
                original_reached_extra_by_side=((event,),()))


if __name__=="__main__":
    unittest.main()

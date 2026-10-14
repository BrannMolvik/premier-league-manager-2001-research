"""Ordered two-owner 5127A0 post-row original match source guard tests."""
from __future__ import annotations
from dataclasses import replace
import unittest
from original_native_5127a0_order_guard import (
    Original5127A0OrderedStep,Original5127A0OrderedSide,
    Original5127A0OrderError,source_original_5127a0_two_owner_order_from_reached,
)
from original_native_5127a0_row_incident_source import Original5127A0RowCall
from original_native_419680_availability import Original419680AvailabilityReceipt


def availability(pid,ptr):
    return Original419680AvailabilityReceipt(
        original_player_id=pid,original_player_after=b"source_only",
        original_calendar_lookup_nonnull=bool(ptr),
        original_league_uefa_source_owner_34_one=None,
        original_fa_due_date_checked=False,
        original_417340_eligibility_callback_reached=False,
        original_status_bit1_source_or_branch=False,
    )


def side(pass_id,ptr=0,extra=False):
    roster=(100+pass_id*10,101+pass_id*10)
    row=Original5127A0RowCall(
        pass_index=pass_id,row_index=0,
        source_current_team_pointer=0x1000+pass_id*0x1000,
        source_opponent_team_pointer=0x2000-pass_id*0x1000,
        source_player_pointer=0x4000+pass_id*0x100,
        source_4197c0_arg1=1,source_4197c0_arg2=0,
        source_4197c0_arg3=0x2000-pass_id*0x1000,
        source_41a5b0_called_after_row=extra,
    )
    stages=[
        *(Original5127A0OrderedStep("return",p) for p in roster),
        Original5127A0OrderedStep("row",row.source_player_pointer,0,row),
    ]
    if extra:
        stages.append(Original5127A0OrderedStep("extra",row.source_player_pointer,0,row))
    stages.extend(Original5127A0OrderedStep(
        "avail",p,original_availability=availability(p,ptr),
        original_lookup_pointer_used=ptr) for p in roster)
    return Original5127A0OrderedSide(pass_id,roster,(row,),ptr,tuple(stages))


def trace(first=None,second=None):
    return (side(0) if first is None else first,
            side(1) if second is None else second)


class Original5127A0OrderGuardTests(unittest.TestCase):
    def test_source_both_owners_with_null_and_nonnull_calendar(self):
        a=trace(second=side(1,ptr=0x5555,extra=True))
        receipt=source_original_5127a0_two_owner_order_from_reached(a)
        self.assertEqual((
            receipt.original_total_return_callbacks,
            receipt.original_total_row_callbacks,
            receipt.original_total_extra_callbacks,
            receipt.original_total_availability_callbacks,
            receipt.original_owner_passes),(4,2,1,4,(0,1)))
        self.assertFalse(receipt.native_callbacks_executed)
        self.assertFalse(receipt.live_game_state_mutated)
        self.assertFalse(receipt.original_match_finished)

    def test_out_of_order_post_row_and_missing_extra_must_fail(self):
        first=side(0,extra=True)
        swapped=list(first.source_steps)
        swapped[1],swapped[-1]=swapped[-1],swapped[1]
        with self.assertRaisesRegex(Original5127A0OrderError,"order"):
            source_original_5127a0_two_owner_order_from_reached(
                trace(first=replace(first,source_steps=tuple(swapped))))
        with self.assertRaisesRegex(Original5127A0OrderError,"missing/extra"):
            source_original_5127a0_two_owner_order_from_reached(
                trace(first=replace(first,source_steps=first.source_steps[:-1])))
        without_extra=tuple(step for step in first.source_steps if step.phase!="extra")
        with self.assertRaisesRegex(Original5127A0OrderError,"missing/extra"):
            source_original_5127a0_two_owner_order_from_reached(
                trace(first=replace(first,source_steps=without_extra)))

    def test_wrong_side_and_duplicate_source_players_rejected(self):
        sides=trace()
        with self.assertRaisesRegex(Original5127A0OrderError,"owner order"):
            source_original_5127a0_two_owner_order_from_reached(sides[::-1])
        broken=replace(sides[0],source_roster_ids=(100,100))
        with self.assertRaisesRegex(Original5127A0OrderError,"duplicate"):
            source_original_5127a0_two_owner_order_from_reached(
                trace(first=broken))
        rows=replace(sides[0],source_rows=(replace(sides[0].source_rows[0],row_index=1),))
        with self.assertRaisesRegex(Original5127A0OrderError,"identity/order"):
            source_original_5127a0_two_owner_order_from_reached(trace(first=rows))

    def test_wrong_post_row_lookup_and_recipient_rejected(self):
        s=side(1,ptr=0x5555)
        p=list(s.source_steps)
        p[-1]=replace(p[-1],original_lookup_pointer_used=0)
        with self.assertRaisesRegex(Original5127A0OrderError,"calendar pointer"):
            source_original_5127a0_two_owner_order_from_reached(
                trace(second=replace(s,source_steps=tuple(p))))
        p=list(s.source_steps)
        p[-1]=replace(p[-1],original_availability=availability(999,0x5555))
        with self.assertRaisesRegex(Original5127A0OrderError,"player/NULL"):
            source_original_5127a0_two_owner_order_from_reached(
                trace(second=replace(s,source_steps=tuple(p))))

    def test_non_availability_phase_cannot_claim_post_row_status(self):
        s=side(0)
        p=list(s.source_steps)
        p[0]=replace(p[0],original_availability=availability(100,0))
        with self.assertRaisesRegex(Original5127A0OrderError,"cannot borrow"):
            source_original_5127a0_two_owner_order_from_reached(
                trace(first=replace(s,source_steps=tuple(p))))


if __name__=="__main__":
    unittest.main()

"""Source owner/row/roster identity plus original two-team callback order."""
from __future__ import annotations

from dataclasses import replace
from struct import pack_into
import unittest

from original_native_5127a0_order_guard import (
    Original5127A0OrderedStep,Original5127A0OrderedSide,
)
from original_native_5127a0_player_identity import (
    Original5127A0ReachedPlayer,Original5127A0IdentityError,
)
from original_native_5127a0_row_incident_source import Original5127A0RowCall
from original_native_419680_availability import Original419680AvailabilityReceipt
from original_native_5127a0_combined_owner import (
    Original5127A0CombinedSourceError,
    source_original_5127a0_qualified_two_owner_identity,
)


def native_player(pid):
    raw=bytearray(0x250)
    pack_into("<H",raw,4,pid)
    return bytes(raw)


def owner(first=0x1000, second=0x2000, source_sides=None):
    raw=bytearray(0xb58)
    pack_into("<I",raw,0,first)
    pack_into("<I",raw,0x5b0,second)
    if source_sides is not None:
        for index,source in enumerate(source_sides):
            count_off=0x5a4 if index==0 else 0xb54
            ptr_off=0x4 if index==0 else 0x5b4
            row_off=0x4c if index==0 else 0x5fc
            pack_into("<i",raw,count_off,len(source.source_rows))
            for i,row in enumerate(source.source_rows):
                pack_into("<I",raw,ptr_off+4*i,row.source_player_pointer)
                raw[row_off+0x48+0x4c*i]=row.source_4197c0_arg1
                raw[row_off+0x49+0x4c*i]=row.source_4197c0_arg2
                raw[row_off+0x4a+0x4c*i]=int(row.source_41a5b0_called_after_row)
    return bytes(raw)


def side(i,*,roster=None,ptr=0,extra=False,row_count=1):
    if roster is None:
        roster=(100+i*10,101+i*10)
    rowptr=0x4000+i*0x200
    first=0x1000 if i==0 else 0x2000
    second=0x2000 if i==0 else 0x1000
    rows=tuple(Original5127A0RowCall(
        pass_index=i,row_index=index,
        source_current_team_pointer=first,source_opponent_team_pointer=second,
        source_player_pointer=rowptr+index*0x40,
        source_4197c0_arg1=1,source_4197c0_arg2=0,
        source_4197c0_arg3=second,source_41a5b0_called_after_row=extra,
    ) for index in range(row_count))
    steps=[*(Original5127A0OrderedStep("return",pid) for pid in roster)]
    for index,row in enumerate(rows):
        steps.append(Original5127A0OrderedStep("row",row.source_player_pointer,index,row))
        if extra:
            steps.append(Original5127A0OrderedStep("extra",row.source_player_pointer,index,row))
    for pid in roster:
        receipt=Original419680AvailabilityReceipt(
            original_player_id=pid,original_player_after=native_player(pid),
            original_calendar_lookup_nonnull=bool(ptr),
            original_league_uefa_source_owner_34_one=None,
            original_fa_due_date_checked=False,
            original_417340_eligibility_callback_reached=False,
            original_status_bit1_source_or_branch=False)
        steps.append(Original5127A0OrderedStep(
            "avail",pid,original_availability=receipt,original_lookup_pointer_used=ptr))
    reached=tuple(Original5127A0ReachedPlayer(
        rowptr+index*0x40,native_player(pid)) for index,pid in enumerate(roster))
    return Original5127A0OrderedSide(i,roster,rows,ptr,tuple(steps)),reached


def qualified(first=None, second=None, source_owner=None):
    one,r1=side(0) if first is None else first
    two,r2=side(1) if second is None else second
    return source_original_5127a0_qualified_two_owner_identity(
        original_processing_owner_record=owner(source_sides=(one,two)) if source_owner is None else source_owner,
        original_sides=(one,two),
        original_reached_roster_players=(r1,r2),
    )


class Original5127A0CombinedOwnerTests(unittest.TestCase):
    def test_two_independent_sides_with_distinct_null_lookup(self):
        first=side(0,ptr=0,extra=True)
        second=side(1,ptr=0x121212,extra=False)
        r=qualified(first,second)
        self.assertEqual(r.original_row_native_ids,((100,),(110,)))
        self.assertEqual(r.first_side.native_roster_pointers,(0x4000,0x4040))
        self.assertEqual(r.second_side.native_roster_pointers,(0x4200,0x4240))
        self.assertEqual((
            r.order.original_total_return_callbacks,
            r.order.original_total_row_callbacks,
            r.order.original_total_extra_callbacks,
            r.order.original_total_availability_callbacks,
        ),(4,2,1,4))
        self.assertFalse(r.source_native_callbacks_executed)
        self.assertFalse(r.live_game_state_updated)
        self.assertFalse(r.finished_match_journey)

    def test_zero_roster_source_branch_can_skip_all_per_player_callbacks(self):
        empty=side(0,roster=(),row_count=0)
        second=side(1)
        result=qualified(empty,second)
        self.assertEqual(result.first_side.native_roster_ids,())
        self.assertEqual(result.order.original_total_return_callbacks,2)
        self.assertEqual(result.original_row_native_ids,((),(110,)))

    def test_reordered_both_owner_passes_and_cross_team_pointer_failclosed(self):
        a=side(0)
        b=side(1)
        with self.assertRaisesRegex(ValueError,"EBX 0 then 1"):
            source_original_5127a0_qualified_two_owner_identity(
                original_processing_owner_record=owner(),
                original_sides=(b[0],a[0]),
                original_reached_roster_players=(b[1],a[1]))
        wrong=replace(a[0].source_rows[0],source_opponent_team_pointer=0x9999)
        source=replace(a[0],source_rows=(wrong,))
        steps=tuple(replace(s,original_row=wrong) if s.phase=="row" else s
                    for s in source.source_steps)
        source=replace(source,source_steps=steps)
        with self.assertRaisesRegex(Original5127A0CombinedSourceError,"opposing team"):
            qualified((source,a[1]),b)

    def test_actual_roster_source_identity_and_duplicate_cross_owner_rejected(self):
        a,b=side(0),side(1)
        forged=(Original5127A0ReachedPlayer(0x4000,native_player(888)),a[1][1])
        with self.assertRaisesRegex(Original5127A0IdentityError,"DBRPlayer"):
            qualified((a[0],forged),b)
        # Same native player ID on the second team, even at different address.
        second=side(1,roster=(100,111))
        with self.assertRaisesRegex(Original5127A0CombinedSourceError,"across opposing teams"):
            qualified(a,second)
        # Same original resolved pointer in two independent native owners.
        second_normal=side(1)
        source_second=second_normal[0]
        cross=replace(source_second.source_rows[0],source_player_pointer=0x4000)
        source_second=replace(
            source_second,
            source_rows=(cross,),
            source_steps=tuple(
                replace(step,original_player_id=0x4000,original_row=cross)
                if step.phase=="row" else step
                for step in source_second.source_steps),
        )
        both_pointer=(Original5127A0ReachedPlayer(0x4000,native_player(110)),
                      second_normal[1][1])
        with self.assertRaisesRegex(Original5127A0CombinedSourceError,"across opposing teams"):
            qualified(a,(source_second,both_pointer))

    def test_duplicated_starting_player_pointer_and_wrong_team_owner_failclosed(self):
        a,b=side(0,row_count=2)
        one=replace(a.source_rows[1],source_player_pointer=a.source_rows[0].source_player_pointer)
        rows=(a.source_rows[0],one)
        source=replace(a,source_rows=rows,
            source_steps=tuple(
                replace(s,original_player_id=one.source_player_pointer,original_row=one)
                if s.phase=="row" and s.original_row_index==1 else s
                for s in a.source_steps))
        with self.assertRaisesRegex(Original5127A0CombinedSourceError,"appears twice"):
            qualified((source,a[1]),b)
        with self.assertRaisesRegex(Original5127A0CombinedSourceError,"distinct"):
            qualified(a,b,owner(0x1000,0x1000,source_sides=(a[0],b[0])))
        # The supplied source owner is canonical even if side rows are forged
        # to maintain internally consistent callback arguments.
        canonical_owner=owner(source_sides=(a[0],b[0]))
        fake=replace(a[0].source_rows[0],source_4197c0_arg1=99)
        forged_side=replace(a[0],source_rows=(fake,),source_steps=tuple(
            replace(step,original_row=fake) if step.phase=="row" else step
            for step in a[0].source_steps))
        with self.assertRaisesRegex(Original5127A0CombinedSourceError,"owner row bytes"):
            qualified((forged_side,a[1]),b,canonical_owner)
        with self.assertRaisesRegex(Original5127A0CombinedSourceError,"record"):
            qualified(a,b,b"")

    def test_reject_extra_or_missing_reached_player_after_original_roster(self):
        first=side(0)
        second=side(1)
        with self.assertRaisesRegex(Original5127A0IdentityError,"coverage"):
            qualified((first[0],first[1][:-1]),second)
        more=first[1]+(Original5127A0ReachedPlayer(0x9999,native_player(999)),)
        with self.assertRaisesRegex(Original5127A0IdentityError,"coverage"):
            qualified((first[0],more),second)


if __name__=="__main__":
    unittest.main()

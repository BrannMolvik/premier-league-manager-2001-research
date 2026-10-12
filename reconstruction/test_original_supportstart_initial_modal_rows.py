"""Exact first six staff and seventh blank from native linked-list order."""
import unittest
from dataclasses import replace

from fm2001_data import Club, CompetitionDefinition, Player
from original_supportstart_name_group_source import OriginalNameGroupCandidateRoute
from original_supportstart_initial_modal_rows import (
    OriginalSupportStartInitialRowsError,
    source_supportstart_initial_modal_rows,
    source_supportstart_native_staging_transfers,
)
from original_supportstart_teamselect_user_birth import (
    replay_original_teamselect_user_birth_direct_rng,
)
from support_staff import INITIAL_SUPPORT_STAFF_TYPES


class SourceZeroRng:
    def __init__(self): self.calls=[]
    def randbelow(self,bound):
        self.calls.append(bound)
        return 0


def original_fixture_birth(rng):
    clubs=(Club(0,"OriginalClub","OC","Ground",0,competition_id=5,country_id=7),)
    players=(Player(0,"David","Seaman",0,1,None,0,0,0,(0,0,0),(),()),)
    source_league=CompetitionDefinition(
        id=5,name="OriginalLeague",substitute_quota=3,
        max_non_eu_players=0,runtime_kind_code=1,
        parent_competition_id=None,country_region_id=7,
    )
    return replay_original_teamselect_user_birth_direct_rng(
        rng,original_clubs=clubs,original_players=players,
        original_root_league=source_league,selected_club_id=0,
        name_route=OriginalNameGroupCandidateRoute(
            7,7,1,"global_players",(),1
        ),
        selection_context=0,require_shipped_club_count=False,
    )


class NativeSupportStartModalInitialRowsTests(unittest.TestCase):
    def test_six_original_final_names_then_blank_seventh_slot(self):
        rng=SourceZeroRng()
        birth=original_fixture_birth(rng)
        prior=len(rng.calls)
        self.assertEqual(prior,98)
        rows=source_supportstart_initial_modal_rows(birth)
        self.assertEqual(len(rows),7)
        self.assertEqual(len(rng.calls),prior) # No new draws for editor model
        self.assertEqual(
            tuple(row.original_staff_type for row in rows),
            INITIAL_SUPPORT_STAFF_TYPES+(None,)
        )
        self.assertEqual(
            tuple(row.original_first_name for row in rows),
            ("David",)*6+(None,)
        )
        self.assertEqual(
            tuple(row.original_surname for row in rows),
            ("Seaman",)*6+(None,)
        )
        self.assertEqual(
            tuple(row.source_has_staff for row in rows),
            (True,)*6+(False,)
        )
        self.assertEqual(
            tuple(row.native_anchor.origin for row in rows),
            tuple((391,181+40*i) for i in range(7))
        )
        self.assertEqual(
            tuple(row.native_anchor.selector_owner_offset for row in rows),
            tuple(0x2224+0x4c*i for i in range(7))
        )
        self.assertEqual(
            tuple(row.native_anchor.display_text_first_owner_offset for row in rows),
            tuple(0x70+0x80*i for i in range(7))
        )
        self.assertEqual(
            tuple(row.native_anchor.display_text_second_owner_offset for row in rows),
            tuple(0x4f0+0x80*i for i in range(7))
        )
        self.assertEqual(
            tuple(row.native_anchor.native_group_index for row in rows),
            tuple(range(8,15))
        )

    def test_no_arbitrary_reordering_or_partial_synthetic_staff_pool(self):
        birth=original_fixture_birth(SourceZeroRng())
        for staff in (birth.staff[::-1],birth.staff[:5],()):
            with self.subTest(staff=staff):
                with self.assertRaises(OriginalSupportStartInitialRowsError):
                    source_supportstart_initial_modal_rows(replace(birth,staff=staff))

    def test_requires_source_birth_receipt(self):
        with self.assertRaises(OriginalSupportStartInitialRowsError):
            source_supportstart_initial_modal_rows(None)


    def test_original_staging_moves_six_staff_in_reverse_slot_order(self):
        rng=SourceZeroRng()
        birth=original_fixture_birth(rng)
        rows=source_supportstart_initial_modal_rows(birth)
        original_rng_length=len(rng.calls)
        changes=source_supportstart_native_staging_transfers(rows)
        self.assertEqual(len(changes),6)
        self.assertEqual(
            [transfer.original_staff_type for transfer in changes],
            [13,5,4,3,2,1]
        )
        self.assertEqual([transfer.source_slot_index for transfer in changes],
                         [5,4,3,2,1,0])
        self.assertEqual([transfer.from_user_list_offset for transfer in changes],
                         [0x5d0]*6)
        self.assertEqual(
            [transfer.to_user_inactive_list_offset for transfer in changes],
            [0x5c4]+[0x5b8]*5
        )
        self.assertTrue(all(
            transfer.source_checks_global_staff_list_for_removal
            for transfer in changes
        ))
        self.assertEqual(len(rng.calls),original_rng_length)

    def test_staging_plan_refuses_made_up_slot_movement(self):
        rows=source_supportstart_initial_modal_rows(
            original_fixture_birth(SourceZeroRng()))
        for bad in (rows[:6],rows[::-1],(None,)+rows[1:]):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalSupportStartInitialRowsError):
                    source_supportstart_native_staging_transfers(bad)


if __name__=="__main__":
    unittest.main()

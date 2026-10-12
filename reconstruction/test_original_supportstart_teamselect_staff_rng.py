"""Actual ordinary TeamSelect source-ordered staff CRT call receipts."""
import unittest
from fm2001_data import Player
from original_supportstart_name_group_source import OriginalNameGroupCandidateRoute
from original_supportstart_teamselect_staff_clubs import SourceTeamSelectStaffClubCandidates
from original_supportstart_teamselect_staff_rng import (
    OriginalTeamSelectStaffRngError,
    replay_original_teamselect_staff_crt_draws,
)


def player(i, first, surname):
    return Player(i, first, surname, 0, 1, None, 0, 0, 0, (0,0,0), (), ())


class RecordingRng:
    def __init__(self, values):
        self.values = list(values)
        self.bounds = []

    def randbelow(self, bound):
        self.bounds.append(bound)
        return self.values.pop(0)


class TeamSelectStaffRngReceiptTests(unittest.TestCase):
    def setUp(self):
        self.players = (player(0, "David", "Seaman"),
                        player(1, "Lee", "Dixon"),
                        player(2, "Nigel", "Winterburn"))
        self.route = OriginalNameGroupCandidateRoute(
            1, 1, 3, "global_players", (), 3
        )
        self.club_candidates = SourceTeamSelectStaffClubCandidates(
            original_group_id=5, matched_original_club_count=2,
            source_club_indices=(40, 41), truncated_original_club_count=0
        )

    def replay(self, rng, *, players=None, name_route=None,
               group=5, candidates=None, selection_context=1, staff_type=13):
        return replay_original_teamselect_staff_crt_draws(
            rng, self.players if players is None else players,
            self.route if name_route is None else name_route,
            self.club_candidates if candidates is None else candidates,
            source_group_id=group, selection_context=selection_context,
            staff_type=staff_type
        )

    def test_one_club_assignment_full_ordinary_source_order(self):
        rng = RecordingRng([4, 0, 1, 1, 0, 11, 14, 0, 1, 2, 1, 8])
        receipt = self.replay(rng)
        self.assertEqual(receipt.age_like, 29)
        self.assertEqual(receipt.constructor_base_scalar, 2)
        self.assertEqual(receipt.constructor_name.full_name, "David Dixon")
        self.assertEqual(receipt.final_name.full_name, "Lee Seaman")
        self.assertEqual((receipt.first_twenty_draw, receipt.thirty_draw,
                          receipt.second_twenty_draw), (11,14,8))
        self.assertEqual(len(receipt.club_assignments), 1)
        assignment = receipt.club_assignments[0]
        self.assertEqual(
            (assignment.original_club_id, assignment.original_club_pointer_slot,
             assignment.first_three_way_value, assignment.second_three_way_value),
            (41,1,2,1)
        )
        self.assertEqual(rng.bounds, [25,3,3,3,3,20,30,3,2,3,3,20])
        self.assertEqual(receipt.direct_source_rng_call_count, 12)
        self.assertEqual(rng.values, [])

    def test_three_associations_and_full_pair_retry(self):
        retry_players = (player(0, "-", "Seaman"), self.players[1], self.players[2])
        # 1 RNG25 + (2 retries for name one, 1 attempt for name two)
        # + RNG20, RNG30, RNG3 count=3, 3 draws per each of 3, RNG20.
        values = [0, 0,1, 1,2, 2,1, 1, 1, 2,
                  0,0,0, 1,1,1, 0,2,2, 3]
        rng = RecordingRng(values)
        result = self.replay(rng, players=retry_players, staff_type=1)
        self.assertEqual(result.first_name_attempts, 2)
        self.assertEqual(result.second_name_attempts, 1)
        self.assertEqual(result.constructor_name.full_name, "Lee Winterburn")
        self.assertEqual(result.final_name.full_name, "Nigel Dixon")
        self.assertEqual(len(result.club_assignments), 3)
        self.assertEqual(result.direct_source_rng_call_count, 20)
        self.assertEqual(
            rng.bounds,
            [25,3,3,3,3,3,3,20,30,3,2,3,3,2,3,3,2,3,3,20]
        )
        self.assertEqual(rng.values, [])

    def test_invalid_context_rejects_without_consuming_shared_rng(self):
        for options in (
            {"group": 8},
            {"staff_type": 9},
            {"selection_context": True},
            {"candidates": SourceTeamSelectStaffClubCandidates(5,0,(),0)},
            {"players": (player(1,"Lee","Dixon"),)},
        ):
            rng = RecordingRng([0])
            with self.subTest(options=options):
                with self.assertRaises(OriginalTeamSelectStaffRngError):
                    self.replay(rng, **options)
                self.assertEqual(rng.bounds, [])

    def test_runtime_rng_invalid_choice_never_mapped_to_another_club(self):
        rng = RecordingRng([25])
        with self.assertRaises(OriginalTeamSelectStaffRngError):
            self.replay(rng)
        self.assertEqual(rng.bounds, [25])


if __name__ == "__main__":
    unittest.main()

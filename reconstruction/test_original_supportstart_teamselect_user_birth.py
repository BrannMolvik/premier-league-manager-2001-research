"""Ordinary TeamSelect first-user creation: no new seed or guessed name stream."""
import unittest

from fm2001_data import Club, CompetitionDefinition, Player
from original_supportstart_name_group_source import OriginalNameGroupCandidateRoute
from original_supportstart_teamselect_user_birth import (
    OriginalTeamSelectUserBirthError,
    replay_original_teamselect_user_birth_direct_rng,
)
from support_staff import INITIAL_SUPPORT_STAFF_TYPES


def club(i, league, country):
    return Club(i, f"Club {i}", f"C{i}", "Ground", 0,
                competition_id=league, country_id=country)


def league(i, country):
    return CompetitionDefinition(
        id=i, name=f"Source league {i}", substitute_quota=3,
        max_non_eu_players=0, runtime_kind_code=1,
        parent_competition_id=None, country_region_id=country,
    )


def player(i, first, surname):
    return Player(i, first, surname, 0, 1, None, 0, 0, 0,
                  (0, 0, 0), (), ())


class SharedTraceRng:
    def __init__(self):
        self.bounds = []

    def randbelow(self, bound):
        self.bounds.append(bound)
        return 0


class OriginalTeamSelectUserBirthTests(unittest.TestCase):
    def setUp(self):
        self.clubs = (club(0, 5, 7), club(1, 5, 7), club(2, 6, 8))
        self.players = (player(0, "David", "Seaman"),
                        player(1, "Lee", "Dixon"),
                        player(2, "Nigel", "Winterburn"))
        self.route = OriginalNameGroupCandidateRoute(
            7, 7, 3, "global_players", (), 3
        )

    def birth(self, rng, **override):
        args = dict(
            original_clubs=self.clubs,
            original_players=self.players,
            original_root_league=league(5, 7),
            selected_club_id=1,
            name_route=self.route,
            selection_context=1,
            require_shipped_club_count=False,
        )
        args.update(override)
        return replay_original_teamselect_user_birth_direct_rng(rng, **args)

    def test_13_user_pairs_then_six_ordinary_staff_on_one_rng(self):
        rng = SharedTraceRng()
        receipt = self.birth(rng)
        self.assertEqual(receipt.selected_club_id, 1)
        self.assertEqual(receipt.selected_root_league_id, 5)
        self.assertEqual(receipt.birth_names.direct_source_rng_call_count, 26)
        self.assertEqual(len(receipt.birth_names.source_pairs), 13)
        self.assertEqual(
            tuple(item.staff_type for item in receipt.staff),
            INITIAL_SUPPORT_STAFF_TYPES
        )
        self.assertEqual(
            tuple(item.direct_source_rng_call_count for item in receipt.staff),
            (12, 12, 12, 12, 12, 12),
        )
        self.assertEqual(receipt.direct_source_rng_call_count, 98)
        self.assertEqual(len(rng.bounds), 98)
        self.assertEqual(rng.bounds[:26], [3]*26)
        single_staff_bounds = [25,3,3,3,3,20,30,3,2,3,3,20]
        self.assertEqual(rng.bounds[26:], single_staff_bounds*6)
        self.assertEqual(
            [x.constructor_base_scalar for x in receipt.staff],
            [2]*6
        )
        self.assertEqual(
            [x.final_name.full_name for x in receipt.staff],
            ["David Seaman"]*6
        )
        self.assertEqual(
            [x.club_assignments[0].original_club_id for x in receipt.staff],
            [0]*6
        )

    def test_2_consecutive_users_share_rng_and_use_their_actual_leagues(self):
        rng = SharedTraceRng()
        first = self.birth(rng)
        second = self.birth(
            rng, selected_club_id=2,
            original_root_league=league(6, 8),
            name_route=OriginalNameGroupCandidateRoute(
                8, 8, 3, "global_players", (), 3
            ),
            selection_context=2,
        )
        self.assertEqual(first.direct_source_rng_call_count, 98)
        self.assertEqual(second.direct_source_rng_call_count, 98)
        self.assertEqual(len(rng.bounds), 196)
        self.assertEqual(rng.bounds[26+8], 2)  # First user's club count
        self.assertEqual(rng.bounds[98+26+8], 1)  # Second user's club count
        self.assertEqual(
            tuple(x.club_assignments[0].original_club_id for x in second.staff),
            (2,)*6
        )
        self.assertEqual(second.staff[0].constructor_base_scalar, 2)

    def test_invalid_native_context_never_consumes_existing_crt(self):
        bad = (
            {"original_root_league": league(6, 8)},
            {"selected_club_id": 4},
            {"selected_club_id": True},
            {"name_route": OriginalNameGroupCandidateRoute(
                8,8,3,"global_players",(),3)},
            {"selection_context": True},
            {"original_root_league": CompetitionDefinition(
                id=5,name="Cup",substitute_quota=3,max_non_eu_players=0,
                runtime_kind_code=2,parent_competition_id=None)},
            {"original_clubs": (club(0, 5, 7),)},
            {"original_players": (player(1,"Lee","Dixon"),)},
            {"original_players": (player(0,"-","Seaman"),)},
        )
        for options in bad:
            with self.subTest(options=options):
                rng = SharedTraceRng()
                with self.assertRaises(OriginalTeamSelectUserBirthError):
                    self.birth(rng, **options)
                self.assertEqual(rng.bounds, [])

    def test_changing_selection_does_not_silently_reseed_or_rollback(self):
        rng = SharedTraceRng()
        first = self.birth(rng)
        self.assertEqual(len(rng.bounds), first.direct_source_rng_call_count)
        second = self.birth(rng)
        self.assertEqual(len(rng.bounds),
                         first.direct_source_rng_call_count +
                         second.direct_source_rng_call_count)


if __name__ == "__main__":
    unittest.main()

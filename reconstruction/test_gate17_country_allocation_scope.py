"""Tests for Gate-17 playable-country LeagueAllocation planning."""
from dataclasses import dataclass
import unittest

from gate17_country_allocation_scope import (
    Gate17CountryAllocationScopeError,
    derive_playable_country_allocation_plan,
)
from gate17_full_scope_catalog import (
    OriginalPlayableScope,
    PlayableCountryScope,
    PlayableLeagueScope,
)


@dataclass(frozen=True)
class Competition:
    id: int
    country_region_id: int


@dataclass(frozen=True)
class Allocation:
    id: int
    competition_a_id: int
    competition_b_id: int


def scope_fixture():
    return OriginalPlayableScope(
        countries=(
            PlayableCountryScope(
                country_id=26,
                name="England",
                source_root_league_count=2,
                visible_league_capacity=15,
                leagues=(
                    PlayableLeagueScope(
                        competition_id=0,
                        name="Premier",
                        source_club_count=2,
                        selectable_club_ids=(1, 2),
                        selectable_club_names=("A", "B"),
                    ),
                    PlayableLeagueScope(
                        competition_id=2,
                        name="Division",
                        source_club_count=2,
                        selectable_club_ids=(3, 4),
                        selectable_club_names=("C", "D"),
                    ),
                ),
            ),
            PlayableCountryScope(
                country_id=66,
                name="Scotland",
                source_root_league_count=1,
                visible_league_capacity=14,
                leagues=(
                    PlayableLeagueScope(
                        competition_id=27,
                        name="Scottish League",
                        source_club_count=2,
                        selectable_club_ids=(5, 6),
                        selectable_club_names=("E", "F"),
                    ),
                ),
            ),
        )
    )


class Gate17CountryAllocationScopeTests(unittest.TestCase):
    def test_groups_rows_by_source_country_and_preserves_input_order(self):
        scope = scope_fixture()
        competitions = (
            Competition(0, 26),
            Competition(2, 26),
            Competition(11, 26),
            Competition(27, 66),
            Competition(28, 66),
            Competition(500, 123),
            Competition(501, 123),
        )
        rows = (
            Allocation(7, 27, 28),
            Allocation(0, 0, 2),
            Allocation(1, 0, 11),
            Allocation(99, 500, 501),
        )

        plan = derive_playable_country_allocation_plan(
            scope,
            rows,
            competitions,
        )

        self.assertEqual(plan.catalog_sha256, scope.catalog_sha256)
        self.assertEqual(plan.assigned_allocation_ids, (0, 1, 7))
        self.assertEqual(plan.ignored_allocation_ids, (99,))
        self.assertEqual(
            tuple(country.country_id for country in plan.countries),
            (26, 66),
        )
        england, scotland = plan.countries
        self.assertEqual(england.selectable_league_ids, (0, 2))
        self.assertEqual(england.allocation_ids, (0, 1))
        self.assertEqual(england.ranking_endpoint_ids, (0, 2, 11))
        self.assertTrue(england.has_transition_rows)
        self.assertEqual(scotland.allocation_ids, (7,))
        self.assertEqual(scotland.ranking_endpoint_ids, (27, 28))
        self.assertTrue(scotland.has_transition_rows)

        payload = plan.as_dict()
        self.assertEqual(payload["country_count"], 2)
        self.assertEqual(payload["assigned_allocation_ids"], [0, 1, 7])
        self.assertEqual(payload["ignored_allocation_ids"], [99])

    def test_country_without_allocation_rows_remains_explicit(self):
        plan = derive_playable_country_allocation_plan(
            scope_fixture(),
            (Allocation(0, 0, 2),),
            (
                Competition(0, 26),
                Competition(2, 26),
                Competition(27, 66),
            ),
        )
        self.assertEqual(plan.countries[1].allocation_ids, ())
        self.assertEqual(plan.countries[1].ranking_endpoint_ids, ())
        self.assertFalse(plan.countries[1].has_transition_rows)

    def test_cross_playable_country_allocation_fails_closed(self):
        with self.assertRaisesRegex(
            Gate17CountryAllocationScopeError,
            "crosses playable-country boundary",
        ):
            derive_playable_country_allocation_plan(
                scope_fixture(),
                (Allocation(0, 0, 27),),
                (
                    Competition(0, 26),
                    Competition(2, 26),
                    Competition(27, 66),
                ),
            )

    def test_missing_competition_and_duplicate_ids_fail_closed(self):
        scope = scope_fixture()
        with self.assertRaisesRegex(
            Gate17CountryAllocationScopeError,
            "missing competitions",
        ):
            derive_playable_country_allocation_plan(
                scope,
                (Allocation(0, 0, 999),),
                (
                    Competition(0, 26),
                    Competition(2, 26),
                    Competition(27, 66),
                ),
            )

        with self.assertRaisesRegex(
            Gate17CountryAllocationScopeError,
            "record IDs must be unique",
        ):
            derive_playable_country_allocation_plan(
                scope,
                (Allocation(0, 0, 2), Allocation(0, 27, 27)),
                (
                    Competition(0, 26),
                    Competition(2, 26),
                    Competition(27, 66),
                ),
            )

        with self.assertRaisesRegex(
            Gate17CountryAllocationScopeError,
            "duplicate competition ID",
        ):
            derive_playable_country_allocation_plan(
                scope,
                (),
                (
                    Competition(0, 26),
                    Competition(0, 26),
                    Competition(2, 26),
                    Competition(27, 66),
                ),
            )


if __name__ == "__main__":
    unittest.main()

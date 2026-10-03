"""Tests for Gate-17 TeamSelect League runtime-ownership planning."""
from dataclasses import dataclass
import unittest

from gate17_full_scope_catalog import (
    OriginalPlayableScope,
    PlayableCountryScope,
    PlayableLeagueScope,
)
from gate17_playable_league_runtime_plan import (
    Gate17PlayableLeagueRuntimePlanError,
    RUNTIME_FIXED_PRIMARY,
    RUNTIME_PROCEDURAL_PRIMARY,
    RUNTIME_PROCEDURAL_SECONDARY,
    derive_playable_league_runtime_plan,
)


@dataclass(frozen=True)
class Competition:
    id: int
    country_region_id: int
    runtime_kind_code: int = 1
    schedule_container_code: int = 0
    parent_competition_id: int | None = None


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
                        name="Scottish",
                        source_club_count=2,
                        selectable_club_ids=(5, 6),
                        selectable_club_names=("E", "F"),
                    ),
                ),
            ),
        )
    )


class Gate17PlayableLeagueRuntimePlanTests(unittest.TestCase):
    def test_classifies_fixed_primary_and_primary_secondary_procedural(self):
        scope = scope_fixture()
        plan = derive_playable_league_runtime_plan(
            scope,
            (
                Competition(0, 26, schedule_container_code=0),
                Competition(2, 26, schedule_container_code=1),
                Competition(27, 66, schedule_container_code=2),
            ),
        )

        self.assertEqual(plan.catalog_sha256, scope.catalog_sha256)
        self.assertEqual(
            tuple(entry.runtime_owner for entry in plan.entries),
            (
                RUNTIME_FIXED_PRIMARY,
                RUNTIME_PROCEDURAL_PRIMARY,
                RUNTIME_PROCEDURAL_SECONDARY,
            ),
        )
        self.assertEqual(plan.primary_scope_ids, ("26:0", "26:2"))
        self.assertEqual(plan.secondary_scope_ids, ("66:27",))
        self.assertEqual(plan.fixed_primary_scope_ids, ("26:0",))
        self.assertEqual(plan.procedural_primary_scope_ids, ("26:2",))
        self.assertEqual(plan.procedural_primary_competition_ids, (2,))
        self.assertEqual(plan.procedural_secondary_scope_ids, ("66:27",))
        self.assertTrue(plan.entries[0].uses_primary_container)
        self.assertTrue(plan.entries[2].uses_secondary_container)

        payload = plan.as_dict()
        self.assertEqual(payload["scope_entry_count"], 3)
        self.assertEqual(payload["primary_scope_ids"], ["26:0", "26:2"])
        self.assertEqual(payload["procedural_primary_competition_ids"], [2])
        self.assertEqual(payload["secondary_scope_ids"], ["66:27"])

    def test_fixed_ids_must_be_playable_primary_leagues(self):
        with self.assertRaisesRegex(
            Gate17PlayableLeagueRuntimePlanError,
            "not TeamSelect-playable",
        ):
            derive_playable_league_runtime_plan(
                scope_fixture(),
                (
                    Competition(0, 26),
                    Competition(2, 26),
                    Competition(27, 66),
                ),
                fixed_fixture_competition_ids=(999,),
            )

        with self.assertRaisesRegex(
            Gate17PlayableLeagueRuntimePlanError,
            "belongs to secondary",
        ):
            derive_playable_league_runtime_plan(
                scope_fixture(),
                (
                    Competition(0, 26, schedule_container_code=2),
                    Competition(2, 26),
                    Competition(27, 66),
                ),
            )

    def test_source_identity_drift_fails_closed(self):
        cases = (
            (
                (
                    Competition(0, 26),
                    Competition(2, 26),
                ),
                "no competition record",
            ),
            (
                (
                    Competition(0, 26),
                    Competition(2, 26),
                    Competition(27, 26),
                ),
                "country identity drifted",
            ),
            (
                (
                    Competition(0, 26),
                    Competition(2, 26),
                    Competition(27, 66, runtime_kind_code=2),
                ),
                "runtime kind 1",
            ),
            (
                (
                    Competition(0, 26),
                    Competition(2, 26),
                    Competition(27, 66, parent_competition_id=100),
                ),
                "not a root competition",
            ),
        )
        for competitions, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    Gate17PlayableLeagueRuntimePlanError,
                    message,
                ):
                    derive_playable_league_runtime_plan(
                        scope_fixture(),
                        competitions,
                    )

    def test_duplicate_and_non_integer_fixed_ids_fail_closed(self):
        competitions = (
            Competition(0, 26),
            Competition(2, 26),
            Competition(27, 66),
        )
        for fixed in ((0, 0), (0, True), (0, "2"), (0, -1)):
            with self.subTest(fixed=fixed):
                with self.assertRaises(Gate17PlayableLeagueRuntimePlanError):
                    derive_playable_league_runtime_plan(
                        scope_fixture(),
                        competitions,
                        fixed_fixture_competition_ids=fixed,
                    )

        with self.assertRaisesRegex(
            Gate17PlayableLeagueRuntimePlanError,
            "duplicate competition ID",
        ):
            derive_playable_league_runtime_plan(
                scope_fixture(),
                competitions + (Competition(27, 66),),
            )


if __name__ == "__main__":
    unittest.main()

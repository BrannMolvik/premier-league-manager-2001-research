"""Tests for Gate-17 runtime-owner capability auditing."""
from unittest import TestCase

from gate17_playable_league_runtime_plan import (
    PlayableLeagueRuntimeEntry,
    PlayableLeagueRuntimePlan,
    RUNTIME_FIXED_PRIMARY,
    RUNTIME_PROCEDURAL_PRIMARY,
    RUNTIME_PROCEDURAL_SECONDARY,
)
from gate17_runtime_owner_capability import (
    Gate17RuntimeOwnerCapabilityError,
    audit_runtime_owner_capability,
    normalized_surface,
)


def plan_fixture():
    return PlayableLeagueRuntimePlan(
        catalog_sha256="a" * 64,
        entries=(
            PlayableLeagueRuntimeEntry(
                scope_id="26:0",
                country_id=26,
                country_name="England",
                competition_id=0,
                competition_name="Premier",
                runtime_kind_code=1,
                schedule_container_code=0,
                runtime_owner=RUNTIME_FIXED_PRIMARY,
                source_club_count=2,
                selectable_club_ids=(1, 2),
            ),
            PlayableLeagueRuntimeEntry(
                scope_id="26:2",
                country_id=26,
                country_name="England",
                competition_id=2,
                competition_name="Division",
                runtime_kind_code=1,
                schedule_container_code=1,
                runtime_owner=RUNTIME_PROCEDURAL_PRIMARY,
                source_club_count=2,
                selectable_club_ids=(3, 4),
            ),
            PlayableLeagueRuntimeEntry(
                scope_id="66:27",
                country_id=66,
                country_name="Scotland",
                competition_id=27,
                competition_name="Scottish",
                runtime_kind_code=1,
                schedule_container_code=2,
                runtime_owner=RUNTIME_PROCEDURAL_SECONDARY,
                source_club_count=2,
                selectable_club_ids=(5, 6),
            ),
        ),
    )


class Gate17RuntimeOwnerCapabilityTests(TestCase):
    def test_current_style_surface_exposes_exact_blockers(self):
        surface = normalized_surface(
            selectable_club_ids=(1, 2),
            fixed_primary_competition_ids=(0,),
            materialized_primary_procedural_ids=(2,),
            materialized_secondary_procedural_ids=(),
            human_primary_procedural_ids=(),
            human_secondary_procedural_ids=(),
            fresh_financial_objective_competition_ids=(0,),
            sporting_objective_progression_competition_ids=(0,),
            annual_progression_country_ids=(26,),
        )
        audit = audit_runtime_owner_capability(plan_fixture(), surface)

        self.assertFalse(audit.complete)
        self.assertEqual(audit.supported_scope_ids, ("26:0",))
        self.assertEqual(audit.blocked_scope_ids, ("26:2", "66:27"))
        fixed, primary, secondary = audit.entries
        self.assertTrue(fixed.complete)
        self.assertEqual(
            primary.blocker_codes,
            (
                "human_selection_unavailable",
                "human_match_dispatch_missing",
                "fresh_financial_objective_missing",
                "sporting_objective_progression_missing",
            ),
        )
        self.assertEqual(
            secondary.blocker_codes,
            (
                "human_selection_unavailable",
                "runtime_owner_not_materialized",
                "human_match_dispatch_missing",
                "fresh_financial_objective_missing",
                "sporting_objective_progression_missing",
                "annual_progression_country_missing",
            ),
        )
        self.assertEqual(
            audit.blocker_codes,
            (
                "human_selection_unavailable",
                "human_match_dispatch_missing",
                "fresh_financial_objective_missing",
                "sporting_objective_progression_missing",
                "runtime_owner_not_materialized",
                "annual_progression_country_missing",
            ),
        )

    def test_complete_surface_requires_every_owner_and_country(self):
        surface = normalized_surface(
            selectable_club_ids=(1, 2, 3, 4, 5, 6),
            fixed_primary_competition_ids=(0,),
            materialized_primary_procedural_ids=(2,),
            materialized_secondary_procedural_ids=(27,),
            human_primary_procedural_ids=(2,),
            human_secondary_procedural_ids=(27,),
            fresh_financial_objective_competition_ids=(0, 2, 27),
            sporting_objective_progression_competition_ids=(0, 2, 27),
            annual_progression_country_ids=(26, 66),
        )
        audit = audit_runtime_owner_capability(plan_fixture(), surface)
        self.assertTrue(audit.complete)
        self.assertEqual(audit.blocked_scope_ids, ())
        self.assertEqual(
            audit.supported_scope_ids,
            ("26:0", "26:2", "66:27"),
        )
        payload = audit.as_dict()
        self.assertTrue(payload["complete"])
        self.assertEqual(payload["schema_version"], 3)

    def test_missing_non_pl_fresh_objective_blocks_scope_fail_closed(self):
        surface = normalized_surface(
            selectable_club_ids=(1, 2, 3, 4),
            fixed_primary_competition_ids=(0,),
            materialized_primary_procedural_ids=(2,),
            materialized_secondary_procedural_ids=(),
            human_primary_procedural_ids=(2,),
            human_secondary_procedural_ids=(),
            fresh_financial_objective_competition_ids=(0,),
            sporting_objective_progression_competition_ids=(0, 2),
            annual_progression_country_ids=(26,),
        )
        audit = audit_runtime_owner_capability(plan_fixture(), surface)

        self.assertTrue(audit.entries[1].selection_supported)
        self.assertTrue(audit.entries[1].runtime_materialized)
        self.assertTrue(audit.entries[1].human_match_supported)
        self.assertFalse(
            audit.entries[1].fresh_financial_objective_supported
        )
        self.assertEqual(
            audit.entries[1].blocker_codes,
            ("fresh_financial_objective_missing",),
        )

    def test_missing_sporting_objective_progression_blocks_scope_separately(self):
        surface = normalized_surface(
            selectable_club_ids=(1, 2, 3, 4),
            fixed_primary_competition_ids=(0,),
            materialized_primary_procedural_ids=(2,),
            materialized_secondary_procedural_ids=(),
            human_primary_procedural_ids=(2,),
            human_secondary_procedural_ids=(),
            fresh_financial_objective_competition_ids=(0, 2),
            sporting_objective_progression_competition_ids=(0,),
            annual_progression_country_ids=(26,),
        )
        audit = audit_runtime_owner_capability(plan_fixture(), surface)

        primary = audit.entries[1]
        self.assertTrue(primary.fresh_financial_objective_supported)
        self.assertFalse(primary.sporting_objective_progression_supported)
        self.assertEqual(
            primary.blocker_codes,
            ("sporting_objective_progression_missing",),
        )

    def test_selection_requires_every_catalog_club_in_scope(self):
        surface = normalized_surface(
            selectable_club_ids=(1, 2, 3),
            fixed_primary_competition_ids=(0,),
            materialized_primary_procedural_ids=(2,),
            materialized_secondary_procedural_ids=(27,),
            human_primary_procedural_ids=(2,),
            human_secondary_procedural_ids=(27,),
            fresh_financial_objective_competition_ids=(0, 2, 27),
            sporting_objective_progression_competition_ids=(0, 2, 27),
            annual_progression_country_ids=(26, 66),
        )
        audit = audit_runtime_owner_capability(plan_fixture(), surface)
        self.assertFalse(audit.entries[1].selection_supported)
        self.assertIn(
            "human_selection_unavailable",
            audit.entries[1].blocker_codes,
        )

    def test_surface_ids_are_exact_unique_nonnegative_ints(self):
        kwargs = dict(
            selectable_club_ids=(1, 2),
            fixed_primary_competition_ids=(0,),
            materialized_primary_procedural_ids=(2,),
            materialized_secondary_procedural_ids=(),
            human_primary_procedural_ids=(),
            human_secondary_procedural_ids=(),
            fresh_financial_objective_competition_ids=(0,),
            sporting_objective_progression_competition_ids=(0,),
            annual_progression_country_ids=(26,),
        )
        for field, bad in (
            ("selectable_club_ids", (1, True)),
            ("fixed_primary_competition_ids", (0, 0)),
            ("materialized_primary_procedural_ids", (-1,)),
            ("fresh_financial_objective_competition_ids", (0, True)),
            ("sporting_objective_progression_competition_ids", (0, True)),
            ("annual_progression_country_ids", ("26",)),
        ):
            changed = dict(kwargs)
            changed[field] = bad
            with self.subTest(field=field, bad=bad):
                with self.assertRaises(Gate17RuntimeOwnerCapabilityError):
                    normalized_surface(**changed)

    def test_wrong_input_types_and_unknown_owner_fail_closed(self):
        surface = normalized_surface(
            selectable_club_ids=(1, 2),
            fixed_primary_competition_ids=(0,),
            materialized_primary_procedural_ids=(),
            materialized_secondary_procedural_ids=(),
            human_primary_procedural_ids=(),
            human_secondary_procedural_ids=(),
            fresh_financial_objective_competition_ids=(0,),
            sporting_objective_progression_competition_ids=(0,),
            annual_progression_country_ids=(26,),
        )
        with self.assertRaisesRegex(
            Gate17RuntimeOwnerCapabilityError,
            "exact PlayableLeagueRuntimePlan",
        ):
            audit_runtime_owner_capability(object(), surface)
        with self.assertRaisesRegex(
            Gate17RuntimeOwnerCapabilityError,
            "exact HumanRuntimeOwnerSurface",
        ):
            audit_runtime_owner_capability(plan_fixture(), object())

        plan = plan_fixture()
        bad_entry = PlayableLeagueRuntimeEntry(
            **{**plan.entries[0].__dict__, "runtime_owner": "mystery"}
        )
        bad_plan = PlayableLeagueRuntimePlan(
            catalog_sha256=plan.catalog_sha256,
            entries=(bad_entry,),
        )
        with self.assertRaisesRegex(
            Gate17RuntimeOwnerCapabilityError,
            "unknown runtime owner",
        ):
            audit_runtime_owner_capability(bad_plan, surface)

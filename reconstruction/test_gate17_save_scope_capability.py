"""Tests for Gate-17 per-scope save/reload capability."""
import unittest

from gate17_playable_league_runtime_plan import (
    PlayableLeagueRuntimeEntry,
    PlayableLeagueRuntimePlan,
    RUNTIME_FIXED_PRIMARY,
    RUNTIME_PROCEDURAL_PRIMARY,
    RUNTIME_PROCEDURAL_SECONDARY,
)
from gate17_save_scope_capability import (
    Gate17SaveScopeCapabilityError,
    audit_save_scope_capability,
    normalized_surface,
)


CATALOG = "a" * 64


def entry(scope_id, country_id, competition_id, owner):
    return PlayableLeagueRuntimeEntry(
        scope_id=scope_id,
        country_id=country_id,
        country_name=f"Country {country_id}",
        competition_id=competition_id,
        competition_name=f"Competition {competition_id}",
        runtime_kind_code=1,
        schedule_container_code=2 if owner == RUNTIME_PROCEDURAL_SECONDARY else 0,
        runtime_owner=owner,
        source_club_count=2,
        selectable_club_ids=(competition_id * 10 + 1, competition_id * 10 + 2),
    )


def plan_fixture():
    return PlayableLeagueRuntimePlan(
        catalog_sha256=CATALOG,
        entries=(
            entry("26:0", 26, 0, RUNTIME_FIXED_PRIMARY),
            entry("26:2", 26, 2, RUNTIME_PROCEDURAL_PRIMARY),
            entry("66:27", 66, 27, RUNTIME_PROCEDURAL_SECONDARY),
        ),
    )


class Gate17SaveScopeCapabilityTests(unittest.TestCase):
    def test_primary_capability_keeps_secondary_explicitly_blocked(self):
        plan = plan_fixture()
        audit = audit_save_scope_capability(
            plan,
            normalized_surface(
                fixed_primary_scope_ids=("26:0",),
                procedural_primary_scope_ids=("26:2",),
                procedural_secondary_scope_ids=(),
            ),
        )

        self.assertFalse(audit.complete)
        self.assertEqual(audit.supported_scope_ids, ("26:0", "26:2"))
        self.assertEqual(audit.blocked_scope_ids, ("66:27",))
        self.assertEqual(audit.blocker_codes, ("save_reload_capability_missing",))
        self.assertEqual(
            tuple(row.save_reload_capable for row in audit.entries),
            (True, True, False),
        )
        self.assertEqual(audit.as_dict()["schema_version"], 1)

    def test_all_owner_surfaces_can_become_complete_without_owner_aliasing(self):
        plan = plan_fixture()
        audit = audit_save_scope_capability(
            plan,
            normalized_surface(
                fixed_primary_scope_ids=("26:0",),
                procedural_primary_scope_ids=("26:2",),
                procedural_secondary_scope_ids=("66:27",),
            ),
        )

        self.assertTrue(audit.complete)
        self.assertEqual(
            audit.supported_scope_ids,
            ("26:0", "26:2", "66:27"),
        )
        self.assertEqual(audit.blocked_scope_ids, ())

    def test_wrong_owner_bucket_does_not_count_as_save_capability(self):
        plan = plan_fixture()
        audit = audit_save_scope_capability(
            plan,
            normalized_surface(
                fixed_primary_scope_ids=("26:0",),
                procedural_primary_scope_ids=("26:2", "66:27"),
                procedural_secondary_scope_ids=(),
            ),
        )
        self.assertFalse(audit.entries[2].save_reload_capable)
        self.assertEqual(audit.blocked_scope_ids, ("66:27",))

    def test_unknown_overlapping_and_duplicate_scope_ids_fail_closed(self):
        plan = plan_fixture()
        with self.assertRaisesRegex(
            Gate17SaveScopeCapabilityError,
            "outside TeamSelect catalog",
        ):
            audit_save_scope_capability(
                plan,
                normalized_surface(
                    fixed_primary_scope_ids=("26:0",),
                    procedural_primary_scope_ids=("26:2",),
                    procedural_secondary_scope_ids=("99:99",),
                ),
            )

        with self.assertRaisesRegex(
            Gate17SaveScopeCapabilityError,
            "overlap across runtime owners",
        ):
            normalized_surface(
                fixed_primary_scope_ids=("26:0",),
                procedural_primary_scope_ids=("26:0",),
                procedural_secondary_scope_ids=(),
            )

        with self.assertRaisesRegex(
            Gate17SaveScopeCapabilityError,
            "duplicate scope ID",
        ):
            normalized_surface(
                fixed_primary_scope_ids=("26:0", "26:0"),
                procedural_primary_scope_ids=(),
                procedural_secondary_scope_ids=(),
            )

    def test_bad_types_and_empty_plan_fail_closed(self):
        with self.assertRaisesRegex(
            Gate17SaveScopeCapabilityError,
            "exact strings",
        ):
            normalized_surface(
                fixed_primary_scope_ids=(26,),
                procedural_primary_scope_ids=(),
                procedural_secondary_scope_ids=(),
            )

        with self.assertRaisesRegex(
            Gate17SaveScopeCapabilityError,
            "runtime ownership plan is empty",
        ):
            audit_save_scope_capability(
                PlayableLeagueRuntimePlan(catalog_sha256=CATALOG, entries=()),
                normalized_surface(
                    fixed_primary_scope_ids=(),
                    procedural_primary_scope_ids=(),
                    procedural_secondary_scope_ids=(),
                ),
            )


if __name__ == "__main__":
    unittest.main()

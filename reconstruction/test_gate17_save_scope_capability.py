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


def surface(
    *,
    fixed_serialized=("26:0",),
    fixed_continuation=("26:0",),
    primary_serialized=("26:2",),
    primary_continuation=("26:2",),
    secondary_serialized=(),
    secondary_continuation=(),
):
    return normalized_surface(
        fixed_primary_serialized_scope_ids=fixed_serialized,
        fixed_primary_continuation_scope_ids=fixed_continuation,
        procedural_primary_serialized_scope_ids=primary_serialized,
        procedural_primary_continuation_scope_ids=primary_continuation,
        procedural_secondary_serialized_scope_ids=secondary_serialized,
        procedural_secondary_continuation_scope_ids=secondary_continuation,
    )


class Gate17SaveScopeCapabilityTests(unittest.TestCase):
    def test_primary_capability_keeps_secondary_explicitly_blocked(self):
        audit = audit_save_scope_capability(plan_fixture(), surface())

        self.assertFalse(audit.complete)
        self.assertEqual(audit.supported_scope_ids, ("26:0", "26:2"))
        self.assertEqual(audit.blocked_scope_ids, ("66:27",))
        self.assertEqual(
            audit.blocker_codes,
            ("save_serialization_missing", "save_reload_continuation_missing"),
        )
        self.assertEqual(
            tuple(row.serialization_supported for row in audit.entries),
            (True, True, False),
        )
        self.assertEqual(
            tuple(row.continuation_supported for row in audit.entries),
            (True, True, False),
        )
        self.assertEqual(audit.as_dict()["schema_version"], 1)

    def test_serialization_without_continuation_stays_blocked(self):
        audit = audit_save_scope_capability(
            plan_fixture(),
            surface(
                secondary_serialized=("66:27",),
                secondary_continuation=(),
            ),
        )

        self.assertFalse(audit.complete)
        self.assertTrue(audit.entries[2].serialization_supported)
        self.assertFalse(audit.entries[2].continuation_supported)
        self.assertEqual(
            audit.entries[2].blocker_codes,
            ("save_reload_continuation_missing",),
        )

    def test_continuation_without_serialization_stays_blocked(self):
        audit = audit_save_scope_capability(
            plan_fixture(),
            surface(
                secondary_serialized=(),
                secondary_continuation=("66:27",),
            ),
        )

        self.assertFalse(audit.complete)
        self.assertFalse(audit.entries[2].serialization_supported)
        self.assertTrue(audit.entries[2].continuation_supported)
        self.assertEqual(
            audit.entries[2].blocker_codes,
            ("save_serialization_missing",),
        )

    def test_all_owner_surfaces_can_become_complete_without_owner_aliasing(self):
        audit = audit_save_scope_capability(
            plan_fixture(),
            surface(
                secondary_serialized=("66:27",),
                secondary_continuation=("66:27",),
            ),
        )

        self.assertTrue(audit.complete)
        self.assertEqual(
            audit.supported_scope_ids,
            ("26:0", "26:2", "66:27"),
        )
        self.assertEqual(audit.blocked_scope_ids, ())

    def test_wrong_owner_bucket_does_not_count_as_save_capability(self):
        audit = audit_save_scope_capability(
            plan_fixture(),
            surface(
                primary_serialized=("26:2", "66:27"),
                primary_continuation=("26:2", "66:27"),
            ),
        )
        self.assertFalse(audit.entries[2].serialization_supported)
        self.assertFalse(audit.entries[2].continuation_supported)
        self.assertEqual(audit.blocked_scope_ids, ("66:27",))

    def test_unknown_overlapping_and_duplicate_scope_ids_fail_closed(self):
        with self.assertRaisesRegex(
            Gate17SaveScopeCapabilityError,
            "outside TeamSelect catalog",
        ):
            audit_save_scope_capability(
                plan_fixture(),
                surface(secondary_serialized=("99:99",)),
            )

        with self.assertRaisesRegex(
            Gate17SaveScopeCapabilityError,
            "overlap across runtime owners",
        ):
            surface(primary_serialized=("26:2", "26:0"))

        with self.assertRaisesRegex(
            Gate17SaveScopeCapabilityError,
            "duplicate scope ID",
        ):
            normalized_surface(
                fixed_primary_serialized_scope_ids=("26:0", "26:0"),
                fixed_primary_continuation_scope_ids=(),
                procedural_primary_serialized_scope_ids=(),
                procedural_primary_continuation_scope_ids=(),
                procedural_secondary_serialized_scope_ids=(),
                procedural_secondary_continuation_scope_ids=(),
            )

    def test_bad_types_and_empty_plan_fail_closed(self):
        with self.assertRaisesRegex(
            Gate17SaveScopeCapabilityError,
            "exact strings",
        ):
            normalized_surface(
                fixed_primary_serialized_scope_ids=(26,),
                fixed_primary_continuation_scope_ids=(),
                procedural_primary_serialized_scope_ids=(),
                procedural_primary_continuation_scope_ids=(),
                procedural_secondary_serialized_scope_ids=(),
                procedural_secondary_continuation_scope_ids=(),
            )

        with self.assertRaisesRegex(
            Gate17SaveScopeCapabilityError,
            "runtime ownership plan is empty",
        ):
            audit_save_scope_capability(
                PlayableLeagueRuntimePlan(catalog_sha256=CATALOG, entries=()),
                surface(
                    fixed_serialized=(),
                    fixed_continuation=(),
                    primary_serialized=(),
                    primary_continuation=(),
                ),
            )


if __name__ == "__main__":
    unittest.main()

"""Tests for the fail-closed Gate-17 human scope capability audit."""
import unittest

from gate17_full_scope_catalog import (
    OriginalPlayableScope,
    PlayableCountryScope,
    PlayableLeagueScope,
)
from gate17_human_scope_capability import (
    Gate17HumanScopeCapabilityError,
    audit_human_selection_scope,
)


def scope_fixture():
    return OriginalPlayableScope(
        countries=(
            PlayableCountryScope(
                country_id=26,
                name="England",
                source_root_league_count=1,
                visible_league_capacity=15,
                leagues=(
                    PlayableLeagueScope(
                        competition_id=100,
                        name="England League",
                        source_club_count=2,
                        selectable_club_ids=(1, 2),
                        selectable_club_names=("Alpha", "Beta"),
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
                        competition_id=200,
                        name="Scotland League",
                        source_club_count=2,
                        selectable_club_ids=(3, 4),
                        selectable_club_names=("Gamma", "Delta"),
                    ),
                ),
            ),
        )
    )


class Gate17HumanScopeCapabilityTests(unittest.TestCase):
    def test_reports_exact_supported_and_unsupported_scope(self):
        scope = scope_fixture()
        audit = audit_human_selection_scope(scope, (1, 2))

        self.assertEqual(audit.catalog_sha256, scope.catalog_sha256)
        self.assertEqual(audit.backend_selectable_club_ids, (1, 2))
        self.assertEqual(audit.catalog_selectable_club_ids, (1, 2, 3, 4))
        self.assertEqual(audit.supported_scope_ids, ("26:100",))
        self.assertEqual(audit.unsupported_scope_ids, ("66:200",))
        self.assertFalse(audit.complete)

        first, second = audit.entries
        self.assertTrue(first.fully_supported)
        self.assertEqual(first.supported_club_ids, (1, 2))
        self.assertEqual(first.unsupported_club_ids, ())
        self.assertFalse(second.fully_supported)
        self.assertEqual(second.supported_club_ids, ())
        self.assertEqual(second.unsupported_club_ids, (3, 4))

        payload = audit.as_dict()
        self.assertFalse(payload["complete"])
        self.assertEqual(payload["scope_entry_count"], 2)
        self.assertEqual(payload["unsupported_scope_ids"], ["66:200"])

    def test_complete_only_when_every_catalog_scope_club_is_selectable(self):
        audit = audit_human_selection_scope(scope_fixture(), (1, 2, 3, 4))
        self.assertTrue(audit.complete)
        self.assertEqual(audit.unsupported_scope_ids, ())
        self.assertEqual(audit.supported_scope_ids, ("26:100", "66:200"))

    def test_backend_extras_are_recorded_without_widening_catalog_scope(self):
        audit = audit_human_selection_scope(scope_fixture(), (1, 2, 99))
        self.assertEqual(audit.backend_club_ids_outside_catalog, (99,))
        self.assertEqual(audit.supported_scope_ids, ("26:100",))
        self.assertEqual(audit.unsupported_scope_ids, ("66:200",))
        self.assertFalse(audit.complete)

    def test_backend_club_ids_require_exact_unique_nonnegative_integers(self):
        for values in ((1, 1), (1, -1), (1, True), (1, "2")):
            with self.subTest(values=values):
                with self.assertRaises(Gate17HumanScopeCapabilityError):
                    audit_human_selection_scope(scope_fixture(), values)

    def test_duplicate_catalog_club_ownership_fails_closed(self):
        scope = scope_fixture()
        duplicated = OriginalPlayableScope(
            countries=(
                scope.countries[0],
                PlayableCountryScope(
                    country_id=66,
                    name="Scotland",
                    source_root_league_count=1,
                    visible_league_capacity=14,
                    leagues=(
                        PlayableLeagueScope(
                            competition_id=200,
                            name="Scotland League",
                            source_club_count=2,
                            selectable_club_ids=(2, 4),
                            selectable_club_names=("Beta", "Delta"),
                        ),
                    ),
                ),
            )
        )
        with self.assertRaisesRegex(
            Gate17HumanScopeCapabilityError,
            "appears in multiple scopes",
        ):
            audit_human_selection_scope(duplicated, (1, 2))


if __name__ == "__main__":
    unittest.main()

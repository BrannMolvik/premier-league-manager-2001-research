"""Tests for Gate-17 extensions to the canonical internal save audit."""
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from canonical_internal_save_audit import (
    _catalog_scope_ids_for_competitions,
    _first_live_procedural_primary_club,
    _json_primary_entry,
    _live_procedural_primary_scope_targets,
    run_canonical_primary_scope_internal_save_audit,
    run_canonical_primary_scope_internal_save_sweep,
)


class _Controller:
    playable_primary_procedural_ids = (14,)
    playable_primary_club_ids = (1, 21, 22)

    def __init__(self, *, owner=True):
        self.state = SimpleNamespace(
            club_competition_membership={1: 0, 21: 14, 22: 14},
            procedural_leagues=(
                {(14, 0): SimpleNamespace(club_ids=(21, 22))}
                if owner
                else {}
            ),
        )

    def selectable_club_ids(self):
        return (1, 21, 22)


class _MultiController:
    playable_primary_procedural_ids = (15, 14)
    playable_primary_club_ids = (21, 22, 31, 32)

    def __init__(self, *, include_first_owner=True):
        owners = {
            (14, 0): SimpleNamespace(club_ids=(21, 22)),
        }
        if include_first_owner:
            owners[(15, 0)] = SimpleNamespace(club_ids=(31, 32))
        self.state = SimpleNamespace(
            club_competition_membership={21: 14, 22: 14, 31: 15, 32: 15},
            procedural_leagues=owners,
        )

    def selectable_club_ids(self):
        # Deliberately does not match competition-policy order. Target ordering
        # must still follow playable_primary_procedural_ids.
        return (21, 31, 22, 32)


def _scope(*, duplicate=False):
    second_leagues = [SimpleNamespace(competition_id=14)]
    if duplicate:
        second_leagues.append(SimpleNamespace(competition_id=15))
    return SimpleNamespace(
        catalog_sha256="a" * 64,
        countries=(
            SimpleNamespace(
                country_id=26,
                leagues=(SimpleNamespace(competition_id=15),),
            ),
            SimpleNamespace(
                country_id=66,
                leagues=tuple(second_leagues),
            ),
        ),
    )


class CanonicalPrimaryScopeSaveAuditTests(unittest.TestCase):
    def test_selects_first_live_procedural_primary_teamselect_club(self):
        self.assertEqual(
            _first_live_procedural_primary_club(_Controller()),
            (21, 14),
        )

    def test_missing_live_owner_fails_closed(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "no live TeamSelect procedural-primary club",
        ):
            _first_live_procedural_primary_club(_Controller(owner=False))

    def test_complete_scope_targets_follow_policy_order(self):
        self.assertEqual(
            _live_procedural_primary_scope_targets(
                _MultiController(),
                require_all=True,
            ),
            ((31, 15), (21, 14)),
        )

    def test_complete_scope_targets_fail_when_expected_owner_is_missing(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "missing live TeamSelect procedural-primary scope targets: 15",
        ):
            _live_procedural_primary_scope_targets(
                _MultiController(include_first_owner=False),
                require_all=True,
            )

    def test_catalog_scope_ids_follow_requested_primary_order(self):
        self.assertEqual(
            _catalog_scope_ids_for_competitions(_scope(), (15, 14)),
            ("26:15", "66:14"),
        )

    def test_catalog_scope_ids_fail_closed_on_missing_or_duplicate_competition(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "missing from canonical TeamSelect catalog: 99",
        ):
            _catalog_scope_ids_for_competitions(_scope(), (15, 99))
        with self.assertRaisesRegex(
            RuntimeError,
            "duplicate competition ID 15",
        ):
            _catalog_scope_ids_for_competitions(_scope(duplicate=True), (15, 14))

    def test_scope_sweep_runs_every_source_order_target(self):
        controller = _MultiController()

        def fake_audit(_game_dir, *, club_id, **_kwargs):
            competition_id = controller.state.club_competition_membership[int(club_id)]
            return {
                "human_club_id": int(club_id),
                "competition_id": int(competition_id),
                "branches_equal": True,
            }

        with (
            patch(
                "canonical_internal_save_audit.HumanGameplayController.from_canonical_game_dir",
                return_value=controller,
            ),
            patch(
                "canonical_internal_save_audit.run_canonical_primary_scope_internal_save_audit",
                side_effect=fake_audit,
            ) as audit,
            patch(
                "canonical_internal_save_audit.load_canonical_original_playable_scope",
                return_value=_scope(),
            ),
        ):
            result = run_canonical_primary_scope_internal_save_sweep(
                "/canonical/game",
                player_seed=7,
            )

        self.assertEqual(result["scope_catalog_sha256"], "a" * 64)
        self.assertEqual(result["procedural_primary_scope_count"], 2)
        self.assertEqual(result["verified_scope_ids"], ["26:15", "66:14"])
        self.assertEqual(result["verified_competition_ids"], [15, 14])
        self.assertEqual(result["target_club_ids"], [31, 21])
        self.assertEqual(result["missing_competition_ids"], [])
        self.assertEqual(result["failed_competition_ids"], [])
        self.assertTrue(result["all_primary_scopes_save_reload_equal"])
        self.assertEqual([call.kwargs["club_id"] for call in audit.call_args_list], [31, 21])

    def test_primary_entry_json_projection_preserves_nested_identity(self):
        self.assertEqual(
            _json_primary_entry(
                ("procedural_league", ("league_match", 14, 0, 3, 7))
            ),
            ["procedural_league", ["league_match", 14, 0, 3, 7]],
        )

    def test_bounds_fail_before_private_canonical_files_are_required(self):
        with self.assertRaisesRegex(
            ValueError,
            "max_matches_before_save must be positive",
        ):
            run_canonical_primary_scope_internal_save_audit(
                "/private/source/not-needed",
                max_matches_before_save=0,
            )
        with self.assertRaisesRegex(
            ValueError,
            "post_save_matches must be positive",
        ):
            run_canonical_primary_scope_internal_save_audit(
                "/private/source/not-needed",
                post_save_matches=0,
            )
        with self.assertRaisesRegex(
            ValueError,
            "max_matches_before_save must be positive",
        ):
            run_canonical_primary_scope_internal_save_sweep(
                "/private/source/not-needed",
                max_matches_before_save=0,
            )
        with self.assertRaisesRegex(
            ValueError,
            "post_save_matches must be positive",
        ):
            run_canonical_primary_scope_internal_save_sweep(
                "/private/source/not-needed",
                post_save_matches=0,
            )


if __name__ == "__main__":
    unittest.main()

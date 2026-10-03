"""Tests for Gate-17 extensions to the canonical internal save audit."""
from types import SimpleNamespace
import unittest

from canonical_internal_save_audit import (
    _first_live_procedural_primary_club,
    _json_primary_entry,
    run_canonical_primary_scope_internal_save_audit,
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


if __name__ == "__main__":
    unittest.main()

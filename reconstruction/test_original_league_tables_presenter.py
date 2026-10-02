from __future__ import annotations

from dataclasses import dataclass
import unittest

from original_league_tables_presenter import (
    OriginalLeagueTablesPresentationError,
    build_league_tables_snapshot,
)
from original_league_tables_resources import LEAGUE_TABLES_RESOURCES


@dataclass(frozen=True)
class Row:
    position: int
    club_id: int
    club_name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int


class OriginalLeagueTablesPresenterTests(unittest.TestCase):
    def row(self, *, position=1, club_id=7, club_name="Source Club",
            played=10, wins=6, draws=2, losses=2,
            goals_for=18, goals_against=9, points=20):
        return Row(
            position, club_id, club_name, played, wins, draws, losses,
            goals_for, goals_against, points,
        )

    def test_default_snapshot_preserves_exact_source_geometry_and_columns(self):
        snapshot = build_league_tables_snapshot((self.row(),))
        self.assertEqual(snapshot.list_rect, (270, 184, 477, 384))
        self.assertEqual(snapshot.row_capacity, 24)
        self.assertEqual(snapshot.row_step, 16)
        self.assertEqual(snapshot.sort_state, 0)
        self.assertTrue(snapshot.stat_headers_active)
        self.assertEqual(
            tuple((header.label, header.rect) for header in snapshot.headers),
            (
                (None, (316, 152, 214, 19)),
                ("P", (532, 152, 27, 19)),
                ("W", (561, 152, 27, 19)),
                ("D", (590, 152, 27, 19)),
                ("L", (619, 152, 27, 19)),
                ("F", (648, 152, 27, 19)),
                ("A", (677, 152, 27, 19)),
                ("Pts", (706, 152, 27, 19)),
            ),
        )
        row = snapshot.rows[0]
        self.assertEqual(row.rank_rect, (23, 1, 21, 12))
        self.assertEqual(row.club_rect, (46, 1, 214, 12))
        self.assertEqual(
            row.stat_rects,
            (
                (262, 1, 27, 12),
                (291, 1, 27, 12),
                (320, 1, 27, 12),
                (349, 1, 27, 12),
                (378, 1, 27, 12),
                (407, 1, 27, 12),
                (436, 1, 27, 12),
            ),
        )
        self.assertEqual(row.values, (10, 6, 2, 2, 18, 9, 20))

    def test_points_must_match_original_three_wins_plus_draws_formula(self):
        with self.assertRaisesRegex(
            OriginalLeagueTablesPresentationError,
            r"3\*W\+D",
        ):
            build_league_tables_snapshot((self.row(points=21),))

    def test_more_than_twenty_four_source_rows_fails_closed(self):
        rows = tuple(
            self.row(position=i + 1, club_id=i + 1, club_name=f"Club {i + 1}")
            for i in range(25)
        )
        with self.assertRaisesRegex(
            OriginalLeagueTablesPresentationError,
            "24-row capacity",
        ):
            build_league_tables_snapshot(rows)

    def test_current_form_sort_is_not_faked_by_reusing_league_position_order(self):
        with self.assertRaisesRegex(
            OriginalLeagueTablesPresentationError,
            "Current Form ordering",
        ):
            build_league_tables_snapshot((self.row(),), sort_state=1)

    def test_exact_art_readiness_requires_all_fifteen_source_resources(self):
        names = tuple(resource.name for resource in LEAGUE_TABLES_RESOURCES)
        snapshot = build_league_tables_snapshot(
            (self.row(),),
            staged_resource_names=names,
        )
        self.assertTrue(snapshot.exact_art_staged)
        self.assertEqual(snapshot.required_art, names)

        partial = build_league_tables_snapshot(
            (self.row(),),
            staged_resource_names=names[:-1],
        )
        self.assertFalse(partial.exact_art_staged)

    def test_unknown_staged_art_fails_closed(self):
        with self.assertRaisesRegex(
            OriginalLeagueTablesPresentationError,
            "Unknown staged League Tables art",
        ):
            build_league_tables_snapshot(
                (self.row(),),
                staged_resource_names=("invented_grid",),
            )

    def test_row_source_types_are_not_coerced_silently(self):
        bad = self.row()
        object.__setattr__(bad, "wins", "6")
        with self.assertRaisesRegex(
            OriginalLeagueTablesPresentationError,
            "wins must be an integer",
        ):
            build_league_tables_snapshot((bad,))


if __name__ == "__main__":
    unittest.main()

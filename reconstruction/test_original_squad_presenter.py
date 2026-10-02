from __future__ import annotations

from dataclasses import dataclass
import unittest

from original_squad_presenter import (
    OriginalSquadPresentationError,
    build_squad_row_viewport,
    source_accepted_squad_view_transition,
)


@dataclass(frozen=True)
class Row:
    source_roster_index: int
    player_id: int
    full_name: str
    current_position: int
    condition: int
    recent_form_average: float
    current_role_rating: int


class OriginalSquadPresenterTests(unittest.TestCase):
    def row(self, index=0):
        return Row(index, 100 + index, f"Player {index}", 12, 88, 7.5, 63)

    def test_exact_native_row_geometry_and_resolved_columns_are_preserved(self):
        snapshot = build_squad_row_viewport((self.row(), self.row(1)))

        self.assertEqual(snapshot.row_capacity, 20)
        self.assertEqual(snapshot.row_y_origins, tuple(154 + 17 * i for i in range(20)))
        self.assertEqual(
            tuple((c.semantic_key, c.x, c.width, c.value_resolved) for c in snapshot.player_columns),
            (
                ("club_relative_assignment", 1, 22, False),
                ("assigned_role", 28, 38, True),
                ("display_name", 76, 144, True),
            ),
        )
        self.assertEqual(
            tuple((c.semantic_key, c.x, c.width, c.value_resolved) for c in snapshot.side_columns),
            (
                ("native_status_icon", 1, None, False),
                ("condition", 24, 19, True),
                ("recent_form_average", 47, 19, True),
                ("current_role_rating", 70, 19, True),
            ),
        )
        self.assertEqual(
            snapshot.unresolved_value_columns,
            ("club_relative_assignment", "native_status_icon"),
        )
        self.assertEqual(snapshot.rows[0].y, 154)
        self.assertEqual(snapshot.rows[1].y, 171)
        self.assertEqual(snapshot.rows[0].display_name, "Player 0")
        self.assertEqual(snapshot.rows[0].assigned_role, 12)
        self.assertEqual(snapshot.rows[0].condition, 88)
        self.assertEqual(snapshot.rows[0].recent_form_average, 7.5)
        self.assertEqual(snapshot.rows[0].current_role_rating, 63)

    def test_source_accepted_view_transitions_match_native_control_contract(self):
        combined = source_accepted_squad_view_transition(3)
        self.assertEqual(
            (
                combined.original_text,
                combined.left_roster,
                combined.second_roster_mask1,
                combined.pitch_mask1,
                combined.pitch_team_index,
            ),
            ("1ST & RES", "first", True, False, None),
        )

        first_form = source_accepted_squad_view_transition(4)
        self.assertEqual(
            (
                first_form.original_text,
                first_form.left_roster,
                first_form.second_roster_mask1,
                first_form.pitch_mask1,
                first_form.pitch_team_index,
            ),
            ("1ST FORM", "first", False, True, 0),
        )

        reserve_form = source_accepted_squad_view_transition(5)
        self.assertEqual(
            (
                reserve_form.original_text,
                reserve_form.left_roster,
                reserve_form.second_roster_mask1,
                reserve_form.pitch_mask1,
                reserve_form.pitch_team_index,
            ),
            ("RES. FORM", "reserve", False, True, 1),
        )

    def test_unproven_squad_view_control_fails_closed(self):
        with self.assertRaisesRegex(
            OriginalSquadPresentationError,
            "not source-proven",
        ):
            source_accepted_squad_view_transition(6)

    def test_more_than_twenty_visible_rows_fails_closed(self):
        with self.assertRaisesRegex(
            OriginalSquadPresentationError,
            "20-row visible viewport",
        ):
            build_squad_row_viewport(tuple(self.row(i) for i in range(21)))

    def test_missing_or_coerced_source_values_fail_closed(self):
        bad = self.row()
        object.__setattr__(bad, "condition", "88")
        with self.assertRaisesRegex(OriginalSquadPresentationError, "condition"):
            build_squad_row_viewport((bad,))

        bad = self.row()
        object.__setattr__(bad, "recent_form_average", True)
        with self.assertRaisesRegex(
            OriginalSquadPresentationError,
            "recent_form_average",
        ):
            build_squad_row_viewport((bad,))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from dataclasses import dataclass, replace
import unittest

from original_squad_presenter import (
    OriginalSquadPresentationError,
    build_squad_row_viewport,
)


@dataclass(frozen=True)
class Row:
    source_roster_index: int
    player_id: int
    first_name: str
    surname: str
    full_name: str
    positions: tuple[int, int, int]
    current_position: int
    assigned_role_abbreviation: str
    match_active: bool
    match_substitute_available: bool
    condition: int
    recent_form_average: float
    current_role_rating: int
    reserve_active: bool = False
    reserve_substitute_available: bool = False
    injured: bool = False
    suspended: bool = False
    international: bool = False
    alternate_on_loan: bool = False
    non_eu: bool = False
    non_eu_registration_expired: bool | None = False
    cup_tied_positive: bool = False


class OriginalSquadPresenterTests(unittest.TestCase):
    def row(self, index=0):
        return Row(
            index,
            100 + index,
            "Player",
            str(index),
            f"Player {index}",
            (12, 4, 7),
            12,
            "FC",
            index == 0,
            index == 1,
            88,
            7.5,
            63,
        )

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
        self.assertEqual(snapshot.rows[0].display_name, "P. 0")
        self.assertEqual(snapshot.rows[0].display_name_rgb, (255, 255, 255))
        self.assertEqual(snapshot.rows[0].assigned_role, 12)
        self.assertEqual(snapshot.rows[0].assigned_role_abbreviation, "FC")
        self.assertEqual(snapshot.rows[0].assigned_role_rgb, (255, 255, 255))
        self.assertEqual(snapshot.rows[0].condition, 88)
        self.assertEqual(snapshot.rows[1].display_name_rgb, (232, 191, 94))
        self.assertEqual(snapshot.rows[0].recent_form_average, 7.5)
        self.assertEqual(snapshot.rows[0].current_role_rating, 63)
        self.assertIsNone(snapshot.rows[0].native_status_frame_index)

    def test_five_state_name_colors_include_fresh_default_and_reserves(self):
        default = self.row(2)
        snapshot = build_squad_row_viewport((default,))
        self.assertEqual(snapshot.rows[0].display_name_rgb, (217, 210, 62))

        reserve_active = replace(default, reserve_active=True)
        snapshot = build_squad_row_viewport((reserve_active,))
        self.assertEqual(snapshot.rows[0].display_name_rgb, (176, 176, 176))

        reserve_substitute = replace(
            default,
            reserve_substitute_available=True,
        )
        snapshot = build_squad_row_viewport((reserve_substitute,))
        self.assertEqual(snapshot.rows[0].display_name_rgb, (185, 167, 131))

    def test_direct_status_frames_follow_native_priority(self):
        injured = self.row()
        object.__setattr__(injured, "injured", True)
        object.__setattr__(injured, "suspended", True)
        object.__setattr__(injured, "international", True)
        self.assertEqual(
            build_squad_row_viewport((injured,)).rows[0].native_status_frame_index,
            0,
        )

        banned = self.row()
        object.__setattr__(banned, "suspended", True)
        object.__setattr__(banned, "international", True)
        self.assertEqual(
            build_squad_row_viewport((banned,)).rows[0].native_status_frame_index,
            1,
        )

        international = self.row()
        object.__setattr__(international, "international", True)
        self.assertEqual(
            build_squad_row_viewport((international,)).rows[0].native_status_frame_index,
            2,
        )

    def test_source_qualified_status_frames_preserve_native_override_priority(self):
        loaned = self.row()
        object.__setattr__(loaned, "alternate_on_loan", True)
        object.__setattr__(loaned, "non_eu", True)
        object.__setattr__(loaned, "cup_tied_positive", True)
        self.assertEqual(
            build_squad_row_viewport((loaned,)).rows[0].native_status_frame_index,
            13,
        )

        expired_non_eu = self.row()
        object.__setattr__(expired_non_eu, "non_eu", True)
        object.__setattr__(expired_non_eu, "non_eu_registration_expired", True)
        object.__setattr__(expired_non_eu, "cup_tied_positive", True)
        self.assertEqual(
            build_squad_row_viewport(
                (expired_non_eu,)
            ).rows[0].native_status_frame_index,
            12,
        )

        current_non_eu = self.row()
        object.__setattr__(current_non_eu, "non_eu", True)
        object.__setattr__(current_non_eu, "non_eu_registration_expired", False)
        object.__setattr__(current_non_eu, "cup_tied_positive", True)
        self.assertEqual(
            build_squad_row_viewport(
                (current_non_eu,)
            ).rows[0].native_status_frame_index,
            3,
        )

        unresolved_non_eu = self.row()
        object.__setattr__(unresolved_non_eu, "non_eu", True)
        object.__setattr__(unresolved_non_eu, "non_eu_registration_expired", None)
        object.__setattr__(unresolved_non_eu, "cup_tied_positive", True)
        self.assertIsNone(
            build_squad_row_viewport(
                (unresolved_non_eu,)
            ).rows[0].native_status_frame_index
        )

        cup_tied = self.row()
        object.__setattr__(cup_tied, "cup_tied_positive", True)
        self.assertEqual(
            build_squad_row_viewport((cup_tied,)).rows[0].native_status_frame_index,
            3,
        )

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
        object.__setattr__(bad, "match_active", None)
        with self.assertRaisesRegex(
            OriginalSquadPresentationError, "selection color states"
        ):
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

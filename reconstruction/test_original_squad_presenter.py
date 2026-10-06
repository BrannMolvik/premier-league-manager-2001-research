from __future__ import annotations

from dataclasses import dataclass, replace
import unittest

from original_squad_presenter import (
    PSQUAD_NAME_CONTROL_SETUP_VA,
    PSQUAD_NAME_FONT_SLOT_VA,
    PSQUAD_NAME_FORMAT_INITIAL_SURNAME,
    PSQUAD_NAME_RAW_FLAGS,
    PSQUAD_NAME_STATUS_RGB,
    PSQUAD_ROLE_PREFERRED_PREDICATE_VA,
    PSQUAD_ROLE_PREFERRED_RGB,
    PSQUAD_ROLE_UNPREFERRED_RGB,
    OriginalSquadPresentationError,
    build_squad_row_viewport,
    native_squad_display_name,
    native_squad_name_status,
)


@dataclass(frozen=True)
class Row:
    source_roster_index: int
    player_id: int
    first_name: str
    surname: str
    positions: tuple[int, int, int]
    current_position: int
    match_active: bool
    match_substitute_available: bool
    injured: bool
    suspended: bool
    condition: int
    recent_form_average: float
    current_role_rating: int


class OriginalSquadPresenterTests(unittest.TestCase):
    def row(self, index=0):
        return Row(
            index,
            100 + index,
            "Player",
            f"Surname{index}",
            (12, 18, 0),
            12,
            False,
            False,
            False,
            False,
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
        self.assertEqual(snapshot.rows[0].display_name, "P. Surname0")
        self.assertEqual(snapshot.rows[0].display_name_status, "default")
        self.assertEqual(snapshot.rows[0].display_name_rgb, (217, 210, 62))
        self.assertEqual(snapshot.rows[0].assigned_role, 12)
        self.assertTrue(snapshot.rows[0].assigned_role_is_preferred)
        self.assertEqual(snapshot.rows[0].assigned_role_rgb, (255, 255, 255))
        self.assertEqual(snapshot.rows[0].condition, 88)
        self.assertEqual(snapshot.rows[0].recent_form_average, 7.5)
        self.assertEqual(snapshot.rows[0].current_role_rating, 63)

    def test_source_helper_addresses_and_control_contract_are_locked(self):
        self.assertEqual(PSQUAD_ROLE_PREFERRED_PREDICATE_VA, 0x4EA3F0)
        self.assertEqual(PSQUAD_NAME_CONTROL_SETUP_VA, 0x5D6C50)
        self.assertEqual(PSQUAD_NAME_FONT_SLOT_VA, 0x94758C)
        self.assertEqual(PSQUAD_NAME_RAW_FLAGS, 0x21)
        self.assertEqual(PSQUAD_NAME_FORMAT_INITIAL_SURNAME, "%c. %s")
        self.assertEqual(PSQUAD_ROLE_PREFERRED_RGB, (255, 255, 255))
        self.assertEqual(PSQUAD_ROLE_UNPREFERRED_RGB, (125, 1, 0))
        self.assertEqual(
            PSQUAD_NAME_STATUS_RGB,
            (
                ("match_active", (255, 255, 255)),
                ("match_substitute_available", (232, 191, 94)),
                ("injured", (176, 176, 176)),
                ("suspended", (185, 167, 131)),
                ("default", (217, 210, 62)),
            ),
        )

    def test_native_name_uses_initial_and_surname_with_special_surname_only_branch(self):
        self.assertEqual(native_squad_display_name("David", "Beckham"), "D. Beckham")
        self.assertEqual(native_squad_display_name("-special", "Pelé"), "Pelé")
        for first, surname in (("", "Surname"), ("Name", "")):
            with self.subTest(first=first, surname=surname):
                with self.assertRaises(OriginalSquadPresentationError):
                    native_squad_display_name(first, surname)

    def test_name_status_priority_and_exact_source_colors_are_preserved(self):
        cases = (
            (
                dict(
                    match_active=True,
                    match_substitute_available=True,
                    injured=True,
                    suspended=True,
                ),
                ("match_active", (255, 255, 255)),
            ),
            (
                dict(
                    match_active=False,
                    match_substitute_available=True,
                    injured=True,
                    suspended=True,
                ),
                ("match_substitute_available", (232, 191, 94)),
            ),
            (
                dict(
                    match_active=False,
                    match_substitute_available=False,
                    injured=True,
                    suspended=True,
                ),
                ("injured", (176, 176, 176)),
            ),
            (
                dict(
                    match_active=False,
                    match_substitute_available=False,
                    injured=False,
                    suspended=True,
                ),
                ("suspended", (185, 167, 131)),
            ),
            (
                dict(
                    match_active=False,
                    match_substitute_available=False,
                    injured=False,
                    suspended=False,
                ),
                ("default", (217, 210, 62)),
            ),
        )
        for flags, expected in cases:
            with self.subTest(flags=flags):
                self.assertEqual(native_squad_name_status(**flags), expected)

    def test_assigned_role_color_tracks_native_preferred_role_predicate(self):
        preferred = build_squad_row_viewport((self.row(),)).rows[0]
        self.assertTrue(preferred.assigned_role_is_preferred)
        self.assertEqual(preferred.assigned_role_rgb, PSQUAD_ROLE_PREFERRED_RGB)

        nonpreferred = replace(self.row(), current_position=11)
        projected = build_squad_row_viewport((nonpreferred,)).rows[0]
        self.assertFalse(projected.assigned_role_is_preferred)
        self.assertEqual(projected.assigned_role_rgb, PSQUAD_ROLE_UNPREFERRED_RGB)

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

        bad = self.row()
        object.__setattr__(bad, "positions", (12, 18))
        with self.assertRaisesRegex(OriginalSquadPresentationError, "three source role"):
            build_squad_row_viewport((bad,))

        bad = self.row()
        object.__setattr__(bad, "match_active", 1)
        with self.assertRaisesRegex(OriginalSquadPresentationError, "match_active"):
            build_squad_row_viewport((bad,))


if __name__ == "__main__":
    unittest.main()

"""Focused regressions for the executable-recovered TeamSelect hierarchy."""
from types import SimpleNamespace
import unittest

from original_teamselect_native import (
    HierarchyRowKind,
    NativeControlState,
    TeamSelectHierarchyModel,
    TeamSelectNativeError,
    animation_source_index,
    club_bar_source_index,
    league_bar_source_index,
    native_clubs_for_competition,
    native_competitions_for_country,
)


def country(source_id, name):
    return SimpleNamespace(id=source_id, name=name)


def competition(source_id, name, order, *, country_id=26, kind=1, parent=None):
    return SimpleNamespace(
        id=source_id,
        name=name,
        initialization_order_value=order,
        country_region_id=country_id,
        runtime_kind_code=kind,
        parent_competition_id=parent,
    )


def club(source_id, name, competition_id=0):
    return SimpleNamespace(index=source_id, name=name, competition_id=competition_id)


class OriginalTeamSelectNativeTests(unittest.TestCase):
    def test_exact_native_source_frame_transforms(self):
        self.assertEqual(
            [animation_source_index(NativeControlState.NORMAL, i) for i in (0, 10)],
            [0, 10],
        )
        self.assertEqual(
            [animation_source_index(NativeControlState.ACTIVE, i) for i in (0, 10)],
            [11, 21],
        )
        self.assertEqual(animation_source_index(NativeControlState.DISABLED), 22)
        self.assertEqual(club_bar_source_index(NativeControlState.NORMAL, 0), 0)
        self.assertEqual(club_bar_source_index(NativeControlState.NORMAL, 1), 1)
        self.assertEqual(club_bar_source_index(NativeControlState.ACTIVE), 2)
        self.assertEqual(club_bar_source_index(NativeControlState.DISABLED), 3)
        self.assertEqual(
            league_bar_source_index(NativeControlState.NORMAL, is_country=True), 0
        )
        self.assertEqual(
            league_bar_source_index(NativeControlState.NORMAL, is_country=False), 1
        )
        self.assertEqual(
            league_bar_source_index(
                NativeControlState.NORMAL, is_country=True, progress=1
            ),
            2,
        )
        self.assertEqual(
            league_bar_source_index(NativeControlState.ACTIVE, is_country=False), 3
        )
        self.assertEqual(
            league_bar_source_index(NativeControlState.DISABLED, is_country=True), 4
        )
        with self.assertRaises(TeamSelectNativeError):
            animation_source_index(NativeControlState.DISABLED, 1)

    def test_competition_filter_is_root_league_country_and_stable_order(self):
        source = (
            competition(21, "Late tie", 9),
            competition(22, "First", 7),
            competition(23, "Early tie", 9),
            competition(24, "Child", 1, parent=22),
            competition(25, "Cup", 1, kind=2),
            competition(26, "Foreign", 1, country_id=66),
        )
        self.assertEqual(
            [item.id for item in native_competitions_for_country(source, 26)],
            [22, 21, 23],
        )

    def test_club_filter_uses_raw_cp1252_name_order(self):
        source = (
            club(3, "Zulu"),
            club(4, "Other", 1),
            club(2, "Arsenal"),
            club(1, "Aston Villa"),
        )
        self.assertEqual(
            [item.index for item in native_clubs_for_competition(source, 0)],
            [2, 1, 3],
        )

    def test_default_population_and_country_competition_club_transitions(self):
        country_order = (
            (26, "England"), (66, "Scotland"), (33, "Germany"),
            (40, "Italy"), (73, "Spain"), (31, "France"),
            (24, "Holland"), (9, "Belgium"),
        )
        countries = {key: country(key, name) for key, name in country_order}
        competitions = (
            competition(0, "F.A. Premier League", 9),
            competition(2, "Division 1", 10),
            competition(3, "Division 2", 11),
            competition(4, "Division 3", 12),
            competition(7, "Conference", 13),
            competition(27, "Premiership", 7, country_id=66),
        )
        clubs = (club(5, "Chelsea"), club(0, "Arsenal"), club(1, "Aston Villa"))
        model = TeamSelectHierarchyModel(countries, competitions, clubs)

        rows = model.hierarchy_rows()
        self.assertEqual(len(rows), 13)
        self.assertEqual(rows[0].text, "England")
        self.assertEqual(rows[1].text, "F.A. Premier League")
        self.assertIs(rows[1].kind, HierarchyRowKind.COMPETITION)
        self.assertIs(rows[1].state, NativeControlState.ACTIVE)
        self.assertEqual([item.text for item in model.club_rows()], [
            "Arsenal", "Aston Villa", "Chelsea",
        ])

        model.toggle_club_row(0)
        self.assertEqual(model.selected_club_record_index, 0)
        self.assertIs(model.club_rows()[0].state, NativeControlState.ACTIVE)
        model.toggle_club_row(0)
        self.assertIsNone(model.selected_club_record_index)

        model.activate_hierarchy_row(0)
        self.assertIsNone(model.selected_competition_id)
        self.assertEqual(model.club_rows(), ())
        self.assertIs(model.hierarchy_rows()[0].state, NativeControlState.ACTIVE)
        model.activate_hierarchy_row(1)
        self.assertEqual(model.selected_competition_id, 0)
        self.assertEqual(len(model.club_rows()), 3)


if __name__ == "__main__":
    unittest.main()

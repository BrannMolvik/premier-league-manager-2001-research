from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from gate13_management_source_data import (
    ManagementPresentationError,
    ManagementSourceDataBridge,
)
from original_league_tables_live_source import (
    SourceProceduralLeagueTableError,
    source_qualified_procedural_league_table,
)
from procedural_league_state import LiveProceduralLeagueState, ProceduralLeagueFixture


def live_state(*, with_results=True):
    fixtures = {
        ("league_match", 31, 0, 1): ProceduralLeagueFixture(
            ("league_match", 31, 0, 1), 10, 11),
        ("league_match", 31, 0, 2): ProceduralLeagueFixture(
            ("league_match", 31, 0, 2), 12, 11),
    }
    state = LiveProceduralLeagueState(
        competition_id=31,
        competition_context=0,
        fixtures=fixtures,
        club_ids=(11, 12, 10),  # Deliberately NOT native ranking order.
    )
    if with_results:
        state.record_result(("league_match", 31, 0, 1), 2, 1)
        state.record_result(("league_match", 31, 0, 2), 1, 0)
    return state


def source(*, live=None):
    if live is None:
        live = live_state()
    return SimpleNamespace(
        clubs={
            10: SimpleNamespace(name="Team Ten", short_name="Team Ten", country_id=26),
            11: SimpleNamespace(name="Team Eleven", short_name="Team Eleven", country_id=26),
            12: SimpleNamespace(name="Team Twelve", short_name="Team Twelve", country_id=26),
        },
        competitions={31: SimpleNamespace(
            id=31, country_region_id=26, parent_competition_id=None,
            runtime_kind_code=1)},
        club_competition_membership={10: 31, 11: 31, 12: 31},
        procedural_leagues={(31, 0): live},
        premier_league_table=Mock(side_effect=AssertionError(
            "Never show Premier League 0 for a different manager competition"
        )),
    )


def exact_rows(s):
    return source_qualified_procedural_league_table(
        human_club_id=10, competition_id=31,
        membership=s.club_competition_membership,
        clubs=s.clubs,
        competitions=s.competitions,
        procedural_leagues=s.procedural_leagues,
    )


class SourceProceduralLeagueTableTests(unittest.TestCase):
    def test_native_ranking_uses_actual_live_results_not_fixture_encounter_order(self):
        s = source()
        rows = exact_rows(s)
        self.assertEqual(tuple(row.club_id for row in rows), (10, 12, 11))
        self.assertEqual(tuple(row.points for row in rows), (3, 3, 0))
        self.assertEqual((rows[0].played, rows[0].goals_for, rows[0].goals_against),
                         (1, 2, 1))
        self.assertEqual(s.procedural_leagues[(31, 0)].club_ids, (11, 12, 10))
        self.assertEqual(len(s.procedural_leagues[(31, 0)].results), 2)

    def test_bridge_projects_real_nonpl_league_rows_with_original_header_data(self):
        s = source()
        c = SimpleNamespace(state=s, human=SimpleNamespace(club_id=10))
        rows = ManagementSourceDataBridge(c).league_table_rows()
        self.assertEqual(tuple(x.position for x in rows), (1, 2, 3))
        self.assertEqual(tuple(x.club_id for x in rows), (10, 12, 11))
        self.assertEqual(tuple(x.club_name for x in rows),
                         ("Team Ten", "Team Twelve", "Team Eleven"))
        self.assertEqual(rows[0].points, 3)
        s.premier_league_table.assert_not_called()

    def test_unplayed_league_still_has_native_cp1252_short_name_tiebreak(self):
        live = LiveProceduralLeagueState(
            competition_id=31, competition_context=0,
            fixtures={("x",): ProceduralLeagueFixture(("x",), 10, 11)},
            club_ids=(10, 11),
        )
        s = source(live=live)
        s.clubs.pop(12)
        s.club_competition_membership.pop(12)
        s.clubs[10].short_name = "À"
        s.clubs[11].short_name = "B"
        self.assertEqual(tuple(row.club_id for row in exact_rows(s)), (11, 10))
        self.assertEqual(len(live.results), 0)

    def test_unresolved_full_native_qsort_tie_must_fail_not_sort_by_club_id(self):
        s = source(live=LiveProceduralLeagueState(
            competition_id=31, competition_context=0,
            fixtures={("x",): ProceduralLeagueFixture(("x",), 10, 11)},
            club_ids=(11, 10),
        ))
        s.clubs.pop(12)
        s.club_competition_membership.pop(12)
        s.clubs[10].short_name = s.clubs[11].short_name = "Same"
        with self.assertRaisesRegex(SourceProceduralLeagueTableError, "CRT sort tie"):
            exact_rows(s)

    def test_career_current_manager_competition_must_match_source_record(self):
        s = source()
        s.club_competition_membership[10] = 0
        with self.assertRaisesRegex(SourceProceduralLeagueTableError, "current"):
            exact_rows(s)
        c = SimpleNamespace(state=s, human=SimpleNamespace(club_id=10))
        # The PL path is distinct; here the sentinel is deliberately hostile.
        with self.assertRaises(AssertionError):
            ManagementSourceDataBridge(c).league_table_rows()

    def test_other_unrepresented_source_club_blocks_partial_fake_table(self):
        s = source()
        s.club_competition_membership[13] = 31
        s.clubs[13] = SimpleNamespace(name="Missing", short_name="Missing", country_id=26)
        with self.assertRaisesRegex(SourceProceduralLeagueTableError, "participants disagree"):
            exact_rows(s)
        s = source()
        s.club_competition_membership[12] = 0
        with self.assertRaises(SourceProceduralLeagueTableError):
            exact_rows(s)

    def test_missing_or_multiple_context_cannot_guess_group_or_rank(self):
        s = source()
        s.procedural_leagues = {}
        with self.assertRaisesRegex(SourceProceduralLeagueTableError, "context-zero"):
            exact_rows(s)
        s = source()
        s.procedural_leagues[(31, 3)] = live_state()
        with self.assertRaisesRegex(SourceProceduralLeagueTableError, "context-zero"):
            exact_rows(s)
        s = source()
        s.procedural_leagues = {(31, 3): live_state()}
        with self.assertRaises(SourceProceduralLeagueTableError):
            exact_rows(s)

    def test_non_league_cup_dummy_child_and_wrong_country_are_rejected(self):
        for attr, value in (
            ("runtime_kind_code", 2),
            ("runtime_kind_code", 3),
            ("parent_competition_id", 99),
            ("country_region_id", 33),
        ):
            with self.subTest(attr=attr, value=value):
                s = source()
                setattr(s.competitions[31], attr, value)
                with self.assertRaisesRegex(SourceProceduralLeagueTableError, "root League"):
                    exact_rows(s)

    def test_source_club_country_name_and_members_must_be_qualified(self):
        s = source()
        s.clubs[11].country_id = 33
        with self.assertRaises(SourceProceduralLeagueTableError):
            exact_rows(s)
        s = source()
        s.clubs[11].short_name = "😀"
        with self.assertRaisesRegex(SourceProceduralLeagueTableError, "CP1252"):
            exact_rows(s)
        s = source()
        del s.clubs[11]
        with self.assertRaises(SourceProceduralLeagueTableError):
            exact_rows(s)

    def test_missing_current_manager_membership_never_defaults_to_pl_zero(self):
        s = source()
        del s.club_competition_membership
        c = SimpleNamespace(state=s, human=SimpleNamespace(club_id=10))
        with self.assertRaisesRegex(ManagementPresentationError, "membership source"):
            ManagementSourceDataBridge(c).league_table_rows()
        s.premier_league_table.assert_not_called()

    def test_missing_canonical_human_country_does_not_imply_valid_root_league(self):
        s = source()
        del s.clubs[10].country_id
        with self.assertRaisesRegex(SourceProceduralLeagueTableError, "country identity"):
            exact_rows(s)

    def test_no_live_nonpl_source_never_calls_premier_league_projection(self):
        s = source()
        s.procedural_leagues = {}
        c = SimpleNamespace(state=s, human=SimpleNamespace(club_id=10))
        with self.assertRaisesRegex(ManagementPresentationError, "context-zero"):
            ManagementSourceDataBridge(c).league_table_rows()
        s.premier_league_table.assert_not_called()


if __name__ == "__main__":
    unittest.main()

"""Original PLeagueTables event15 selected League Current Form source-only data.

These are native ranking/data-bridge tests, not native 0x4480A0 row geometry,
WM_LBUTTON, modal/raster, or Windows 11 acceptance tests.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from types import SimpleNamespace as Obj
import unittest

from gate13_management_source_data import (
    LeagueCurrentFormSourceRowView,
    ManagementPresentationError,
)
from test_original_league_tables_current_form_premier0 import scenario as premier_form_scenario
from test_original_league_tables_selected_premier0 import (
    prepared_state, source_bridge, select_premier,
)
from test_original_league_tables_selected_source import context, bridge
from test_original_league_fixtures_selected_source import state_two_source_leagues


def nonpl_ready():
    state = state_two_source_leagues()
    state.clubs[10].team_category_code = 1
    state.clubs[11].team_category_code = 1
    # Legacy selector fixture source omits these fields; the real production
    # DBRCompetition resolves both from verified native source code.
    state.competitions[2].runtime_kind = "league"
    state.competitions[2].uses_secondary_schedule_container = False
    first = date(2000, 8, 17)
    for on_date, token, home, away, played in (
        (first, ("alt", 1), 11, 10, False),
        (first + timedelta(days=7), ("alt", 0), 10, 11, True),
    ):
        entry = Obj(
            competition_id=2, competition_context=0,
            node_kind="league_match", node_token=token,
            participant_0_ref=Obj(direct_club_id=home),
            participant_1_ref=Obj(direct_club_id=away),
            side_club_cache=(home, away),
            payload_filter_bits=int(played),
            wrapper_link_state="clear",
        )
        state.primary_schedule_shadow.days[on_date] = (entry,)
    state.calendar.current_date = first + timedelta(days=7)
    state.primary_schedule_end_date = first + timedelta(days=373)
    selected = context(state).accept_native_radio_event(10).accept_native_radio_event(15)
    return state, selected


def premier_ready():
    state = prepared_state()
    source = premier_form_scenario()
    state.premier_league = source.premier_league
    state.primary_schedule_shadow = source.primary_schedule_shadow
    state.primary_schedule_end_date = source.primary_schedule_end_date
    state.calendar.current_date = source.calendar.current_date
    state.competitions[0].scheduled_matchday_count = 38
    state.competitions[0].uses_secondary_schedule_container = False
    for cid in state.premier_league.club_ids:
        state.clubs[cid].team_category_code = 1
    return state, select_premier(state).accept_native_radio_event(15)


class SelectedOriginalCurrentFormBridgeTests(unittest.TestCase):
    def test_other_native_league_uses_current_form_not_position_standings(self):
        state, selected = nonpl_ready()
        view = bridge(state).source_selected_league_current_form_rows(selected)
        self.assertEqual(len(view), 2)
        self.assertTrue(all(type(row) is LeagueCurrentFormSourceRowView for row in view))
        self.assertEqual([(r.club_id, r.form_score) for r in view], [(10, 4), (11, 1)])
        self.assertEqual(view[0].six_form_labels, (" ", " ", " ", " ", "D", "W"))
        self.assertEqual(view[1].six_form_labels, (" ", " ", " ", " ", "D", "L"))
        self.assertEqual(view[0].matching_source_tokens, (("alt", 0), ("alt", 1)))
        self.assertEqual(state.club_competition_membership[349], 7)
        with self.assertRaisesRegex(ManagementPresentationError, "sort"):
            bridge(state).source_selected_league_current_form_rows(
                selected.accept_native_radio_event(14))

    def test_premier0_uses_distinct_fixed_380_source_not_procedural_owner(self):
        state, selected = premier_ready()
        view = source_bridge(state).source_selected_league_current_form_rows(selected)
        self.assertEqual(len(view), 20)
        self.assertEqual({r.club_id for r in view}, set(range(1000, 1020)))
        by_id = {r.club_id: r for r in view}
        self.assertEqual(by_id[1000].six_form_labels[-1], "W")
        self.assertEqual(by_id[1001].six_form_labels[-1], "L")
        self.assertNotIn(349, by_id)
        self.assertEqual(state.club_competition_membership[349], 7)

    def test_immutable_native_selection_rejects_manipulation(self):
        state, good = nonpl_ready()
        for altered in (
            replace(good, sort_state=0),
            replace(good, sort_state=True),
            replace(good, active_country_index=True),
            replace(good, selected_division_index=True),
            replace(good, human_competition_id=0),
            replace(good, division_candidates=tuple(
                (((999, "not-original"),) if i == 0 else row)
                for i, row in enumerate(good.division_candidates))),
        ):
            with self.subTest(altered=altered), self.assertRaises(ManagementPresentationError):
                bridge(state).source_selected_league_current_form_rows(altered)

    def test_secondary_and_truncated_calendar_fail_without_original_ui_fallback(self):
        state, selected = nonpl_ready()
        state.clubs[11].team_category_code = 2
        with self.assertRaisesRegex(ManagementPresentationError, "secondary"):
            bridge(state).source_selected_league_current_form_rows(selected)
        state, selected = nonpl_ready()
        state.competitions[2].scheduled_matchday_count = 4
        with self.assertRaisesRegex(ManagementPresentationError, "fixture count"):
            bridge(state).source_selected_league_current_form_rows(selected)
        state, selected = nonpl_ready()
        state.primary_schedule_shadow.days[date(2000, 8, 24)][0].wrapper_link_state = "unknown"
        with self.assertRaisesRegex(ManagementPresentationError, "wrapper"):
            bridge(state).source_selected_league_current_form_rows(selected)

    def test_read_only_selection_and_source_results(self):
        state, selected = nonpl_ready()
        old_days = dict(state.primary_schedule_shadow.days)
        old_results = dict(state.procedural_leagues[(2, 0)].results)
        owner = bridge(state)
        first = owner.source_selected_league_current_form_rows(selected)
        self.assertEqual(first, owner.source_selected_league_current_form_rows(selected))
        self.assertEqual(old_days, state.primary_schedule_shadow.days)
        self.assertEqual(old_results, state.procedural_leagues[(2, 0)].results)


if __name__ == "__main__":
    unittest.main()

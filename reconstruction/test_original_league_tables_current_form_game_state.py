"""Read-only primary Current Form GameState source validation tests."""
from datetime import date, timedelta
from types import SimpleNamespace as Obj
import unittest

from original_league_tables_current_form import OriginalCurrentFormSourceError
from original_league_tables_current_form_game_state import (
    source_qualified_primary_current_form_from_game_state as bridge,
)

D = date(2000, 9, 5)
TOK = ("league", 4, 0, 1)


def scenario(*, results=False):
    fixture = Obj(node_token=TOK, home_club_id=1, away_club_id=2)
    result = Obj(node_token=TOK, home_goals=2, away_goals=1)
    entry = Obj(
        competition_id=4, competition_context=0, node_kind="league_match",
        node_token=TOK,
        participant_0_ref=Obj(direct_club_id=1),
        participant_1_ref=Obj(direct_club_id=2),
        side_club_cache=(1, 2),
        payload_filter_bits=1 if results else 0,
        wrapper_link_state="clear",
    )
    live = Obj(competition_id=4, competition_context=0,
               club_ids=(1, 2), fixtures={TOK: fixture},
               results={TOK: result} if results else {})
    state = Obj(
        competitions={4: Obj(runtime_kind="league", parent_competition_id=None,
                              country_region_id=26, scheduled_matchday_count=1,
                              uses_secondary_schedule_container=False)},
        procedural_leagues={(4, 0): live},
        clubs={1: Obj(team_category_code=1, country_id=26, short_name="Zeta"),
               2: Obj(team_category_code=1, country_id=26, short_name="Alpha")},
        club_competition_membership={1: 4, 2: 4},
        primary_schedule_shadow=Obj(days={D: (entry,)}),
        primary_schedule_end_date=D + timedelta(days=400),
        calendar=Obj(current_date=D),
    )
    return state, entry, live


class PrimaryGameStateCurrentFormTests(unittest.TestCase):
    def test_clean_source_unplayed_original_zero_zero_is_native_draw(self):
        state, _, _ = scenario()
        rows = {row.club_id: row for row in bridge(state, competition_id=4)}
        self.assertEqual(rows[1].score, 1)
        self.assertEqual(rows[2].score, 1)
        self.assertEqual(rows[1].form_result_labels, (" ", " ", " ", " ", " ", "D"))

    def test_played_exact_shadow_and_live_result(self):
        state, _, _ = scenario(results=True)
        rows = bridge(state, competition_id=4)
        self.assertEqual([(row.club_id, row.score) for row in rows], [(1, 3), (2, 0)])
        self.assertEqual(rows[0].form_result_labels[-1], "W")

    def test_refuses_truncated_but_self_consistent_league_history(self):
        state, _, live = scenario(results=True)
        # Same one fixture, same one source head and result, but original
        # root League defines two scheduled rounds rather than one.
        state.competitions[4].scheduled_matchday_count = 2
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "fixture count"):
            bridge(state, competition_id=4)
        state, _, _ = scenario()
        del state.competitions[4].scheduled_matchday_count
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "scheduled matchday count"):
            bridge(state, competition_id=4)
        state, _, _ = scenario()
        state.competitions[4].scheduled_matchday_count = True
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "scheduled matchday count"):
            bridge(state, competition_id=4)

    def test_rejects_result_flag_divergence_in_both_directions(self):
        state, entry, live = scenario(results=True)
        entry.payload_filter_bits = 0
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "played bit"):
            bridge(state, competition_id=4)
        state, entry, live = scenario()
        entry.payload_filter_bits = 1
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "played bit"):
            bridge(state, competition_id=4)

    def test_rejects_secondary_modes_and_container(self):
        state, _, _ = scenario()
        state.clubs[2].team_category_code = 2
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "secondary"):
            bridge(state, competition_id=4)
        state, _, _ = scenario()
        state.competitions[4].uses_secondary_schedule_container = True
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "primary container"):
            bridge(state, competition_id=4)

    def test_rejects_nonroot_and_cross_country_source_members(self):
        state, _, _ = scenario()
        state.competitions[4].parent_competition_id = 3
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "root League"):
            bridge(state, competition_id=4)
        state, _, _ = scenario()
        state.clubs[1].country_id = 9
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "member country"):
            bridge(state, competition_id=4)
        state, _, _ = scenario()
        state.competitions[4].country_region_id = None
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "root League"):
            bridge(state, competition_id=4)

    def test_rejects_missing_history_members_or_source_sides(self):
        state, entry, live = scenario()
        state.club_competition_membership[2] = 9
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "membership"):
            bridge(state, competition_id=4)
        state, entry, live = scenario()
        entry.side_club_cache = (None, 2)
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "Side cache"):
            bridge(state, competition_id=4)
        state, entry, live = scenario()
        live.fixtures[("missing",)] = Obj(node_token=("missing",), home_club_id=1, away_club_id=2)
        # An extra registry fixture fails the newly required source-season
        # completeness check before the subsequent shadow identity check.
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "fixture count"):
            bridge(state, competition_id=4)

    def test_rejects_unknown_flags_and_wrapper_while_preserving_link_exclusion(self):
        state, entry, _ = scenario()
        entry.payload_filter_bits = None
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "status bits"):
            bridge(state, competition_id=4)
        state, entry, _ = scenario()
        entry.wrapper_link_state = "unknown"
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "wrapper"):
            bridge(state, competition_id=4)
        state, entry, _ = scenario()
        entry.wrapper_link_state = "linked"
        self.assertEqual([r.score for r in bridge(state, competition_id=4)], [0, 0])

    def test_rejects_non_root_context_and_expired_history(self):
        state, _, _ = scenario()
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "context"):
            bridge(state, competition_id=4, competition_context=1)
        state.primary_schedule_end_date = D
        with self.assertRaisesRegex(OriginalCurrentFormSourceError, "window"):
            bridge(state, competition_id=4)

    def test_read_only(self):
        state, entry, live = scenario(results=True)
        original_days = dict(state.primary_schedule_shadow.days)
        original_results = dict(live.results)
        bridge(state, competition_id=4)
        self.assertEqual(state.primary_schedule_shadow.days, original_days)
        self.assertEqual(live.results, original_results)
        self.assertEqual(entry.payload_filter_bits, 1)


if __name__ == "__main__":
    unittest.main()

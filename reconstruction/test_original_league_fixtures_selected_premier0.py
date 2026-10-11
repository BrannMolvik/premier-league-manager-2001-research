"""Original 373-head selected fixed Premier0 fixtures, source-derived contracts.

Scores, club names and calendar are synthetic *test-only* source-shape data.
The current real human is always Southport349 in original Conference7.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from types import SimpleNamespace
import unittest

from gate13_management_source_data import (
    ManagementPresentationError, ManagementSourceDataBridge,
)
from original_league_fixtures_presenter import build_league_fixtures_snapshot
from original_league_fixtures_selected_premier0 import (
    SourceSelectedPremierFixturesError,
    source_qualified_selected_premier0_league_fixtures,
)
from test_original_league_fixtures_selected_source import context_for
from test_original_league_tables_selected_premier0 import prepared_state


def complete_state():
    state = prepared_state()
    # Synthetic selector definitions omit the original Premier0 calendar count;
    # supply the verified 38-matchday source shape without relaxing production.
    state.competitions[0].scheduled_matchday_count = 38
    start = date(2000, 8, 2)
    per_day = {}
    source = state.premier_league
    for fixture in source.fixtures.values():
        matchday = start + timedelta(days=fixture.round_index)
        token = ("fixed_league_match", 0, 0, fixture.id)
        node = SimpleNamespace(
            competition_id=0, competition_context=0,
            node_kind="fixed_league_match", node_token=token,
            participant_0_ref=SimpleNamespace(direct_club_id=fixture.home_club_id),
            participant_1_ref=SimpleNamespace(direct_club_id=fixture.away_club_id),
            side_club_cache=(fixture.home_club_id, fixture.away_club_id),
            payload_filter_bits=0,
        )
        per_day.setdefault(matchday, []).append(node)
    for day, nodes in per_day.items():
        prior = state.primary_schedule_shadow.days.get(day, ())
        state.primary_schedule_shadow.days[day] = tuple(prior) + tuple(nodes)
    return state


def selected(state):
    first = context_for(state)
    assert first.selected_competition_id == 7
    result = first.accept_native_radio_event(9)
    assert result.selected_competition_id == 0
    return result


def source(state, context):
    return source_qualified_selected_premier0_league_fixtures(
        human_club_id=349, selection=context, clubs=state.clubs,
        membership=state.club_competition_membership,
        competitions=state.competitions, premier_league=state.premier_league,
        days=state.primary_schedule_shadow.days,
    )


def bridge(state):
    return ManagementSourceDataBridge(SimpleNamespace(
        state=state, human=SimpleNamespace(club_id=349),
    ))


class OriginalSelectedPremier0FixturesTests(unittest.TestCase):
    def test_real_native_other_league_selector_source_complete_grid(self):
        state = complete_state()
        context = selected(state)
        actual = source(state, context)
        self.assertEqual(actual.competition_id, 0)
        self.assertEqual(len(actual.member_club_ids), 20)
        self.assertEqual(len(actual.fixtures_in_source_order), 380)
        self.assertEqual((actual.scheduled_matchday_count,
                          actual.schedule_cycle_count, actual.matrix_layer_count),
                         (38, 2, 1))
        self.assertEqual(state.club_competition_membership[349], 7)
        self.assertNotIn(349, actual.member_club_ids)
        day = date(2000, 8, 2)
        match = next(row for row in actual.fixtures_in_source_order
                     if row.fixture_id == 0)
        self.assertEqual(match.scheduled_date, day)
        self.assertEqual((match.home_goals, match.away_goals), (2, 1))
        self.assertTrue(match.played)
        self.assertEqual(len({(row.home_club_id, row.away_club_id)
                              for row in actual.fixtures_in_source_order}), 380)

    def test_source_bridge_and_original_visible_matrix_keep_selected_fixed_identity(self):
        state = complete_state()
        view = bridge(state).source_selected_league_fixtures_grid_source(selected(state))
        self.assertEqual(view.competition_id, 0)
        self.assertEqual(len(view.fixtures_in_source_order), 380)
        self.assertEqual(view.fixtures_in_source_order[0].fixture_id, 0)
        self.assertIsNone(view.fixtures_in_source_order[0].source_node_token)
        self.assertEqual(view.fixtures_in_source_order[0].scheduled_date,
                         date(2000, 8, 2))
        snapshot = build_league_fixtures_snapshot(view)
        self.assertEqual(snapshot.competition_id, 0)
        self.assertEqual(len(snapshot.member_club_ids), 20)
        # Native 12-column viewport hides the away club at the far right;
        # select the source-available second page rather than forging visibility.
        paged = build_league_fixtures_snapshot(view, column_offset=8)
        self.assertTrue(any(cell.text == "2:1" for cell in paged.cells))
        self.assertEqual(bridge(state).league_fixtures_grid_source().competition_id, 7)

    def test_original_373_head_encounter_order_precedes_fixture_id_order(self):
        state = complete_state()
        target_date = date(2000, 8, 2)
        bucket = state.primary_schedule_shadow.days[target_date]
        state.primary_schedule_shadow.days[target_date] = tuple(reversed(bucket))
        actual = source(state, selected(state))
        from_day = tuple(row.fixture_id for row in actual.fixtures_in_source_order
                         if row.scheduled_date == target_date)
        native_source = tuple(
            entry.node_token[-1] for entry in state.primary_schedule_shadow.days[target_date]
            if entry.competition_id == 0
        )
        self.assertEqual(from_day, native_source)
        self.assertNotEqual(from_day, tuple(sorted(from_day)))

    def test_original_status_bit20_excludes_only_source_filtered_match(self):
        state = complete_state()
        day = date(2000, 8, 2)
        bucket = list(state.primary_schedule_shadow.days[day])
        target = next(i for i, entry in enumerate(bucket) if entry.competition_id == 0)
        flagged = SimpleNamespace(**vars(bucket[target]))
        flagged.payload_filter_bits = 0x20
        bucket[target] = flagged
        state.primary_schedule_shadow.days[day] = tuple(bucket)
        result = source(state, selected(state))
        self.assertEqual(len(result.fixtures_in_source_order), 379)
        self.assertNotIn(flagged.node_token[-1],
                         tuple(row.fixture_id for row in result.fixtures_in_source_order))

    def test_annual_premier0_native_league_match_tokens_use_true_live_owner(self):
        """Second-season original procedural League0 emits league_match IDs."""
        state = complete_state()
        for day, bucket in tuple(state.primary_schedule_shadow.days.items()):
            updated = []
            for entry in bucket:
                if entry.competition_id == 0:
                    node = SimpleNamespace(**vars(entry))
                    node.node_kind = "league_match"
                    node.node_token = ("league_match", 0, 0, entry.node_token[-1])
                    updated.append(node)
                else:
                    updated.append(entry)
            state.primary_schedule_shadow.days[day] = tuple(updated)
        annual = source(state, selected(state))
        self.assertEqual(len(annual.fixtures_in_source_order), 380)
        self.assertEqual(annual.fixtures_in_source_order[0].node_token[0],
                         "league_match")
        self.assertEqual(annual.fixtures_in_source_order[0].fixture_id, 0)
        # A single season cannot claim two mutually incompatible native node
        # producers without stronger original evidence.
        first_day = date(2000, 8, 2)
        first_bucket = list(state.primary_schedule_shadow.days[first_day])
        bad = SimpleNamespace(**vars(first_bucket[0]))
        bad.node_kind = "fixed_league_match"
        bad.node_token = ("fixed_league_match", 0, 0, bad.node_token[-1])
        first_bucket[0] = bad
        state.primary_schedule_shadow.days[first_day] = tuple(first_bucket)
        with self.assertRaisesRegex(SourceSelectedPremierFixturesError,
                                    "mixes incompatible"):
            source(state, selected(state))

    def test_missing_duplicate_foreign_or_bad_status_source_cannot_fake_full_calendar(self):
        state = complete_state()
        context = selected(state)
        day = date(2000, 8, 2)
        original = state.primary_schedule_shadow.days[day]
        state.primary_schedule_shadow.days[day] = original[1:]
        with self.assertRaisesRegex(SourceSelectedPremierFixturesError, "lacks fixed"):
            source(state, context)
        state.primary_schedule_shadow.days[day] = original + (original[0],)
        with self.assertRaisesRegex(SourceSelectedPremierFixturesError, "duplicat"):
            source(state, context)
        state.primary_schedule_shadow.days[day] = original
        foreign = SimpleNamespace(**vars(original[0]))
        foreign.participant_0_ref = SimpleNamespace(direct_club_id=9988)
        state.primary_schedule_shadow.days[day] = (foreign,) + original[1:]
        with self.assertRaisesRegex(SourceSelectedPremierFixturesError, "Side pointers"):
            source(state, context)
        invalid = SimpleNamespace(**vars(original[0]))
        invalid.payload_filter_bits = None
        state.primary_schedule_shadow.days[day] = (invalid,) + original[1:]
        with self.assertRaisesRegex(SourceSelectedPremierFixturesError, "status bits"):
            source(state, context)

    def test_invalid_real_membership_source_owner_and_selection_all_fail_closed(self):
        state = complete_state()
        choice = selected(state)
        state.club_competition_membership[1019] = 2
        with self.assertRaisesRegex(SourceSelectedPremierFixturesError, "DBRClub"):
            source(state, choice)
        state = complete_state()
        choice = selected(state)
        state.premier_league.fixtures.pop(379)
        with self.assertRaisesRegex(SourceSelectedPremierFixturesError, "380 source"):
            source(state, choice)
        state = complete_state()
        choice = selected(state)
        state.clubs[1005].short_name = "🦊"
        with self.assertRaisesRegex(SourceSelectedPremierFixturesError, "CP1252"):
            source(state, choice)
        state = complete_state()
        choice = selected(state)
        for corrupt in (replace(choice, active_country_index=True),
                        replace(choice, selected_league_indices=(False,) * 8)):
            with self.subTest(corrupt=corrupt):
                with self.assertRaises(SourceSelectedPremierFixturesError):
                    source(state, corrupt)

    def test_bridge_refuses_missing_calendar_and_preserves_foreign_nonpl_dispatch(self):
        state = complete_state()
        selected_prem = selected(state)
        del state.primary_schedule_shadow
        with self.assertRaises(ManagementPresentationError):
            bridge(state).source_selected_league_fixtures_grid_source(selected_prem)
        state = complete_state()
        other = context_for(state).accept_native_radio_event(10)
        rows = bridge(state).source_selected_league_fixtures_grid_source(other)
        self.assertEqual(rows.competition_id, 2)
        self.assertEqual(tuple(row.source_node_token for row in rows.fixtures_in_source_order),
                         (("alt", 1), ("alt", 0)))


if __name__ == "__main__":
    unittest.main()

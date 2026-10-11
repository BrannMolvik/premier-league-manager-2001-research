"""Source-verified fixed/annual Premier0 Current Form adapter boundaries."""
from datetime import date, timedelta
from types import SimpleNamespace as Obj
import unittest

from competition_state import PremierLeagueState, ProceduralPremierFixture
from original_league_tables_current_form import OriginalCurrentFormSourceError as Error
from original_league_tables_current_form_premier0 import (
    source_qualified_premier0_current_form_from_game_state as form,
)

D = date(2000, 8, 2)


def scenario():
    ids = tuple(range(1000, 1020))
    ordered_pairs = tuple((h, a) for h in ids for a in ids if h != a)
    fixtures = tuple(ProceduralPremierFixture(
        id=i, round_index=i % 38, home_club_id=h, away_club_id=a
    ) for i, (h, a) in enumerate(ordered_pairs))
    live = PremierLeagueState(fixtures)
    live.record_result(0, 2, 1)
    by_date = {}
    for fixture in fixtures:
        kind = "fixed_league_match"
        node = Obj(
            competition_id=0, competition_context=0, node_kind=kind,
            node_token=(kind, 0, 0, fixture.id),
            participant_0_ref=Obj(direct_club_id=fixture.home_club_id),
            participant_1_ref=Obj(direct_club_id=fixture.away_club_id),
            side_club_cache=(fixture.home_club_id, fixture.away_club_id),
            payload_filter_bits=1 if fixture.id == 0 else 0,
            wrapper_link_state="clear",
        )
        by_date.setdefault(D+timedelta(days=fixture.round_index), []).append(node)
    return Obj(
        competitions={0: Obj(runtime_kind_code=1,parent_competition_id=None,
                             country_region_id=26, scheduled_matchday_count=38,
                             uses_secondary_schedule_container=False)},
        clubs={cid: Obj(country_id=26, team_category_code=1, short_name=f"PL{cid}")
               for cid in ids},
        club_competition_membership={cid:0 for cid in ids},
        premier_league=live,
        calendar=Obj(current_date=D),
        primary_schedule_end_date=D+timedelta(days=373),
        primary_schedule_shadow=Obj(days={d:tuple(row) for d,row in by_date.items()}),
    )


class OriginalPremierCurrentFormTests(unittest.TestCase):
    def test_native_original_source_complete_default_premier0(self):
        state=scenario()
        rows={row.club_id:row for row in form(state)}
        self.assertEqual(len(rows),20)
        self.assertEqual(rows[1000].score,3)
        self.assertEqual(rows[1000].form_result_labels[-1],"W")
        self.assertEqual(rows[1001].score,0)
        self.assertEqual(rows[1001].form_result_labels[-1],"L")

    def test_original_unplayed_zero_zero_on_current_day_not_discarded(self):
        state=scenario()
        state.premier_league.results.clear()
        day = state.primary_schedule_shadow.days[D]
        day[0].payload_filter_bits=0
        rows={row.club_id:row for row in form(state)}
        self.assertEqual(rows[1000].score,1)
        self.assertEqual(rows[1001].score,1)
        self.assertEqual(rows[1000].form_result_labels[-1],"D")

    def test_refuses_stale_match_completion_flags(self):
        state=scenario()
        state.primary_schedule_shadow.days[D][0].payload_filter_bits=0
        with self.assertRaisesRegex(Error,"played bit0"):form(state)
        state=scenario()
        state.premier_league.results.clear()
        with self.assertRaisesRegex(Error,"played bit0"):form(state)

    def test_refuses_secondary_calendar_or_foreign_club(self):
        state=scenario()
        state.competitions[0].uses_secondary_schedule_container=True
        with self.assertRaisesRegex(Error,"primary calendar"):form(state)
        state=scenario()
        state.clubs[1000].team_category_code=2
        with self.assertRaisesRegex(Error,"source calendar mode"):form(state)
        state=scenario()
        state.clubs[1000].country_id=33
        with self.assertRaisesRegex(Error,"foreign"):form(state)

    def test_refuses_incomplete_380_and_duplicate_native_nodes(self):
        state=scenario()
        state.premier_league.fixtures.pop(379)
        with self.assertRaisesRegex(Error,"380-fixture"):form(state)
        state=scenario()
        row=list(state.primary_schedule_shadow.days[D])
        row.append(row[0])
        state.primary_schedule_shadow.days[D]=tuple(row)
        with self.assertRaisesRegex(Error,"duplicated"):form(state)

    def test_refuses_unverified_side_and_wrapper(self):
        state=scenario()
        state.primary_schedule_shadow.days[D][0].side_club_cache=(1000,9999)
        with self.assertRaisesRegex(Error,"Side source"):form(state)
        state=scenario()
        state.primary_schedule_shadow.days[D][0].wrapper_link_state="unknown"
        with self.assertRaisesRegex(Error,"wrapper"):form(state)

    def test_refuses_mixed_original_first_and_annual_node_class(self):
        state=scenario()
        node=state.primary_schedule_shadow.days[D][0]
        node.node_kind="league_match"
        node.node_token=("league_match",0,0,0)
        with self.assertRaisesRegex(Error,"mixes"):form(state)

    def test_native_linked_event_never_counts_even_with_historical_scores(self):
        state=scenario()
        state.primary_schedule_shadow.days[D][0].wrapper_link_state="linked"
        rows={row.club_id:row for row in form(state)}
        # The synthetic full season has other same-day unplayed fixtures.
        # The original source skips the linked match, not the whole day.
        self.assertNotIn(("fixed_league_match",0,0,0),rows[1000].matching_tokens)
        self.assertNotIn(("fixed_league_match",0,0,0),rows[1001].matching_tokens)

    def test_read_only_of_original_runtime_state(self):
        state=scenario()
        original_result=dict(state.premier_league.results)
        original_days=dict(state.primary_schedule_shadow.days)
        form(state)
        self.assertEqual(state.premier_league.results,original_result)
        self.assertEqual(state.primary_schedule_shadow.days,original_days)

if __name__ == "__main__":
    unittest.main()

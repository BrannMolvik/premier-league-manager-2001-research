"""Original Current Form live primary-source adapter — guarded, not a GUI test."""
from dataclasses import replace
from datetime import date, timedelta
from types import SimpleNamespace
import unittest

from original_league_tables_current_form_live import (
    OriginalLiveCurrentFormSourceError as Error,
    source_qualified_primary_current_form as source_form,
)
from procedural_league_state import LiveProceduralLeagueState, ProceduralLeagueFixture

D = date(2000, 9, 10)
T = ("native-league", 3, 1)


def setup(*, mode_a=1, result=None, bits=0, wrapper="clear",
          incomplete=False, cache=None, side_a=101):
    live = LiveProceduralLeagueState(
        competition_id=3, competition_context=0,
        fixtures={T: ProceduralLeagueFixture(T, 101, 102)},
        club_ids=(101, 102),
    )
    if result is not None:
        live.record_result(T, *result)
    entry = SimpleNamespace(
        competition_id=3, competition_context=0, node_kind="league_match",
        node_token=T, payload_filter_bits=bits, wrapper_link_state=wrapper,
        side_club_cache=cache,
        participant_0_ref=SimpleNamespace(direct_club_id=side_a),
        participant_1_ref=SimpleNamespace(direct_club_id=102),
    )
    kwargs = dict(
        selected_country_id=26, competition_id=3, current_date=D,
        membership={101:3,102:3},
        clubs={
            101: SimpleNamespace(country_id=26,short_name="Zeta",team_category_code=mode_a),
            102: SimpleNamespace(country_id=26,short_name="Alpha",team_category_code=1),
        },
        competitions={3: SimpleNamespace(
            runtime_kind_code=1,parent_competition_id=None,
            country_region_id=26,scheduled_matchday_count=2 if incomplete else 1,
        )},
        procedural_leagues={(3,0):live},
        primary_shadow=SimpleNamespace(days={D:(entry,)}),
    )
    return kwargs


class CurrentFormLiveSourceTests(unittest.TestCase):
    def test_original_primary_unplayed_same_day_scored_as_native_draw(self):
        rows=source_form(**setup(bits=0))
        self.assertEqual([(r.club_id,r.score,r.form_result_labels[-1]) for r in rows],
                         [(102,1,"D"),(101,1,"D")])

    def test_original_primary_played_winner_and_loss(self):
        rows=source_form(**setup(result=(2,1),bits=1))
        self.assertEqual([(r.club_id,r.score,r.form_result_labels[-1]) for r in rows],
                         [(101,3,"W"),(102,0,"L")])

    def test_original_primary_status_bits_fail_closed(self):
        for payload in (
            setup(result=(2,1),bits=0),
            setup(result=None,bits=1),
            setup(result=None,bits=None),
            setup(result=None,bits=0x80),
            setup(result=None,bits=0,wrapper="unknown"),
            setup(result=None,bits=0,side_a=None),
            setup(result=None,bits=0,cache=(101,103)),
            setup(result=None,bits=0,incomplete=True),
            setup(result=None,bits=0,mode_a=2),
            setup(result=None,bits=0,mode_a=3),
        ):
            with self.subTest(payload=payload["clubs"][101].team_category_code,
                              bits=payload["primary_shadow"].days[D][0].payload_filter_bits,
                              link=payload["primary_shadow"].days[D][0].wrapper_link_state):
                with self.assertRaises(Error):
                    source_form(**payload)

    def test_source_competition_and_calendar_membership_not_replaced(self):
        x=setup()
        x["membership"][102]=0
        with self.assertRaises(Error):source_form(**x)
        x=setup()
        x["primary_shadow"].days={}
        with self.assertRaises(Error):source_form(**x)
        x=setup()
        x["primary_shadow"].days[D][0].competition_id=7
        with self.assertRaises(Error):source_form(**x)

    def test_skip_future_unplayed_original_match_by_current_day(self):
        x=setup()
        x["current_date"]=D-timedelta(days=1)
        self.assertEqual([r.score for r in source_form(**x)],[0,0])

if __name__=="__main__":
    unittest.main()

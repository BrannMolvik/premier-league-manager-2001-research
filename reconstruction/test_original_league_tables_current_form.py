"""Source-derived native Current Form candidate/kernel tests, NOT GUI acceptance."""
from dataclasses import replace
from datetime import date, timedelta
import unittest

from original_league_tables_current_form import (
    OriginalCurrentFormSourceError as Error,
    SourceCurrentFormClub as Club,
    SourceCurrentFormMatch as Match,
    source_qualified_current_form_ranking as ranked,
)

D = date(2000, 9, 5)
C = (Club(1, b"Zeta", 0), Club(2, b"Alpha", 0))


def m(n, *, h=1, a=2, hg=0, ag=0, status=1, secondary=False, link=0, league=4):
    return Match(("native", n), league, h, a, secondary, status, link, hg, ag)


def run(primary=None, secondary=None, members=C, on=D):
    return ranked(competition_id=4, current_date=on, members=members,
                  primary_days=primary or {}, secondary_days=secondary or {})


class OriginalCurrentFormTests(unittest.TestCase):
    def test_win_loss_draw_and_original_name_tie(self):
        rows = run({D: (m(1, hg=2, ag=1),), D-timedelta(days=2): (m(2, hg=1, ag=1),)})
        self.assertEqual([(r.club_id, r.score) for r in rows], [(1, 4), (2, 1)])
        self.assertEqual(rows[0].matching_tokens, (("native", 1), ("native", 2)))
        self.assertEqual(rows[0].form_result_labels, (" ", " ", " ", " ", "D", "W"))
        self.assertEqual(rows[1].form_result_labels, (" ", " ", " ", " ", "D", "L"))
        self.assertEqual([r.club_id for r in run()], [2, 1])

    def test_unplayed_0_0_eligible_and_not_automatically_skipped(self):
        self.assertEqual([r.score for r in run({D: (m(1, status=0),)})], [1, 1])
        self.assertEqual(
            [r.form_result_labels[-1] for r in run({D: (m(1, status=0),)})],
            ["D", "D"],
        )

    def test_secondary_uses_per_club_mode_not_global_mode(self):
        members = (Club(1, b"Beta", 2), Club(2, b"Alpha", 0))
        rows = run({D: (m(1, hg=0, ag=3),)}, {D: (m(2, hg=4, ag=0, secondary=True),)}, members)
        self.assertEqual([(r.club_id, r.score) for r in rows], [(2, 3), (1, 3)])
        self.assertEqual(rows[0].matching_tokens, (("native", 1),))
        self.assertEqual(rows[1].matching_tokens, (("native", 2),))
        self.assertEqual([r.score for r in run({D: (m(1, hg=1, ag=0),)}, {},
            (Club(1, b"Beta", 3), Club(2,b"Alpha", 1)))], [0, 0])

    def test_original_first_eligible_same_day_and_six_day_cap(self):
        days={D-timedelta(days=i): (m(i*2, hg=1,ag=0),m(i*2+1,hg=0,ag=4))
              for i in range(8)}
        rows=run(days)
        self.assertEqual([(r.club_id,r.score,len(r.matching_tokens)) for r in rows],
                         [(1,18,6),(2,0,6)])
        self.assertEqual(rows[0].matching_tokens, tuple(("native", i*2) for i in range(6)))
        self.assertEqual(rows[0].form_result_labels, ("W",) * 6)
        self.assertEqual(rows[1].form_result_labels, ("L",) * 6)

    def test_native_strict_flags_wrapper_and_other_competition(self):
        rows=run({D: (m(1, status=0x20),m(2,status=0x40),m(3,link=3),m(4,league=9),m(5,hg=0,ag=1))})
        self.assertEqual([(r.club_id,r.score) for r in rows], [(2,3),(1,0)])
        self.assertEqual(rows[1].matching_tokens, (("native",5),))

    def test_original_native_wdl_alignment_after_broken_date_history(self):
        # Original LeagueMatch winner getter, same calendar day exclusion,
        # oldest-left six-cell buffer with missing leading slots as spaces.
        dates = {
            D: (m(10, hg=0, ag=0),),
            D-timedelta(days=3): (m(20, hg=3, ag=0),),
            D-timedelta(days=6): (m(30, hg=0, ag=4),),
        }
        rows = {row.club_id: row for row in run(dates)}
        self.assertEqual(rows[1].form_result_labels, (" ", " ", " ", "L", "W", "D"))
        self.assertEqual(rows[2].form_result_labels, (" ", " ", " ", "W", "L", "D"))
        self.assertEqual(rows[1].score, 4)
        self.assertEqual(rows[2].score, 4)

    def test_future_fixture_ignored(self):
        self.assertEqual([r.score for r in run({D+timedelta(days=1): (m(1,hg=2,ag=0),)})], [0,0])

    def test_cp1252_bytes_and_exact_equal_tie_fail_closed(self):
        a=Club(1,b"\xc9clair",0);b=Club(2,b"Zeta",0)
        self.assertEqual([r.club_id for r in run(members=(a,b))],[2,1])
        with self.assertRaisesRegex(Error, "qsort equality"):
            run(members=(a,Club(2,b"\xc9clair",0)))
        with self.assertRaisesRegex(Error, "CP1252"):
            run(members=(Club(1,"Zeta",0),b))

    def test_refuses_unknown_native_source(self):
        for args in [dict(primary={D: (m(1,secondary=True),)}),
                     dict(primary={D: (replace(m(1), source_status_bits=0x80),)}),
                     dict(primary={D: (replace(m(1),source_wrapper_link=-1),)}),
                     dict(primary={D: (replace(m(1),home_goals=40000),)}),
                     dict(primary={D: (replace(m(1),source_class="CupMatch"),)}),
                     dict(members=(C[0],C[0]))]:
            with self.subTest(args=args), self.assertRaises(Error):run(**args)
        with self.assertRaisesRegex(Error,"both source calendars"):
            run({D: (m(1),)}, {D: (replace(m(1),fixture_secondary_calendar=True),)})

if __name__ == '__main__': unittest.main()

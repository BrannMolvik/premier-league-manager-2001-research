import unittest

from match_clock import build_match_phase_plan
from match_events import BoundaryType


class MatchClockTests(unittest.TestCase):
    def test_normal_time_segments_match_original_loop(self):
        plan = build_match_phase_plan()
        self.assertEqual(
            plan.segment_minutes,
            (5,10,15,20,25,30,35,40,50,55,60,65,70,75,80,85),
        )
        self.assertEqual(
            [(b.minute, b.kind) for b in plan.boundaries],
            [(45, BoundaryType.HALF_TIME), (90, BoundaryType.FULL_TIME)],
        )
        self.assertEqual(plan.final_record_minute, 90)

    def test_extra_time_uses_two_two_segment_halves(self):
        plan = build_match_phase_plan(extra_time=True)
        self.assertEqual(plan.segment_minutes[-4:], (95, 100, 110, 115))
        self.assertEqual(
            [(b.minute, b.kind) for b in plan.boundaries],
            [
                (45, BoundaryType.HALF_TIME),
                (90, BoundaryType.EXTRA_TIME),
                (105, BoundaryType.EXTRA_TIME),
                (120, BoundaryType.FULL_TIME),
            ],
        )

    def test_penalties_without_extra_time_start_at_90(self):
        plan = build_match_phase_plan(extra_time=False, penalties=True)
        self.assertEqual(
            [(b.minute, b.kind) for b in plan.boundaries],
            [
                (45, BoundaryType.HALF_TIME),
                (90, BoundaryType.PENALTIES),
                (130, BoundaryType.FULL_TIME),
            ],
        )

    def test_penalties_after_extra_time_start_at_120(self):
        plan = build_match_phase_plan(extra_time=True, penalties=True)
        self.assertEqual(
            [(b.minute, b.kind) for b in plan.boundaries],
            [
                (45, BoundaryType.HALF_TIME),
                (90, BoundaryType.EXTRA_TIME),
                (105, BoundaryType.EXTRA_TIME),
                (120, BoundaryType.PENALTIES),
                (130, BoundaryType.FULL_TIME),
            ],
        )
        self.assertEqual(plan.final_record_minute, 130)


if __name__ == '__main__':
    unittest.main()

import unittest
from dataclasses import dataclass

from competition_startup import (
    europe_root_cup_candidate_ids,
    select_europe_root_cup_candidate,
)


@dataclass(frozen=True)
class Club:
    index: int
    country_id: int
    runtime_value_1c_source: int
    team_category_code: int


@dataclass(frozen=True)
class Country:
    id: int
    eu_status_flag: int


class RecordingRng:
    def __init__(self, value):
        self.value = value
        self.calls = []

    def randbelow(self, bound):
        self.calls.append(bound)
        if not 0 <= self.value < bound:
            raise AssertionError((self.value, bound))
        return self.value


class EuropeRootCupSelectorTests(unittest.TestCase):
    def test_candidate_filter_preserves_team_table_order(self):
        countries = (
            Country(26, 1),
            Country(31, 1),
            Country(11, 0),
        )
        clubs = (
            Club(1118, 26, 90000, 2),
            Club(1120, 26, 90000, 1),  # wrong runtime team category
            Club(1135, 31, 90000, 3),
            Club(1140, 31, 50000, 2),  # threshold is strictly greater
            Club(1141, 11, 90000, 2),  # country +0x18 is zero
        )

        self.assertEqual(
            europe_root_cup_candidate_ids(clubs, countries),
            (1118, 1135),
        )

    def test_excluded_entry_is_removed_before_selection(self):
        countries = (Country(26, 1),)
        clubs = (
            Club(1, 26, 60000, 2),
            Club(2, 26, 60000, 2),
        )
        self.assertEqual(
            europe_root_cup_candidate_ids(
                clubs,
                countries,
                excluded_club_id=1,
            ),
            (2,),
        )

    def test_original_count_minus_one_bound_makes_final_entry_unreachable(self):
        candidates = (1118, 1135, 1137, 1139, 1143, 1159, 1162)
        rng = RecordingRng(5)

        self.assertEqual(
            select_europe_root_cup_candidate(candidates, rng),
            1159,
        )
        self.assertEqual(rng.calls, [6])

    def test_empty_and_singleton_lists_consume_no_rng(self):
        class NoRng:
            def randbelow(self, bound):
                raise AssertionError(f"unexpected RNG({bound})")

        rng = NoRng()
        self.assertEqual(select_europe_root_cup_candidate((), rng), -1)
        self.assertEqual(select_europe_root_cup_candidate((42,), rng), 42)


if __name__ == "__main__":
    unittest.main()

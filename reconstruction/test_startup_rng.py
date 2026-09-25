import unittest
from dataclasses import dataclass

from startup_rng import (
    generated_name_rng_bound,
    generated_name_source_eligible,
    generated_name_source_ids,
    select_startup_youth_candidate,
    startup_youth_candidate_ids,
    startup_youth_target_count,
    startup_team_name_country_ids,
    startup_team_name_rng_bounds,
)


class RecordingRng:
    def __init__(self, values):
        self.values = list(values)
        self.calls = []

    def randbelow(self, bound):
        self.calls.append(bound)
        if not self.values:
            raise AssertionError(f"unexpected RNG({bound})")
        value = self.values.pop(0)
        if not 0 <= value < bound:
            raise AssertionError((value, bound))
        return value


@dataclass(frozen=True)
class Player:
    index: int
    club_id: int
    initial_flags: int = 0


class StartupYouthRngTests(unittest.TestCase):
    def test_option_target_count_preserves_exact_bounds_and_offsets(self):
        rng = RecordingRng([1, 0, 2])
        self.assertEqual(startup_youth_target_count(0, rng), 5)
        self.assertEqual(startup_youth_target_count(1, rng), 5)
        self.assertEqual(startup_youth_target_count(2, rng), 8)
        self.assertEqual(rng.calls, [2, 2, 3])

    def test_missing_or_unknown_option_consumes_no_rng(self):
        class NoRng:
            def randbelow(self, bound):
                raise AssertionError(f"unexpected RNG({bound})")
        rng = NoRng()
        self.assertEqual(startup_youth_target_count(None, rng), 4)
        self.assertEqual(startup_youth_target_count(99, rng), 4)

    def test_candidate_scan_uses_club_and_bit_three_in_source_order(self):
        players = (
            Player(7, 50, 0),
            Player(8, 50, 0x08),
            Player(9, 49, 0),
            Player(10, 50, 0x10),
        )
        self.assertEqual(startup_youth_candidate_ids(players, 50), (7, 10))

    def test_selection_uses_current_count_then_swap_deletes(self):
        candidates = [10, 20, 30, 40]
        rng = RecordingRng([1, 1])
        self.assertEqual(select_startup_youth_candidate(candidates, rng), 20)
        self.assertEqual(candidates, [10, 40, 30])
        self.assertEqual(select_startup_youth_candidate(candidates, rng), 40)
        self.assertEqual(candidates, [10, 30])
        self.assertEqual(rng.calls, [4, 3])


@dataclass(frozen=True)
class NamePlayer:
    index: int
    first_name: str
    surname: str
    nationality_id: int


@dataclass(frozen=True)
class Country:
    id: int
    nationality_id: int


@dataclass(frozen=True)
class Club:
    index: int
    name: str
    country_id: int
    team_category_code: int


class GeneratedNameRngTests(unittest.TestCase):
    def test_name_source_filter_preserves_original_literal_character_quirks(self):
        self.assertTrue(generated_name_source_eligible("Alan", "Smith"))
        self.assertFalse(generated_name_source_eligible("A.", "Smith"))
        self.assertFalse(generated_name_source_eligible("Alan", "Nash"))
        self.assertFalse(generated_name_source_eligible("Alan", "Bob"))
        self.assertFalse(generated_name_source_eligible("Alan", "Ab."))

    def test_nationality_source_vector_preserves_player_table_order(self):
        players = (
            NamePlayer(3, "Alan", "Smith", 7),
            NamePlayer(4, "A.", "Smith", 7),
            NamePlayer(5, "John", "Jones", 8),
            NamePlayer(6, "Eric", "Brown", 7),
        )
        self.assertEqual(generated_name_source_ids(players, 7), (3, 6))

    def test_name_rng_uses_nationality_count_only_when_above_ten(self):
        players = tuple(
            NamePlayer(i, "Alan", f"Smith{i}", 7 if i < 11 else 8)
            for i in range(15)
        )
        countries = (Country(26, 7), Country(31, 8))
        self.assertEqual(generated_name_rng_bound(26, countries, players), 11)
        self.assertEqual(generated_name_rng_bound(31, countries, players), 15)

    def test_country_minus_one_nationality_falls_back_to_index_26(self):
        players = tuple(
            NamePlayer(i, "Alan", f"Smith{i}", 26)
            for i in range(12)
        )
        countries = (Country(199, 0xFFFFFFFF),)
        self.assertEqual(generated_name_rng_bound(199, countries, players), 12)

    def test_team_name_loop_filter_and_two_draws_per_team(self):
        clubs = (
            Club(0, "Arsenal", 26, 1),
            Club(1, "!Spare", 26, 1),
            Club(2, "England", 26, 2),
            Club(3, "Chelsea", 31, 1),
        )
        players = tuple(
            [NamePlayer(i, "Alan", f"Smith{i}", 26) for i in range(12)]
            + [NamePlayer(100+i, "Eric", f"Brown{i}", 31) for i in range(13)]
        )
        countries = (Country(26, 26), Country(31, 31))
        self.assertEqual(startup_team_name_country_ids(clubs), (26, 31))
        self.assertEqual(
            startup_team_name_rng_bounds(clubs, countries, players),
            (12, 12, 13, 13),
        )


if __name__ == "__main__":
    unittest.main()

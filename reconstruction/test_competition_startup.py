import unittest
from dataclasses import dataclass

from competition_startup import (
    europe_root_cup_candidate_ids,
    ordered_cup_allocation_instructions,
    primary_cup_round_initialization_order,
    primary_mode0_cup_pairing_draw_count,
    primary_mode0_cup_round_team_counts,
    primary_mode0_root_initialization_order,
    replay_primary_mode0_ordered_competition_rng,
    replay_primary_mode0_competition_rng,
    replay_primary_mode0_pre_shuffle_state,
    select_europe_root_cup_candidate,
)
from match_schedule import MsvcCrtRng


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


@dataclass(frozen=True)
class Competition:
    id: int
    runtime_kind_code: int
    schedule_container_code: int
    parent_competition_id: int | None = None
    initialization_order_value: int = 0
    country_region_id: int = 0


@dataclass(frozen=True)
class Round:
    competition_id: int
    team_count: int
    id: int = 0
    type_code: int = 1
    scheduled_week: int = 0
    scheduled_weekday: int = 1
    source_competition_reference: int = 0xFFFFFFFF


@dataclass(frozen=True)
class CupAllocation:
    id: int
    destination_competition_id: int
    sequence_index: int
    instruction_type: int = 5
    source_reference: int = 0
    quantity: int = 0
    auxiliary: int = 0


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

    def test_primary_mode0_tail_replays_two_rng6_draws_in_root_order(self):
        countries = (
            Country(26, 1),
            Country(31, 1),
            Country(33, 1),
            Country(24, 1),
            Country(40, 1),
            Country(66, 1),
            Country(73, 1),
        )
        clubs = (
            Club(1118, 26, 90000, 2),
            Club(1135, 31, 90000, 2),
            Club(1137, 33, 75000, 2),
            Club(1139, 24, 60000, 2),
            Club(1143, 40, 60000, 2),
            Club(1159, 66, 55000, 2),
            Club(1162, 73, 100000, 2),
        )
        # This is the exact post-youth checkpoint from the synthetic
        # end-to-end startup replay in test_startup_rng.py.
        rng = MsvcCrtRng(0x2797444C)

        replay = replay_primary_mode0_competition_rng(rng, clubs, countries)

        self.assertEqual(
            replay.candidate_ids,
            (1118, 1135, 1137, 1139, 1143, 1159, 1162),
        )
        self.assertEqual(replay.champions_league_club_id, 1118)
        self.assertEqual(replay.uefa_cup_club_id, 1143)
        self.assertEqual(replay.draw_count, 2)
        self.assertEqual(rng.state, 0x5D07D526)

    def test_empty_and_singleton_lists_consume_no_rng(self):
        class NoRng:
            def randbelow(self, bound):
                raise AssertionError(f"unexpected RNG({bound})")

        rng = NoRng()
        self.assertEqual(select_europe_root_cup_candidate((), rng), -1)
        self.assertEqual(select_europe_root_cup_candidate((42,), rng), 42)


class PrimaryCupSchedulerStateTests(unittest.TestCase):
    def test_primary_cup_round_counts_exclude_secondary_and_non_cups(self):
        competitions = (
            Competition(9, 2, 1),
            Competition(10, 2, 0),
            Competition(170, 2, 2),
            Competition(0, 1, 1),
        )
        rounds = (
            Round(9, 4),
            Round(9, 2),
            Round(10, 8),
            Round(170, 16),
            Round(0, 20),
        )

        self.assertEqual(
            primary_mode0_cup_round_team_counts(competitions, rounds),
            (4, 2, 8),
        )
        self.assertEqual(
            primary_mode0_cup_pairing_draw_count(competitions, rounds),
            3 + 1 + 7,
        )

    def test_state_only_replay_adds_pairing_and_two_selector_calls(self):
        competitions = (Competition(9, 2, 1),)
        rounds = (Round(9, 4), Round(9, 2))
        countries = (
            Country(26, 1),
            Country(31, 1),
            Country(33, 1),
            Country(24, 1),
            Country(40, 1),
            Country(66, 1),
            Country(73, 1),
        )
        clubs = (
            Club(1118, 26, 90000, 2),
            Club(1135, 31, 90000, 2),
            Club(1137, 33, 75000, 2),
            Club(1139, 24, 60000, 2),
            Club(1143, 40, 60000, 2),
            Club(1159, 66, 55000, 2),
            Club(1162, 73, 100000, 2),
        )
        rng = MsvcCrtRng(0x2797444C)

        replay = replay_primary_mode0_pre_shuffle_state(
            rng,
            competitions,
            rounds,
            clubs,
            countries,
        )

        self.assertEqual(replay.primary_cup_round_count, 2)
        self.assertEqual(replay.cup_pairing_draw_count, 4)
        self.assertEqual(replay.europe_selector_draw_count, 2)
        self.assertEqual(replay.total_draw_count, 6)
        self.assertEqual(replay.state_entering_primary_shuffle, 0x0A7571CA)
        self.assertEqual(rng.state, 0x0A7571CA)

class OrderedCompetitionRngTests(unittest.TestCase):
    def test_small_country_root_qsort_resolves_spanish_equal_key_order(self):
        competitions = (
            Competition(31, 1, 1, None, 7, 73),
            Competition(32, 1, 1, None, 8, 73),
            Competition(33, 2, 1, None, 5, 73),
            Competition(34, 2, 1, None, 5, 73),
            Competition(95, 3, 1, None, 9, 73),
        )

        ordered = primary_mode0_root_initialization_order(
            competitions,
            (73,),
        )

        self.assertEqual(
            tuple(competition.id for competition in ordered),
            (33, 34, 31, 32, 95),
        )

    def test_cup_round_qsort_uses_child_league_date_for_minileague(self):
        rounds = (
            Round(9, 32, 201, 3, 0, 0, 14),
            Round(9, 28, 198, 2, 2, 3),
            Round(9, 16, 202, 3, 0, 0, 167),
            Round(14, 4, 224, 4, 11, 3),
            Round(167, 4, 910, 4, 21, 3),
        )

        ordered = primary_cup_round_initialization_order(9, rounds)

        self.assertEqual(
            tuple(round_definition.id for round_definition in ordered),
            (198, 201, 202),
        )

    def test_ordered_replay_places_selector_before_its_cup_rounds(self):
        countries = (
            Country(26, 1),
            Country(31, 1),
            Country(33, 1),
            Country(24, 1),
            Country(40, 1),
            Country(66, 1),
            Country(73, 1),
            Country(123, 1),
        )
        clubs = (
            Club(1118, 26, 90000, 2),
            Club(1135, 31, 90000, 2),
            Club(1137, 33, 75000, 2),
            Club(1139, 24, 60000, 2),
            Club(1143, 40, 60000, 2),
            Club(1159, 66, 55000, 2),
            Club(1162, 73, 100000, 2),
        )
        competitions = (
            Competition(9, 2, 1, None, 0, 123),
            Competition(10, 2, 1, None, 1, 123),
        )
        rounds = (
            Round(9, 4, 198, 2, 2, 3),
            Round(9, 2, 205, 1, 47, 3),
            Round(10, 6, 210, 2, 6, 4),
        )
        rng = MsvcCrtRng(0x12345678)

        replay = replay_primary_mode0_ordered_competition_rng(
            rng,
            competitions,
            rounds,
            clubs,
            countries,
        )

        self.assertEqual(
            tuple(
                (event.kind, event.competition_id, event.round_id, event.bounds)
                for event in replay.events
            ),
            (
                ("europe_selector", 9, None, (6,)),
                ("cup_round_shuffle", 9, 198, (4, 3, 2)),
                ("cup_round_shuffle", 9, 205, (2,)),
                ("europe_selector", 10, None, (6,)),
                ("cup_round_shuffle", 10, 210, (6, 5, 4, 3, 2)),
            ),
        )
        self.assertEqual(replay.total_draw_count, 11)
        self.assertEqual(replay.primary_cup_round_count, 3)
        self.assertEqual(replay.cup_pairing_draw_count, 9)
        self.assertEqual(replay.europe_selector_draw_count, 2)


if __name__ == "__main__":
    unittest.main()



class CupAllocationOrderingTests(unittest.TestCase):
    def test_small_equal_key_order_matches_crt_qsort(self):
        instructions = (
            CupAllocation(160, 23, 1, source_reference=21, quantity=18),
            CupAllocation(161, 23, 2, source_reference=22, quantity=18),
            CupAllocation(162, 23, 2, source_reference=24, quantity=5),
            CupAllocation(163, 23, 4, source_reference=83, quantity=5),
            CupAllocation(164, 23, 5, source_reference=24, quantity=13),
            CupAllocation(165, 23, 6, source_reference=83, quantity=13),
            CupAllocation(166, 23, 7, source_reference=25, quantity=10),
        )

        ordered = ordered_cup_allocation_instructions(23, instructions)

        self.assertEqual(
            tuple(instruction.id for instruction in ordered),
            (160, 162, 161, 163, 164, 165, 166),
        )

    def test_large_unique_sequence_order_is_ascending(self):
        instructions = tuple(
            CupAllocation(i, 10, 20 - i)
            for i in range(12)
        )

        ordered = ordered_cup_allocation_instructions(10, instructions)

        self.assertEqual(
            tuple(instruction.sequence_index for instruction in ordered),
            tuple(sorted(instruction.sequence_index for instruction in instructions)),
        )

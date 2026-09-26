import unittest
from dataclasses import dataclass

from competition_startup import (
    CupClubRefDescriptor,
    compare_cup_club_refs,
    europe_root_cup_candidate_ids,
    initial_competition_enumeration_club_ids,
    initial_dummy_league_sort_entries,
    initial_league_club_ids,
    initial_ranked_league_club_ids,
    msvc_crt_qsort,
    ordered_cup_allocation_instructions,
    primary_cup_round_initialization_order,
    primary_mode0_cup_pairing_draw_count,
    primary_mode0_cup_round_team_counts,
    primary_mode0_dummy_league_sort_draw_count,
    primary_mode0_dummy_league_sort_source_ids,
    primary_mode0_root_initialization_order,
    prepare_cup_knockout_round,
    rank_dummy_league_for_type5,
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
    short_name: str = ""
    competition_id: int = 0


@dataclass(frozen=True)
class HistoricalClub:
    index: int
    competition_id: int
    historical_competition_id: int
    historical_slot_index: int


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



class HistoricalCompetitionEnumerationTests(unittest.TestCase):
    def test_preferred_slot_collision_moves_displaced_club_to_first_empty(self):
        clubs = (
            HistoricalClub(10, 7, 7, 1),
            HistoricalClub(11, 7, 7, 1),
            HistoricalClub(12, 7, 7, 2),
        )

        self.assertEqual(
            initial_competition_enumeration_club_ids(clubs, 7),
            (10, 11, 12),
        )

    def test_out_of_range_slot_uses_first_empty_and_full_array_drops_extra(self):
        clubs = (
            HistoricalClub(20, 8, 8, 99),
            HistoricalClub(21, 8, 8, 1),
            HistoricalClub(22, 9, 8, 0),  # target history array only, not capacity
        )

        # Capacity is two because only clubs 20/21 are current members of 8.
        # 20 falls back to first empty, 21 takes slot 1. Club 22 then displaces
        # 20 from slot 0, but there is no empty slot for the displaced club.
        self.assertEqual(
            initial_competition_enumeration_club_ids(clubs, 8),
            (22, 21),
        )

    def test_only_target_historical_competition_contributes(self):
        clubs = (
            HistoricalClub(1, 5, 5, 0),
            HistoricalClub(2, 5, 6, 1),
            HistoricalClub(3, 5, 5, 2),
        )

        self.assertEqual(
            initial_competition_enumeration_club_ids(clubs, 5),
            (1, None, 3),
        )



class InitialLeagueOrderingTests(unittest.TestCase):
    def test_initial_membership_preserves_master_source_order(self):
        clubs = (
            Club(0, 26, 0, 0, "Zulu", 7),
            Club(1, 26, 0, 0, "Alpha", 3),
            Club(2, 26, 0, 0, "Bravo", 7),
            Club(3, 26, 0, 0, "Echo", 7),
        )

        self.assertEqual(initial_league_club_ids(clubs, 7), (0, 2, 3))

    def test_initial_ranking_uses_short_name_byte_order(self):
        clubs = (
            Club(0, 26, 0, 0, "Zulu", 7),
            Club(1, 26, 0, 0, "Alpha", 7),
            Club(2, 26, 0, 0, "Bravo", 7),
        )

        self.assertEqual(
            initial_ranked_league_club_ids(clubs, 7),
            (1, 2, 0),
        )


class LegacyCrtQsortTests(unittest.TestCase):
    def test_equal_small_range_uses_unstable_shortsort_rotation(self):
        self.assertEqual(
            msvc_crt_qsort((0, 1, 2, 3), lambda left, right: 0),
            (1, 2, 3, 0),
        )

    def test_equal_large_range_keeps_exact_middle_pivot_swap(self):
        self.assertEqual(
            msvc_crt_qsort(tuple(range(10)), lambda left, right: 0),
            (5, 1, 2, 3, 4, 0, 6, 7, 8, 9),
        )

    def test_mixed_values_sort_ascending(self):
        values = (4, 1, 4, 2, 3, 1, 0, 5, 2, 4, 3)
        ordered = msvc_crt_qsort(
            values,
            lambda left, right: (left > right) - (left < right),
        )
        self.assertEqual(ordered, tuple(sorted(values)))


class CupKnockoutPreparationTests(unittest.TestCase):
    def test_clubref_comparator_groups_type2_first(self):
        direct = CupClubRefDescriptor(type_code=0, direct_club_id=10)
        position_a = CupClubRefDescriptor(
            type_code=2,
            selector=3,
            competition_id=7,
            competition_context=0,
        )
        position_b = CupClubRefDescriptor(
            type_code=2,
            selector=1,
            competition_id=8,
            competition_context=0,
        )

        self.assertLess(compare_cup_club_refs(position_a, direct), 0)
        self.assertGreater(compare_cup_club_refs(direct, position_a), 0)
        self.assertLess(compare_cup_club_refs(position_a, position_b), 0)
        self.assertEqual(compare_cup_club_refs(direct, direct), 0)

    def test_knockout_round_uses_exact_qsort_then_split_half_pairs(self):
        class ZeroRng:
            def __init__(self):
                self.calls = []

            def randbelow(self, bound):
                self.calls.append(bound)
                return 0

        refs = tuple(
            CupClubRefDescriptor(type_code=0, direct_club_id=club_id)
            for club_id in range(4)
        )
        rng = ZeroRng()

        prepared = prepare_cup_knockout_round(refs, rng)

        self.assertEqual(rng.calls, [4, 3, 2])
        self.assertEqual(
            tuple(ref.direct_club_id for ref in prepared.shuffled_refs),
            (1, 2, 3, 0),
        )
        # All four records compare equal, so the CRT <=8 shortsort rotates the
        # shuffled block once more before the original split-half pairing.
        self.assertEqual(
            tuple(ref.direct_club_id for ref in prepared.sorted_refs),
            (2, 3, 0, 1),
        )
        self.assertEqual(
            tuple(
                (left.direct_club_id, right.direct_club_id)
                for left, right in prepared.pairs
            ),
            ((2, 0), (3, 1)),
        )

    def test_odd_synthetic_knockout_round_is_rejected(self):
        refs = tuple(
            CupClubRefDescriptor(type_code=0, direct_club_id=club_id)
            for club_id in range(3)
        )

        with self.assertRaises(ValueError):
            prepare_cup_knockout_round(refs, RecordingRng(0))


@dataclass(frozen=True)
class DummyPlayer:
    club_id: int
    current_raw: tuple[int, ...]
    positions: tuple[int, int, int]


class DummyLeagueLazySortTests(unittest.TestCase):
    def test_type5_small_dummy_ranking_is_stable_on_equal_scores(self):
        from competition_startup import DummyLeagueSortEntry

        entries = (
            DummyLeagueSortEntry(10, 100, 10),
            DummyLeagueSortEntry(11, 100, 10),
            DummyLeagueSortEntry(12, 90, 9),
        )

        class ZeroRng:
            def randbelow(self, bound):
                return 0

        ranked = rank_dummy_league_for_type5(entries, ZeroRng(), 3)

        self.assertEqual(
            tuple(entry.club_id for entry in ranked),
            (10, 11, 12),
        )

    def test_type5_ranking_uses_score_minus_roll(self):
        from competition_startup import DummyLeagueSortEntry

        entries = (
            DummyLeagueSortEntry(10, 100, 10),
            DummyLeagueSortEntry(11, 98, 9),
            DummyLeagueSortEntry(12, 95, 9),
        )

        class SequenceRng:
            def __init__(self):
                self.values = iter((9, 0, 0))

            def randbelow(self, bound):
                value = next(self.values)
                self.assert_bound = bound
                return value

        ranked = rank_dummy_league_for_type5(entries, SequenceRng(), 3)

        self.assertEqual(
            tuple((entry.club_id, entry.randomized_score) for entry in ranked),
            ((11, 98), (12, 95), (10, 91)),
        )

    def test_initial_sort_entry_uses_first_eleven_roster_players(self):
        clubs = (
            Club(10, 26, 0, 0, "Dummy", 5),
        )
        # Goalkeeper role with max raw skills caps 0x41E1D0 at 99.
        players = tuple(
            DummyPlayer(
                club_id=10,
                current_raw=(255,) * 17,
                positions=(1, 0, 0),
            )
            for _ in range(12)
        )

        entries = initial_dummy_league_sort_entries(5, clubs, players)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].club_id, 10)
        self.assertEqual(entries[0].base_score, 11 * 99)
        self.assertEqual(entries[0].rng_bound, (11 * 99) // 20)

    def test_primary_type5_dummy_sources_are_unique_and_count_members(self):
        competitions = (
            Competition(5, 3, 1),
            Competition(9, 2, 1),
        )
        instructions = (
            CupAllocation(1, 9, 1, 5, 5, 2),
            CupAllocation(2, 9, 2, 5, 5, 1),
        )
        clubs = (
            Club(10, 26, 0, 0, "A", 5),
            Club(11, 26, 0, 0, "B", 5),
        )

        self.assertEqual(
            primary_mode0_dummy_league_sort_source_ids(
                competitions,
                instructions,
            ),
            (5,),
        )
        self.assertEqual(
            primary_mode0_dummy_league_sort_draw_count(
                competitions,
                instructions,
                clubs,
            ),
            2,
        )


if __name__ == "__main__":
    unittest.main()

import unittest
from dataclasses import dataclass

from cup_runtime import materialize_primary_cup_runtime


@dataclass(frozen=True)
class Competition:
    id: int
    runtime_kind_code: int
    schedule_container_code: int = 0
    parent_competition_id: int | None = None
    initialization_order_value: int = 0
    country_region_id: int = 1


@dataclass(frozen=True)
class Round:
    id: int
    competition_id: int
    type_code: int
    team_count: int
    new_entrants: int
    scheduled_week: int
    scheduled_weekday: int
    source_competition_reference: int = 0xFFFFFFFF


@dataclass(frozen=True)
class Allocation:
    id: int
    destination_competition_id: int
    sequence_index: int
    instruction_type: int
    source_reference: int
    quantity: int
    auxiliary: int = 0


@dataclass(frozen=True)
class Club:
    index: int
    short_name: str
    competition_id: int
    historical_competition_id: int
    historical_slot_index: int
    country_id: int = 1
    runtime_value_1c_source: int = 0
    team_category_code: int = 1


@dataclass(frozen=True)
class Country:
    id: int
    eu_status_flag: int = 0


class IdentityRng:
    def randbelow(self, bound):
        return int(bound) - 1


class PrimaryCupRuntimeTests(unittest.TestCase):
    def _fixture(self):
        competitions = (
            Competition(20, 1, initialization_order_value=-1),
            Competition(50, 2, initialization_order_value=0),
            Competition(60, 2, initialization_order_value=1),
        )
        rounds = (
            Round(100, 50, 1, 4, 4, 1, 1),
            Round(101, 50, 1, 2, 0, 2, 1),
            Round(200, 60, 1, 2, 2, 3, 1),
        )
        allocations = (
            Allocation(1, 50, 1, 3, 20, 4),
            Allocation(2, 60, 1, 2, 50, 2, 0),
        )
        clubs = tuple(
            Club(
                index=club_id,
                short_name=f"Club {club_id}",
                competition_id=20,
                historical_competition_id=20,
                historical_slot_index=slot,
            )
            for slot, club_id in enumerate((10, 11, 12, 13))
        )
        return competitions, rounds, allocations, clubs, (Country(1),)

    def test_cross_cup_type2_transfer_is_injected_in_runtime_order(self):
        competitions, rounds, allocations, clubs, countries = self._fixture()

        result = materialize_primary_cup_runtime(
            IdentityRng(),
            competitions,
            rounds,
            clubs,
            countries,
            allocations,
        )

        self.assertEqual(
            tuple(cup.competition_id for cup in result.cups),
            (50, 60),
        )
        self.assertEqual(result.round_count, 3)
        self.assertEqual(result.type2_injected_ref_count, 2)
        self.assertEqual(result.dropped_ref_count, 0)
        self.assertEqual(result.ordered_bounds, (4, 3, 2, 2, 2))

        destination = result.cups[1]
        self.assertEqual(destination.injected_type2_instruction_ids, (2,))
        refs = dict(destination.runtime.round_participant_refs)[200]
        self.assertEqual(len(refs), 2)
        self.assertTrue(all(ref.type_code == 1 for ref in refs))
        self.assertTrue(all(ref.selector == 1 for ref in refs))
        self.assertEqual(
            {tuple(ref.reference_token) for ref in refs},
            {
                ("cup_result", 50, 100, 0),
                ("cup_result", 50, 100, 1),
            },
        )

    def test_participant_and_pairing_digests_are_repeatable(self):
        fixture = self._fixture()
        first = materialize_primary_cup_runtime(
            IdentityRng(),
            fixture[0],
            fixture[1],
            fixture[3],
            fixture[4],
            fixture[2],
        )
        second = materialize_primary_cup_runtime(
            IdentityRng(),
            fixture[0],
            fixture[1],
            fixture[3],
            fixture[4],
            fixture[2],
        )

        self.assertEqual(first.participant_sha256, second.participant_sha256)
        self.assertEqual(first.pairing_sha256, second.pairing_sha256)
        self.assertEqual(len(first.participant_sha256), 64)
        self.assertEqual(len(first.pairing_sha256), 64)
        self.assertNotEqual(first.participant_sha256, first.pairing_sha256)

    def test_type3_cup_source_requires_exact_cup_enumerator(self):
        competitions = (
            Competition(40, 2, initialization_order_value=0),
            Competition(50, 2, initialization_order_value=1),
        )
        rounds = (
            Round(100, 40, 1, 2, 2, 1, 1),
            Round(200, 50, 1, 1, 1, 2, 1),
        )
        allocations = (
            Allocation(1, 40, 1, 3, 40, 2),
        )

        with self.assertRaisesRegex(ValueError, r"Cup\+0x40/\+0x44"):
            materialize_primary_cup_runtime(
                IdentityRng(),
                competitions,
                rounds,
                (),
                (Country(1),),
                allocations,
            )


if __name__ == "__main__":
    unittest.main()

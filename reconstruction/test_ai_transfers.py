from __future__ import annotations

from datetime import date
from types import SimpleNamespace
import unittest

from ai_transfers import (
    autonomous_contract_length_months,
    buyer_club_eligible,
    candidate_has_spare_position_coverage,
    related_club_suppression_passes,
    run_weekly_ai_acquisitions,
)
from game_state import GameCalendar, GameState
from runtime_state import RuntimePlayer
from transfer_state import TransferRuntimeState


class ScriptedRng:
    def __init__(self, values):
        self.values = list(values)
        self.bounds = []

    def randbelow(self, bound):
        bound = int(bound)
        self.bounds.append(bound)
        if not self.values:
            raise AssertionError(f"unexpected RNG({bound}) call")
        value = int(self.values.pop(0))
        if not 0 <= value < bound:
            raise AssertionError(f"scripted value {value} is invalid for RNG({bound})")
        return value


def player(index, club_id, *, joined=date(1999, 1, 1), age_year=1975):
    return RuntimePlayer(
        index=index,
        first_name=f"P{index}",
        surname="Test",
        club_id=club_id,
        nationality_id=0,
        date_of_birth=date(age_year, 1, 1),
        shirt_number=index,
        height_cm=180,
        weight_kg=75,
        positions=(0, 0, 0),
        current_raw=[128] * 17,
        target_raw=(128,) * 17,
        development=None,
        current_position=0,
        current_club_join_date=joined,
        contract_expiry_date=date(2002, 1, 1),
    )


def financial_rows():
    return tuple(
        SimpleNamespace(
            id=i,
            field_08=100_000,
            field_0c=20_000,
            weekly_wage_base=1_000,
            weekly_wage_random_range=100,
            field_18=0,
            field_1c=0,
        )
        for i in range(100)
    )


def build_state(on_date=date(2000, 8, 19)):
    buyer_id = 1
    seller_id = 2
    players = {
        10: player(10, buyer_id),
        20: player(20, seller_id),
    }
    clubs = {
        buyer_id: SimpleNamespace(
            index=buyer_id,
            name="Buyer",
            manager_id=101,
            competition_id=0,
            country_id=0,
            team_category_code=0,
            fan_base_index=22,
            related_club_id_0=-1,
            related_club_id_1=-1,
            related_club_id_2=-1,
        ),
        seller_id: SimpleNamespace(
            index=seller_id,
            name="Seller",
            manager_id=102,
            competition_id=0,
            country_id=0,
            team_category_code=0,
            fan_base_index=22,
            related_club_id_0=-1,
            related_club_id_1=-1,
            related_club_id_2=-1,
        ),
    }
    fan_rows = tuple(
        SimpleNamespace(field_48=4)
        for _ in range(23)
    )
    return SimpleNamespace(
        calendar=GameCalendar(on_date),
        players=players,
        club_roster_order={buyer_id: [10], seller_id: [20]},
        clubs=clubs,
        managers={
            101: SimpleNamespace(index=101, club_id=buyer_id),
            102: SimpleNamespace(index=102, club_id=seller_id),
        },
        competitions={
            0: SimpleNamespace(
                id=0,
                runtime_kind_code=1,
                schedule_container_code=1,
                parent_competition_id=None,
                initialization_order_value=9,
                country_region_id=0,
                valuation_division_category=4,
            ),
        },
        countries={
            0: SimpleNamespace(
                id=0,
                financial_multiplier_percent=100,
                eu_status_flag=1,
            ),
        },
        positions={
            0: SimpleNamespace(lineup_group=0),
        },
        access_fan_bases=fan_rows,
        access_skill_financial_values=financial_rows(),
        transfers=TransferRuntimeState(),
        ai_transfer_startup_roster_count={buyer_id: 1, seller_id: 1},
        ai_transfer_buy_counter={buyer_id: 0, seller_id: 0},
        country_transfer_window_open={0: True},
        user_controlled_club_id=None,
    )


class WeeklyAiTransferTests(unittest.TestCase):
    def test_candidate_position_gate_uses_exact_coverage_tables(self):
        state = build_state()
        self.assertTrue(candidate_has_spare_position_coverage(state, 20, 2))
        state.players[20].ai_transfer_block_value_64 = 0
        self.assertFalse(candidate_has_spare_position_coverage(state, 20, 2))

    def test_buyer_gate_rejects_user_and_closed_country(self):
        state = build_state()
        self.assertTrue(buyer_club_eligible(state, 1))
        self.assertFalse(
            buyer_club_eligible(state, 1, user_controlled_club_id=1)
        )
        state.country_transfer_window_open[0] = False
        self.assertFalse(buyer_club_eligible(state, 1))

    def test_related_club_direction_consumes_rng_and_can_reject(self):
        state = build_state()
        state.clubs[1].related_club_id_0 = 2
        rng = ScriptedRng([11])
        self.assertFalse(related_club_suppression_passes(state, 1, 2, rng))
        self.assertEqual(rng.bounds, [100])

    def test_contract_table_uses_country_league_root_index_not_valuation_proxy(self):
        state = build_state()
        # Packed valuation category deliberately says 4, but 0x4FA510 resolves
        # the sole League root at country +0x48 index 0.
        self.assertEqual(state.competitions[0].valuation_division_category, 4)
        self.assertEqual(autonomous_contract_length_months(state, 20, 1), 4)
        state.players[20].date_of_birth = date(1965, 1, 1)
        self.assertEqual(autonomous_contract_length_months(state, 20, 1), 2)

    def test_contract_table_maps_five_playable_english_league_rows(self):
        state = build_state()
        state.competitions = {
            0: SimpleNamespace(id=0, runtime_kind_code=1, schedule_container_code=1,
                               parent_competition_id=None, initialization_order_value=9,
                               country_region_id=26),
            2: SimpleNamespace(id=2, runtime_kind_code=1, schedule_container_code=1,
                               parent_competition_id=None, initialization_order_value=10,
                               country_region_id=26),
            3: SimpleNamespace(id=3, runtime_kind_code=1, schedule_container_code=1,
                               parent_competition_id=None, initialization_order_value=11,
                               country_region_id=26),
            4: SimpleNamespace(id=4, runtime_kind_code=1, schedule_container_code=1,
                               parent_competition_id=None, initialization_order_value=12,
                               country_region_id=26),
            7: SimpleNamespace(id=7, runtime_kind_code=1, schedule_container_code=1,
                               parent_competition_id=None, initialization_order_value=13,
                               country_region_id=26),
            89: SimpleNamespace(id=89, runtime_kind_code=3, schedule_container_code=1,
                                parent_competition_id=None, initialization_order_value=14,
                                country_region_id=26),
        }
        # Buyer competition 7 is the fifth playable root, category 4.
        state.clubs[1].competition_id = 7
        state.players[20].date_of_birth = date(1975, 1, 1)  # age 25
        self.assertEqual(autonomous_contract_length_months(state, 20, 1), 3)

        # The trailing DummyLeague is index 5 and must not be silently clamped.
        state.clubs[1].competition_id = 89
        with self.assertRaisesRegex(RuntimeError, "outside"):
            autonomous_contract_length_months(state, 20, 1)

    def test_saturday_pass_completes_direct_ai_transfer(self):
        state = build_state()
        # Buyer 1: first draw == 3 bypasses the capacity branch.
        # Seller draw 1 selects club 2 from [1,2].
        # Candidate draw 0 selects player 20.
        # Fee random add 0; wage random add 0; completed-transfer
        # SignedNewContactMorale consumes RNG(2)=0. Buyer 2 then fails its
        # first buyer roll (0) because its startup roster capacity check is
        # false after player 20 moved.
        rng = ScriptedRng([3, 1, 0, 0, 0, 0, 0])
        results = run_weekly_ai_acquisitions(state, rng)

        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result.buyer_club_id, 1)
        self.assertEqual(result.seller_club_id, 2)
        self.assertEqual(result.player_id, 20)
        self.assertEqual(result.contract_length_months, 4)
        self.assertEqual(result.weekly_wage, 1000)
        self.assertEqual(state.players[20].club_id, 1)
        self.assertEqual(state.players[20].current_club_join_date, date(2000, 8, 19))
        self.assertEqual(state.club_roster_order[1], [10, 20])
        self.assertEqual(state.club_roster_order[2], [])
        self.assertEqual(len(state.transfers.movements), 1)
        self.assertEqual(state.ai_transfer_buy_counter[1], 1)

    def test_calendar_progression_runs_saturday_ai_transfer_pass(self):
        source = build_state(date(2000, 8, 18))
        rng = ScriptedRng([3, 1, 0, 0, 0, 0, 0])
        state = GameState(
            calendar=source.calendar,
            players=source.players,
            club_roster_order=source.club_roster_order,
            clubs=source.clubs,
            managers=source.managers,
            competitions=source.competitions,
            countries=source.countries,
            positions=source.positions,
            access_fan_bases=source.access_fan_bases,
            access_skill_financial_values=source.access_skill_financial_values,
            transfers=source.transfers,
            ai_transfer_startup_roster_count=source.ai_transfer_startup_roster_count,
            ai_transfer_buy_counter=source.ai_transfer_buy_counter,
            country_transfer_window_open=source.country_transfer_window_open,
            rng=rng,
        )

        self.assertEqual(state.advance_one_day(), date(2000, 8, 19))
        self.assertEqual(state.players[20].club_id, 1)
        self.assertEqual(len(state.transfers.movements), 1)
        self.assertEqual(state.transfers.movements[0].player_id, 20)

    def test_non_saturday_consumes_no_rng(self):
        state = build_state(date(2000, 8, 18))
        rng = ScriptedRng([])
        self.assertEqual(run_weekly_ai_acquisitions(state, rng), ())
        self.assertEqual(rng.bounds, [])


if __name__ == "__main__":
    unittest.main()

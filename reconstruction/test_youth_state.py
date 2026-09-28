import unittest
from datetime import date

from youth_state import (
    YOUTH_LIST_CAP,
    YouthRecord,
    YouthTeamState,
    generate_fresh_user_youth,
    initialize_user_youth_for_club_activation,
    promote_youth_player,
    release_youth_player,
)


class ScriptedRng:
    def __init__(self, values):
        self.values = list(values)
        self.bounds = []

    def randbelow(self, bound):
        bound = int(bound)
        self.bounds.append(bound)
        if not self.values:
            raise AssertionError(f"unexpected RNG({bound})")
        value = int(self.values.pop(0))
        if not 0 <= value < bound:
            raise AssertionError((value, bound))
        return value


class Player:
    def __init__(self, index, club_id=332, nationality_id=26):
        self.index = int(index)
        self.first_name = f"Alan{index}"
        self.surname = f"Smith{index}"
        self.club_id = int(club_id)
        self.nationality_id = int(nationality_id)
        self.date_of_birth = date(1975, 1, 1)
        self.shirt_number = 9
        self.positions = (1, 0, 0)
        self.current_position = 1
        self.position_aux_code = 0
        self.injured = True
        self.suspended = True
        self.selection_excluded = False
        self.status_bit_3 = False
        self.non_eu = True
        self.out_of_contract = True
        self.transfer_listed = True
        self.loan_listed = False
        self.signed_for_other_club = True
        self.match_active = True
        self.match_substitute_available = True
        self.loan_club_id = None
        self.previous_club_id_74 = 4
        self.eu_status_code = 2
        self.weekly_wage = 77
        self.contract_expiry_date = date(2002, 1, 1)
        self.training_method_id = 2
        self.training_countdown = 3
        self.training_active_count = 4
        self.training_modifiers = [9] * 17
        self.training_skill_states = [0] * 17
        self.training_method_results = [8] * 7
        self.current_raw = [20] * 17
        self.morale = 50

    def age(self, on_date):
        return on_date.year - self.date_of_birth.year - (
            (on_date.month, on_date.day)
            < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def reset_match_position(self):
        self.current_position = int(self.positions[0])
        self.position_aux_code = 0


class Club:
    def __init__(self, index, name, country_id):
        self.index = int(index)
        self.name = str(name)
        self.country_id = int(country_id)


class Country:
    def __init__(self, country_id, nationality_id):
        self.id = int(country_id)
        self.nationality_id = int(nationality_id)


class Calendar:
    def __init__(self, current_date):
        self.current_date = current_date


class State:
    def __init__(self, players):
        self.calendar = Calendar(date(2000, 7, 1))
        self.players = {player.index: player for player in players}
        self.clubs = {
            1: Club(1, "Arsenal", 26),
            332: Club(332, "!Spare", 116),
        }
        self.countries = {
            26: Country(26, 26),
            116: Country(116, 116),
        }
        self.club_roster_order = {
            1: [],
            332: [player.index for player in players],
        }


class YouthStateTests(unittest.TestCase):
    def test_fresh_generation_materializes_names_and_keeps_separate_roster(self):
        state = State([Player(i) for i in range(12)])
        # Unknown option => deterministic target 4. For each youth: candidate,
        # signed-contract morale, first-name source, surname source.
        rng = ScriptedRng([
            0, 0, 1, 2,
            0, 0, 3, 4,
            0, 0, 5, 6,
            0, 0, 7, 8,
        ])

        youth = generate_fresh_user_youth(
            state,
            user_club_id=1,
            option_mode=99,
            rng=rng,
        )

        self.assertEqual(youth.player_ids(), (0, 11, 10, 9))
        self.assertEqual(
            rng.bounds,
            [12, 2, 12, 12, 11, 2, 12, 12, 10, 2, 12, 12, 9, 2, 12, 12],
        )
        self.assertEqual(state.players[0].first_name, "Alan1")
        self.assertEqual(state.players[0].surname, "Smith2")
        self.assertEqual(state.players[0].age(state.calendar.current_date), 17)
        self.assertEqual(state.players[0].contract_expiry_date, date(2001, 7, 1))
        self.assertEqual(state.players[0].club_id, 1)
        self.assertEqual(state.players[0].morale, 82)
        self.assertTrue(state.players[0].status_bit_3)
        self.assertFalse(state.players[0].injured)
        self.assertFalse(state.players[0].suspended)
        self.assertFalse(state.players[0].transfer_listed)
        self.assertFalse(state.players[0].out_of_contract)
        # 0x41E510 does not append the player to the first-team roster.
        self.assertNotIn(0, state.club_roster_order[1])
        self.assertIn(0, state.club_roster_order[332])

    def test_club_activation_replaces_list_with_age_17_and_age_15_cohorts(self):
        players = [Player(i) for i in range(20)]
        state = State(players)
        state.players[0].status_bit_3 = True
        youth = YouthTeamState(
            [YouthRecord(player_id=0, source_roster_club_id=332)]
        )
        rng = ScriptedRng([0] * 32)

        result = initialize_user_youth_for_club_activation(
            state,
            youth,
            user_club_id=1,
            option_mode=99,
            rng=rng,
        )

        self.assertIs(result, youth)
        self.assertEqual(
            youth.player_ids(),
            (1, 19, 18, 17, 2, 16, 15, 14),
        )
        self.assertEqual(
            rng.bounds,
            [
                19, 2, 20, 20,
                18, 2, 20, 20,
                17, 2, 20, 20,
                16, 2, 20, 20,
                15, 2, 20, 20,
                14, 2, 20, 20,
                13, 2, 20, 20,
                12, 2, 20, 20,
            ],
        )
        for player_id in youth.player_ids()[:4]:
            self.assertEqual(
                state.players[player_id].age(state.calendar.current_date),
                17,
            )
        for player_id in youth.player_ids()[4:]:
            self.assertEqual(
                state.players[player_id].age(state.calendar.current_date),
                15,
            )
        for record in youth.records:
            player = state.players[record.player_id]
            self.assertEqual(player.contract_expiry_date, date(2001, 6, 30))
            self.assertEqual(record.training.method_id, 5)
            self.assertEqual(record.training.countdown, 8)
        self.assertTrue(state.players[0].status_bit_3)
        self.assertNotIn(0, youth.player_ids())

    def test_youth_list_has_hard_twenty_record_cap_and_compacts_on_remove(self):
        youth = YouthTeamState()
        for player_id in range(YOUTH_LIST_CAP):
            self.assertTrue(
                youth.append(
                    YouthRecord(player_id=player_id, source_roster_club_id=332)
                )
            )
        self.assertFalse(
            youth.append(YouthRecord(player_id=99, source_roster_club_id=332))
        )
        self.assertEqual(len(youth.records), 20)

        removed = youth.remove_player(4)
        self.assertEqual(removed.player_id, 4)
        self.assertEqual(youth.player_ids()[3:6], (3, 5, 6))
        self.assertEqual(len(youth.records), 19)

    def test_neutral_status_byte_set_get_matches_record_helpers(self):
        youth = YouthTeamState(
            [YouthRecord(player_id=7, source_roster_club_id=332)]
        )
        self.assertFalse(youth.status_14_for(7))
        self.assertTrue(youth.set_status_14(7))
        self.assertTrue(youth.status_14_for(7))
        self.assertFalse(youth.set_status_14(99))
        self.assertFalse(youth.status_14_for(99))

    def test_promotion_removes_spare_roster_and_copies_youth_training(self):
        player = Player(7)
        state = State([player])
        youth = YouthTeamState(
            [YouthRecord(player_id=7, source_roster_club_id=332)]
        )
        record = youth.records[0]
        record.training.method_id = 1
        record.training.countdown = 6
        record.training.active_count = 2
        record.training.modifiers[0] = 5
        record.training.skill_states[0] = 0
        record.training.method_results[1] = 3

        promoted = promote_youth_player(
            state,
            youth,
            player_id=7,
            target_club_id=1,
            weekly_wage=1234.9,
            contract_months=24,
            rng=ScriptedRng([0]),
        )

        self.assertIs(promoted, player)
        self.assertEqual(youth.player_ids(), ())
        self.assertNotIn(7, state.club_roster_order[332])
        self.assertIn(7, state.club_roster_order[1])
        self.assertEqual(player.club_id, 1)
        self.assertEqual(player.weekly_wage, 1234)
        self.assertEqual(player.contract_expiry_date, date(2002, 7, 1))
        self.assertEqual(player.morale, 82)
        self.assertFalse(player.status_bit_3)
        self.assertFalse(player.out_of_contract)
        self.assertEqual(player.training_method_id, 1)
        self.assertEqual(player.training_countdown, 6)
        self.assertEqual(player.training_active_count, 2)
        self.assertEqual(player.training_modifiers[0], 5)
        self.assertEqual(player.training_skill_states[0], 0)
        self.assertEqual(player.training_method_results[1], 3)

    def test_release_removes_youth_and_spare_roster_then_detaches_player(self):
        player = Player(7)
        state = State([player])
        youth = YouthTeamState(
            [YouthRecord(player_id=7, source_roster_club_id=332)]
        )

        self.assertTrue(
            release_youth_player(
                state,
                youth,
                player_id=7,
                user_club_id=1,
            )
        )

        self.assertEqual(youth.player_ids(), ())
        self.assertNotIn(7, state.club_roster_order[332])
        self.assertEqual(player.club_id, -1)
        self.assertTrue(player.out_of_contract)
        self.assertFalse(player.status_bit_3)
        self.assertEqual(player.previous_club_id_74, 1)
        self.assertFalse(
            release_youth_player(
                state,
                youth,
                player_id=7,
                user_club_id=1,
            )
        )


if __name__ == "__main__":
    unittest.main()

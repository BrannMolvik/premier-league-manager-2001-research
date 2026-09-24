import unittest

from match_strength import (
    ATTACK_ROLE_FACTORS,
    DEFENCE_ROLE_FACTORS,
    TeamStrengthContext,
    TeamStrengthPlayer,
    attack_team_strength,
    attack_weights,
    defence_team_strength,
    schedule_segment_attacks,
)


class ScriptedRng:
    def __init__(self, values):
        self.values = list(values)
        self.calls = []

    def randbelow(self, bound):
        self.calls.append(bound)
        if not self.values:
            raise AssertionError(f"unexpected RNG({bound})")
        value = self.values.pop(0)
        if not 0 <= value < bound:
            raise AssertionError(f"scripted value {value} outside RNG({bound})")
        return value


def matrix(value):
    return tuple(
        tuple(
            tuple(float(value) for _ in range(17))
            for _ in range(20)
        )
        for _ in range(4)
    )


def player(
    idx=1,
    role=12,
    side=0,
    skill=100,
    confidence=100,
    leadership=100,
):
    skills = [skill] * 17
    skills[14] = confidence
    skills[15] = leadership
    return TeamStrengthPlayer(
        side=side,
        player_index=idx,
        condition=100,
        form_state=2,
        current_position=role,
        preferred_positions=(role, 0, 0),
        skills=tuple(skills),
    )


class TeamStrengthTests(unittest.TestCase):
    def test_exact_role_balance_tables(self):
        self.assertEqual(
            ATTACK_ROLE_FACTORS[:13],
            (105, 108, 110, 120, 112, 115, 97, 95, 102, 92, 90, 117, 100),
        )
        self.assertEqual(
            DEFENCE_ROLE_FACTORS[:13],
            (95, 92, 90, 80, 88, 85, 103, 105, 98, 108, 110, 83, 100),
        )

    def test_attack_exact_one_player_sum_and_neutral_context(self):
        subject = player(role=12)
        expected = 17 * ((9900 / 255.0) * 1.0 * 1.0)
        actual = attack_team_strength(
            [subject],
            matrix(1),
            TeamStrengthContext(
                tactic_style=0,
                match_bias=2,
                user_controlled=True,
                aggression=5,
            ),
        )
        self.assertAlmostEqual(actual, expected)

    def test_attack_user_captain_aggression_and_bias(self):
        subject = player(role=12)
        base = 17 * (9900 / 255.0)
        expected = base * 1.20 * (0.95 + 200 / 5120.0) * 1.08
        actual = attack_team_strength(
            [subject],
            matrix(1),
            TeamStrengthContext(
                tactic_style=0,
                match_bias=4,
                user_controlled=True,
                aggression=9,
                captain_player_index=subject.player_index,
            ),
        )
        self.assertAlmostEqual(actual, expected)

    def test_ai_modifier_replaces_user_captain_and_aggression_branch(self):
        subject = player(role=12)
        base = 17 * (9900 / 255.0)
        actual = attack_team_strength(
            [subject],
            matrix(1),
            TeamStrengthContext(
                tactic_style=0,
                match_bias=2,
                user_controlled=False,
                aggression=9,
                captain_player_index=subject.player_index,
            ),
        )
        self.assertAlmostEqual(actual, base * 1.05)

    def test_defence_modifiers_include_formation_coverage(self):
        players = [
            player(1, 4),
            player(2, 4),
            player(3, 2),
            player(4, 3),
            player(5, 9),
        ]

        base = 0.0
        for subject in players:
            factor = DEFENCE_ROLE_FACTORS[int(subject.current_position)] / 100.0
            base += 17 * (9900 / 255.0) * factor

        # This shape satisfies the two central, left, right and central-mid
        # requirements, leaving only two advanced-side flags: 1 - .05*2.
        coverage = 0.90
        expected = (
            base
            * 1.10
            * (0.90 + 200 / 2560.0)
            * 0.90
            * coverage
        )
        actual = defence_team_strength(
            players,
            matrix(1),
            TeamStrengthContext(
                tactic_style=0,
                match_bias=1,
                user_controlled=True,
                aggression=0,
                captain_player_index=players[0].player_index,
            ),
        )
        self.assertAlmostEqual(actual, expected)


class AttackSchedulerTests(unittest.TestCase):
    def test_attack_weight_formula(self):
        self.assertEqual(
            attack_weights(
                side0_attack=120,
                side0_defence=100,
                side1_attack=80,
                side1_defence=160,
            ),
            (82, 72),
        )

    def test_sequence_count_side_selection_and_minute_distribution(self):
        rng = ScriptedRng([0, 99, 100, 199, 50, 150])
        attacks = schedule_segment_attacks(5, (100, 100), rng)

        self.assertEqual(len(attacks), 6)
        self.assertEqual(
            [attack.side for attack in attacks],
            [0, 0, 1, 1, 0, 1],
        )
        self.assertEqual(
            [attack.minute for attack in attacks],
            [6, 6, 7, 8, 9, 10],
        )
        self.assertEqual(rng.calls, [200] * 6)


if __name__ == "__main__":
    unittest.main()

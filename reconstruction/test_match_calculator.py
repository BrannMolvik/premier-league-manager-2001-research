import unittest

from match_calculator import (
    FORM_MULTIPLIERS,
    MatchSkillPlayer,
    PositionalPools,
    OpenPlayResolution,
    PositionRole,
    SetPieceResolution,
    build_positional_pools,
    choose_finish_mode,
    control_tackle_duel_won,
    effective_match_skill,
    encode_open_play_outcome,
    goalkeeper_stops_open_play,
    heading_attempt_on_target,
    heading_duel_won,
    first_duel_defender_wins,
    passing_gate_succeeds,
    position_compatibility_multiplier,
    resolve_corner,
    resolve_free_kick,
    resolve_open_play_attempt,
    resolve_penalty,
    select_close_defender,
    select_finisher,
    select_first_defender,
    select_initial_carrier,
    set_piece_execution_succeeds,
    shooting_attempt_on_target,
)
from match_events import ChanceOutcome, ChanceSource, FinishMode


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


class PositionCompatibilityTests(unittest.TestCase):
    def test_static_position_codes_match_known_roles(self):
        self.assertEqual(int(PositionRole.GOALKEEPER), 1)
        self.assertEqual(int(PositionRole.CENTRE_BACK), 4)
        self.assertEqual(int(PositionRole.CENTRE_MIDFIELD), 12)
        self.assertEqual(int(PositionRole.CENTRE_FORWARD), 18)
        self.assertEqual(int(PositionRole.STRIKER), 19)

    def test_exact_position_is_full_strength(self):
        self.assertEqual(position_compatibility_multiplier(19, (19, 18, 14)), 1.0)

    def test_goalkeeper_out_of_position_floor(self):
        self.assertEqual(position_compatibility_multiplier(1, (19, 18, 14)), 0.10)

    def test_defensive_fallbacks(self):
        self.assertEqual(position_compatibility_multiplier(2, (6, 0, 0)), 0.90)
        self.assertEqual(position_compatibility_multiplier(2, (3, 0, 0)), 0.75)
        self.assertEqual(position_compatibility_multiplier(4, (5, 0, 0)), 0.90)

    def test_midfield_and_forward_fallbacks(self):
        self.assertEqual(position_compatibility_multiplier(10, (13, 0, 0)), 0.85)
        self.assertEqual(position_compatibility_multiplier(10, (11, 0, 0)), 0.70)
        self.assertEqual(position_compatibility_multiplier(12, (15, 0, 0)), 0.90)
        self.assertEqual(position_compatibility_multiplier(15, (18, 0, 0)), 0.75)
        self.assertEqual(position_compatibility_multiplier(18, (19, 0, 0)), 0.90)


class EffectiveSkillTests(unittest.TestCase):
    def test_form_modifiers_match_shipped_values(self):
        self.assertEqual(FORM_MULTIPLIERS, (0.90, 0.95, 1.00, 1.05, 1.10))

    def test_effective_skill_exact_position_normal_form(self):
        self.assertEqual(effective_match_skill(100, 100, 19, (19, 18, 14), 2), 9900)

    def test_effective_skill_truncates_after_each_multiplier(self):
        self.assertEqual(effective_match_skill(100, 100, 15, (18, 0, 0), 3), 7796)

    def test_minimum_override_forces_one(self):
        self.assertEqual(effective_match_skill(255, 255, 19, (19, 0, 0), 4, True), 1)


class PenaltyResolverTests(unittest.TestCase):
    def setUp(self):
        self.taker = MatchSkillPlayer(
            side=0,
            player_index=9,
            condition=100,
            form_state=2,
            current_position=19,
            preferred_positions=(19, 18, 14),
            shooting=100,
        )
        self.keeper = MatchSkillPlayer(
            side=1,
            player_index=0,
            condition=100,
            form_state=2,
            current_position=1,
            preferred_positions=(1, 0, 0),
            goalkeeping=100,
        )

    def test_explicit_miss_path_and_rng_order(self):
        rng = ScriptedRng([0, 255, 50])
        event = resolve_penalty(self.taker, self.keeper, 0, rng)
        self.assertEqual(event.source, ChanceSource.PENALTY)
        self.assertEqual(event.outcome, ChanceOutcome.MISS)
        self.assertEqual(event.raw_outcome, 1)
        self.assertTrue(event.context_flag)
        self.assertEqual(rng.calls, [3, 256, 100])

    def test_saved_penalty_and_presentation_variant(self):
        rng = ScriptedRng([1, 0, 5])
        event = resolve_penalty(self.taker, self.keeper, 0, rng)
        self.assertEqual(event.outcome, ChanceOutcome.SAVE)
        self.assertEqual(event.raw_outcome, 5)
        self.assertEqual(rng.calls, [3, 800, 100])

    def test_goal_path_and_rng_order(self):
        rng = ScriptedRng([1, 799, 0, 50])
        event = resolve_penalty(self.taker, self.keeper, 0, rng)
        self.assertEqual(event.outcome, ChanceOutcome.GOAL)
        self.assertEqual(event.raw_outcome, 0)
        self.assertEqual(event.credited_side, 0)
        self.assertEqual(rng.calls, [3, 800, 10, 100])

    def test_goal_presentation_variant(self):
        rng = ScriptedRng([1, 799, 0, 9])
        event = resolve_penalty(self.taker, self.keeper, 0, rng)
        self.assertEqual(event.raw_outcome, 3)
        self.assertTrue(event.presentation_variant)

    def test_score_suppression_can_emit_no_record(self):
        rng = ScriptedRng([1, 799, 0])
        event = resolve_penalty(self.taker, self.keeper, 10, rng)
        self.assertIsNone(event)
        self.assertEqual(rng.calls, [3, 800, 10])

    def test_score_nine_allows_only_roll_zero(self):
        rng = ScriptedRng([1, 799, 1])
        self.assertIsNone(resolve_penalty(self.taker, self.keeper, 9, rng))
        rng = ScriptedRng([1, 799, 0, 50])
        self.assertEqual(resolve_penalty(self.taker, self.keeper, 9, rng).outcome, ChanceOutcome.GOAL)


class OpenPlayPrimitiveTests(unittest.TestCase):
    def make_player(self, **kwargs):
        base = dict(
            side=0,
            player_index=1,
            condition=100,
            form_state=2,
            current_position=19,
            preferred_positions=(19, 18, 14),
            shooting=100,
            tackling=100,
            heading=100,
            control=100,
            goalkeeping=100,
            set_piece=100,
        )
        base.update(kwargs)
        return MatchSkillPlayer(**base)

    def test_finish_mode_uses_weighted_heading_vs_shooting(self):
        player = self.make_player()
        self.assertEqual(choose_finish_mode(player, ScriptedRng([0])), FinishMode.HEADED)
        self.assertEqual(choose_finish_mode(player, ScriptedRng([15000])), FinishMode.SHOOTING)

    def test_heading_duel_is_weighted_attacker_vs_defender(self):
        attacker = self.make_player()
        defender = self.make_player(side=1, player_index=2)
        self.assertTrue(heading_duel_won(attacker, defender, ScriptedRng([0])))
        self.assertFalse(heading_duel_won(attacker, defender, ScriptedRng([15000])))
        self.assertTrue(heading_duel_won(attacker, None, ScriptedRng([])))

    def test_control_tackle_duel_uses_control_and_tackling(self):
        attacker = self.make_player(control=120)
        defender = self.make_player(side=1, player_index=2, tackling=120)
        self.assertTrue(control_tackle_duel_won(attacker, defender, ScriptedRng([0])))
        self.assertFalse(control_tackle_duel_won(attacker, defender, ScriptedRng([20000])))

    def test_accuracy_gates_use_rng320_then_coin_fallback(self):
        player = self.make_player()
        rng = ScriptedRng([0])
        self.assertTrue(heading_attempt_on_target(player, rng))
        self.assertEqual(rng.calls, [320])

        rng = ScriptedRng([319, 0])
        self.assertTrue(shooting_attempt_on_target(player, rng))
        self.assertEqual(rng.calls, [320, 2])

        rng = ScriptedRng([319, 1])
        self.assertFalse(set_piece_execution_succeeds(player, rng))
        self.assertEqual(rng.calls, [320, 2])

    def test_goalkeeper_stop_gate_matches_rng256_and_score_gate(self):
        keeper = self.make_player(side=1, player_index=0, current_position=1,
                                  preferred_positions=(1, 0, 0), goalkeeping=100)
        rng = ScriptedRng([0])
        self.assertTrue(goalkeeper_stops_open_play(keeper, 0, rng))
        self.assertEqual(rng.calls, [256])

        rng = ScriptedRng([255, 0])
        self.assertFalse(goalkeeper_stops_open_play(keeper, 0, rng))
        self.assertEqual(rng.calls, [256, 10])

        rng = ScriptedRng([255, 9])
        self.assertTrue(goalkeeper_stops_open_play(keeper, 9, rng))

    def test_type1_record_creator_suppresses_plain_normal_time_misses(self):
        self.assertIsNone(encode_open_play_outcome(1, 45, ScriptedRng([50])))
        self.assertEqual(encode_open_play_outcome(1, 45, ScriptedRng([5])), 4)
        self.assertEqual(encode_open_play_outcome(2, 45, ScriptedRng([50])), 2)
        self.assertEqual(encode_open_play_outcome(0, 45, ScriptedRng([5])), 3)

    def test_type1_shootout_time_retains_miss_without_variant(self):
        self.assertEqual(encode_open_play_outcome(1, 130, ScriptedRng([5])), 1)

class OpenPlaySelectionTests(unittest.TestCase):
    def p(self, idx, role, side=0, **kwargs):
        base=dict(side=side, player_index=idx, condition=100, form_state=2, current_position=role, preferred_positions=(role,0,0), shooting=100, passing=100, tackling=100, heading=100, control=100, goalkeeping=0, set_piece=100)
        base.update(kwargs)
        return MatchSkillPlayer(**base)

    def test_pool_builder_matches_role_groups(self):
        players=[self.p(0,1),self.p(1,2),self.p(2,4),self.p(3,9),self.p(4,10),self.p(5,12),self.p(6,13),self.p(7,15),self.p(8,18),self.p(9,19),self.p(10,16)]
        pools=build_positional_pools(players)
        self.assertEqual([p.player_index for p in pools.midfield],[4,5])
        self.assertEqual([p.player_index for p in pools.attacking_mid],[6,7])
        self.assertEqual([p.player_index for p in pools.forwards],[8,9])
        self.assertEqual(pools.goalkeeper.player_index,0)
        self.assertEqual([p.player_index for p in pools.holding_mid],[3,5])
        self.assertNotIn(10,[p.player_index for p in pools.forwards])

    def test_initial_carrier_prefers_midfield(self):
        pools=PositionalPools((self.p(1,10),self.p(2,12)),(self.p(3,13),),(),None,(),(),(),(),(),())
        rng=ScriptedRng([1])
        self.assertEqual(select_initial_carrier(pools,rng).player_index,2)
        self.assertEqual(rng.calls,[2])

    def test_first_defender_role_fallbacks(self):
        rm=self.p(1,10,1); rb=self.p(2,2,1); cb=self.p(3,4,1); hold=self.p(4,9,1)
        defending=PositionalPools((),(),(),None,(rb,),(),(cb,),(hold,),(rm,),())
        self.assertEqual(select_first_defender(self.p(10,13),defending,ScriptedRng([0])).player_index,1)
        defending=PositionalPools((),(),(),None,(rb,),(),(cb,),(hold,),(),())
        self.assertEqual(select_first_defender(self.p(10,13),defending,ScriptedRng([0])).player_index,2)
        self.assertEqual(select_first_defender(self.p(11,15),defending,ScriptedRng([0])).player_index,4)

    def test_close_defender_fullback_then_centre_fallback(self):
        rb=self.p(1,2,1); cb=self.p(2,4,1)
        defending=PositionalPools((),(),(),None,(rb,),(),(cb,),(),(),())
        self.assertEqual(select_close_defender(self.p(10,13),defending,ScriptedRng([0])).player_index,1)
        defending=PositionalPools((),(),(),None,(),(),(cb,),(),(),())
        self.assertEqual(select_close_defender(self.p(10,13),defending,ScriptedRng([0])).player_index,2)

    def test_finisher_reuses_one_roll_across_empty_buckets(self):
        mid=self.p(1,12); wing=self.p(2,13); fwd=self.p(3,19)
        pools=PositionalPools((mid,),(wing,),(fwd,),None,(),(),(),(),(),())
        self.assertEqual(select_finisher(pools,ScriptedRng([49,0])).player_index,3)
        pools=PositionalPools((mid,),(wing,),(),None,(),(),(),(),(),())
        self.assertEqual(select_finisher(pools,ScriptedRng([49,0])).player_index,2)
        pools=PositionalPools((),(),(fwd,),None,(),(),(),(),(),())
        self.assertEqual(select_finisher(pools,ScriptedRng([80,0])).player_index,3)

    def test_first_duel_true_means_defender_win(self):
        carrier=self.p(1,12,control=100); defender=self.p(2,9,1,tackling=100)
        defend=effective_match_skill(100,100,9,(9,0,0),2)
        self.assertTrue(first_duel_defender_wins(carrier,defender,ScriptedRng([0])))
        self.assertFalse(first_duel_defender_wins(carrier,defender,ScriptedRng([defend])))
        self.assertFalse(first_duel_defender_wins(carrier,None,ScriptedRng([])))

    def test_passing_gate_has_no_coin_fallback(self):
        carrier=self.p(1,12,passing=100)
        threshold=effective_match_skill(100,100,12,(12,0,0),2)//100
        self.assertTrue(passing_gate_succeeds(carrier,ScriptedRng([threshold-1])))
        self.assertFalse(passing_gate_succeeds(carrier,ScriptedRng([threshold])))
class FullOpenPlayResolverTests(unittest.TestCase):
    def p(self, idx, role, side=0, **kwargs):
        base=dict(side=side, player_index=idx, condition=100, form_state=2, current_position=role, preferred_positions=(role,0,0), shooting=100, passing=100, tackling=100, heading=100, control=100, goalkeeping=0, set_piece=100)
        base.update(kwargs)
        return MatchSkillPlayer(**base)

    def basic_teams(self):
        attack=[self.p(1,PositionRole.CENTRE_MIDFIELD)]
        defend=[self.p(0,PositionRole.GOALKEEPER,1,goalkeeping=100), self.p(2,PositionRole.CENTRE_BACK,1,tackling=100,heading=100)]
        return attack,defend

    def test_direct_five_percent_corner_precedes_possession_accounting(self):
        attack,defend=self.basic_teams()
        result=resolve_open_play_attempt(attack,defend,5,0,ScriptedRng([0]))
        self.assertEqual(result.transition,ChanceSource.CORNER)
        self.assertEqual((result.neutral_increment,result.attacking_possession_increment),(0,0))

    def test_complete_shooting_goal_path(self):
        attack,defend=self.basic_teams()
        rng=ScriptedRng([50,0,0,80,0,0,0,0,255,0,1,50])
        result=resolve_open_play_attempt(attack,defend,25,0,rng)
        self.assertIsNotNone(result.event)
        self.assertEqual(result.event.outcome,ChanceOutcome.GOAL)
        self.assertEqual(result.event.finish_mode,FinishMode.SHOOTING)
        self.assertFalse(result.event.is_own_goal)
        self.assertEqual((result.neutral_increment,result.attacking_possession_increment),(1,2))

    def test_goal_can_be_attributed_as_own_goal(self):
        attack,defend=self.basic_teams()
        rng=ScriptedRng([50,0,0,80,0,0,0,0,255,0,0,50])
        result=resolve_open_play_attempt(attack,defend,25,0,rng)
        self.assertTrue(result.event.is_own_goal)
        self.assertEqual(result.event.player_side,1)
        self.assertEqual(result.event.credited_side,0)

    def test_first_defender_win_aborts_before_passing(self):
        attack=[self.p(1,PositionRole.CENTRE_MIDFIELD)]
        defend=[self.p(0,PositionRole.GOALKEEPER,1,goalkeeping=100), self.p(2,PositionRole.DEFENSIVE_MIDFIELD,1,tackling=100)]
        result=resolve_open_play_attempt(attack,defend,25,0,ScriptedRng([50,0,0,0]))
        self.assertIsNone(result.event)
        self.assertIsNone(result.transition)
        self.assertEqual((result.neutral_increment,result.attacking_possession_increment),(1,1))

    def test_lost_final_duel_can_transition_to_penalty(self):
        attack,defend=self.basic_teams()
        rng=ScriptedRng([50,0,80,0,0,15000,0,0])
        result=resolve_open_play_attempt(attack,defend,25,0,rng)
        self.assertEqual(result.transition,ChanceSource.PENALTY)
        self.assertEqual((result.neutral_increment,result.attacking_possession_increment),(1,2))


class SetPieceResolverTests(unittest.TestCase):
    def p(self, idx, role, side=0, **kwargs):
        base=dict(
            side=side, player_index=idx, condition=100, form_state=2,
            current_position=role, preferred_positions=(role,0,0),
            shooting=100, passing=100, tackling=100, heading=100,
            control=100, goalkeeping=0, set_piece=100,
        )
        base.update(kwargs)
        return MatchSkillPlayer(**base)

    def teams(self):
        taker=self.p(1, PositionRole.CENTRE_MIDFIELD, shooting=100, passing=100, set_piece=100)
        receiver=self.p(2, PositionRole.STRIKER, shooting=100, heading=100)
        keeper=self.p(0, PositionRole.GOALKEEPER, 1, goalkeeping=100)
        centre=self.p(3, PositionRole.CENTRE_BACK, 1, tackling=100, heading=100)
        return taker, receiver, [taker, receiver], [keeper, centre]

    def test_direct_free_kick_goal(self):
        taker,receiver,attack,defend=self.teams()
        rng=ScriptedRng([0, 0, 255, 0, 50])
        result=resolve_free_kick(taker,attack,defend,0,rng)
        self.assertEqual(result.event.source, ChanceSource.FREE_KICK)
        self.assertEqual(result.event.outcome, ChanceOutcome.GOAL)
        self.assertEqual(result.event.finish_mode, FinishMode.SHOOTING)
        self.assertEqual(result.attacking_possession_increment,1)

    def test_cached_receiver_forces_headed_free_kick_delivery(self):
        taker,receiver,attack,defend=self.teams()
        rng=ScriptedRng([0, 0, 0, 0, 0, 50])
        result=resolve_free_kick(taker,attack,defend,0,rng,receiver_override=receiver)
        self.assertIsNotNone(result.event)
        self.assertEqual(result.event.finish_mode,FinishMode.HEADED)
        self.assertEqual(result.attacking_possession_increment,2)

    def test_force_direct_free_kick_skips_source_choice(self):
        taker,receiver,attack,defend=self.teams()
        rng=ScriptedRng([0,255,0,50])
        result=resolve_free_kick(taker,attack,defend,0,rng,force_direct=True)
        self.assertEqual(result.event.outcome,ChanceOutcome.GOAL)
        self.assertEqual(rng.calls[0],320)

    def test_corner_requires_set_piece_execution(self):
        taker,receiver,attack,defend=self.teams()
        result=resolve_corner(taker,attack,defend,0,ScriptedRng([319,1]))
        self.assertIsNone(result.event)
        self.assertEqual(result.attacking_possession_increment,1)

    def test_corner_cached_receiver_forces_heading(self):
        taker,receiver,attack,defend=self.teams()
        rng=ScriptedRng([0,0,0,0,0,50])
        result=resolve_corner(taker,attack,defend,0,rng,receiver_override=receiver)
        self.assertIsNotNone(result.event)
        self.assertEqual(result.event.source,ChanceSource.CORNER)
        self.assertEqual(result.event.finish_mode,FinishMode.HEADED)
        self.assertEqual(result.attacking_possession_increment,2)

    def test_corner_rejects_taker_as_receiver(self):
        taker,receiver,attack,defend=self.teams()
        result=resolve_corner(taker,attack,defend,0,ScriptedRng([0]),receiver_override=taker)
        self.assertIsNone(result.event)
        self.assertEqual(result.attacking_possession_increment,2)


if __name__ == '__main__':
    unittest.main()

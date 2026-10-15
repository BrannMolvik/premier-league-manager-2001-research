"""Source native class-factor -> original 5DA250 argument ownership on both teams."""
from struct import pack,pack_into
from unittest import TestCase
from original_match_5daa47_stage_two_factor import (
    source_original_5daa47_or_5dacc0_team_factor,
)
from original_match_stage2_5da250_factor_join import (
    OriginalScoredFactorJoinError,
    source_original_5daa_or_5dad_scored_factor_to_5da250,
)


def bundle(stage=1,enum=0,human=False):
    team=bytearray(0x18);pack_into('<I',team,0x14,3)
    p=0x3000 if stage==1 else 0x4000
    fac=source_original_5daa47_or_5dacc0_team_factor(
       original_side=stage,original_team_pointer=p,
       original_team_record=bytes(team),
       original_874be0_global_class_table_pointer=0x100000,
       original_410ff0_reached_ecx_class_pointer=0x100000+3*108,
       original_410ff0_return_eax=enum)
    snapshot=bytearray(0x40)
    snapshot[0x18:0x20]=fac.original_qword_factor
    snapshot[0x30:0x38]=pack('<d',8. if human else 0.)
    snapshot[0x38:0x40]=pack('<d',30.)
    kwargs=dict(original_scoring_stage=stage,
        original_coefficient_team_pointer=p,
        original_class_factor=fac,
        original_stage_stack_before_argument_pushes=bytes(snapshot),
        original_4037b0_human_gate=human,
        original_selected_user_694_record_if_human=None,
        original_5e48d0_stored_qword_if_directly_copied_to_b=None if stage==2 and not human else pack('<d',30.))
    if human:
        user=bytearray(0x10);pack_into('<i',user,0xc,37)
        kwargs['original_selected_user_694_record_if_human']=bytes(user)
    return kwargs


class OriginalScoredStage2FactorJoinTests(TestCase):
    def test_first_side_source_factor_qword_and_native_5dab07_nonhuman(self):
        for e in (0,1,2,3,4,5,0xffffffff):
            r=source_original_5daa_or_5dad_scored_factor_to_5da250(**bundle(1,e,False))
            self.assertEqual(r.original_stage,1)
            self.assertEqual(r.source_original_arguments.source_5da250_call_site,0x5dab07)
            self.assertEqual(r.source_original_arguments.source_b_owner,'stage-5e48d0-direct')
            self.assertEqual(r.original_qword_factor_at_esp18,r.source_class_factor.original_qword_factor)
            self.assertFalse(r.actual_original_5da250_executed)
            self.assertFalse(r.original_game_state_modified)

    def test_second_side_class_factor_uses_distinct_opponent_ecx_class_owner(self):
        for e in range(7):
            r=source_original_5daa_or_5dad_scored_factor_to_5da250(**bundle(2,e,False))
            self.assertEqual(r.source_original_arguments.source_5da250_call_site,0x5dad84)
            self.assertEqual(r.source_original_arguments.source_b_owner,
                             'stage-stack-retained-origin-unresolved')
            self.assertEqual(r.original_qword_factor_at_esp18,pack('<d',(.9,.8,.7,.6,.5,.5)[e] if e<=5 else .5))

    def test_original_human_stage_requires_exact_original_694_stat_and_B_callback(self):
        for stage in (1,2):
            r=source_original_5daa_or_5dad_scored_factor_to_5da250(**bundle(stage,3,True))
            self.assertEqual(r.source_original_arguments.human_user_694_signed_dword_if_reached,37)
            self.assertEqual(r.source_original_arguments.native_first_qword_a,pack('<d',8.))
            self.assertEqual(r.source_original_arguments.native_second_qword_b,pack('<d',30.))

    def test_wrong_team_source_enum_mutated_stack_and_mixed_stage_fail_closed(self):
        valid=bundle(2,1,True)
        wrong=bytearray(valid['original_stage_stack_before_argument_pushes'])
        wrong[0x18:0x20]=pack('<d',.9)
        cases=(
          {'original_scoring_stage':1},
          {'original_coefficient_team_pointer':0x3000},
          {'original_class_factor':None},
          {'original_stage_stack_before_argument_pushes':bytes(wrong)},
          {'original_stage_stack_before_argument_pushes':b''},
          {'original_selected_user_694_record_if_human':None},
          {'original_5e48d0_stored_qword_if_directly_copied_to_b':None},
          {'original_coefficient_team_pointer':False},
          {'original_scoring_stage':True},
        )
        for delta in cases:
            with self.subTest(delta=delta),self.assertRaises(OriginalScoredFactorJoinError):
                source_original_5daa_or_5dad_scored_factor_to_5da250(**(valid|delta))
        nonhuman=bundle(1,0,False)
        with self.assertRaises(OriginalScoredFactorJoinError):
            source_original_5daa_or_5dad_scored_factor_to_5da250(
                **(nonhuman|{'original_selected_user_694_record_if_human':bytes(16)}))

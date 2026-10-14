"""Reached native four-float source -> match context -> first side, fail closed."""
from unittest import TestCase
from original_match_calculation_reached_chain import (
    OriginalNativeReachedCalculationError,source_original_5db389_through_5db6fa_joined_source,
)
from test_original_native_5db389_component_inputs import fixture as source_float
from test_original_match_context_to_side_world import joined

def fixture(add=None):
    world=joined()
    total=33+(add or 0)
    world['original_ebx_component_at_5db6fc']=total
    world['original_ecx_component_at_5db704']=17
    return dict(original_four_float_source_input=source_float(human=add),
                original_actual_final_ebx_at_5db6fc=total,
                original_actual_final_ecx_at_5db704=17,
                original_context_side_stage_input=world)

class ReachedNativeMatchWorldTests(TestCase):
    def test_four_native_floats_to_first_side_source_world(self):
        one=source_original_5db389_through_5db6fa_joined_source(**fixture())
        human=source_original_5db389_through_5db6fa_joined_source(**fixture(add=9))
        self.assertEqual(one.original_source_context_and_side_world.source_native_context.source_context_d84,50)
        self.assertEqual(human.original_source_context_and_side_world.source_native_context.source_context_d84,59)
        self.assertFalse(human.live_game_state_committed)

    def test_native_final_register_mismatch_fails_closed(self):
        state=fixture()
        for change in (
            {'original_actual_final_ebx_at_5db6fc':999},
            {'original_actual_final_ecx_at_5db704':True},
            {'original_context_side_stage_input':state['original_context_side_stage_input']|
                {'original_ebx_component_at_5db6fc':0}},
        ):
            with self.subTest(change=change):
                with self.assertRaises(OriginalNativeReachedCalculationError):
                    source_original_5db389_through_5db6fa_joined_source(**(state|change))

"""Reached native four-float source -> match context -> first side, fail closed."""
from unittest import TestCase
from original_match_calculation_reached_chain import (
    OriginalNativeReachedCalculationError,source_original_5db389_through_5db6fa_joined_source,
)
from test_original_native_5db389_component_inputs import fixture as source_float
from test_original_match_context_to_side_world import joined

def fixture(add=None, *, keys=None, skip=False):
    world=joined(skip=skip, keys=keys if keys is not None else ((777,) if add is not None else (111,)))
    total=33+(add or 0)
    world['original_ebx_component_at_5db6fc']=total
    world['original_ecx_component_at_5db704']=17
    inputs=source_float(human=add)
    if add is not None:
        inputs['original_user_694_owner_pointer_if_reached']=0xA0000
    return dict(original_four_float_source_input=inputs,
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

    def test_actual_source_human_gate_and_pointer_identity_fail_closed(self):
        for case in (fixture(add=9,keys=(111,)),
                     fixture(add=9,skip=True),
                     fixture(keys=(777,))):
            with self.subTest(branch=case['original_four_float_source_input']):
                with self.assertRaisesRegex(OriginalNativeReachedCalculationError,'branch contradicts'):
                    source_original_5db389_through_5db6fa_joined_source(**case)
        valid=fixture(add=9)
        bad=valid['original_four_float_source_input'] | {
            'original_user_694_owner_pointer_if_reached':0xA0100}
        with self.assertRaisesRegex(OriginalNativeReachedCalculationError,'owner pointer mismatch'):
            source_original_5db389_through_5db6fa_joined_source(**(
                valid | {'original_four_float_source_input':bad}))
        # A first-side human with local skip 1 reaches no 5DB4C4.
        skipped=fixture(keys=(777,),skip=True)
        received=source_original_5db389_through_5db6fa_joined_source(**skipped)
        self.assertTrue(received.original_source_context_and_side_world.source_first_side.source_tail.source_first_side_writes_skipped)

    def test_optional_original_branch_site_byte_checks(self):
        import os
        from hashlib import sha256
        from pathlib import Path
        path=os.environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('proprietary original absent from hosted CI')
        exe=Path(path).read_bytes()
        self.assertEqual(sha256(exe).hexdigest(),
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3')
        signatures={0x5db3ac:'8b ce',0x5db3b2:'e8 f9 83 e2 ff',
            0x5db3b9:'8a 44 24 0f',0x5db3bd:'0f 84 0c 01 00 00',
            0x5db3c3:'84 c0',0x5db3c5:'0f 85 0c 01 00 00',
            0x5db3cd:'e8 7e 84 e2 ff',
            0x5db4be:'8b 8f 94 06 00 00',0x5db4c4:'03 19',
            0x5db4ca:'e9 2b 02 00 00'}
        for va,encoded in signatures.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(encoded)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(expected)],expected)

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

"""Source native coefficient/read, signed bound clamp and per-thread 64D540."""
from unittest import TestCase
from original_match_stage4_rng_join import (
    OriginalStageFourRngSourceError,source_original_fourth_stage_to_rand,
)
from test_original_match_stage4_coefficient_player_source import fixture as coeff_fixture
from test_original_native_64d540_rand_step import fixture as rand_fixture


def input_fixture(eax=0x7fffffff,cat=3):
    rng=rand_fixture(seed=12345)
    return dict(original_reached_stage4_coefficient_input=coeff_fixture(category=cat),
                original_reached_668350_eax_at_5db346=eax,
                original_66951c_rng_owner_pointer=rng['original_66d553_rng_owner_pointer'],
                original_66951c_rng_owner_before=rng['original_rng_owner_before_66951c'])

class OriginalStageFourRngJoinTests(TestCase):
    def test_reached_native_edi_clamp_is_signed_and_rng_consumes_state(self):
        for eax,expect in ((0,1),(0xffffffff,1),(0x80000000,1),(1,1),(42,42),(0x7fffffff,0x7fffffff)):
            with self.subTest(eax=eax):
                out=source_original_fourth_stage_to_rand(**input_fixture(eax))
                self.assertEqual(out.original_edi_signed_clamped_at_5db35b,expect)
                self.assertEqual(out.original_source_rng_step.native_reached_signed_bound,expect)
                self.assertEqual(out.original_stage4_coefficient_player.original_global_player_signed_dword,61)
                self.assertFalse(out.original_native_5da250_executed)
                self.assertFalse(out.original_source_rng_step.native_rng_executed)
                self.assertFalse(out.live_game_state_updated)

    def test_invalid_native_668350_eax_or_skipped_stage_fails_closed(self):
        original=input_fixture()
        for change in ({'original_reached_668350_eax_at_5db346':-1},
                       {'original_reached_668350_eax_at_5db346':True},
                       {'original_reached_668350_eax_at_5db346':0x100000000},
                       {'original_reached_stage4_coefficient_input':coeff_fixture(ah=0x40)}):
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    source_original_fourth_stage_to_rand(**(original|change))

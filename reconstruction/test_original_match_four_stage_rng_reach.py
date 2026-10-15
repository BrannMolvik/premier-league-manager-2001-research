"""No guessed RNG sequence: four optional original stage-specific draws."""
from struct import pack_into
from itertools import product
from unittest import TestCase
from original_match_four_stage_rng_reach import (
    OriginalFourStageRngReachError,source_original_four_stage_rng_reach,
)

def fixture(mask=(0,0,0,0),bound=(1,12,0xffffffff,0x80000000),seeds=(7,5,100,1)):
    owners=[]
    for i,(skip,seed) in enumerate(zip(mask,seeds)):
        if skip:owners.append(None);continue
        raw=bytearray(0x18)
        pack_into('<I',raw,0x14,seed)
        owners.append(bytes(raw))
    return dict(original_native_x87_ah_at_four_stage_guards=tuple(0x40 if s else 0 for s in mask),
        original_native_668350_eax_at_each_reached_clamp=tuple(None if s else bound[i] for i,s in enumerate(mask)),
        original_66d553_rng_owner_pointer=0x20000,
        original_rng_owner_bytes_before_each_reached_call=tuple(owners))

class OriginalFourStageRngReachTests(TestCase):
    def test_all_sixteen_independent_guard_masks_preserve_source_rng_order(self):
        sites=(0x5dabed,0x5dae68,0x5db0e9,0x5db364)
        edi=(1,12,1,1)
        for mask in product((0,1),repeat=4):
            with self.subTest(mask=mask):
                source=fixture(mask)
                out=source_original_four_stage_rng_reach(**source)
                self.assertEqual(out.original_stage_rng_call_addresses_if_reached,tuple(None if skip else sites[i] for i,skip in enumerate(mask)))
                self.assertEqual(tuple(d.native_reached_signed_bound if d is not None else None for d in out.original_stage_rng_draws_if_reached),tuple(None if skip else edi[i] for i,skip in enumerate(mask)))
                self.assertFalse(out.actual_original_rng_callbacks_executed)
                self.assertFalse(out.original_intermittent_rng_consumption_qualified)

    def test_independent_owner_snapshots_are_not_falsely_chained(self):
        out=source_original_four_stage_rng_reach(**fixture())
        states=tuple(d.original_seed_before for d in out.original_stage_rng_draws_if_reached)
        self.assertEqual(states,(7,5,100,1))
        self.assertNotEqual(out.original_stage_rng_draws_if_reached[0].original_seed_after,states[1])
        self.assertFalse(out.live_game_state_updated)

    def test_unsupported_intervening_guards_and_missing_snapshots_fail_closed(self):
        x=fixture(mask=(0,1,0,1))
        for bad in (
            {'original_native_668350_eax_at_each_reached_clamp':(1,1,1,None)},
            {'original_rng_owner_bytes_before_each_reached_call':(None,None,x['original_rng_owner_bytes_before_each_reached_call'][2],None)},
            {'original_native_668350_eax_at_each_reached_clamp':(1,None,True,None)},
            {'original_native_668350_eax_at_each_reached_clamp':[1,None,1,None]},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises((ValueError,TypeError)):
                    source_original_four_stage_rng_reach(**(x|bad))

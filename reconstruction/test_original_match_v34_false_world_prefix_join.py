"""510D60 four native 407770 AL states to 512D80 then v38/v3c."""
from struct import unpack_from
from unittest import TestCase
from original_match_v34_false_world_prefix_join import (
    Original510D60ToFallbackSourceError,
    source_original_reached_v34_false_fallback_to_world_prefix as chain,
)
from original_native_510d60_readiness_producer import (
    source_original_510d60_actual_four_team_guard_results as source,
    source_original_511120_preserves_510d60_native_readiness as wrap,
)
from test_original_native_510d60_readiness_producer import inputs as ready_inputs,match
from test_original_match_512d80_fallback_scores import inputs as fallback_inputs,reached_after_512d80


def args(vt=0x7c4c24,checks=(False,None,None,None)):
    r=source(**ready_inputs(vt,checks))
    w=wrap(original_base_readiness=r,
           original_native_match_record_at_511120=match(vt),
           original_reached_virtual28_kind=2) if r.source_wrapped_511120_required else None
    fb=fallback_inputs()
    return dict(original_native_510d60_readiness=r,
                original_native_wrapped_511120_if_reached=w,
                original_native_match_record_before_v38=match(vt),
                original_context_pointer_at_512d80=0x9000,
                original_original_context_before_512d80=fb['original_context_record_before_512d80'],
                original_processing_context_actual_after_512d80_callbacks=reached_after_512d80(),
                original_tls_record_source=fb['original_tls_record_source'],
                original_first_team_407770_eax_nonzero_at_512db4=True,
                original_second_team_407770_eax_nonzero_at_512dca=True,
                original_four_special_gates=fb['original_four_special_gates'])


class OriginalV34FallbackJoinTests(TestCase):
    def test_first_second_407770_zero_arg_fail_and_late_one_arg_fail_all_route_to_real_prefix(self):
        for checks in ((False,None,None,None),(True,False,None,None),
                       (True,True,False,None),(True,True,True,False)):
            with self.subTest(checks=checks):
                receipt=chain(**args(checks=checks))
                self.assertFalse(receipt.original_base_510d60_readiness.original_510d60_return_al_nonzero)
                self.assertTrue(receipt.original_5130c2_branch_to_512d80_proven_by_source)
                final=receipt.source_original_512d80_fallback.original_v38_then_v3c_prefix.native_v3c_first_flag.match_record_after_first_bit0_store
                self.assertEqual(unpack_from('<HH',final,0x3c),(0,3))
                self.assertFalse(receipt.original_v3c_calendar_world_completed)
                self.assertFalse(receipt.original_live_game_state_modified)

    def test_original_511120_wrapped_match_returns_source_false_and_composes_without_513570_events(self):
        for vt in (0x7c9d9c,0x7c9e80,0x7c9ef8,0x7c9f70):
            with self.subTest(vt=hex(vt)):
                r=chain(**args(vt))
                self.assertIsNotNone(r.original_wrapped_511120_if_reached)
                self.assertFalse(r.original_wrapped_511120_if_reached.source_final_v34_return_al_nonzero)
                self.assertFalse(r.original_v3c_calendar_world_completed)
                self.assertEqual(unpack_from('<HH',
                      r.source_original_512d80_fallback.original_v38_then_v3c_prefix.native_v3c_first_flag.match_record_after_first_bit0_store,0x3c),(0,3))

    def test_unreached_positive_v34_or_missing_original_wrapper_cannot_trigger_fallback(self):
        native=args()
        ready_positive=source(**ready_inputs(checks=(True,True,True,True)))
        bads=(
            {'original_native_510d60_readiness':ready_positive},
            {'original_native_510d60_readiness':None},
            {'original_original_context_before_512d80':bytes(0xd54)},
            {'original_native_match_record_before_v38':match(0x7c9d9c)},
            {'original_context_pointer_at_512d80':True},
            {'original_context_pointer_at_512d80':0},
            {'original_processing_context_actual_after_512d80_callbacks':reached_after_512d80(first=99)},
        )
        for changes in bads:
            with self.subTest(changes=changes),self.assertRaises(Original510D60ToFallbackSourceError):
                chain(**(native|changes))
        w=args(0x7c9d9c)
        with self.assertRaises(Original510D60ToFallbackSourceError):
            chain(**(w|{'original_native_wrapped_511120_if_reached':None}))
        with self.assertRaises(Original510D60ToFallbackSourceError):
            chain(**(native|{'original_native_wrapped_511120_if_reached':
                              w['original_native_wrapped_511120_if_reached']}))

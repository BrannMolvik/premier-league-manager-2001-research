"""Strict original 0x513238 source reachability; no simulated matches."""
from __future__ import annotations
import os
from pathlib import Path
import unittest

from original_native_match_detail_gate import (
    OriginalNativeMatchPresentationGateError,
    source_original_native_match_view_gate_513238 as gate,
)
from gate14_match_detail_route_source import (
    MatchPresentationRoute,
    source_match_detail_dispatch,
)


class OriginalNativeMatchModeReachabilityTests(unittest.TestCase):
    def call_gate(self, prepare=True, before=0, ptr=0x12345678,
                  after=0x10, mode=2):
        return gate(
            original_v34_prepare_succeeded=prepare,
            original_flags44_at_pre_shared_gate=before,
            original_native_side0_club_pointer_from_reached_v0=ptr,
            original_flags44_after_reached_5da2f0=after,
            original_mode_global_877530_if_view_reached=mode,
        )

    def test_virtual34_failure_skips_even_first_flag_read_but_reaches_post_callbacks(self):
        x=self.call_gate(prepare=False,before=None,ptr=None,after=None,mode=None)
        self.assertFalse(x.shared_stage_5da2f0_reached)
        self.assertFalse(x.view_51325d_reached)
        self.assertTrue(x.post_virtual38_and_virtual3c_reached)
        self.assertIsNone(x.source_view_route)

    def test_bit5_skips_side0_and_shared_stage_not_post_callbacks(self):
        x=self.call_gate(before=0x20,ptr=None,after=None,mode=None)
        self.assertFalse(x.shared_stage_5da2f0_reached)
        self.assertTrue(x.post_virtual38_and_virtual3c_reached)
        self.assertIsNone(x.source_view_route)

    def test_view_gate_reads_flags_after_shared_stage_not_stale_before(self):
        # 0x5DA2F0 (or the reached side0 accessor) can change +0x44.
        # Native 0x513257 performs a NEW byte read, not the 0x513238 EAX.
        source_sets_bit4=self.call_gate(before=0,after=0x10,mode=2)
        self.assertTrue(source_sets_bit4.shared_stage_5da2f0_reached)
        self.assertTrue(source_sets_bit4.view_51325d_reached)
        self.assertEqual(source_sets_bit4.source_view_route.route,
                         MatchPresentationRoute.FASTVIEW)
        source_clears_bit4=self.call_gate(before=0x10,after=0,mode=None)
        self.assertTrue(source_clears_bit4.shared_stage_5da2f0_reached)
        self.assertFalse(source_clears_bit4.view_51325d_reached)
        self.assertIsNone(source_clears_bit4.source_view_route)

    def test_every_original_selection_reaches_own_source_route(self):
        expected=(
            MatchPresentationRoute.THREE_D_MATCH,
            MatchPresentationRoute.THREE_D_HIGHLIGHTS,
            MatchPresentationRoute.FASTVIEW,
            MatchPresentationRoute.QUICK_MATCH,
        )
        for mode,route in enumerate(expected):
            with self.subTest(mode=mode):
                x=self.call_gate(mode=mode)
                self.assertEqual(x.source_view_route,
                                 source_match_detail_dispatch(mode))
                self.assertEqual(x.source_view_route.route,route)
                self.assertTrue(x.post_virtual38_and_virtual3c_reached)
        self.assertIsNone(source_match_detail_dispatch(3).presentation_wrapper_va)

    def test_skipped_source_callbacks_cannot_be_supplied_from_guess(self):
        good=dict(
            original_v34_prepare_succeeded=False,
            original_flags44_at_pre_shared_gate=None,
            original_native_side0_club_pointer_from_reached_v0=None,
            original_flags44_after_reached_5da2f0=None,
            original_mode_global_877530_if_view_reached=None,
        )
        for bad in (
            dict(original_flags44_at_pre_shared_gate=0),
            dict(original_native_side0_club_pointer_from_reached_v0=1),
            dict(original_flags44_after_reached_5da2f0=0),
            dict(original_mode_global_877530_if_view_reached=3),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalNativeMatchPresentationGateError):
                    gate(**(good|bad))
        for bad in (
            dict(ptr=1),dict(after=0),dict(mode=3),
        ):
            with self.subTest(bad=bad):
                kw=dict(before=0x20,ptr=None,after=None,mode=None)
                kw.update(bad)
                with self.assertRaises(OriginalNativeMatchPresentationGateError):
                    self.call_gate(**kw)

    def test_genuine_source_required_for_reached_reads(self):
        for kwargs in (
            dict(prepare=1),
            dict(before=None),
            dict(before=True),
            dict(ptr=None),
            dict(ptr=0),
            dict(ptr=-1),
            dict(after=None),
            dict(after=True),
            dict(mode=None),
            dict(mode=5),
            dict(mode=True),
            dict(before=0,after=0,mode=2),
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(OriginalNativeMatchPresentationGateError):
                    self.call_gate(**kwargs)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "original private PE not mounted")
    def test_direct_original_pe_guard_v34_bit5_mode_and_common_post_callbacks(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        signatures=(
            (0x5130C2,"ff 50 34 84 c0"),
            (0x513238,"8b 4e 44 5d c1 e9 05 f6 c1 01"),
            (0x513244,"8b 17 8b cf ff 12"),
            (0x513252,"e8 99 70 0c 00"),
            (0x513257,"f6 46 44 10 74 37"),
            (0x51325D,"a1 30 75 87 00"),
            (0x513272,"e8 49 ff 01 00"),
            (0x51328C,"e8 ef 0a 02 00"),
            (0x513294,"8b 16"),
            (0x51329D,"ff 52 38"),
            (0x5132A9,"ff 52 3c"),
        )
        for address,hexbytes in signatures:
            with self.subTest(address=hex(address)):
                expected=bytes.fromhex(hexbytes)
                self.assertEqual(pe.read(address,len(expected)),expected)


if __name__=="__main__":
    unittest.main()

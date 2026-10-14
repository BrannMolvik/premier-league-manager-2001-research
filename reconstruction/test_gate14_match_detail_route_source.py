from __future__ import annotations

import unittest

from gate14_match_detail_route_source import (
    FASTVIEW_PRESENTATION_WRAPPER_VA,
    MatchPresentationRoute,
    THREED_PRESENTATION_WRAPPER_VA,
    match_detail_route_source_contract,
    source_match_detail_dispatch,
    source_match_mode_preparation,
    source_requires_prematch_modal,
)
from match_detail_mode import MatchDetailMode


class MatchDetailRouteSourceTests(unittest.TestCase):
    def test_all_four_modes_follow_exact_source_presentation_dispatch(self):
        expected = {
            MatchDetailMode.THREE_D_MATCH: (
                MatchPresentationRoute.THREE_D_MATCH,
                THREED_PRESENTATION_WRAPPER_VA,
                0,
            ),
            MatchDetailMode.THREE_D_HIGHLIGHTS: (
                MatchPresentationRoute.THREE_D_HIGHLIGHTS,
                THREED_PRESENTATION_WRAPPER_VA,
                1,
            ),
            MatchDetailMode.FASTVIEW: (
                MatchPresentationRoute.FASTVIEW,
                FASTVIEW_PRESENTATION_WRAPPER_VA,
                None,
            ),
            MatchDetailMode.QUICK_MATCH: (
                MatchPresentationRoute.QUICK_MATCH,
                None,
                None,
            ),
        }
        for mode, values in expected.items():
            with self.subTest(mode=mode):
                dispatch = source_match_detail_dispatch(mode)
                self.assertEqual(
                    (
                        dispatch.route,
                        dispatch.presentation_wrapper_va,
                        dispatch.wrapper_variant,
                    ),
                    values,
                )

    def test_integer_modes_share_the_same_source_validation(self):
        for mode in MatchDetailMode:
            self.assertEqual(
                source_match_detail_dispatch(int(mode)),
                source_match_detail_dispatch(mode),
            )
        for invalid in (-1, 4, 5, True, "2"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    source_match_detail_dispatch(invalid)

    def test_contract_closes_modal_route_but_not_management_trigger_or_gate(self):
        contract = match_detail_route_source_contract()
        self.assertTrue(contract["prematch_modal_to_presentation_dispatch_recovered"])
        self.assertFalse(contract["management_ui_entry_trigger_recovered"])
        self.assertFalse(contract["three_d_choreography_recovered"])
        self.assertFalse(contract["complete_match_presentation_recovered"])
        self.assertFalse(contract["gate14_complete"])
        self.assertEqual(
            contract["mode_routes"],
            (
                (0, "three_d_match", THREED_PRESENTATION_WRAPPER_VA, 0),
                (1, "three_d_highlights", THREED_PRESENTATION_WRAPPER_VA, 1),
                (2, "fastview", FASTVIEW_PRESENTATION_WRAPPER_VA, None),
                (3, "quick_match", None, None),
            ),
        )

    def test_modal_predicate_keeps_settings_owner_unknown_distinct(self):
        self.assertTrue(source_requires_prematch_modal(None, None))
        self.assertTrue(source_requires_prematch_modal(False, MatchDetailMode.QUICK_MATCH))
        self.assertTrue(source_requires_prematch_modal(True, None))
        self.assertFalse(source_requires_prematch_modal(
            True, MatchDetailMode.QUICK_MATCH))
        with self.assertRaisesRegex(RuntimeError, "owner availability is unknown"):
            source_requires_prematch_modal(None, MatchDetailMode.QUICK_MATCH)

    def test_mode_preparation_preserves_three_d_preclear_boundary(self):
        for mode in MatchDetailMode:
            with self.subTest(mode=mode):
                preparation = source_match_mode_preparation(mode)
                self.assertEqual(
                    preparation.clears_context_byte_1145,
                    mode in (MatchDetailMode.THREE_D_MATCH,
                             MatchDetailMode.THREE_D_HIGHLIGHTS),
                )


    def test_original_pre_wrapper_and_post_callbacks_keep_both_native_flag_reads(self):
        from gate14_match_detail_route_source import (
            MATCH_PRE_PRESENTATION_NATIVE_CALL_VA,
            MATCH_POST_PRESENTATION_VIRTUAL_OFFSETS,
            source_original_match_mode_handoff_phase,
        )
        for mode in MatchDetailMode:
            with self.subTest(mode=mode):
                route=source_match_detail_dispatch(mode)
                step=source_original_match_mode_handoff_phase(
                    mode,original_flags_at_513238=0,
                    original_flags_at_513257_if_reached=0x10)
                self.assertEqual(step.pre_presentation_native_call_va,
                                 MATCH_PRE_PRESENTATION_NATIVE_CALL_VA)
                self.assertEqual(step.native_post_virtual_offsets,
                                 MATCH_POST_PRESENTATION_VIRTUAL_OFFSETS)
                self.assertEqual(step.selected_presentation_wrapper_va,
                                 route.presentation_wrapper_va)
                self.assertEqual(step.selected_wrapper_variant,
                                 route.wrapper_variant)
                self.assertFalse(step.native_callbacks_executed)
                self.assertFalse(step.live_match_state_committed)

    def test_original_pre_callback_can_change_presentation_enablement(self):
        from gate14_match_detail_route_source import (
            source_original_match_mode_handoff_phase,
        )
        # Original esi+44 is fetched again at 513257 AFTER 5DA2F0.
        enabled=source_original_match_mode_handoff_phase(
            2,original_flags_at_513238=0,
            original_flags_at_513257_if_reached=0x10)
        disabled=source_original_match_mode_handoff_phase(
            2,original_flags_at_513238=0x10,
            original_flags_at_513257_if_reached=0)
        self.assertEqual(enabled.selected_presentation_wrapper_va,
                         FASTVIEW_PRESENTATION_WRAPPER_VA)
        self.assertIsNone(disabled.selected_presentation_wrapper_va)
        self.assertEqual(disabled.pre_presentation_native_call_va,0x5DA2F0)
        for flags in (0x20,0x30):
            skipped=source_original_match_mode_handoff_phase(
                2,original_flags_at_513238=flags,
                original_flags_at_513257_if_reached=None)
            self.assertIsNone(skipped.pre_presentation_native_call_va)
            self.assertIsNone(skipped.selected_presentation_wrapper_va)
            self.assertEqual(skipped.native_post_virtual_offsets,(0x38,0x3C))

    def test_original_handoff_rejects_guessed_or_unreached_flag_reads(self):
        from gate14_match_detail_route_source import (
            source_original_match_mode_handoff_phase,
        )
        for before,after in ((True,0x10),(-1,0x10),(0x100000000,0x10),
                             (0,None),(0,False),(0,-1),(0,0x100000000),
                             (0x20,0),(0x20,0x10)):
            with self.subTest(before=before,after=after):
                with self.assertRaises(ValueError):
                    source_original_match_mode_handoff_phase(
                        2,original_flags_at_513238=before,
                        original_flags_at_513257_if_reached=after)
        with self.assertRaises(ValueError):
            source_original_match_mode_handoff_phase(
                5,original_flags_at_513238=0,
                original_flags_at_513257_if_reached=0x10)

    def test_optional_original_exe_match_phase_opcode_signatures(self):
        import os
        from pathlib import Path
        from hashlib import sha256
        original=os.environ.get("FM2001_ORIGINAL_EXE")
        if not original:
            self.skipTest("Original executable is private and absent from CI")
        data=Path(original).read_bytes()
        self.assertEqual(sha256(data).hexdigest(),
                         "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        signatures={
            0x513238:"8b 4e 44",0x51323c:"c1 e9 05",0x51323f:"f6 c1 01",
            0x513242:"75 50",0x51324e:"51",0x51324f:"56",
            0x513252:"e8 99 70 0c 00",0x513257:"f6 46 44 10",
            0x51325b:"74 37",0x51325d:"a1 30 75 87 00",
            0x51326a:"48",0x513272:"e8 49 ff 01 00",
            0x51328c:"e8 ef 0a 02 00",0x51329d:"ff 52 38",
            0x5132a9:"ff 52 3c",0x5331fd:"56",
            0x5331fe:"e8 6d 00 00 00",
            0x53322b:"c7 84 24 28 05 00 00 00 00 00 00",
            0x533236:"e8 15 f4 ff ff",0x53323c:"e8 5f 0a 00 00",
        }
        for va,hex_bytes in signatures.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(hex_bytes)
                self.assertEqual(data[va-0x400000:va-0x400000+len(expected)],
                                 expected)



if __name__ == "__main__":
    unittest.main()

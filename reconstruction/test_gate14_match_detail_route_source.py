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


if __name__ == "__main__":
    unittest.main()

"""Tests for the roadmap-aligned Gate-14 readiness audit."""
from dataclasses import replace
import unittest

from gate14_readiness import (
    Gate14ReadinessError,
    canonical_gate14_readiness,
)


class Gate14ReadinessTests(unittest.TestCase):
    def test_canonical_state_keeps_only_satisfied_roadmap_criteria_true(self):
        state = canonical_gate14_readiness()

        self.assertTrue(state.criterion_state_event_consumption)
        self.assertFalse(state.criterion_original_audio_integrated)
        self.assertFalse(state.criterion_recognizable_original_match_presentation)
        self.assertTrue(state.criterion_presentation_does_not_block_management)
        self.assertFalse(state.gate14_ready)

        self.assertTrue(state.completed_human_resolved_fastview_path)
        self.assertTrue(state.operator_visible_resolved_fastview_surface)
        self.assertFalse(state.source_fastview_navigation_trigger_recovered)
        self.assertTrue(state.playerrow_energy_pixels_recovered)
        self.assertTrue(state.playerrow_text_pixels_recovered)
        self.assertTrue(state.score_subpanel_parameterized_construction_recovered)
        self.assertTrue(state.team_subpanel_parameterized_construction_recovered)
        self.assertFalse(state.score_subpanel_complete_pixels_recovered)
        self.assertFalse(state.team_subpanel_complete_pixels_recovered)
        self.assertTrue(state.possession_pairwise_draw_order_recovered)
        self.assertTrue(state.goalflash_source_contract_recovered)
        self.assertFalse(state.goalflash_absolute_position_recovered)
        self.assertFalse(state.goalflash_pixels_rasterized)
        self.assertTrue(state.scorecomposite_main_source_contract_recovered)
        self.assertFalse(state.scorecomposite_main_geometry_recovered)
        self.assertFalse(state.scorecomposite_main_pixels_rasterized)
        self.assertTrue(state.embedded_outer_controls_source_contract_recovered)
        self.assertFalse(state.embedded_outer_controls_geometry_recovered)
        self.assertFalse(state.embedded_outer_controls_pixels_rasterized)
        self.assertTrue(state.font_blend_rule_recovered)
        self.assertTrue(state.audio_bank_ownership_recovered)
        self.assertTrue(state.audio_playback_entrypoints_recovered)
        self.assertTrue(state.audio_sample_decode_ready)
        self.assertTrue(state.first_screen_press_audio_bound)
        self.assertTrue(state.startup_media_default_windows_path_integrated)
        self.assertFalse(state.startup_media_real_windows_verified)
        self.assertFalse(state.audible_windows_verified)
        self.assertTrue(state.chant_runtime_selection_recovered)
        self.assertTrue(state.chant_runtime_timing_recovered)

    def test_canonical_blockers_name_only_unresolved_capabilities(self):
        blockers = canonical_gate14_readiness().blockers
        self.assertEqual(
            blockers,
            (
                "audio_event_binding",
                "audible_windows_output",
                "login_menu_audio_integration",
                "score_subpanel_complete_pixels",
                "team_subpanel_complete_pixels",
                "goalflash_absolute_position",
                "goalflash_rasterization",
                "scorecomposite_main_geometry",
                "scorecomposite_main_rasterization",
                "embedded_outer_controls_geometry",
                "embedded_outer_controls_rasterization",
                "global_fastview_z_order",
                "complete_fastview_frame",
                "chant_event_semantics",
                "3d_choreography",
                "recognizable_original_match_workflow",
            ),
        )

    def test_new_capability_flags_keep_their_own_prerequisites_fail_closed(self):
        state = canonical_gate14_readiness()

        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "operator-visible FastView surface",
        ):
            replace(
                state,
                completed_human_resolved_fastview_path=False,
            )

        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "source FastView navigation trigger",
        ):
            replace(
                state,
                operator_visible_resolved_fastview_surface=False,
                source_fastview_navigation_trigger_recovered=True,
            )

        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "first-screen press audio binding",
        ):
            replace(
                state,
                audio_sample_decode_ready=False,
            )

        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "startup-media Windows acceptance",
        ):
            replace(
                state,
                startup_media_default_windows_path_integrated=False,
                startup_media_real_windows_verified=True,
            )

    def test_audio_integration_cannot_bypass_decode_prerequisites(self):
        state = canonical_gate14_readiness()
        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "audio integration cannot precede",
        ):
            replace(
                state,
                audio_sample_decode_ready=False,
                login_menu_audio_integrated=True,
            )

    def test_audio_integration_requires_binding_and_audible_windows_evidence(self):
        state = canonical_gate14_readiness()

        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "event binding, and audible Windows verification",
        ):
            replace(
                state,
                audio_event_binding_recovered=True,
                login_menu_audio_integrated=True,
            )

        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "event binding, and audible Windows verification",
        ):
            replace(
                state,
                audible_windows_verified=True,
                login_menu_audio_integrated=True,
            )

    def test_audible_windows_evidence_alone_does_not_promote_audio_integration(self):
        state = canonical_gate14_readiness()
        audible = replace(state, audible_windows_verified=True)

        self.assertTrue(audible.audible_windows_verified)
        self.assertFalse(audible.audio_event_binding_recovered)
        self.assertFalse(audible.login_menu_audio_integrated)
        self.assertFalse(audible.criterion_original_audio_integrated)
        self.assertFalse(audible.gate14_ready)

    def test_complete_frame_cannot_bypass_raster_prerequisites(self):
        state = canonical_gate14_readiness()
        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "complete FastView frame cannot bypass",
        ):
            replace(state, complete_fastview_frame_recovered=True)

    def test_complete_frame_requires_goalflash_position_and_pixels(self):
        state = canonical_gate14_readiness()
        otherwise_ready = replace(
            state,
            score_subpanel_complete_pixels_recovered=True,
            team_subpanel_complete_pixels_recovered=True,
            scorecomposite_main_geometry_recovered=True,
            scorecomposite_main_pixels_rasterized=True,
            embedded_outer_controls_geometry_recovered=True,
            embedded_outer_controls_pixels_rasterized=True,
            global_fastview_z_order_recovered=True,
        )
        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "complete FastView frame cannot bypass",
        ):
            replace(
                otherwise_ready,
                complete_fastview_frame_recovered=True,
            )

        position_only = replace(
            otherwise_ready,
            goalflash_absolute_position_recovered=True,
        )
        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "complete FastView frame cannot bypass",
        ):
            replace(
                position_only,
                complete_fastview_frame_recovered=True,
            )

    def test_complete_frame_requires_scorecomposite_main_geometry_and_pixels(self):
        state = canonical_gate14_readiness()
        otherwise_ready = replace(
            state,
            score_subpanel_complete_pixels_recovered=True,
            team_subpanel_complete_pixels_recovered=True,
            goalflash_absolute_position_recovered=True,
            goalflash_pixels_rasterized=True,
            embedded_outer_controls_geometry_recovered=True,
            embedded_outer_controls_pixels_rasterized=True,
            global_fastview_z_order_recovered=True,
        )
        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "complete FastView frame cannot bypass",
        ):
            replace(
                otherwise_ready,
                complete_fastview_frame_recovered=True,
            )

        geometry_only = replace(
            otherwise_ready,
            scorecomposite_main_geometry_recovered=True,
        )
        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "complete FastView frame cannot bypass",
        ):
            replace(
                geometry_only,
                complete_fastview_frame_recovered=True,
            )

    def test_complete_frame_requires_embedded_outer_control_geometry_and_pixels(self):
        state = canonical_gate14_readiness()
        otherwise_ready = replace(
            state,
            score_subpanel_complete_pixels_recovered=True,
            team_subpanel_complete_pixels_recovered=True,
            goalflash_absolute_position_recovered=True,
            goalflash_pixels_rasterized=True,
            scorecomposite_main_geometry_recovered=True,
            scorecomposite_main_pixels_rasterized=True,
            global_fastview_z_order_recovered=True,
        )
        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "complete FastView frame cannot bypass",
        ):
            replace(
                otherwise_ready,
                complete_fastview_frame_recovered=True,
            )

        geometry_only = replace(
            otherwise_ready,
            embedded_outer_controls_geometry_recovered=True,
        )
        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "complete FastView frame cannot bypass",
        ):
            replace(
                geometry_only,
                complete_fastview_frame_recovered=True,
            )

    def test_complete_frame_requires_both_nested_subpanels_pixel_complete(self):
        state = canonical_gate14_readiness()
        otherwise_ready = replace(
            state,
            goalflash_absolute_position_recovered=True,
            goalflash_pixels_rasterized=True,
            scorecomposite_main_geometry_recovered=True,
            scorecomposite_main_pixels_rasterized=True,
            embedded_outer_controls_geometry_recovered=True,
            embedded_outer_controls_pixels_rasterized=True,
            global_fastview_z_order_recovered=True,
        )

        for field in (
            "score_subpanel_complete_pixels_recovered",
            "team_subpanel_complete_pixels_recovered",
        ):
            with self.subTest(field=field):
                one_nested_family_only = replace(
                    otherwise_ready,
                    **{field: True},
                )
                with self.assertRaisesRegex(
                    Gate14ReadinessError,
                    "complete FastView frame cannot bypass",
                ):
                    replace(
                        one_nested_family_only,
                        complete_fastview_frame_recovered=True,
                    )

        complete_nested = replace(
            otherwise_ready,
            score_subpanel_complete_pixels_recovered=True,
            team_subpanel_complete_pixels_recovered=True,
            complete_fastview_frame_recovered=True,
        )
        self.assertTrue(complete_nested.complete_fastview_frame_recovered)

    def test_recognizable_workflow_cannot_be_asserted_without_completed_path(self):
        state = canonical_gate14_readiness()
        with self.assertRaisesRegex(
            Gate14ReadinessError,
            "recognizable original workflow requires",
        ):
            replace(state, recognizable_original_match_workflow_verified=True)

    def test_full_completion_requires_all_four_roadmap_criteria(self):
        state = canonical_gate14_readiness()
        completed = replace(
            state,
            score_subpanel_complete_pixels_recovered=True,
            team_subpanel_complete_pixels_recovered=True,
            goalflash_absolute_position_recovered=True,
            goalflash_pixels_rasterized=True,
            scorecomposite_main_geometry_recovered=True,
            scorecomposite_main_pixels_rasterized=True,
            embedded_outer_controls_geometry_recovered=True,
            embedded_outer_controls_pixels_rasterized=True,
            global_fastview_z_order_recovered=True,
            font_blend_rule_recovered=True,
            complete_fastview_frame_recovered=True,
            source_fastview_navigation_trigger_recovered=True,
            audio_sample_decode_ready=True,
            audio_event_binding_recovered=True,
            startup_media_real_windows_verified=True,
            audible_windows_verified=True,
            login_menu_audio_integrated=True,
            chant_event_semantics_recovered=True,
            choreography_3d_recovered=True,
            recognizable_original_match_workflow_verified=True,
        )
        self.assertTrue(completed.criterion_state_event_consumption)
        self.assertTrue(completed.criterion_original_audio_integrated)
        self.assertTrue(completed.criterion_recognizable_original_match_presentation)
        self.assertTrue(completed.criterion_presentation_does_not_block_management)
        self.assertTrue(completed.gate14_ready)
        self.assertEqual(completed.blockers, ())


if __name__ == "__main__":
    unittest.main()

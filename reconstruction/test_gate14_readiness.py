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
        self.assertTrue(state.playerrow_energy_pixels_recovered)
        self.assertTrue(state.playerrow_text_pixels_recovered)
        self.assertTrue(state.possession_pairwise_draw_order_recovered)
        self.assertTrue(state.goalflash_source_contract_recovered)
        self.assertFalse(state.goalflash_absolute_position_recovered)
        self.assertFalse(state.goalflash_pixels_rasterized)
        self.assertTrue(state.scorecomposite_main_source_contract_recovered)
        self.assertFalse(state.scorecomposite_main_geometry_recovered)
        self.assertFalse(state.scorecomposite_main_pixels_rasterized)
        self.assertTrue(state.font_blend_rule_recovered)
        self.assertTrue(state.audio_bank_ownership_recovered)
        self.assertTrue(state.audio_playback_entrypoints_recovered)
        self.assertTrue(state.audio_sample_decode_ready)
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
                "goalflash_absolute_position",
                "goalflash_rasterization",
                "scorecomposite_main_geometry",
                "scorecomposite_main_rasterization",
                "global_fastview_z_order",
                "complete_fastview_frame",
                "chant_event_semantics",
                "3d_choreography",
                "recognizable_original_match_workflow",
            ),
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
            goalflash_absolute_position_recovered=True,
            goalflash_pixels_rasterized=True,
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
            goalflash_absolute_position_recovered=True,
            goalflash_pixels_rasterized=True,
            scorecomposite_main_geometry_recovered=True,
            scorecomposite_main_pixels_rasterized=True,
            global_fastview_z_order_recovered=True,
            font_blend_rule_recovered=True,
            complete_fastview_frame_recovered=True,
            audio_sample_decode_ready=True,
            audio_event_binding_recovered=True,
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

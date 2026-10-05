"""Fail-closed Gate-14 readiness audit aligned to ROADMAP.md.

The audit exposes the four official Gate-14 completion criteria and the concrete
source-backed capabilities beneath them. It does not infer readiness from the
presence of tooling alone and cannot mark Gate 14 complete while audio decode /
event binding or recognizable full-match presentation remain unresolved.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate14ReadinessError(ValueError):
    pass


@dataclass(frozen=True)
class Gate14ReadinessEvidence:
    match_presentation_consumes_reconstructed_events: bool
    presentation_separated_from_core_management: bool

    completed_human_resolved_fastview_path: bool
    operator_visible_resolved_fastview_surface: bool
    source_fastview_navigation_trigger_recovered: bool
    playerrow_energy_pixels_recovered: bool
    playerrow_text_pixels_recovered: bool
    score_subpanel_parameterized_construction_recovered: bool
    team_subpanel_parameterized_construction_recovered: bool
    score_subpanel_complete_pixels_recovered: bool
    team_subpanel_complete_pixels_recovered: bool
    possession_pairwise_draw_order_recovered: bool
    goalflash_source_contract_recovered: bool
    goalflash_absolute_position_recovered: bool
    goalflash_pixels_rasterized: bool
    scorecomposite_main_source_contract_recovered: bool
    scorecomposite_main_geometry_recovered: bool
    scorecomposite_main_pixels_rasterized: bool
    embedded_outer_controls_source_contract_recovered: bool
    embedded_outer_controls_geometry_recovered: bool
    embedded_outer_controls_pixels_rasterized: bool
    global_fastview_z_order_recovered: bool
    font_blend_rule_recovered: bool
    complete_fastview_frame_recovered: bool

    audio_bank_ownership_recovered: bool
    audio_playback_entrypoints_recovered: bool
    audio_sample_decode_ready: bool
    first_screen_press_audio_bound: bool
    first_screen_press_audio_windows_acceptance_tooling: bool
    first_screen_press_audio_real_windows_verified: bool
    startup_media_default_windows_path_integrated: bool
    startup_media_windows_acceptance_tooling: bool
    startup_media_real_windows_verified: bool
    audio_event_binding_recovered: bool
    audible_windows_verified: bool
    login_menu_audio_integrated: bool

    chant_runtime_selection_recovered: bool
    chant_runtime_timing_recovered: bool
    chant_event_semantics_recovered: bool

    choreography_3d_recovered: bool
    recognizable_original_match_workflow_verified: bool

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if type(value) is not bool:
                raise Gate14ReadinessError(f"{name} must be boolean")

        if self.operator_visible_resolved_fastview_surface and not (
            self.completed_human_resolved_fastview_path
        ):
            raise Gate14ReadinessError(
                "operator-visible FastView surface requires completed-human resolved path"
            )
        if self.source_fastview_navigation_trigger_recovered and not (
            self.operator_visible_resolved_fastview_surface
        ):
            raise Gate14ReadinessError(
                "source FastView navigation trigger requires operator-visible surface"
            )
        if self.first_screen_press_audio_bound and not (
            self.audio_bank_ownership_recovered
            and self.audio_playback_entrypoints_recovered
            and self.audio_sample_decode_ready
        ):
            raise Gate14ReadinessError(
                "first-screen press audio binding requires source-backed bank/playback/decode"
            )
        if self.first_screen_press_audio_windows_acceptance_tooling and not (
            self.first_screen_press_audio_bound
        ):
            raise Gate14ReadinessError(
                "first-screen audio Windows acceptance tooling requires the bound runtime path"
            )
        if self.first_screen_press_audio_real_windows_verified and not (
            self.first_screen_press_audio_bound
            and self.first_screen_press_audio_windows_acceptance_tooling
        ):
            raise Gate14ReadinessError(
                "first-screen audio Windows acceptance requires bound runtime tooling"
            )
        if self.startup_media_windows_acceptance_tooling and not (
            self.startup_media_default_windows_path_integrated
        ):
            raise Gate14ReadinessError(
                "startup-media Windows acceptance tooling requires the default runtime path"
            )
        if self.startup_media_real_windows_verified and not (
            self.startup_media_default_windows_path_integrated
            and self.startup_media_windows_acceptance_tooling
        ):
            raise Gate14ReadinessError(
                "startup-media Windows acceptance requires default runtime tooling"
            )

        if self.login_menu_audio_integrated and not (
            self.audio_bank_ownership_recovered
            and self.audio_playback_entrypoints_recovered
            and self.audio_sample_decode_ready
            and self.audio_event_binding_recovered
            and self.audible_windows_verified
        ):
            raise Gate14ReadinessError(
                "login/menu audio integration cannot precede source-backed decode, "
                "event binding, and audible Windows verification"
            )
        if self.complete_fastview_frame_recovered and not (
            self.completed_human_resolved_fastview_path
            and self.playerrow_energy_pixels_recovered
            and self.playerrow_text_pixels_recovered
            and self.score_subpanel_parameterized_construction_recovered
            and self.team_subpanel_parameterized_construction_recovered
            and self.score_subpanel_complete_pixels_recovered
            and self.team_subpanel_complete_pixels_recovered
            and self.goalflash_source_contract_recovered
            and self.goalflash_absolute_position_recovered
            and self.goalflash_pixels_rasterized
            and self.scorecomposite_main_source_contract_recovered
            and self.scorecomposite_main_geometry_recovered
            and self.scorecomposite_main_pixels_rasterized
            and self.embedded_outer_controls_source_contract_recovered
            and self.embedded_outer_controls_geometry_recovered
            and self.embedded_outer_controls_pixels_rasterized
            and self.global_fastview_z_order_recovered
            and self.font_blend_rule_recovered
        ):
            raise Gate14ReadinessError(
                "complete FastView frame cannot bypass unresolved raster prerequisites"
            )
        if self.recognizable_original_match_workflow_verified and not (
            self.complete_fastview_frame_recovered
            or self.choreography_3d_recovered
        ):
            raise Gate14ReadinessError(
                "recognizable original workflow requires a completed source-backed match presentation path"
            )

    @property
    def criterion_state_event_consumption(self) -> bool:
        return self.match_presentation_consumes_reconstructed_events

    @property
    def criterion_original_audio_integrated(self) -> bool:
        return (
            self.login_menu_audio_integrated
            and self.audio_sample_decode_ready
            and self.audio_event_binding_recovered
            and self.audible_windows_verified
        )

    @property
    def criterion_recognizable_original_match_presentation(self) -> bool:
        return self.recognizable_original_match_workflow_verified

    @property
    def criterion_presentation_does_not_block_management(self) -> bool:
        return self.presentation_separated_from_core_management

    @property
    def gate14_ready(self) -> bool:
        return all(
            (
                self.criterion_state_event_consumption,
                self.criterion_original_audio_integrated,
                self.criterion_recognizable_original_match_presentation,
                self.criterion_presentation_does_not_block_management,
            )
        )

    @property
    def blockers(self) -> tuple[str, ...]:
        blockers: list[str] = []
        if not self.audio_sample_decode_ready:
            blockers.append("audio_sample_decode")
        if not self.first_screen_press_audio_real_windows_verified:
            blockers.append("first_screen_press_audio_real_windows_acceptance")
        if not self.startup_media_real_windows_verified:
            blockers.append("startup_media_real_windows_acceptance")
        if not self.audio_event_binding_recovered:
            blockers.append("audio_event_binding")
        if not self.audible_windows_verified:
            blockers.append("audible_windows_output")
        if not self.login_menu_audio_integrated:
            blockers.append("login_menu_audio_integration")
        if not self.score_subpanel_complete_pixels_recovered:
            blockers.append("score_subpanel_complete_pixels")
        if not self.team_subpanel_complete_pixels_recovered:
            blockers.append("team_subpanel_complete_pixels")
        if not self.goalflash_source_contract_recovered:
            blockers.append("goalflash_source_contract")
        if not self.goalflash_absolute_position_recovered:
            blockers.append("goalflash_absolute_position")
        if not self.goalflash_pixels_rasterized:
            blockers.append("goalflash_rasterization")
        if not self.scorecomposite_main_source_contract_recovered:
            blockers.append("scorecomposite_main_source_contract")
        if not self.scorecomposite_main_geometry_recovered:
            blockers.append("scorecomposite_main_geometry")
        if not self.scorecomposite_main_pixels_rasterized:
            blockers.append("scorecomposite_main_rasterization")
        if not self.embedded_outer_controls_source_contract_recovered:
            blockers.append("embedded_outer_controls_source_contract")
        if not self.embedded_outer_controls_geometry_recovered:
            blockers.append("embedded_outer_controls_geometry")
        if not self.embedded_outer_controls_pixels_rasterized:
            blockers.append("embedded_outer_controls_rasterization")
        if not self.global_fastview_z_order_recovered:
            blockers.append("global_fastview_z_order")
        if not self.font_blend_rule_recovered:
            blockers.append("font_blend_rule")
        if not self.complete_fastview_frame_recovered:
            blockers.append("complete_fastview_frame")
        if not self.chant_event_semantics_recovered:
            blockers.append("chant_event_semantics")
        if not self.choreography_3d_recovered:
            blockers.append("3d_choreography")
        if not self.recognizable_original_match_workflow_verified:
            blockers.append("recognizable_original_match_workflow")
        return tuple(blockers)


def canonical_gate14_readiness() -> Gate14ReadinessEvidence:
    """Return only facts already canonical on main at this checkpoint."""
    return Gate14ReadinessEvidence(
        match_presentation_consumes_reconstructed_events=True,
        presentation_separated_from_core_management=True,

        completed_human_resolved_fastview_path=True,
        operator_visible_resolved_fastview_surface=True,
        source_fastview_navigation_trigger_recovered=False,
        playerrow_energy_pixels_recovered=True,
        playerrow_text_pixels_recovered=True,
        score_subpanel_parameterized_construction_recovered=True,
        team_subpanel_parameterized_construction_recovered=True,
        score_subpanel_complete_pixels_recovered=False,
        team_subpanel_complete_pixels_recovered=False,
        possession_pairwise_draw_order_recovered=True,
        goalflash_source_contract_recovered=True,
        goalflash_absolute_position_recovered=False,
        goalflash_pixels_rasterized=False,
        scorecomposite_main_source_contract_recovered=True,
        scorecomposite_main_geometry_recovered=False,
        scorecomposite_main_pixels_rasterized=False,
        embedded_outer_controls_source_contract_recovered=True,
        embedded_outer_controls_geometry_recovered=False,
        embedded_outer_controls_pixels_rasterized=False,
        global_fastview_z_order_recovered=False,
        font_blend_rule_recovered=True,
        complete_fastview_frame_recovered=False,

        audio_bank_ownership_recovered=True,
        audio_playback_entrypoints_recovered=True,
        audio_sample_decode_ready=True,
        first_screen_press_audio_bound=True,
        first_screen_press_audio_windows_acceptance_tooling=True,
        first_screen_press_audio_real_windows_verified=False,
        startup_media_default_windows_path_integrated=True,
        startup_media_windows_acceptance_tooling=True,
        startup_media_real_windows_verified=False,
        audio_event_binding_recovered=False,
        audible_windows_verified=False,
        login_menu_audio_integrated=False,

        chant_runtime_selection_recovered=True,
        chant_runtime_timing_recovered=True,
        chant_event_semantics_recovered=False,

        choreography_3d_recovered=False,
        recognizable_original_match_workflow_verified=False,
    )

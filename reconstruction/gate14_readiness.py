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
    playerrow_energy_pixels_recovered: bool
    playerrow_text_pixels_recovered: bool
    possession_pairwise_draw_order_recovered: bool
    global_fastview_z_order_recovered: bool
    font_blend_rule_recovered: bool
    complete_fastview_frame_recovered: bool

    audio_bank_ownership_recovered: bool
    audio_playback_entrypoints_recovered: bool
    audio_sample_decode_ready: bool
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
        if not self.audio_event_binding_recovered:
            blockers.append("audio_event_binding")
        if not self.audible_windows_verified:
            blockers.append("audible_windows_output")
        if not self.login_menu_audio_integrated:
            blockers.append("login_menu_audio_integration")
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
        playerrow_energy_pixels_recovered=True,
        playerrow_text_pixels_recovered=True,
        possession_pairwise_draw_order_recovered=True,
        global_fastview_z_order_recovered=False,
        font_blend_rule_recovered=False,
        complete_fastview_frame_recovered=False,

        audio_bank_ownership_recovered=True,
        audio_playback_entrypoints_recovered=True,
        audio_sample_decode_ready=True,
        audio_event_binding_recovered=False,
        audible_windows_verified=False,
        login_menu_audio_integrated=False,

        chant_runtime_selection_recovered=True,
        chant_runtime_timing_recovered=True,
        chant_event_semantics_recovered=False,

        choreography_3d_recovered=False,
        recognizable_original_match_workflow_verified=False,
    )

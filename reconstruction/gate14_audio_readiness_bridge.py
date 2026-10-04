"""Gate-14 readiness bridge for strictly validated Windows menu-audio evidence."""
from __future__ import annotations

from dataclasses import replace
from typing import Mapping

from gate14_readiness import Gate14ReadinessEvidence, Gate14ReadinessError
from gate14_windows_menu_audio_receipt import (
    Gate14WindowsMenuAudioReceiptError,
    validate_windows_menu_audio_receipt,
)


_REQUIRED_VALIDATION_TRUE = (
    "passed",
    "source_bank_verified",
    "deterministic_numeric_route_replay_verified",
    "prior_human_audibility_receipt_accepted",
    "audible_windows_verified",
)
_REQUIRED_VALIDATION_FALSE = (
    "new_device_audibility_replayed",
    "semantic_event_binding_recovered",
    "sample_meaning_recovered",
    "modern_ui_event_equivalence_recovered",
    "login_menu_audio_integrated",
    "gate14_complete",
)


def apply_validated_windows_menu_audio_receipt(
    readiness: Gate14ReadinessEvidence,
    receipt: Mapping[str, object],
    menus_bnk: bytes,
) -> Gate14ReadinessEvidence:
    """Advance only audible-Windows readiness after strict canonical replay.

    The bridge deliberately takes the original private receipt plus canonical
    menus.bnk bytes and invokes the canonical strict validator itself. It does
    not accept a caller-supplied "already validated" dictionary as evidence.

    Semantic event binding, login/menu integration, FastView state, and all
    other readiness capabilities are preserved exactly.
    """
    if type(readiness) is not Gate14ReadinessEvidence:
        raise Gate14ReadinessError(
            "audio readiness bridge requires exact Gate14ReadinessEvidence"
        )

    try:
        validation = validate_windows_menu_audio_receipt(receipt, menus_bnk)
    except Gate14WindowsMenuAudioReceiptError as exc:
        raise Gate14ReadinessError(
            "audio readiness bridge rejected Windows menu-audio evidence"
        ) from exc

    if type(validation) is not dict:
        raise Gate14ReadinessError(
            "strict Windows menu-audio validator returned unexpected evidence type"
        )
    for field in _REQUIRED_VALIDATION_TRUE:
        if type(validation.get(field)) is not bool or validation[field] is not True:
            raise Gate14ReadinessError(
                f"strict Windows menu-audio validation field {field} must be true"
            )
    for field in _REQUIRED_VALIDATION_FALSE:
        if type(validation.get(field)) is not bool or validation[field] is not False:
            raise Gate14ReadinessError(
                f"strict Windows menu-audio validation field {field} must be false"
            )

    advanced = replace(readiness, audible_windows_verified=True)

    preserved_fields = (
        "audio_event_binding_recovered",
        "login_menu_audio_integrated",
        "global_fastview_z_order_recovered",
        "font_blend_rule_recovered",
        "complete_fastview_frame_recovered",
        "chant_event_semantics_recovered",
        "choreography_3d_recovered",
        "recognizable_original_match_workflow_verified",
    )
    for field in preserved_fields:
        if getattr(advanced, field) is not getattr(readiness, field):
            raise Gate14ReadinessError(
                f"audio readiness bridge attempted to promote unrelated field {field}"
            )
    return advanced

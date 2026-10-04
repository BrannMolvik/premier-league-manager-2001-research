"""Bounded Gate-14 readiness bridge for replay-validated audible evidence."""
from __future__ import annotations

from dataclasses import replace

from gate14_readiness import Gate14ReadinessEvidence, Gate14ReadinessError
from gate14_windows_menu_audio_receipt import VerifiedWindowsMenuAudioReceipt


def apply_verified_windows_menu_audio_receipt(
    readiness: Gate14ReadinessEvidence,
    receipt: VerifiedWindowsMenuAudioReceipt,
) -> Gate14ReadinessEvidence:
    """Advance only the audible-Windows capability from a strict receipt replay.

    Semantic event binding, login/menu integration, FastView fidelity and all
    unrelated Gate-14 capabilities are preserved exactly from the input state.
    """
    if type(readiness) is not Gate14ReadinessEvidence:
        raise Gate14ReadinessError(
            "readiness bridge requires exact Gate14ReadinessEvidence"
        )
    if type(receipt) is not VerifiedWindowsMenuAudioReceipt:
        raise Gate14ReadinessError(
            "readiness bridge requires replay-validated Windows menu-audio receipt"
        )
    if not receipt.audible_windows_verified:
        raise Gate14ReadinessError(
            "validated menu-audio receipt lacks audible Windows evidence"
        )

    advanced = replace(
        readiness,
        audible_windows_verified=True,
    )
    if (
        advanced.audio_event_binding_recovered
        != readiness.audio_event_binding_recovered
        or advanced.login_menu_audio_integrated
        != readiness.login_menu_audio_integrated
        or advanced.gate14_ready
        and not readiness.gate14_ready
    ):
        # The final guard is intentionally redundant with the field-preservation
        # checks: one audible receipt must never complete Gate 14 by itself.
        raise Gate14ReadinessError(
            "audible receipt bridge attempted to promote unrelated Gate-14 state"
        )
    return advanced

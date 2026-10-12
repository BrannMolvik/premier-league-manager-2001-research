"""Source-bounded original Win32 row candidate -> observed row input -> editor.

This is a pure transaction boundary, not a Tk event, a substitute for
native input observations, or a live original DBRUser/GameState update.

Canonical original footballmanager.exe private SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Source 0x531F70/0x653B40/0x653480 -> 0x5D6270/0x5D4790,
0x64F7A0 input bit gates, PSupportStart owner+0x0C 0x42DE00,
row+0x98 bit15, native event IDs8..14 (NOT Apply2/Cancel1).

A geometry candidate alone MUST NEVER flip a row or commit staff.
The caller must also present the actual callback result / source row
identity receipt from project_original_supportstart_row_native_dispatch.
Other native global input observers and live shared CRT still require
source verification before this may be wired to the production game.
"""
from __future__ import annotations

from dataclasses import dataclass

from original_supportstart_editor_projection import OriginalSupportStartEditorProjection
from original_supportstart_input import (
    OriginalSupportStartRowNativeDispatchObservation,
    original_supportstart_row_callback_contract,
)
from original_supportstart_pointer_candidate import SourceSupportStartPointerCandidate


class OriginalSupportStartPointerObservationError(ValueError):
    """No original-qualified row event can be committed at this boundary."""


@dataclass(frozen=True)
class OriginalSupportStartPointerObservationReceipt:
    source_row_index: int
    native_event_id: int
    native_row_input_accepted: bool
    editor_after_observed_input: OriginalSupportStartEditorProjection


def project_original_supportstart_observed_pointer_row_input(
    editor: OriginalSupportStartEditorProjection,
    *,
    original_window_candidate: SourceSupportStartPointerCandidate,
    observed_native_input: OriginalSupportStartRowNativeDispatchObservation,
) -> OriginalSupportStartPointerObservationReceipt:
    """Compose exact native row candidate and separate actual input observation.

    Source window may emit only a CANDIDATE for native row+0x6C, not
    accepted mouse event. Requires a single source row candidate
    (no fabricated order for overlapping native selectors), actual
    source callback observation from THAT row, equal pre-event
    control DWORDs and exact original row eventID8..14.
    A rejected original input is a no-op; an accepted input updates
    the immutable source-only editor's bit15 state. It NEVER calls
    editor.close(2), changes GameState, or advances the original CRT.
    """
    if type(editor) is not OriginalSupportStartEditorProjection:
        raise TypeError("Require original source seven-row editor")
    if type(original_window_candidate) is not SourceSupportStartPointerCandidate:
        raise TypeError("Require previously source-qualified Win32 row candidate")
    if type(observed_native_input) is not OriginalSupportStartRowNativeDispatchObservation:
        raise TypeError("Require separate original native callback observation")
    if (not original_window_candidate.source_modal_window_reached
            or original_window_candidate.native_row_event_accepted):
        raise OriginalSupportStartPointerObservationError(
            "Window dispatch must be a modal candidate, not an invented accepted event"
        )
    ids = original_window_candidate.source_candidate_row_indices
    if type(ids) is not tuple or len(ids) != 1:
        raise OriginalSupportStartPointerObservationError(
            "Require exactly one original registered selector hit candidate"
        )
    index = ids[0]
    if type(index) is not int or not 0 <= index < 7:
        raise OriginalSupportStartPointerObservationError("Unknown native row identity")
    contract = original_supportstart_row_callback_contract(index)
    if original_window_candidate.source_candidate_native_control_ids != (
        contract.original_native_control_event_id,
    ):
        raise OriginalSupportStartPointerObservationError(
            "Native modal selector event ID mismatched source row"
        )
    if observed_native_input.source_row_index != index:
        raise OriginalSupportStartPointerObservationError(
            "Native input observation belongs to another original row"
        )
    if observed_native_input.source_row_before != editor.rows[index]:
        raise OriginalSupportStartPointerObservationError(
            "Native input observation based on stale row flags"
        )
    if not observed_native_input.native_handler_accepted:
        if (observed_native_input.source_post_virtual_gate_row != editor.rows[index]
                or observed_native_input.source_after_row_bit15_toggle != editor.rows[index]):
            raise OriginalSupportStartPointerObservationError(
                "Rejected native callback cannot mutate original row controls"
            )
        return OriginalSupportStartPointerObservationReceipt(
            index, contract.original_native_control_event_id, False, editor,
        )
    updated = editor.with_observed_native_row_input(index, observed_native_input)
    return OriginalSupportStartPointerObservationReceipt(
        index, contract.original_native_control_event_id, True, updated,
    )

"""Fail-closed Gate-17 audit of source-proven multi-human capability.

The original TeamSelect path is source-proven to append human users and enforce
an absolute global cap of six. This module does not implement that gameplay
surface. It records whether the current clean-room layers can carry the same
simultaneous-user contract through selection, Start, shared runtime ownership
and internal save/reload.

The current canonical runner intentionally reports the repository boundary:
TeamSelect can retain six ordered selections, while the gameplay controller,
Start handoff and save schema still model one HumanManagerState.
"""
from __future__ import annotations

from dataclasses import dataclass


ORIGINAL_MAX_SIMULTANEOUS_HUMAN_USERS = 6


class Gate17MultiHumanCapabilityError(RuntimeError):
    pass


@dataclass(frozen=True)
class MultiHumanCapabilityAudit:
    required_simultaneous_users: int
    teamselect_selection_capacity: int
    gameplay_simultaneous_users_supported: int
    multi_human_start_supported: bool
    shared_runtime_supported: bool
    save_reload_supported: bool
    blocker_codes: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.blocker_codes

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "required_simultaneous_users": self.required_simultaneous_users,
            "teamselect_selection_capacity": self.teamselect_selection_capacity,
            "gameplay_simultaneous_users_supported": (
                self.gameplay_simultaneous_users_supported
            ),
            "multi_human_start_supported": self.multi_human_start_supported,
            "shared_runtime_supported": self.shared_runtime_supported,
            "save_reload_supported": self.save_reload_supported,
            "blocker_codes": list(self.blocker_codes),
            "complete": self.complete,
        }


def audit_multi_human_capability(
    *,
    teamselect_selection_capacity: int,
    gameplay_simultaneous_users_supported: int,
    multi_human_start_supported: bool,
    shared_runtime_supported: bool,
    save_reload_supported: bool,
    required_simultaneous_users: int = ORIGINAL_MAX_SIMULTANEOUS_HUMAN_USERS,
) -> MultiHumanCapabilityAudit:
    """Measure implementation capability against the recovered six-user contract."""
    values = {
        "required_simultaneous_users": required_simultaneous_users,
        "teamselect_selection_capacity": teamselect_selection_capacity,
        "gameplay_simultaneous_users_supported": gameplay_simultaneous_users_supported,
    }
    for label, value in values.items():
        if type(value) is not int or value <= 0:
            raise Gate17MultiHumanCapabilityError(
                f"{label} must be an exact positive integer"
            )
    for label, value in {
        "multi_human_start_supported": multi_human_start_supported,
        "shared_runtime_supported": shared_runtime_supported,
        "save_reload_supported": save_reload_supported,
    }.items():
        if type(value) is not bool:
            raise Gate17MultiHumanCapabilityError(
                f"{label} must be an exact boolean"
            )

    required = int(required_simultaneous_users)
    selection_capacity = int(teamselect_selection_capacity)
    gameplay_capacity = int(gameplay_simultaneous_users_supported)
    blockers: list[str] = []
    if selection_capacity < required:
        blockers.append("teamselect_multi_human_selection_incomplete")
    if gameplay_capacity < required:
        blockers.append("multi_human_gameplay_capacity_incomplete")
    if not multi_human_start_supported:
        blockers.append("multi_human_start_missing")
    if not shared_runtime_supported:
        blockers.append("shared_multi_human_runtime_missing")
    if not save_reload_supported:
        blockers.append("multi_human_save_reload_missing")

    return MultiHumanCapabilityAudit(
        required_simultaneous_users=required,
        teamselect_selection_capacity=selection_capacity,
        gameplay_simultaneous_users_supported=gameplay_capacity,
        multi_human_start_supported=multi_human_start_supported,
        shared_runtime_supported=shared_runtime_supported,
        save_reload_supported=save_reload_supported,
        blocker_codes=tuple(blockers),
    )


def run_current_multi_human_capability() -> MultiHumanCapabilityAudit:
    """Report the current repository's known multi-human implementation surface.

    Source-backed TeamSelect already retains up to six ordered club selections.
    FrontEndSession deliberately refuses Start for more than one selected user;
    HumanGameplayController and schema-43 internal saves each contain one
    HumanManagerState. Those are implementation facts, not inferred original
    behavior.
    """
    return audit_multi_human_capability(
        teamselect_selection_capacity=6,
        gameplay_simultaneous_users_supported=1,
        multi_human_start_supported=False,
        shared_runtime_supported=False,
        save_reload_supported=False,
    )

"""Fail-closed adjudication plan for Gate-17 secondary ScheduleContainer ownership.

This module consumes the neutral private trace contract produced by
gate17_secondary_owner_source_trace.py and turns it into a deterministic
source-inspection plan. It never upgrades candidate CALL sites or raw address
occurrences into runtime semantics.

The plan separates four proofs that must each be established independently:
ordinary/daily runtime ownership, season continuation/finalization, human match
dispatch, and save/reload persistence. Procedural-secondary gameplay remains
unimplemented until those proofs are source-closed and integrated separately.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate17SecondaryOwnerAdjudicationError(ValueError):
    pass


TRACE_CLASSIFICATION_DIRECT_CALL = (
    "decoded_direct_call_candidate_not_lifecycle_semantic_proof"
)
TRACE_REQUIRED_DIRECT_TARGETS = (
    "schedule_container_runtime_traversal",
    "schedule_container_later_finalization",
    "schedule_container_final_shuffle",
)
TRACE_REQUIRED_GLOBAL_TARGETS = (
    "primary_schedule_container_global",
    "secondary_schedule_container_global",
)

STAGE_DAILY_RUNTIME_OWNER = "daily_runtime_owner"
STAGE_SEASON_CONTINUATION = "season_continuation"
STAGE_HUMAN_MATCH_DISPATCH = "human_match_dispatch"
STAGE_SAVE_RELOAD = "save_reload_persistence"


@dataclass(frozen=True)
class SecondaryOwnerAdjudicationStage:
    stage: str
    priority: int
    candidate_target_names: tuple[str, ...]
    required_source_proof: tuple[str, ...]
    capability_flags_unlocked_only_after_proof: tuple[str, ...]
    status: str = "needs_private_source"

    def __post_init__(self) -> None:
        if self.stage not in {
            STAGE_DAILY_RUNTIME_OWNER,
            STAGE_SEASON_CONTINUATION,
            STAGE_HUMAN_MATCH_DISPATCH,
            STAGE_SAVE_RELOAD,
        }:
            raise Gate17SecondaryOwnerAdjudicationError("unknown adjudication stage")
        if type(self.priority) is not int or self.priority < 1:
            raise Gate17SecondaryOwnerAdjudicationError(
                "adjudication priority must be a positive integer"
            )
        if self.status != "needs_private_source":
            raise Gate17SecondaryOwnerAdjudicationError(
                "cloud-safe plan cannot pre-adjudicate private source"
            )
        if not self.required_source_proof:
            raise Gate17SecondaryOwnerAdjudicationError(
                "adjudication stage requires explicit source proof"
            )
        if not self.capability_flags_unlocked_only_after_proof:
            raise Gate17SecondaryOwnerAdjudicationError(
                "adjudication stage requires explicit capability boundary"
            )


@dataclass(frozen=True)
class SecondaryOwnerAdjudicationPlan:
    source_sha256: str
    stages: tuple[SecondaryOwnerAdjudicationStage, ...]
    trace_candidates_are_semantic_proof: bool = False
    secondary_runtime_owner_recovered: bool = False
    procedural_secondary_scope_playable: bool = False
    gate17_complete: bool = False

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_sha256, str)
            or len(self.source_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.source_sha256)
        ):
            raise Gate17SecondaryOwnerAdjudicationError(
                "source SHA-256 must be lowercase hexadecimal"
            )
        if type(self.stages) is not tuple or len(self.stages) != 4:
            raise Gate17SecondaryOwnerAdjudicationError(
                "secondary-owner adjudication requires exactly four stages"
            )
        if tuple(stage.priority for stage in self.stages) != (1, 2, 3, 4):
            raise Gate17SecondaryOwnerAdjudicationError(
                "secondary-owner adjudication stages must retain priority 1..4"
            )
        if (
            self.trace_candidates_are_semantic_proof
            or self.secondary_runtime_owner_recovered
            or self.procedural_secondary_scope_playable
            or self.gate17_complete
        ):
            raise Gate17SecondaryOwnerAdjudicationError(
                "adjudication plan cannot promote unresolved Gate-17 capability"
            )


def _named_rows(rows: object, *, label: str) -> dict[str, dict]:
    if type(rows) not in (tuple, list):
        raise Gate17SecondaryOwnerAdjudicationError(
            f"{label} must be an array of trace records"
        )
    output: dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise Gate17SecondaryOwnerAdjudicationError(
                f"{label} records must be objects"
            )
        name = row.get("target_name")
        if not isinstance(name, str) or not name:
            raise Gate17SecondaryOwnerAdjudicationError(
                f"{label} record target_name must be non-empty"
            )
        if name in output:
            raise Gate17SecondaryOwnerAdjudicationError(
                f"{label} contains duplicate target {name}"
            )
        output[name] = row
    return output


def _validate_trace_contract(report: dict) -> tuple[dict[str, dict], dict[str, dict]]:
    if not isinstance(report, dict):
        raise Gate17SecondaryOwnerAdjudicationError(
            "secondary-owner trace report must be an object"
        )
    source_sha256 = report.get("source_sha256")
    if (
        not isinstance(source_sha256, str)
        or len(source_sha256) != 64
        or any(ch not in "0123456789abcdef" for ch in source_sha256)
    ):
        raise Gate17SecondaryOwnerAdjudicationError(
            "secondary-owner trace report has invalid source SHA-256"
        )

    for key in (
        "live_secondary_runtime_owner_recovered",
        "live_secondary_daily_execution_binding_recovered",
        "secondary_season_continuation_recovered",
        "secondary_human_match_dispatch_recovered",
        "secondary_save_serialization_recovered",
        "secondary_save_reload_continuation_recovered",
        "procedural_secondary_scope_playable",
        "gate17_full_scope_ready",
        "gate17_complete",
    ):
        if report.get(key) is not False:
            raise Gate17SecondaryOwnerAdjudicationError(
                f"neutral source trace must keep {key}=false"
            )

    direct = _named_rows(report.get("direct_call_candidates"), label="direct calls")
    globals_by_name = _named_rows(report.get("global_candidates"), label="globals")

    missing_direct = tuple(
        name for name in TRACE_REQUIRED_DIRECT_TARGETS if name not in direct
    )
    missing_globals = tuple(
        name for name in TRACE_REQUIRED_GLOBAL_TARGETS if name not in globals_by_name
    )
    if missing_direct or missing_globals:
        raise Gate17SecondaryOwnerAdjudicationError(
            "trace report is missing required candidate families: "
            f"direct={missing_direct}, globals={missing_globals}"
        )

    for name, row in direct.items():
        candidates = row.get(
            "decoded_direct_calls_not_lifecycle_semantic_proof"
        )
        if type(candidates) not in (tuple, list):
            raise Gate17SecondaryOwnerAdjudicationError(
                f"direct-call target {name} has invalid candidate list"
            )
        for candidate in candidates:
            if not isinstance(candidate, dict):
                raise Gate17SecondaryOwnerAdjudicationError(
                    "direct-call candidate must be an object"
                )
            if candidate.get("classification") != TRACE_CLASSIFICATION_DIRECT_CALL:
                raise Gate17SecondaryOwnerAdjudicationError(
                    "direct-call candidate lost its non-semantic classification"
                )

    return direct, globals_by_name


def build_secondary_owner_adjudication_plan(
    report: dict,
) -> SecondaryOwnerAdjudicationPlan:
    """Build the next private-source inspection plan from one neutral trace."""
    _direct, _globals = _validate_trace_contract(report)

    stages = (
        SecondaryOwnerAdjudicationStage(
            stage=STAGE_DAILY_RUNTIME_OWNER,
            priority=1,
            candidate_target_names=(
                "schedule_container_runtime_traversal",
                "secondary_schedule_container_global",
            ),
            required_source_proof=(
                "identify ordinary calendar/day owner callsites that reach 0x615C10",
                "prove the concrete receiver/this value or selected global for each call",
                "prove whether 0x947AF0 participates in ordinary runtime traversal",
                "separate startup-only/finalization callers from daily execution callers",
            ),
            capability_flags_unlocked_only_after_proof=(
                "live_secondary_runtime_owner_recovered",
                "live_secondary_daily_execution_binding_recovered",
            ),
        ),
        SecondaryOwnerAdjudicationStage(
            stage=STAGE_SEASON_CONTINUATION,
            priority=2,
            candidate_target_names=(
                "schedule_container_later_finalization",
                "schedule_container_final_shuffle",
                "secondary_schedule_container_global",
            ),
            required_source_proof=(
                "identify season-boundary callers of 0x616A70 and 0x615BE0",
                "prove secondary-container receiver/ownership where applicable",
                "prove lifecycle ordering from completed season into next schedule state",
                "reject one-time new-game setup as season-continuation evidence",
            ),
            capability_flags_unlocked_only_after_proof=(
                "secondary_season_continuation_recovered",
            ),
        ),
        SecondaryOwnerAdjudicationStage(
            stage=STAGE_HUMAN_MATCH_DISPATCH,
            priority=3,
            candidate_target_names=(
                "schedule_container_runtime_traversal",
                "secondary_schedule_container_global",
            ),
            required_source_proof=(
                "trace a secondary-owned due fixture from ordinary traversal to match dispatch",
                "prove the branch that distinguishes human-controlled participation",
                "identify the exact human-match owner/continuation contract",
                "do not reuse primary procedural dispatch without source equivalence",
            ),
            capability_flags_unlocked_only_after_proof=(
                "secondary_human_match_dispatch_recovered",
            ),
        ),
        SecondaryOwnerAdjudicationStage(
            stage=STAGE_SAVE_RELOAD,
            priority=4,
            candidate_target_names=(
                "secondary_schedule_container_global",
            ),
            required_source_proof=(
                "find save serializer ownership/reference for 0x947AF0 or its live object",
                "find reload/deserializer restoration of secondary schedule state",
                "prove post-reload ordinary traversal resumes the same logical owner",
                "separate serialized schedule data from regenerated startup-only state",
            ),
            capability_flags_unlocked_only_after_proof=(
                "secondary_save_serialization_recovered",
                "secondary_save_reload_continuation_recovered",
            ),
        ),
    )

    return SecondaryOwnerAdjudicationPlan(
        source_sha256=report["source_sha256"],
        stages=stages,
    )


def adjudication_plan_contract() -> dict:
    """Expose ordering and fail-closed semantics without requiring private bytes."""
    return {
        "stage_order": (
            STAGE_DAILY_RUNTIME_OWNER,
            STAGE_SEASON_CONTINUATION,
            STAGE_HUMAN_MATCH_DISPATCH,
            STAGE_SAVE_RELOAD,
        ),
        "raw_global_candidates_are_xrefs": False,
        "decoded_direct_calls_are_lifecycle_semantics": False,
        "private_source_required_for_stage_completion": True,
        "procedural_secondary_scope_playable": False,
        "gate17_complete": False,
    }

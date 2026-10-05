"""Fail-closed adjudication plan for Gate-17 sporting-objective progression.

Consumes the neutral private trace contract prepared for the annual sporting
objective boundary. The plan requires source closure of annual owner chronology,
the complete non-PL objective/classification branches, and the exact progression
state update before runtime integration may be considered.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate17SportingObjectiveAdjudicationError(ValueError):
    pass


TRACE_CLASSIFICATION_DIRECT_CALL = (
    "decoded_direct_call_candidate_not_lifecycle_semantic_proof"
)

ANNUAL_COMPETITION_TRANSITION_VA = 0x4A8628
SPORTING_OBJECTIVE_PROGRESS_VA = 0x5E1C00
SPORTING_OBJECTIVE_BRANCH_VA = 0x5E0310
SPORTING_OBJECTIVE_CLASSIFICATION_COMPARE_VA = 0x5E07E4
BETWEEN_PROGRESSION_PASSES_TRANSITION_VA = 0x4F9010
ANNUAL_OBJECTIVE_EVALUATION_CALLER_VA = 0x426220
ANNUAL_OBJECTIVE_EVALUATION_VA = 0x5E1D90
DBRUSER_SACKING_REASON_SETTER_VA = 0x42C6C0
OBJECTIVE_SELECTED_ID_OFFSET = 0x64
OBJECTIVE_PROGRESSION_GATE_OFFSET = 0x68
OBJECTIVE_PROGRESSION_STATE_OFFSET = 0x9C
SPORTING_OBJECTIVE_SWITCH_CASE_COUNT = 17
SPORTING_OBJECTIVE_PASS_SEQUENCE = (1, 0)

REQUIRED_DIRECT_TARGETS = (
    "sporting_objective_progression",
    "sporting_objective_branch",
    "sporting_objective_classification_compare",
    "annual_objective_evaluation",
    "dbruser_sacking_reason_setter",
)

STAGE_ANNUAL_OWNER = "annual_sporting_owner_chronology"
STAGE_NON_PL_BRANCHES = "non_pl_objective_branch_and_classification_semantics"
STAGE_STATE_UPDATE = "non_pl_progression_state_update_semantics"


@dataclass(frozen=True)
class SportingObjectiveAdjudicationStage:
    stage: str
    priority: int
    candidate_target_names: tuple[str, ...]
    required_source_proof: tuple[str, ...]
    capability_flags_unlocked_only_after_proof: tuple[str, ...]
    status: str = "needs_private_source"

    def __post_init__(self) -> None:
        if self.stage not in {
            STAGE_ANNUAL_OWNER,
            STAGE_NON_PL_BRANCHES,
            STAGE_STATE_UPDATE,
        }:
            raise Gate17SportingObjectiveAdjudicationError(
                "unknown sporting-objective adjudication stage"
            )
        if type(self.priority) is not int or self.priority < 1:
            raise Gate17SportingObjectiveAdjudicationError(
                "sporting-objective adjudication priority must be positive"
            )
        if self.status != "needs_private_source":
            raise Gate17SportingObjectiveAdjudicationError(
                "cloud-safe plan cannot pre-complete private source"
            )
        if not self.required_source_proof:
            raise Gate17SportingObjectiveAdjudicationError(
                "sporting-objective stage requires source-proof criteria"
            )
        if not self.capability_flags_unlocked_only_after_proof:
            raise Gate17SportingObjectiveAdjudicationError(
                "sporting-objective stage requires capability flags"
            )


@dataclass(frozen=True)
class SportingObjectiveAdjudicationPlan:
    source_sha256: str
    stages: tuple[SportingObjectiveAdjudicationStage, ...]
    trace_candidates_are_sporting_semantic_proof: bool = False
    non_pl_sporting_objective_progression_ready: bool = False
    all_playable_scope_sporting_progression_ready: bool = False
    gate17_full_scope_ready: bool = False
    gate17_complete: bool = False

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_sha256, str)
            or len(self.source_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.source_sha256)
        ):
            raise Gate17SportingObjectiveAdjudicationError(
                "source SHA-256 must be lowercase hexadecimal"
            )
        if type(self.stages) is not tuple or len(self.stages) != 3:
            raise Gate17SportingObjectiveAdjudicationError(
                "sporting-objective adjudication requires exactly three stages"
            )
        if tuple(stage.priority for stage in self.stages) != (1, 2, 3):
            raise Gate17SportingObjectiveAdjudicationError(
                "sporting-objective stage priorities must remain 1..3"
            )
        if (
            self.trace_candidates_are_sporting_semantic_proof
            or self.non_pl_sporting_objective_progression_ready
            or self.all_playable_scope_sporting_progression_ready
            or self.gate17_full_scope_ready
            or self.gate17_complete
        ):
            raise Gate17SportingObjectiveAdjudicationError(
                "adjudication plan cannot promote unresolved sporting capability"
            )


def _named_rows(rows: object) -> dict[str, dict]:
    if type(rows) not in (tuple, list):
        raise Gate17SportingObjectiveAdjudicationError(
            "direct calls must be an array of trace records"
        )
    output: dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise Gate17SportingObjectiveAdjudicationError(
                "direct-call records must be objects"
            )
        name = row.get("target_name")
        if not isinstance(name, str) or not name:
            raise Gate17SportingObjectiveAdjudicationError(
                "direct-call target_name must be non-empty"
            )
        if name in output:
            raise Gate17SportingObjectiveAdjudicationError(
                f"duplicate direct-call target {name}"
            )
        output[name] = row
    return output


def _validate_trace_contract(report: dict) -> dict[str, dict]:
    if not isinstance(report, dict):
        raise Gate17SportingObjectiveAdjudicationError(
            "sporting-objective trace report must be an object"
        )
    source_sha = report.get("source_sha256")
    if (
        not isinstance(source_sha, str)
        or len(source_sha) != 64
        or any(ch not in "0123456789abcdef" for ch in source_sha)
    ):
        raise Gate17SportingObjectiveAdjudicationError(
            "sporting-objective trace has invalid source SHA-256"
        )

    contract = report.get("source_contract")
    if not isinstance(contract, dict):
        raise Gate17SportingObjectiveAdjudicationError(
            "sporting-objective trace requires source_contract"
        )
    exact = {
        "annual_competition_transition_va": ANNUAL_COMPETITION_TRANSITION_VA,
        "sporting_objective_progress_va": SPORTING_OBJECTIVE_PROGRESS_VA,
        "sporting_objective_branch_va": SPORTING_OBJECTIVE_BRANCH_VA,
        "sporting_objective_classification_compare_va": (
            SPORTING_OBJECTIVE_CLASSIFICATION_COMPARE_VA
        ),
        "between_progression_passes_transition_va": (
            BETWEEN_PROGRESSION_PASSES_TRANSITION_VA
        ),
        "annual_objective_evaluation_caller_va": (
            ANNUAL_OBJECTIVE_EVALUATION_CALLER_VA
        ),
        "annual_objective_evaluation_va": ANNUAL_OBJECTIVE_EVALUATION_VA,
        "dbruser_sacking_reason_setter_va": DBRUSER_SACKING_REASON_SETTER_VA,
        "objective_selected_id_offset": OBJECTIVE_SELECTED_ID_OFFSET,
        "objective_progression_gate_offset": OBJECTIVE_PROGRESSION_GATE_OFFSET,
        "objective_progression_state_offset": OBJECTIVE_PROGRESSION_STATE_OFFSET,
        "sporting_objective_switch_case_count": SPORTING_OBJECTIVE_SWITCH_CASE_COUNT,
        "sporting_objective_pass_sequence": SPORTING_OBJECTIVE_PASS_SEQUENCE,
    }
    for key, expected in exact.items():
        if contract.get(key) != expected:
            raise Gate17SportingObjectiveAdjudicationError(
                f"trace source contract drifted for {key}"
            )
    for key in (
        "same_premier_league_slice_recovered",
        "annual_evaluation_year_gate_recovered",
    ):
        if contract.get(key) is not True:
            raise Gate17SportingObjectiveAdjudicationError(
                f"trace must retain source-proven {key}=true"
            )

    for key in (
        "annual_sporting_owner_chronology_recovered",
        "non_pl_objective_branch_table_recovered",
        "promotion_relegation_classification_semantics_recovered",
        "non_pl_progression_gate_update_recovered",
        "non_pl_sporting_objective_progression_ready",
        "all_playable_scope_sporting_progression_ready",
        "gate17_full_scope_ready",
        "gate17_complete",
    ):
        if report.get(key) is not False:
            raise Gate17SportingObjectiveAdjudicationError(
                f"neutral sporting-objective trace must keep {key}=false"
            )

    direct = _named_rows(report.get("direct_call_candidates"))
    missing = tuple(name for name in REQUIRED_DIRECT_TARGETS if name not in direct)
    if missing:
        raise Gate17SportingObjectiveAdjudicationError(
            "trace report is missing required sporting candidate families: "
            f"{missing}"
        )
    for name, row in direct.items():
        candidates = row.get(
            "decoded_direct_calls_not_sporting_progression_semantic_proof"
        )
        if type(candidates) not in (tuple, list):
            raise Gate17SportingObjectiveAdjudicationError(
                f"direct-call target {name} has invalid candidate list"
            )
        for candidate in candidates:
            if not isinstance(candidate, dict):
                raise Gate17SportingObjectiveAdjudicationError(
                    "direct-call candidate must be object"
                )
            if candidate.get("classification") != TRACE_CLASSIFICATION_DIRECT_CALL:
                raise Gate17SportingObjectiveAdjudicationError(
                    "direct-call candidate lost its non-semantic classification"
                )
    return direct


def build_sporting_objective_adjudication_plan(
    report: dict,
) -> SportingObjectiveAdjudicationPlan:
    """Return the exact private-source proof order for non-PL progression."""
    _validate_trace_contract(report)

    stages = (
        SportingObjectiveAdjudicationStage(
            stage=STAGE_ANNUAL_OWNER,
            priority=1,
            candidate_target_names=("sporting_objective_progression",),
            required_source_proof=(
                "prove the per-DBRUser annual caller path rooted around 0x4A8628",
                "prove pass 1 occurs before 0x4F9010 and pass 0 after it",
                "identify the competition context visible to each pass",
                "separate normal annual progression from unrelated callers",
            ),
            capability_flags_unlocked_only_after_proof=(
                "annual_sporting_owner_chronology_recovered",
            ),
        ),
        SportingObjectiveAdjudicationStage(
            stage=STAGE_NON_PL_BRANCHES,
            priority=2,
            candidate_target_names=(
                "sporting_objective_branch",
                "sporting_objective_classification_compare",
            ),
            required_source_proof=(
                "recover all relevant 17 objective-ID switch branches beyond the PL slice",
                "recover which branches are pass-sensitive",
                "recover same-class, improved-class, relegated and promoted comparisons",
                "bind each classification decision to original competition data/ownership",
            ),
            capability_flags_unlocked_only_after_proof=(
                "non_pl_objective_branch_table_recovered",
                "promotion_relegation_classification_semantics_recovered",
            ),
        ),
        SportingObjectiveAdjudicationStage(
            stage=STAGE_STATE_UPDATE,
            priority=3,
            candidate_target_names=(
                "sporting_objective_branch",
                "annual_objective_evaluation",
                "dbruser_sacking_reason_setter",
            ),
            required_source_proof=(
                "prove the success paths that set objective +0x68",
                "prove the common-tail +0x9C update for non-PL branches",
                "prove annual evaluation ordering relative to both sporting passes",
                "prove failed sporting progression reaches later reason-4 evaluation unchanged",
            ),
            capability_flags_unlocked_only_after_proof=(
                "non_pl_progression_gate_update_recovered",
            ),
        ),
    )

    return SportingObjectiveAdjudicationPlan(
        source_sha256=report["source_sha256"],
        stages=stages,
    )


def sporting_objective_adjudication_contract() -> dict:
    return {
        "stage_order": (
            STAGE_ANNUAL_OWNER,
            STAGE_NON_PL_BRANCHES,
            STAGE_STATE_UPDATE,
        ),
        "source_switch_case_count": SPORTING_OBJECTIVE_SWITCH_CASE_COUNT,
        "source_pass_sequence": SPORTING_OBJECTIVE_PASS_SEQUENCE,
        "candidate_calls_are_sporting_semantics": False,
        "private_source_required_for_stage_completion": True,
        "runtime_integration_after_source_required": True,
        "non_pl_sporting_objective_progression_ready": False,
        "all_playable_scope_sporting_progression_ready": False,
        "gate17_full_scope_ready": False,
        "gate17_complete": False,
    }

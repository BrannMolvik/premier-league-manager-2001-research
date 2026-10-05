"""Fail-closed adjudication plan for Gate-17 fresh-objective RNG ownership.

Consumes the neutral private source trace produced by
gate17_objective_rng_caller_source_trace.py and defines the source proofs needed
before RNG-bearing fresh chairman-objective branches may use the clean-room
shared MSVC CRT stream.

Decoded CALL candidates remain discovery aids. They do not prove ordinary setup
ownership, CRT entry state, draw chronology, replay readiness, or all-scope
objective readiness.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate17ObjectiveRngAdjudicationError(ValueError):
    pass


TRACE_CLASSIFICATION_DIRECT_CALL = (
    "decoded_direct_call_candidate_not_lifecycle_semantic_proof"
)

SOURCE_DBRUSER_CONSTRUCTOR_VA = 0x425680
SOURCE_OBJECTIVE_SETUP_VA = 0x5DF670
SOURCE_FRESH_OBJECTIVE_GENERATOR_VA = 0x5DFD30
SOURCE_SHARED_CRT_BOUNDED_RNG_VA = 0x64D540
SOURCE_HIERARCHY_CLASS_HELPER_VA = 0x4FA520
SOURCE_FIRST_CLASS_HELPER_VA = 0x4FA570
SOURCE_LAST_CLASS_EQUAL_HELPER_VA = 0x4FA590
SOURCE_PROMOTION_PLAYOFF_STATUS_HELPER_VA = 0x4F88C0
SOURCE_OBJECTIVE_RNG_BOUND = 100
SOURCE_OBJECTIVE_RNG_LOWER_BRANCH_MAX = 50
SOURCE_OBJECTIVE_SETUP_SLOT_COUNT = 3

REQUIRED_DIRECT_TARGETS = (
    "objective_setup",
    "fresh_objective_generator",
    "shared_crt_bounded_rng",
)

STAGE_SETUP_OWNER = "objective_setup_owner_chronology"
STAGE_ENTRY_CRT_STATE = "objective_setup_entry_crt_state"
STAGE_DRAW_POSITION = "rng_bearing_branch_draw_position"


@dataclass(frozen=True)
class ObjectiveRngAdjudicationStage:
    stage: str
    priority: int
    candidate_target_names: tuple[str, ...]
    required_source_proof: tuple[str, ...]
    capability_flags_unlocked_only_after_proof: tuple[str, ...]
    status: str = "needs_private_source"

    def __post_init__(self) -> None:
        if self.stage not in {
            STAGE_SETUP_OWNER,
            STAGE_ENTRY_CRT_STATE,
            STAGE_DRAW_POSITION,
        }:
            raise Gate17ObjectiveRngAdjudicationError(
                "unknown objective RNG adjudication stage"
            )
        if type(self.priority) is not int or self.priority < 1:
            raise Gate17ObjectiveRngAdjudicationError(
                "objective RNG adjudication priority must be positive integer"
            )
        if self.status != "needs_private_source":
            raise Gate17ObjectiveRngAdjudicationError(
                "cloud-safe adjudication cannot pre-complete private source"
            )
        if not self.required_source_proof:
            raise Gate17ObjectiveRngAdjudicationError(
                "objective RNG stage requires source-proof criteria"
            )
        if not self.capability_flags_unlocked_only_after_proof:
            raise Gate17ObjectiveRngAdjudicationError(
                "objective RNG stage requires capability flags"
            )


@dataclass(frozen=True)
class ObjectiveRngAdjudicationPlan:
    source_sha256: str
    stages: tuple[ObjectiveRngAdjudicationStage, ...]
    trace_candidates_are_objective_rng_semantic_proof: bool = False
    fresh_objective_rng_replay_ready: bool = False
    all_playable_scope_fresh_objectives_ready: bool = False
    gate17_full_scope_ready: bool = False
    gate17_complete: bool = False

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_sha256, str)
            or len(self.source_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.source_sha256)
        ):
            raise Gate17ObjectiveRngAdjudicationError(
                "source SHA-256 must be lowercase hexadecimal"
            )
        if type(self.stages) is not tuple or len(self.stages) != 3:
            raise Gate17ObjectiveRngAdjudicationError(
                "objective RNG adjudication requires exactly three stages"
            )
        if tuple(stage.priority for stage in self.stages) != (1, 2, 3):
            raise Gate17ObjectiveRngAdjudicationError(
                "objective RNG adjudication priorities must remain 1..3"
            )
        if (
            self.trace_candidates_are_objective_rng_semantic_proof
            or self.fresh_objective_rng_replay_ready
            or self.all_playable_scope_fresh_objectives_ready
            or self.gate17_full_scope_ready
            or self.gate17_complete
        ):
            raise Gate17ObjectiveRngAdjudicationError(
                "adjudication plan cannot promote unresolved objective RNG capability"
            )


def _named_rows(rows: object, *, label: str) -> dict[str, dict]:
    if type(rows) not in (tuple, list):
        raise Gate17ObjectiveRngAdjudicationError(
            f"{label} must be an array of trace records"
        )
    output: dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise Gate17ObjectiveRngAdjudicationError(
                f"{label} records must be objects"
            )
        name = row.get("target_name")
        if not isinstance(name, str) or not name:
            raise Gate17ObjectiveRngAdjudicationError(
                f"{label} target_name must be non-empty"
            )
        if name in output:
            raise Gate17ObjectiveRngAdjudicationError(
                f"{label} contains duplicate target {name}"
            )
        output[name] = row
    return output


def _validate_trace_contract(report: dict) -> dict[str, dict]:
    if not isinstance(report, dict):
        raise Gate17ObjectiveRngAdjudicationError(
            "objective RNG trace report must be an object"
        )

    source_sha = report.get("source_sha256")
    if (
        not isinstance(source_sha, str)
        or len(source_sha) != 64
        or any(ch not in "0123456789abcdef" for ch in source_sha)
    ):
        raise Gate17ObjectiveRngAdjudicationError(
            "objective RNG trace has invalid source SHA-256"
        )

    contract = report.get("source_contract")
    if not isinstance(contract, dict):
        raise Gate17ObjectiveRngAdjudicationError(
            "objective RNG trace requires source_contract"
        )

    exact_source_contract = {
        "dbruser_constructor_va": SOURCE_DBRUSER_CONSTRUCTOR_VA,
        "objective_setup_va": SOURCE_OBJECTIVE_SETUP_VA,
        "fresh_objective_generator_va": SOURCE_FRESH_OBJECTIVE_GENERATOR_VA,
        "shared_crt_bounded_rng_va": SOURCE_SHARED_CRT_BOUNDED_RNG_VA,
        "hierarchy_class_helper_va": SOURCE_HIERARCHY_CLASS_HELPER_VA,
        "first_class_helper_va": SOURCE_FIRST_CLASS_HELPER_VA,
        "last_class_equal_helper_va": SOURCE_LAST_CLASS_EQUAL_HELPER_VA,
        "promotion_playoff_status_helper_va": SOURCE_PROMOTION_PLAYOFF_STATUS_HELPER_VA,
        "objective_rng_bound": SOURCE_OBJECTIVE_RNG_BOUND,
        "objective_rng_lower_branch_max_inclusive": (
            SOURCE_OBJECTIVE_RNG_LOWER_BRANCH_MAX
        ),
        "objective_setup_slot_count": SOURCE_OBJECTIVE_SETUP_SLOT_COUNT,
    }
    for key, expected in exact_source_contract.items():
        if contract.get(key) != expected:
            raise Gate17ObjectiveRngAdjudicationError(
                f"trace source contract drifted for {key}"
            )

    for key in (
        "fresh_branch_table_recovered",
        "deterministic_non_pl_branches_materializable",
        "rng_bearing_branches_require_shared_crt_state",
    ):
        if contract.get(key) is not True:
            raise Gate17ObjectiveRngAdjudicationError(
                f"trace must retain source-proven {key}=true"
            )

    for key in (
        "objective_setup_callers_classified",
        "objective_setup_entry_crt_state_recovered",
        "rng_bearing_branch_draw_position_recovered",
        "fresh_objective_rng_replay_ready",
        "all_playable_scope_fresh_objectives_ready",
        "gate17_full_scope_ready",
        "gate17_complete",
    ):
        if report.get(key) is not False:
            raise Gate17ObjectiveRngAdjudicationError(
                f"neutral objective RNG trace must keep {key}=false"
            )

    direct = _named_rows(
        report.get("direct_call_candidates"),
        label="direct calls",
    )
    missing = tuple(name for name in REQUIRED_DIRECT_TARGETS if name not in direct)
    if missing:
        raise Gate17ObjectiveRngAdjudicationError(
            "trace report is missing required objective RNG candidate families: "
            f"{missing}"
        )

    for name, row in direct.items():
        candidates = row.get(
            "decoded_direct_calls_not_objective_rng_semantic_proof"
        )
        if type(candidates) not in (tuple, list):
            raise Gate17ObjectiveRngAdjudicationError(
                f"direct-call target {name} has invalid candidate list"
            )
        for candidate in candidates:
            if not isinstance(candidate, dict):
                raise Gate17ObjectiveRngAdjudicationError(
                    "direct-call candidate must be object"
                )
            if candidate.get("classification") != TRACE_CLASSIFICATION_DIRECT_CALL:
                raise Gate17ObjectiveRngAdjudicationError(
                    "direct-call candidate lost its non-semantic classification"
                )

    return direct


def build_objective_rng_adjudication_plan(
    report: dict,
) -> ObjectiveRngAdjudicationPlan:
    """Return the exact next private-source proof order for RNG-bearing objectives."""
    _validate_trace_contract(report)

    stages = (
        ObjectiveRngAdjudicationStage(
            stage=STAGE_SETUP_OWNER,
            priority=1,
            candidate_target_names=("objective_setup",),
            required_source_proof=(
                "classify every ordinary caller of 0x5DF670 relevant to fresh users",
                "identify the owning user/setup lifecycle for each ordinary call",
                "place the setup event relative to user creation and competition startup",
                "separate fresh-game setup from later refresh or progression callsites",
            ),
            capability_flags_unlocked_only_after_proof=(
                "objective_setup_callers_classified",
            ),
        ),
        ObjectiveRngAdjudicationStage(
            stage=STAGE_ENTRY_CRT_STATE,
            priority=2,
            candidate_target_names=(
                "objective_setup",
                "shared_crt_bounded_rng",
            ),
            required_source_proof=(
                "connect 0x5DF670 entry to the same process-global MSVC CRT stream",
                "enumerate intervening CRT consumers after the recovered startup ledger",
                "prove no hidden reseed or independent RNG stream is substituted",
                "recover the exact CRT state immediately before objective setup",
            ),
            capability_flags_unlocked_only_after_proof=(
                "objective_setup_entry_crt_state_recovered",
            ),
        ),
        ObjectiveRngAdjudicationStage(
            stage=STAGE_DRAW_POSITION,
            priority=3,
            candidate_target_names=(
                "fresh_objective_generator",
                "shared_crt_bounded_rng",
            ),
            required_source_proof=(
                "prove the slot 0, 1, 2 invocation chronology for 0x5DFD30",
                "prove which recovered branch consumes RNG(100) and which slots do not",
                "recover the exact bounded-draw position in the shared CRT stream",
                "account for sequential fresh users so one user's draw advances the next",
            ),
            capability_flags_unlocked_only_after_proof=(
                "rng_bearing_branch_draw_position_recovered",
            ),
        ),
    )

    return ObjectiveRngAdjudicationPlan(
        source_sha256=report["source_sha256"],
        stages=stages,
    )


def objective_rng_adjudication_contract() -> dict:
    """Expose proof order while keeping runtime integration explicitly separate."""
    return {
        "stage_order": (
            STAGE_SETUP_OWNER,
            STAGE_ENTRY_CRT_STATE,
            STAGE_DRAW_POSITION,
        ),
        "source_objective_rng_bound": SOURCE_OBJECTIVE_RNG_BOUND,
        "source_lower_branch_max_inclusive": (
            SOURCE_OBJECTIVE_RNG_LOWER_BRANCH_MAX
        ),
        "source_setup_slot_count": SOURCE_OBJECTIVE_SETUP_SLOT_COUNT,
        "candidate_calls_are_objective_rng_semantics": False,
        "private_source_required_for_stage_completion": True,
        "runtime_integration_after_source_required": True,
        "fresh_objective_rng_replay_ready": False,
        "all_playable_scope_fresh_objectives_ready": False,
        "gate17_full_scope_ready": False,
        "gate17_complete": False,
    }

"""Fail-closed adjudication plan for Gate-17 multi-human gameplay.

Consumes the neutral private TeamSelect Start/user-list trace and defines the
ordered source proofs required before widening the clean-room runtime beyond one
HumanManagerState. Candidate address hits and decoded direct CALLs remain
discovery aids, never handoff/runtime/save semantic proof.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate17MultiHumanAdjudicationError(ValueError):
    pass


TRACE_CLASSIFICATION_DIRECT_CALL = (
    "decoded_direct_call_candidate_not_lifecycle_semantic_proof"
)
SOURCE_PROVEN_USER_CAP = 6
SOURCE_TEAMSELECT_START_EVENT_VA = 0x4DA480
SOURCE_TEAMSELECT_START_CONTINUATION_VA = 0x4C41C0
SOURCE_TEAMSELECT_SATURATION_VA = 0x4DA4D0
SOURCE_GLOBAL_USER_COUNT_VA = 0x8755E4
SOURCE_USER_SELECTED_CLUB_POINTER_OFFSET = 0x5B4

STAGE_START_ITERATION = "ordered_start_iteration"
STAGE_SHARED_RUNTIME = "shared_runtime_handoff"
STAGE_FIXTURE_DISPATCH = "simultaneous_human_fixture_dispatch"
STAGE_SAVE_RELOAD = "multi_human_save_reload"

REQUIRED_DIRECT_TARGETS = (
    "teamselect_start_continuation",
    "user_lookup_current",
    "user_lookup_indexed",
)
REQUIRED_GLOBAL_TARGETS = ("global_user_count",)


@dataclass(frozen=True)
class MultiHumanAdjudicationStage:
    stage: str
    priority: int
    candidate_target_names: tuple[str, ...]
    required_source_proof: tuple[str, ...]
    capability_dimensions_unlocked_only_after_proof: tuple[str, ...]
    status: str = "needs_private_source"

    def __post_init__(self) -> None:
        if self.stage not in {
            STAGE_START_ITERATION,
            STAGE_SHARED_RUNTIME,
            STAGE_FIXTURE_DISPATCH,
            STAGE_SAVE_RELOAD,
        }:
            raise Gate17MultiHumanAdjudicationError("unknown adjudication stage")
        if type(self.priority) is not int or self.priority < 1:
            raise Gate17MultiHumanAdjudicationError(
                "adjudication priority must be positive integer"
            )
        if self.status != "needs_private_source":
            raise Gate17MultiHumanAdjudicationError(
                "cloud-safe adjudication cannot pre-complete private source"
            )
        if not self.required_source_proof:
            raise Gate17MultiHumanAdjudicationError(
                "adjudication stage requires source-proof criteria"
            )
        if not self.capability_dimensions_unlocked_only_after_proof:
            raise Gate17MultiHumanAdjudicationError(
                "adjudication stage requires capability dimensions"
            )


@dataclass(frozen=True)
class MultiHumanAdjudicationPlan:
    source_sha256: str
    source_proven_hard_user_cap: int
    stages: tuple[MultiHumanAdjudicationStage, ...]
    trace_candidates_are_handoff_semantic_proof: bool = False
    multi_human_start_supported: bool = False
    shared_runtime_supported: bool = False
    save_reload_supported: bool = False
    multi_human_gameplay_supported: bool = False
    gate17_complete: bool = False

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_sha256, str)
            or len(self.source_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.source_sha256)
        ):
            raise Gate17MultiHumanAdjudicationError(
                "source SHA-256 must be lowercase hexadecimal"
            )
        if self.source_proven_hard_user_cap != SOURCE_PROVEN_USER_CAP:
            raise Gate17MultiHumanAdjudicationError(
                "source-proven multi-human cap must remain exactly six"
            )
        if type(self.stages) is not tuple or len(self.stages) != 4:
            raise Gate17MultiHumanAdjudicationError(
                "multi-human adjudication requires exactly four stages"
            )
        if tuple(stage.priority for stage in self.stages) != (1, 2, 3, 4):
            raise Gate17MultiHumanAdjudicationError(
                "multi-human adjudication priorities must remain 1..4"
            )
        if (
            self.trace_candidates_are_handoff_semantic_proof
            or self.multi_human_start_supported
            or self.shared_runtime_supported
            or self.save_reload_supported
            or self.multi_human_gameplay_supported
            or self.gate17_complete
        ):
            raise Gate17MultiHumanAdjudicationError(
                "adjudication plan cannot promote unresolved multi-human capability"
            )


def _named_rows(rows: object, *, label: str) -> dict[str, dict]:
    if type(rows) not in (tuple, list):
        raise Gate17MultiHumanAdjudicationError(
            f"{label} must be an array of trace records"
        )
    output: dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise Gate17MultiHumanAdjudicationError(
                f"{label} records must be objects"
            )
        name = row.get("target_name")
        if not isinstance(name, str) or not name:
            raise Gate17MultiHumanAdjudicationError(
                f"{label} target_name must be non-empty"
            )
        if name in output:
            raise Gate17MultiHumanAdjudicationError(
                f"{label} contains duplicate target {name}"
            )
        output[name] = row
    return output


def _validate_trace_contract(report: dict) -> tuple[dict[str, dict], dict[str, dict]]:
    if not isinstance(report, dict):
        raise Gate17MultiHumanAdjudicationError(
            "multi-human Start trace report must be an object"
        )

    source_sha = report.get("source_sha256")
    if (
        not isinstance(source_sha, str)
        or len(source_sha) != 64
        or any(ch not in "0123456789abcdef" for ch in source_sha)
    ):
        raise Gate17MultiHumanAdjudicationError(
            "multi-human Start trace has invalid source SHA-256"
        )

    contract = report.get("source_contract")
    if not isinstance(contract, dict):
        raise Gate17MultiHumanAdjudicationError(
            "multi-human Start trace requires source_contract"
        )
    exact_source_contract = {
        "teamselect_start_event_va": SOURCE_TEAMSELECT_START_EVENT_VA,
        "teamselect_start_continuation_va": SOURCE_TEAMSELECT_START_CONTINUATION_VA,
        "teamselect_saturation_va": SOURCE_TEAMSELECT_SATURATION_VA,
        "global_user_count_va": SOURCE_GLOBAL_USER_COUNT_VA,
        "user_selected_club_pointer_offset": SOURCE_USER_SELECTED_CLUB_POINTER_OFFSET,
        "source_proven_hard_user_cap": SOURCE_PROVEN_USER_CAP,
    }
    for key, expected in exact_source_contract.items():
        if contract.get(key) != expected:
            raise Gate17MultiHumanAdjudicationError(
                f"trace source contract drifted for {key}"
            )
    if contract.get("selection_appends_users_recovered") is not True:
        raise Gate17MultiHumanAdjudicationError(
            "trace must retain source-proven user append behavior"
        )
    if contract.get("start_consumes_existing_user_list_recovered") is not True:
        raise Gate17MultiHumanAdjudicationError(
            "trace must retain source-proven Start user-list behavior"
        )

    unresolved_false = (
        "ordered_multi_user_start_iteration_recovered",
        "shared_multi_human_runtime_owner_recovered",
        "simultaneous_human_fixture_dispatch_order_recovered",
        "multi_human_save_serialization_recovered",
        "multi_human_save_reload_continuation_recovered",
        "multi_human_gameplay_supported",
        "gate17_full_scope_ready",
        "gate17_complete",
    )
    for key in unresolved_false:
        if report.get(key) is not False:
            raise Gate17MultiHumanAdjudicationError(
                f"neutral multi-human trace must keep {key}=false"
            )

    direct = _named_rows(report.get("direct_call_candidates"), label="direct calls")
    globals_by_name = _named_rows(report.get("global_candidates"), label="globals")

    missing_direct = tuple(name for name in REQUIRED_DIRECT_TARGETS if name not in direct)
    missing_globals = tuple(name for name in REQUIRED_GLOBAL_TARGETS if name not in globals_by_name)
    if missing_direct or missing_globals:
        raise Gate17MultiHumanAdjudicationError(
            "trace report is missing required multi-human candidate families: "
            f"direct={missing_direct}, globals={missing_globals}"
        )

    for name, row in direct.items():
        candidates = row.get("decoded_direct_calls_not_handoff_semantic_proof")
        if type(candidates) not in (tuple, list):
            raise Gate17MultiHumanAdjudicationError(
                f"direct-call target {name} has invalid candidate list"
            )
        for candidate in candidates:
            if not isinstance(candidate, dict):
                raise Gate17MultiHumanAdjudicationError(
                    "direct-call candidate must be object"
                )
            if candidate.get("classification") != TRACE_CLASSIFICATION_DIRECT_CALL:
                raise Gate17MultiHumanAdjudicationError(
                    "direct-call candidate lost its non-semantic classification"
                )

    return direct, globals_by_name


def build_multi_human_adjudication_plan(report: dict) -> MultiHumanAdjudicationPlan:
    """Return the next exact private-source proof plan for six-user support."""
    _direct, _globals = _validate_trace_contract(report)
    contract = report["source_contract"]

    stages = (
        MultiHumanAdjudicationStage(
            stage=STAGE_START_ITERATION,
            priority=1,
            candidate_target_names=(
                "teamselect_start_continuation",
                "user_lookup_current",
                "user_lookup_indexed",
                "global_user_count",
            ),
            required_source_proof=(
                "prove whether 0x4C41C0 visits every selected user on Start",
                "prove the exact global-user-list traversal and ordering rule",
                "prove how the six-user count bounds Start iteration",
                "identify any per-user continuation call and selected-club consumption",
            ),
            capability_dimensions_unlocked_only_after_proof=(
                "multi_human_start_supported",
                "gameplay_simultaneous_users_supported",
            ),
        ),
        MultiHumanAdjudicationStage(
            stage=STAGE_SHARED_RUNTIME,
            priority=2,
            candidate_target_names=(
                "teamselect_start_continuation",
                "user_lookup_current",
                "user_lookup_indexed",
            ),
            required_source_proof=(
                "prove whether all selected users enter one shared live world/runtime",
                "identify the owner object(s) retaining each user after TeamSelect",
                "prove current-user switching or equivalent ownership semantics",
                "reject independent duplicated worlds unless source explicitly does so",
            ),
            capability_dimensions_unlocked_only_after_proof=(
                "shared_runtime_supported",
            ),
        ),
        MultiHumanAdjudicationStage(
            stage=STAGE_FIXTURE_DISPATCH,
            priority=3,
            candidate_target_names=(
                "user_lookup_current",
                "user_lookup_indexed",
            ),
            required_source_proof=(
                "trace two or more selected users with due fixtures to match dispatch",
                "prove exact arbitration/order when multiple human fixtures are due",
                "prove continuation/current-user transitions after each human match",
                "prove whether one pending-fixture slot is global or per-user",
            ),
            capability_dimensions_unlocked_only_after_proof=(
                "simultaneous_human_fixture_dispatch_order_recovered",
                "shared_runtime_supported",
            ),
        ),
        MultiHumanAdjudicationStage(
            stage=STAGE_SAVE_RELOAD,
            priority=4,
            candidate_target_names=(
                "global_user_count",
                "user_lookup_current",
                "user_lookup_indexed",
            ),
            required_source_proof=(
                "identify original save serialization of the complete selected-user list",
                "prove each user's club/runtime state serialization ownership",
                "identify reload restoration order and current-user restoration",
                "prove pending human-fixture/continuation state survives reload coherently",
            ),
            capability_dimensions_unlocked_only_after_proof=(
                "multi_human_save_serialization_recovered",
                "multi_human_save_reload_continuation_recovered",
                "save_reload_supported",
            ),
        ),
    )

    return MultiHumanAdjudicationPlan(
        source_sha256=report["source_sha256"],
        source_proven_hard_user_cap=contract["source_proven_hard_user_cap"],
        stages=stages,
    )


def multi_human_adjudication_contract() -> dict:
    """Expose only the fail-closed proof order and implementation boundary."""
    return {
        "source_proven_hard_user_cap": SOURCE_PROVEN_USER_CAP,
        "stage_order": (
            STAGE_START_ITERATION,
            STAGE_SHARED_RUNTIME,
            STAGE_FIXTURE_DISPATCH,
            STAGE_SAVE_RELOAD,
        ),
        "candidate_calls_are_handoff_semantics": False,
        "raw_global_occurrences_are_xrefs": False,
        "private_source_required_for_stage_completion": True,
        "current_gameplay_simultaneous_users_supported": 1,
        "current_multi_human_start_supported": False,
        "current_shared_runtime_supported": False,
        "current_save_reload_supported": False,
        "gate17_complete": False,
    }

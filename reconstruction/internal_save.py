"""Versioned internal save/load for the modern FM2001 runtime.

This is deliberately an internal port format. It does not parse or claim
compatibility with original FM2001 save files. Immutable source definitions are
reloaded from the same verified database; live runtime state is serialized as
JSON-compatible data and guarded by a structural source signature.
"""

from __future__ import annotations

from datetime import date
from hashlib import sha256
import gzip
import json
from pathlib import Path
from typing import Any

from commercial_timers import UserCommercialTimerState
from concession_offer import ConcessionRuntimeSource
from competition_state import MatchResult, PremierLeagueState
from cup_progression import CupResultRegistry
from domestic_cup_state import DomesticCupScheduleState
from contract_maintenance import (
    ContractRenewalSuggestion,
    ContractRenewalSuggestionKind,
)
from finance_state import BalanceRuntimeState, FinancePosting, FinancialObjectiveState
from game_state import GameCalendar, GameState
from human_gameplay import HumanGameplayController, HumanManagerState
from primary_schedule_shadow import PrimaryScheduleShadowState
from procedural_league_state import LiveProceduralLeagueState
from match_environment import MatchEnvironment
from match_events import (
    BoundaryRecord,
    ChanceRecord,
    IncidentRecord,
    PossessionRecord,
    SubstitutionRecord,
)
from match_orders import TeamOrderPriorities
from match_postmatch import PlayerTransferRequest
from match_schedule import MsvcCrtRng
from match_simulation import NormalMatchResult, SegmentPossession, TimedMatchEvent
from original_fixture_report_capture import NativeCapturedPossession, capture_completed_possession_rows
from match_team_setup import TeamTacticalState
from player_development import DevelopmentState, PeakAges
from runtime_state import RuntimePlayer
from transfer_state import (
    ContractTerms,
    DealInProgress,
    PlayerBidLogEntry,
    PlayerMovement,
    ScheduledTransfer,
    TransferProposal,
    TransferRuntimeState,
)
from youth_state import YouthRecord, YouthTeamState, YouthTrainingState


SAVE_FORMAT = "fm2001-modern-internal-save"
SAVE_SCHEMA_VERSION = 37


def _iso(value: date | None) -> str | None:
    return None if value is None else value.isoformat()


def _date(value: str | None) -> date | None:
    return None if value is None else date.fromisoformat(str(value))


_PLAYER_SIGNATURE_FIELDS = (
    "index", "first_name", "surname", "nationality_id", "date_of_birth",
    "height_cm", "weight_kg", "positions", "target_raw", "eu_status_code",
    "joined_current_club_date",
)
_CLUB_SIGNATURE_FIELDS = (
    "index", "manager_id", "competition_id", "country_id",
    "runtime_value_1c_source", "team_category_code",
    "historical_competition_id", "historical_slot_index",
    "fan_base_index", "related_club_id_0", "related_club_id_1",
    "related_club_id_2",
)
_MANAGER_SIGNATURE_FIELDS = (
    "index", "club_id", "formation_default", "formation_class3",
    "formation_class1", "ai_play_style_source", "ai_aggression_source",
    "ai_with_ball_source", "ai_without_ball_source",
)
_COMPETITION_SIGNATURE_FIELDS = (
    "id", "substitute_quota", "max_non_eu_players", "schedule_container_code",
    "runtime_kind_code", "parent_competition_id", "initialization_order_value",
    "country_region_id", "enumerated_club_reference_0",
    "enumerated_club_reference_1", "runtime_instance_count",
    "scheduled_matchday_count", "valuation_division_category",
)


def _stable_source_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (tuple, list)):
        return [_stable_source_value(v) for v in value]
    return str(value)


def _source_records(values, fields):
    return sorted(
        [
            _stable_source_value(getattr(value, field_name, None))
            for field_name in fields
        ]
        for value in values
    )


def _source_payload(players, clubs, managers, competitions, fixtures):
    return {
        "players": _source_records(players, _PLAYER_SIGNATURE_FIELDS),
        "clubs": _source_records(clubs, _CLUB_SIGNATURE_FIELDS),
        "managers": _source_records(managers, _MANAGER_SIGNATURE_FIELDS),
        "competitions": _source_records(competitions, _COMPETITION_SIGNATURE_FIELDS),
        "fixtures": sorted(
            [
                int(fixture.id),
                int(fixture.round_index),
                int(fixture.home_club_id),
                int(fixture.away_club_id),
            ]
            for fixture in fixtures
        ),
    }


def _source_payload_from_database(database) -> dict[str, Any]:
    return _source_payload(
        tuple(getattr(database, "players", ())),
        tuple(getattr(database, "clubs", ())),
        tuple(getattr(database, "managers", ())),
        tuple(getattr(database, "competitions", ())),
        tuple(getattr(database, "real_fixtures", ())),
    )


def _source_payload_from_state(state: GameState) -> dict[str, Any]:
    """Build source validation from immutable database identity.

    Fresh youth generation mutates live first/surname, nationality and DOB
    through 0x41E510/0x61DD30. RuntimePlayer keeps immutable mirrors for those
    source fields so a valid youth save still hashes against the supplied
    original database.

    Annual mode regenerates Premier League fixtures procedurally, so the live
    league cannot define source-database identity after a rollover. Database-
    backed GameState instances retain the original fixture rows separately.
    Lightweight states that did not originate from a database keep the legacy
    live-fixture fallback.
    """

    player_records = []
    for player in state.players.values():
        values = []
        for field_name in _PLAYER_SIGNATURE_FIELDS:
            mirror_name = {
                "first_name": "source_first_name",
                "surname": "source_surname",
                "nationality_id": "source_nationality_id",
                "date_of_birth": "source_date_of_birth",
                "joined_current_club_date": "source_joined_current_club_date",
            }.get(field_name)
            if mirror_name is not None:
                mirror = getattr(player, mirror_name, None)
                value = (
                    mirror
                    if mirror is not None
                    else getattr(player, field_name, None)
                )
            else:
                value = getattr(player, field_name, None)
            values.append(_stable_source_value(value))
        player_records.append(values)

    source_fixture_identity = getattr(state, "source_fixture_identity", None)
    if source_fixture_identity is None:
        league = state.premier_league
        fixture_rows = tuple(
            (
                int(fixture.id),
                int(fixture.round_index),
                int(fixture.home_club_id),
                int(fixture.away_club_id),
            )
            for fixture in (
                () if league is None else tuple(league.fixtures.values())
            )
        )
    else:
        fixture_rows = tuple(
            tuple(int(value) for value in row)
            for row in source_fixture_identity
        )

    return {
        "players": sorted(player_records),
        "clubs": _source_records(tuple(state.clubs.values()), _CLUB_SIGNATURE_FIELDS),
        "managers": _source_records(tuple(state.managers.values()), _MANAGER_SIGNATURE_FIELDS),
        "competitions": _source_records(
            tuple(state.competitions.values()),
            _COMPETITION_SIGNATURE_FIELDS,
        ),
        "fixtures": sorted([list(row) for row in fixture_rows]),
    }


def _source_signature(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return sha256(blob).hexdigest()


def _source_descriptor_from_state(state: GameState) -> dict[str, Any]:
    payload = _source_payload_from_state(state)
    return {
        "signature_sha256": _source_signature(payload),
        "player_count": len(payload["players"]),
        "club_count": len(payload["clubs"]),
        "manager_count": len(payload["managers"]),
        "competition_count": len(payload["competitions"]),
        "fixture_count": len(payload["fixtures"]),
    }


def _assert_database_matches(database, descriptor: dict[str, Any]) -> None:
    payload = _source_payload_from_database(database)
    actual = _source_signature(payload)
    expected = str(descriptor["signature_sha256"])
    if actual != expected:
        raise ValueError(
            "save source database does not match the supplied FM2001 database: "
            f"expected {expected}, got {actual}"
        )


def _snapshot_development(value: DevelopmentState | None):
    if value is None:
        return None
    return [
        int(value.baseline_age),
        [int(v) for v in value.baseline_raw],
        [
            int(value.peak_ages.physical),
            int(value.peak_ages.skill),
            int(value.peak_ages.late),
        ],
    ]


def _restore_development(value, target_raw) -> DevelopmentState | None:
    if value is None:
        return None
    peaks = value[2]
    return DevelopmentState(
        baseline_age=int(value[0]),
        baseline_raw=tuple(int(v) for v in value[1]),
        target_raw=tuple(int(v) for v in target_raw),
        peak_ages=PeakAges(
            physical=int(peaks[0]),
            skill=int(peaks[1]),
            late=int(peaks[2]),
        ),
    )


_PLAYER_FLAG_MATCH_ACTIVE = 1 << 0
_PLAYER_FLAG_SUBSTITUTE = 1 << 1
_PLAYER_FLAG_INJURED = 1 << 2
_PLAYER_FLAG_SUSPENDED = 1 << 3
_PLAYER_FLAG_SELECTION_EXCLUDED = 1 << 4
_PLAYER_FLAG_NON_EU = 1 << 5
_PLAYER_FLAG_TRANSFER_LISTED = 1 << 6
_PLAYER_FLAG_SIGNED_FOR_OTHER_CLUB = 1 << 7
_PLAYER_FLAG_LOAN_LISTED = 1 << 8
_PLAYER_FLAG_OUT_OF_CONTRACT = 1 << 9
_PLAYER_FLAG_STATUS_BIT_3 = 1 << 10
_PLAYER_FLAG_WANTED = 1 << 11

# Schema-2 player records intentionally use positional arrays. With roughly 30k
# players, repeating descriptive JSON keys for every player dominated the save
# size. The schema version plus this ordered field definition keeps the format
# explicit while source-backed immutable identity/biographical fields stay in
# Master.dat rather than being duplicated into each save.
PLAYER_RECORD_FIELDS = (
    "index",
    "club_id",
    "shirt_number",
    "current_raw",
    "development",
    "training_modifiers_or_null",
    "flags",
    "condition",
    "form_state",
    "current_position",
    "position_aux_code",
    "balance_position_code",
    "discipline_yellow_total",
    "discipline_yellow_cycle",
    "suspension_matches_remaining",
    "suspension_effective_date",
    "injury_return_date",
    "injury_source_mode",
    "injury_severity_code",
    "injury_history_weight",
    "morale",
    "startup_month_span",
    "weekly_wage",
    "contract_expiry_date",
    "loan_club_id",
    "current_club_join_date",
    "promotion_bonus",
    "appearance_fee",
    "relegation_transfer_request_clause",
    "big_club_offer_clause",
    "big_money_offer_clause",
    "house",
    "car",
    "ai_transfer_block_value_64",
    "ai_transfer_status_bit_9",
    "training_method_id",
    "training_countdown",
    "training_active_count",
    "training_skill_states_or_null",
    "training_method_results_or_null",
    "match_performance_history_or_null",
    "match_performance_history_count",
    "match_performance_history_write_index",
    "contract_special_state_138",
    "contract_renewal_suggestion_pending",
    "previous_club_id_74",
    "live_first_name",
    "live_surname",
    "live_nationality_id",
    "live_date_of_birth",
)


def _snapshot_player(player: RuntimePlayer) -> list[Any]:
    flags = 0
    if player.match_active:
        flags |= _PLAYER_FLAG_MATCH_ACTIVE
    if player.match_substitute_available:
        flags |= _PLAYER_FLAG_SUBSTITUTE
    if player.injured:
        flags |= _PLAYER_FLAG_INJURED
    if player.suspended:
        flags |= _PLAYER_FLAG_SUSPENDED
    if player.selection_excluded:
        flags |= _PLAYER_FLAG_SELECTION_EXCLUDED
    if player.non_eu:
        flags |= _PLAYER_FLAG_NON_EU
    if player.transfer_listed:
        flags |= _PLAYER_FLAG_TRANSFER_LISTED
    if player.signed_for_other_club:
        flags |= _PLAYER_FLAG_SIGNED_FOR_OTHER_CLUB
    if player.loan_listed:
        flags |= _PLAYER_FLAG_LOAN_LISTED
    if player.out_of_contract:
        flags |= _PLAYER_FLAG_OUT_OF_CONTRACT
    if player.status_bit_3:
        flags |= _PLAYER_FLAG_STATUS_BIT_3
    if player.wanted:
        flags |= _PLAYER_FLAG_WANTED

    training = [int(v) for v in player.training_modifiers]
    return [
        int(player.index),
        int(player.club_id),
        int(player.shirt_number),
        [int(v) for v in player.current_raw],
        _snapshot_development(player.development),
        None if not any(training) else training,
        flags,
        int(player.condition),
        int(player.form_state),
        int(player.current_position),
        int(player.position_aux_code),
        int(player.balance_position_code),
        int(player.discipline_yellow_total),
        int(player.discipline_yellow_cycle),
        int(player.suspension_matches_remaining),
        _iso(player.suspension_effective_date),
        _iso(player.injury_return_date),
        player.injury_source_mode,
        player.injury_severity_code,
        int(player.injury_history_weight),
        int(player.morale),
        int(player.startup_month_span),
        int(player.weekly_wage),
        _iso(player.contract_expiry_date),
        None if player.loan_club_id is None else int(player.loan_club_id),
        _iso(player.current_club_join_date),
        int(player.promotion_bonus),
        int(player.appearance_fee),
        bool(player.relegation_transfer_request_clause),
        bool(player.big_club_offer_clause),
        bool(player.big_money_offer_clause),
        bool(player.house),
        bool(player.car),
        int(player.ai_transfer_block_value_64),
        bool(player.ai_transfer_status_bit_9),
        int(player.training_method_id),
        int(player.training_countdown),
        int(player.training_active_count),
        (
            None
            if player.training_skill_states == [1] * 17
            else [int(v) for v in player.training_skill_states]
        ),
        (
            None
            if not any(player.training_method_results)
            else [int(v) for v in player.training_method_results]
        ),
        (
            None
            if int(player.match_performance_history_count) == 0
            and not any(player.match_performance_history)
            else [int(v) & 0xFF for v in player.match_performance_history]
        ),
        int(player.match_performance_history_count),
        int(player.match_performance_history_write_index),
        int(player.contract_special_state_138),
        bool(player.contract_renewal_suggestion_pending),
        (
            None
            if player.previous_club_id_74 is None
            else int(player.previous_club_id_74)
        ),
        str(player.first_name),
        str(player.surname),
        int(player.nationality_id),
        _iso(player.date_of_birth),
    ]


def _restore_player(value: list[Any], source) -> RuntimePlayer:
    if len(value) != len(PLAYER_RECORD_FIELDS):
        raise ValueError(
            f"invalid schema-2 player record length {len(value)}; "
            f"expected {len(PLAYER_RECORD_FIELDS)}"
        )
    if int(value[0]) != int(source.index):
        raise ValueError("saved player record does not match source player ID")

    flags = int(value[6])
    training = value[5]
    return RuntimePlayer(
        index=int(source.index),
        first_name=str(value[46]),
        surname=str(value[47]),
        club_id=int(value[1]),
        nationality_id=int(value[48]),
        date_of_birth=_date(value[49]),
        shirt_number=int(value[2]),
        height_cm=int(source.height_cm),
        weight_kg=int(source.weight_kg),
        positions=tuple(int(v) for v in source.positions),
        current_raw=[int(v) for v in value[3]],
        target_raw=tuple(int(v) for v in source.target_raw),
        development=_restore_development(value[4], source.target_raw),
        source_first_name=str(source.first_name),
        source_surname=str(source.surname),
        source_nationality_id=int(source.nationality_id),
        source_date_of_birth=source.date_of_birth,
        source_joined_current_club_date=getattr(
            source, "joined_current_club_date", None
        ),
        training_modifiers=(
            [0] * 17 if training is None else [int(v) for v in training]
        ),
        match_active=bool(flags & _PLAYER_FLAG_MATCH_ACTIVE),
        match_substitute_available=bool(flags & _PLAYER_FLAG_SUBSTITUTE),
        condition=int(value[7]),
        form_state=int(value[8]),
        current_position=int(value[9]),
        position_aux_code=int(value[10]),
        balance_position_code=int(value[11]),
        injured=bool(flags & _PLAYER_FLAG_INJURED),
        suspended=bool(flags & _PLAYER_FLAG_SUSPENDED),
        selection_excluded=bool(flags & _PLAYER_FLAG_SELECTION_EXCLUDED),
        status_bit_3=bool(flags & _PLAYER_FLAG_STATUS_BIT_3),
        non_eu=bool(flags & _PLAYER_FLAG_NON_EU),
        eu_status_code=int(getattr(source, "eu_status_code", 2)),
        transfer_listed=bool(flags & _PLAYER_FLAG_TRANSFER_LISTED),
        wanted=bool(flags & _PLAYER_FLAG_WANTED),
        out_of_contract=bool(flags & _PLAYER_FLAG_OUT_OF_CONTRACT),
        loan_listed=bool(flags & _PLAYER_FLAG_LOAN_LISTED),
        loan_club_id=(None if value[24] is None else int(value[24])),
        signed_for_other_club=bool(
            flags & _PLAYER_FLAG_SIGNED_FOR_OTHER_CLUB
        ),
        current_club_join_date=_date(value[25]),
        promotion_bonus=int(value[26]),
        appearance_fee=int(value[27]),
        relegation_transfer_request_clause=bool(value[28]),
        big_club_offer_clause=bool(value[29]),
        big_money_offer_clause=bool(value[30]),
        house=bool(value[31]),
        car=bool(value[32]),
        ai_transfer_block_value_64=int(value[33]),
        ai_transfer_status_bit_9=bool(value[34]),
        training_method_id=int(value[35]),
        training_countdown=int(value[36]),
        training_active_count=int(value[37]),
        training_skill_states=(
            [1] * 17 if value[38] is None else [int(v) for v in value[38]]
        ),
        training_method_results=(
            [0] * 7 if value[39] is None else [int(v) for v in value[39]]
        ),
        match_performance_history=(
            [0] * 6 if value[40] is None else [int(v) & 0xFF for v in value[40]]
        ),
        match_performance_history_count=int(value[41]),
        match_performance_history_write_index=int(value[42]),
        contract_special_state_138=int(value[43]),
        contract_renewal_suggestion_pending=bool(value[44]),
        previous_club_id_74=(None if value[45] is None else int(value[45])),
        discipline_yellow_total=int(value[12]),
        discipline_yellow_cycle=int(value[13]),
        suspension_matches_remaining=int(value[14]),
        suspension_effective_date=_date(value[15]),
        injury_return_date=_date(value[16]),
        injury_source_mode=(None if value[17] is None else int(value[17])),
        injury_severity_code=(None if value[18] is None else int(value[18])),
        injury_history_weight=int(value[19]),
        morale=int(value[20]),
        startup_month_span=int(value[21]),
        weekly_wage=int(value[22]),
        contract_expiry_date=_date(value[23]),
    )


def _snapshot_event(event) -> dict[str, Any]:
    if isinstance(event, ChanceRecord):
        return {
            "type": "chance",
            "source": int(event.source),
            "raw_outcome": int(event.raw_outcome),
            "player_side": int(event.player_side),
            "player_index": int(event.player_index),
            "side_inversion": bool(event.side_inversion),
            "finish_mode": int(event.finish_mode),
            "secondary_player_side": (
                None
                if event.secondary_player_side is None
                else int(event.secondary_player_side)
            ),
            "secondary_player_index": (
                None
                if event.secondary_player_index is None
                else int(event.secondary_player_index)
            ),
        }
    if isinstance(event, IncidentRecord):
        return {
            "type": "incident",
            "kind": int(event.kind),
            "player_side": int(event.player_side),
            "player_index": int(event.player_index),
        }
    if isinstance(event, SubstitutionRecord):
        return {
            "type": "substitution",
            "player_side": int(event.player_side),
            "outgoing_player_index": int(event.outgoing_player_index),
            "incoming_player_index": int(event.incoming_player_index),
        }
    if isinstance(event, BoundaryRecord):
        return {"type": "boundary", "kind": int(event.kind), "outcome": event.outcome}
    if isinstance(event, PossessionRecord):
        return {
            "type": "possession",
            "territory": int(event.territory),
            "side0_percent": int(event.side0_percent),
            "neutral_percent": int(event.neutral_percent),
        }
    raise TypeError(f"unsupported match event type {type(event)!r}")


def _restore_event(value: dict[str, Any]):
    kind = value["type"]
    if kind == "chance":
        return ChanceRecord(
            source=int(value["source"]),
            raw_outcome=int(value["raw_outcome"]),
            player_side=int(value["player_side"]),
            player_index=int(value["player_index"]),
            side_inversion=bool(value["side_inversion"]),
            finish_mode=int(value["finish_mode"]),
            secondary_player_side=(
                None
                if value.get("secondary_player_side") is None
                else int(value["secondary_player_side"])
            ),
            secondary_player_index=(
                None
                if value.get("secondary_player_index") is None
                else int(value["secondary_player_index"])
            ),
        )
    if kind == "incident":
        return IncidentRecord(
            kind=int(value["kind"]),
            player_side=int(value["player_side"]),
            player_index=int(value["player_index"]),
        )
    if kind == "substitution":
        return SubstitutionRecord(
            player_side=int(value["player_side"]),
            outgoing_player_index=int(value["outgoing_player_index"]),
            incoming_player_index=int(value["incoming_player_index"]),
        )
    if kind == "boundary":
        return BoundaryRecord(kind=int(value["kind"]), outcome=value['outcome'])
    if kind == "possession":
        return PossessionRecord(
            territory=int(value["territory"]),
            side0_percent=int(value["side0_percent"]),
            neutral_percent=int(value["neutral_percent"]),
        )
    raise ValueError(f"unknown saved match event type {kind!r}")


def _snapshot_normal_match_result(result: NormalMatchResult) -> dict[str, Any]:
    from original_fixture_report_capture import LiveReportCompletionScalars
    scalars = result.native_completion_scalars
    if scalars is not None and type(scalars) is not LiveReportCompletionScalars:
        raise ValueError('Invalid retained completion scalars')
    capture = result.captured_possession
    if capture is not None:
        _validate_retained_possession(result)
    return {
        "native_completion_scalars": None if scalars is None else {
            "calendar": list(scalars.calendar), "scores": list(scalars.scores),
        },
        "native_compact_events": None if result.native_compact_events is None else [
            {"minute": r.minute, "kind": r.kind, "fields": [list(f) for f in r.fields]}
            for r in _validated_compact_stream(result.native_compact_events)
        ],
        # A complete calculator output, not a captured report / ownership link.
        "captured_possession": None if capture is None else {
            "triplets": capture.triplets.hex(), "averages": capture.averages.hex(),
        },
        "events": [
            {"minute": int(timed.minute), "event": _snapshot_event(timed.event)}
            for timed in result.events
        ],
        "possession_segments": [
            {
                "calculation_minute": int(segment.calculation_minute),
                "record": _snapshot_event(segment.record),
            }
            for segment in result.possession_segments
        ],
    }


def _validate_retained_possession(result: NormalMatchResult) -> None:
    capture = result.captured_possession
    if type(capture) is not NativeCapturedPossession:
        raise ValueError('Invalid retained possession input')
    expected = capture_completed_possession_rows(tuple(
        (segment.calculation_minute, bytes((segment.record.territory,
                                          segment.record.side0_percent,
                                          segment.record.neutral_percent)))
        for segment in result.possession_segments
    ))
    if capture != expected:
        raise ValueError('Retained possession disagrees with complete calculator rows')


def _restore_normal_match_result(value: dict[str, Any]) -> NormalMatchResult:
    from original_fixture_report_capture import LiveReportCompletionScalars
    saved_scalars = value['native_completion_scalars']
    scalars = None
    if saved_scalars is not None:
        if (type(saved_scalars) is not dict or set(saved_scalars) != {'calendar', 'scores'}
                or any(type(v) is not list for v in saved_scalars.values())):
            raise ValueError('Invalid saved completion scalars')
        scalars = LiveReportCompletionScalars(tuple(saved_scalars['calendar']),
                                            tuple(saved_scalars['scores']))
    # Missing input is NOT rebuilt from semantic rows, score or completion.
    saved_capture = value["captured_possession"]
    capture = None
    if saved_capture is not None:
        if (type(saved_capture) is not dict
                or set(saved_capture) != {"triplets", "averages"}
                or any(type(item) is not str for item in saved_capture.values())):
            raise ValueError('Invalid saved possession input')
        capture = NativeCapturedPossession(bytes.fromhex(saved_capture['triplets']),
                                           bytes.fromhex(saved_capture['averages']))
    from native_compact_match import NativeCompactRecord
    compact = value['native_compact_events']
    if compact is not None:
        if type(compact) is not list or any(
                type(r) is not dict or set(r) != {'minute', 'kind', 'fields'}
                or type(r['fields']) is not list
                or any(type(f) is not list or len(f) != 2 for f in r['fields']) for r in compact):
            raise ValueError('Invalid saved native compact stream')
        compact = _validated_compact_stream(tuple(NativeCompactRecord(
            r['minute'], r['kind'], tuple(tuple(f) for f in r['fields'])
        ) for r in compact))
    result = NormalMatchResult(
        native_completion_scalars=scalars,
        captured_possession=capture,
        native_compact_events=compact,
        events=tuple(
            TimedMatchEvent(
                minute=int(item["minute"]),
                event=_restore_event(item["event"]),
            )
            for item in value["events"]
        ),
        possession_segments=tuple(
            SegmentPossession(
                calculation_minute=int(item["calculation_minute"]),
                record=_restore_event(item["record"]),
            )
            for item in value["possession_segments"]
        ),
    )
    if capture is not None:
        _validate_retained_possession(result)
    return result


def _validated_compact_stream(records):
    from native_compact_match import NativeCompactRecord
    from original_fixture_report_packing import pack_live_native_match_script
    if type(records) is not tuple or any(type(r) is not NativeCompactRecord for r in records):
        raise ValueError('Saved compact stream requires immutable native records')
    if not records or not any(r.kind == 6 for r in records) or not any(r.kind == 7 for r in records):
        raise ValueError('Saved compact stream must retain ordinary boundaries')
    if tuple(r.minute for r in records) != tuple(sorted(r.minute for r in records)):
        raise ValueError('Saved compact stream must retain finalized link order')
    for record in records:
        if record.kind == 7 and record.field(0x24) not in (0, 1, 2):
            raise ValueError('Saved compact stream has invalid FullTime payload')
    pack_live_native_match_script(records)
    return records


def _snapshot_contract_terms(value: ContractTerms) -> dict[str, Any]:
    return {
        "weekly_wage": int(value.weekly_wage),
        "signing_on_fee": int(value.signing_on_fee),
        "promotion_bonus": int(value.promotion_bonus),
        "contract_length_months": int(value.contract_length_months),
        "appearance_fee": int(value.appearance_fee),
        "relegation_transfer_request_clause": bool(
            value.relegation_transfer_request_clause
        ),
        "big_club_offer_clause": bool(value.big_club_offer_clause),
        "big_money_offer_clause": bool(value.big_money_offer_clause),
        "house": bool(value.house),
        "car": bool(value.car),
    }


def _restore_contract_terms(value: dict[str, Any]) -> ContractTerms:
    return ContractTerms(
        weekly_wage=int(value["weekly_wage"]),
        signing_on_fee=int(value["signing_on_fee"]),
        promotion_bonus=int(value["promotion_bonus"]),
        contract_length_months=int(value["contract_length_months"]),
        appearance_fee=int(value["appearance_fee"]),
        relegation_transfer_request_clause=bool(
            value["relegation_transfer_request_clause"]
        ),
        big_club_offer_clause=bool(value["big_club_offer_clause"]),
        big_money_offer_clause=bool(value["big_money_offer_clause"]),
        house=bool(value["house"]),
        car=bool(value["car"]),
    )


def _snapshot_transfer_state(value: TransferRuntimeState) -> dict[str, Any]:
    return {
        "proposals": [
            {
                "target_player_id": int(proposal.target_player_id),
                "buying_club_id": int(proposal.buying_club_id),
                "cash_fee": int(proposal.cash_fee),
                "exchange_player_ids": [
                    int(player_id) for player_id in proposal.exchange_player_ids
                ],
                "negotiation_state_14": int(proposal.negotiation_state_14),
                "negotiation_state_15": int(proposal.negotiation_state_15),
                "contract_terms": _snapshot_contract_terms(
                    proposal.contract_terms
                ),
                "previous_wage_offer": int(proposal.previous_wage_offer),
                "previous_signing_on_fee_offer": int(
                    proposal.previous_signing_on_fee_offer
                ),
                "field_40": int(proposal.field_40),
                "field_44": int(proposal.field_44),
                "previous_total_value": int(proposal.previous_total_value),
                "field_4c": int(proposal.field_4c),
            }
            for _, proposal in sorted(value.proposals.items())
        ],
        "deals": [
            {
                "player_id": int(deal.player_id),
                "buying_club_id": int(deal.buying_club_id),
                "selling_club_id": int(deal.selling_club_id),
                "state": int(deal.state),
                "contract_terms": _snapshot_contract_terms(
                    deal.contract_terms
                ),
                "created_date": deal.created_date.isoformat(),
            }
            for _, deal in sorted(value.deals.items())
        ],
        "bid_log": [
            {
                "player_id": int(entry.player_id),
                "bidding_club_id": int(entry.bidding_club_id),
                "bid_value": int(entry.bid_value),
                "bid_date": entry.bid_date.isoformat(),
                "status_counter": int(entry.status_counter),
            }
            for _, entry in sorted(value.bid_log.items())
        ],
        "movements": [
            {
                "player_id": int(movement.player_id),
                "from_club_id": int(movement.from_club_id),
                "to_club_id": int(movement.to_club_id),
                "consideration": int(movement.consideration),
                "movement_date": movement.movement_date.isoformat(),
            }
            for movement in value.movements
        ],
        "scheduled_transfers": [
            {
                "due_date": scheduled.due_date.isoformat(),
                "mode": int(scheduled.mode),
                "proposal": {
                    "target_player_id": int(scheduled.proposal.target_player_id),
                    "buying_club_id": int(scheduled.proposal.buying_club_id),
                    "cash_fee": int(scheduled.proposal.cash_fee),
                    "exchange_player_ids": [
                        int(player_id)
                        for player_id in scheduled.proposal.exchange_player_ids
                    ],
                    "negotiation_state_14": int(
                        scheduled.proposal.negotiation_state_14
                    ),
                    "negotiation_state_15": int(
                        scheduled.proposal.negotiation_state_15
                    ),
                    "contract_terms": _snapshot_contract_terms(
                        scheduled.proposal.contract_terms
                    ),
                    "previous_wage_offer": int(
                        scheduled.proposal.previous_wage_offer
                    ),
                    "previous_signing_on_fee_offer": int(
                        scheduled.proposal.previous_signing_on_fee_offer
                    ),
                    "field_40": int(scheduled.proposal.field_40),
                    "field_44": int(scheduled.proposal.field_44),
                    "previous_total_value": int(
                        scheduled.proposal.previous_total_value
                    ),
                    "field_4c": int(scheduled.proposal.field_4c),
                },
            }
            for scheduled in value.scheduled_transfers
        ],
    }


def _restore_transfer_state(value: dict[str, Any] | None) -> TransferRuntimeState:
    if value is None:
        return TransferRuntimeState()

    runtime = TransferRuntimeState()
    for proposal_value in value.get("proposals", ()):
        proposal = TransferProposal(
            target_player_id=int(proposal_value["target_player_id"]),
            buying_club_id=int(proposal_value["buying_club_id"]),
            cash_fee=int(proposal_value["cash_fee"]),
            exchange_player_ids=tuple(
                int(player_id)
                for player_id in proposal_value["exchange_player_ids"]
            ),
            negotiation_state_14=int(proposal_value["negotiation_state_14"]),
            negotiation_state_15=int(proposal_value["negotiation_state_15"]),
            contract_terms=_restore_contract_terms(
                proposal_value["contract_terms"]
            ),
            previous_wage_offer=int(proposal_value["previous_wage_offer"]),
            previous_signing_on_fee_offer=int(
                proposal_value["previous_signing_on_fee_offer"]
            ),
            field_40=int(proposal_value["field_40"]),
            field_44=int(proposal_value["field_44"]),
            previous_total_value=int(proposal_value["previous_total_value"]),
            field_4c=int(proposal_value["field_4c"]),
        )
        runtime.proposals[
            runtime.proposal_key(
                proposal.target_player_id,
                proposal.buying_club_id,
            )
        ] = proposal

    for deal_value in value.get("deals", ()):
        deal = DealInProgress(
            player_id=int(deal_value["player_id"]),
            buying_club_id=int(deal_value["buying_club_id"]),
            selling_club_id=int(deal_value["selling_club_id"]),
            state=int(deal_value["state"]),
            contract_terms=_restore_contract_terms(
                deal_value["contract_terms"]
            ),
            created_date=date.fromisoformat(deal_value["created_date"]),
        )
        runtime.deals[int(deal.player_id)] = deal

    for entry_value in value.get("bid_log", ()):
        entry = PlayerBidLogEntry(
            player_id=int(entry_value["player_id"]),
            bidding_club_id=int(entry_value["bidding_club_id"]),
            bid_value=int(entry_value["bid_value"]),
            bid_date=date.fromisoformat(entry_value["bid_date"]),
            status_counter=int(entry_value["status_counter"]),
        )
        runtime.bid_log[
            runtime.proposal_key(entry.player_id, entry.bidding_club_id)
        ] = entry

    for movement_value in value.get("movements", ()):
        runtime.movements.append(
            PlayerMovement(
                player_id=int(movement_value["player_id"]),
                from_club_id=int(movement_value["from_club_id"]),
                to_club_id=int(movement_value["to_club_id"]),
                consideration=int(movement_value["consideration"]),
                movement_date=date.fromisoformat(
                    movement_value["movement_date"]
                ),
            )
        )

    for scheduled_value in value.get("scheduled_transfers", ()):
        proposal_value = scheduled_value["proposal"]
        proposal = TransferProposal(
            target_player_id=int(proposal_value["target_player_id"]),
            buying_club_id=int(proposal_value["buying_club_id"]),
            cash_fee=int(proposal_value["cash_fee"]),
            exchange_player_ids=tuple(
                int(player_id)
                for player_id in proposal_value["exchange_player_ids"]
            ),
            negotiation_state_14=int(proposal_value["negotiation_state_14"]),
            negotiation_state_15=int(proposal_value["negotiation_state_15"]),
            contract_terms=_restore_contract_terms(
                proposal_value["contract_terms"]
            ),
            previous_wage_offer=int(proposal_value["previous_wage_offer"]),
            previous_signing_on_fee_offer=int(
                proposal_value["previous_signing_on_fee_offer"]
            ),
            field_40=int(proposal_value["field_40"]),
            field_44=int(proposal_value["field_44"]),
            previous_total_value=int(proposal_value["previous_total_value"]),
            field_4c=int(proposal_value["field_4c"]),
        )
        runtime.scheduled_transfers.append(
            ScheduledTransfer(
                proposal=proposal,
                due_date=date.fromisoformat(scheduled_value["due_date"]),
                mode=int(scheduled_value["mode"]),
            )
        )
    return runtime


def _snapshot_youth_state(value: YouthTeamState | None):
    if value is None:
        return None
    return [
        {
            "player_id": int(record.player_id),
            "source_roster_club_id": int(record.source_roster_club_id),
            "field_08": int(record.field_08),
            "field_0c": int(record.field_0c),
            "field_10": int(record.field_10),
            "status_14": bool(record.status_14),
            "training": {
                "method_id": int(record.training.method_id),
                "countdown": int(record.training.countdown),
                "active_count": int(record.training.active_count),
                "modifiers": [int(v) for v in record.training.modifiers],
                "skill_states": [int(v) for v in record.training.skill_states],
                "method_results": [int(v) for v in record.training.method_results],
            },
        }
        for record in value.records
    ]


def _restore_youth_state(value) -> YouthTeamState | None:
    if value is None:
        return None
    return YouthTeamState(
        records=[
            YouthRecord(
                player_id=int(record["player_id"]),
                source_roster_club_id=int(record["source_roster_club_id"]),
                field_08=int(record["field_08"]),
                field_0c=int(record["field_0c"]),
                field_10=int(record["field_10"]),
                status_14=bool(record["status_14"]),
                training=YouthTrainingState(
                    method_id=int(record["training"]["method_id"]),
                    countdown=int(record["training"]["countdown"]),
                    active_count=int(record["training"]["active_count"]),
                    modifiers=[int(v) for v in record["training"]["modifiers"]],
                    skill_states=[int(v) for v in record["training"]["skill_states"]],
                    method_results=[int(v) for v in record["training"]["method_results"]],
                ),
            )
            for record in value
        ]
    )


def _snapshot_cup_result_registry(registry: CupResultRegistry) -> dict[str, Any]:
    return {
        "outcomes": [
            {
                "result_token": list(outcome.result_token),
                "participant_0_club_id": int(outcome.participant_0_club_id),
                "participant_1_club_id": int(outcome.participant_1_club_id),
                "winner_club_id": int(outcome.winner_club_id),
            }
            for _, outcome in sorted(
                registry.outcomes.items(),
                key=lambda item: repr(item[0]),
            )
        ],
        "competition_rankings": [
            {
                "competition_id": int(key[0]),
                "competition_context": int(key[1]),
                "club_ids": [int(club_id) for club_id in ranking],
            }
            for key, ranking in sorted(registry.competition_rankings.items())
        ],
        "group_position_rankings": [
            {
                "competition_id": int(key[0]),
                "position_index": int(key[1]),
                "club_ids": [int(club_id) for club_id in ranking],
            }
            for key, ranking in sorted(registry.group_position_rankings.items())
        ],
    }


def _restore_cup_result_registry(value) -> CupResultRegistry:
    registry = CupResultRegistry()
    # Tolerate the pre-schema-29 helper shape for direct GameState restore
    # callers even though normal save loading remains schema-version strict.
    if isinstance(value, list):
        outcomes = value
        rankings = ()
        group_position_rankings = ()
    else:
        value = value or {}
        outcomes = value.get("outcomes", ())
        rankings = value.get("competition_rankings", ())
        group_position_rankings = value.get("group_position_rankings", ())

    for record in outcomes:
        registry.record_knockout_outcome(
            tuple(record["result_token"]),
            int(record["participant_0_club_id"]),
            int(record["participant_1_club_id"]),
            int(record["winner_club_id"]),
        )
    for record in rankings:
        registry.record_competition_ranking(
            int(record["competition_id"]),
            tuple(int(club_id) for club_id in record["club_ids"]),
            competition_context=int(record.get("competition_context", 0)),
        )
    for record in group_position_rankings:
        registry.replace_group_position_ranking(
            int(record["competition_id"]),
            int(record["position_index"]),
            tuple(int(club_id) for club_id in record["club_ids"]),
        )
    return registry


def snapshot_game_state(state: GameState) -> dict[str, Any]:
    league = state.premier_league
    league_snapshot = None
    if league is not None:
        league_snapshot = {
            "fixture_source_order": [int(v) for v in league.fixture_source_order],
            "round_source_order": [int(v) for v in league.round_source_order],
            "club_ids": [int(v) for v in league.club_ids],
            "results": [
                {
                    "fixture_id": int(result.fixture_id),
                    "home_goals": int(result.home_goals),
                    "away_goals": int(result.away_goals),
                }
                for _, result in sorted(league.results.items())
            ],
            "round_dates": {
                str(int(round_index)): value.isoformat()
                for round_index, value in sorted(league.round_dates.items())
            },
        }

    return {
        "calendar_date": state.calendar.current_date.isoformat(),
        "monthly_player_updates": int(state.monthly_player_updates),
        "players": [
            _snapshot_player(state.players[player_id])
            for player_id in sorted(state.players)
        ],
        "club_roster_order": {
            str(int(club_id)): [int(v) for v in values]
            for club_id, values in sorted(state.club_roster_order.items())
        },
        "club_competition_membership": {
            str(int(club_id)): int(competition_id)
            for club_id, competition_id
            in sorted(state.club_competition_membership.items())
        },
        "premier_league": league_snapshot,
        "cup_results": _snapshot_cup_result_registry(state.cup_results),
        "domestic_cups": state.domestic_cups.snapshot(),
        "european_cups": state.european_cups.snapshot(),
        "qualification_cups": state.qualification_cups.snapshot(),
        "procedural_leagues": [
            live.snapshot()
            for _, live in sorted(state.procedural_leagues.items())
        ],
        "team_tactics": {
            str(int(club_id)): {
                "play_style": int(value.play_style),
                "without_ball_style": int(value.without_ball_style),
                "with_ball_style": int(value.with_ball_style),
                "aggression": int(value.aggression),
            }
            for club_id, value in sorted(state.team_tactics.items())
        },
        "pitch_wear": {
            str(int(club_id)): int(value)
            for club_id, value in sorted(state.pitch_wear.items())
        },
        "prepared_match_environments": {
            str(int(fixture_id)): {
                "temperature_c": int(value.temperature_c),
                "weather_code": int(value.weather_code),
                "weekday_evening": bool(value.weekday_evening),
            }
            for fixture_id, value in sorted(state.prepared_match_environments.items())
        },
        "premier_league_scheduler_order": {
            str(int(round_index)): [int(v) for v in values]
            for round_index, values in sorted(state.premier_league_scheduler_order.items())
        },
        "primary_schedule_shadow": state.primary_schedule_shadow.snapshot(),
        "primary_matchday_order": {
            on_date.isoformat(): [
                (
                    [str(entry[0]), int(entry[1])]
                    if entry[0] == "premier_league"
                    else [str(entry[0]), list(entry[1])]
                )
                for entry in entries
            ]
            for on_date, entries in sorted(state.primary_matchday_order.items())
        },
        "transfers": _snapshot_transfer_state(state.transfers),
        "contract_renewal_suggestions": [
            {
                "player_id": int(value.player_id),
                "queued_on": value.queued_on.isoformat(),
                "kind": str(value.kind.value),
            }
            for value in state.contract_renewal_suggestions
        ],
        "player_transfer_requests": [
            {
                "player_id": int(value.player_id),
                "queued_on": value.queued_on.isoformat(),
                "due_on": value.due_on.isoformat(),
            }
            for value in state.player_transfer_requests
        ],
        "finance_balances": {
            str(int(club_id)): {
                "current_cash": balance.current_cash,
                "financial_objective": (
                    None
                    if balance.financial_objective is None
                    else {
                        "base_cash": balance.financial_objective.base_cash,
                        "candidate_ids": [
                            int(value) for value in balance.financial_objective.candidate_ids
                        ],
                        "selected_objective_id": int(
                            balance.financial_objective.selected_objective_id
                        ),
                        "starting_funds": balance.financial_objective.starting_funds,
                        "target_cash": balance.financial_objective.target_cash,
                        "starting_funds_snapshot": (
                            balance.financial_objective.starting_funds_snapshot
                        ),
                        "selected_on": _iso(balance.financial_objective.selected_on),
                        "deadline": _iso(balance.financial_objective.deadline),
                        "active": bool(balance.financial_objective.active),
                        "progression_gate_reached": bool(
                            balance.financial_objective.progression_gate_reached
                        ),
                        "progression_state": int(
                            balance.financial_objective.progression_state
                        ),
                    }
                ),
                "ledger": [
                    {
                        "amount": posting.amount,
                        "category": int(posting.category),
                        "posting_date": posting.posting_date.isoformat(),
                    }
                    for posting in balance.ledger
                ],
            }
            for club_id, balance in sorted(state.finance_balances.items())
        },
        "ai_transfer_buy_counter": {
            str(int(club_id)): int(value)
            for club_id, value in sorted(state.ai_transfer_buy_counter.items())
        },
        "country_transfer_window_open": {
            str(int(country_id)): bool(value)
            for country_id, value in sorted(state.country_transfer_window_open.items())
        },
        "user_controlled_club_id": (
            None
            if state.user_controlled_club_id is None
            else int(state.user_controlled_club_id)
        ),
        "user_youth": _snapshot_youth_state(state.user_youth),
        "user_sacking_reason": (
            None
            if state.user_sacking_reason is None
            else int(state.user_sacking_reason)
        ),
        "user_training_calendar": (
            None
            if (
                state.user_training_recovery_threshold is None
                or state.user_training_quality_multiplier is None
            )
            else {
                "recovery_threshold": int(state.user_training_recovery_threshold),
                "quality_multiplier": float(state.user_training_quality_multiplier),
            }
        ),
        "user_commercial_timers": (
            None
            if state.user_commercial_timers is None
            else {
                "concession_wait_days": int(state.user_commercial_timers.concession_wait_days),
                "concession_elapsed_days": int(state.user_commercial_timers.concession_elapsed_days),
                "sponsor_wait_days": int(state.user_commercial_timers.sponsor_wait_days),
                "sponsor_elapsed_days": int(state.user_commercial_timers.sponsor_elapsed_days),
            }
        ),
        "user_concession_source": (
            None
            if state.user_concession_source is None
            else {
                "selector_capacities": [
                    int(value) for value in state.user_concession_source.selector_capacities
                ],
                "stadium_total": int(state.user_concession_source.stadium_total),
                "club_metric": int(state.user_concession_source.club_metric),
                "access_metric": int(state.user_concession_source.access_metric),
                "adjustment_percent": float(state.user_concession_source.adjustment_percent),
            }
        ),
        "rng_state": None if state.rng is None else int(state.rng.state),
    }


def restore_game_state(database, snapshot: dict[str, Any]) -> GameState:
    source_players = {
        int(player.index): player
        for player in getattr(database, "players", ())
    }
    players = {}
    for value in snapshot["players"]:
        player_id = int(value[0])
        source = source_players.get(player_id)
        if source is None:
            raise ValueError(f"saved player {player_id} is absent from source database")
        players[player_id] = _restore_player(value, source)
    clubs = {
        int(club.index): club
        for club in getattr(database, "clubs", ())
    }
    managers = {
        int(manager.index): manager
        for manager in getattr(database, "managers", ())
    }
    competitions = {
        int(comp.id): comp
        for comp in getattr(database, "competitions", ())
    }
    countries = {
        int(country.id): country
        for country in getattr(database, "countries", ())
        if hasattr(country, "id")
    }
    # Preserve the source-table index used by DBRPlayer position bytes and
    # 0x4EA310; Position.id is a different semantic field.
    positions = {
        int(index): position
        for index, position in enumerate(getattr(database, "positions", ()))
    }
    access_fan_bases = tuple(
        getattr(database, "access_fan_bases", ())
    )
    access_skill_financial_values = tuple(
        getattr(database, "access_skill_financial_values", ())
    )
    startup_roster_count: dict[int, int] = {
        club_id: 0 for club_id in clubs
    }
    for source_player in getattr(database, "players", ()):
        club_id = int(source_player.club_id)
        startup_roster_count[club_id] = startup_roster_count.get(club_id, 0) + 1

    league_snapshot = snapshot["premier_league"]
    league = None
    if league_snapshot is not None:
        league = PremierLeagueState(
            getattr(database, "real_fixtures", ()),
            getattr(database, "premier_league_rounds", ()),
            season_year=None,
        )
        league.fixture_source_order = tuple(
            int(v) for v in league_snapshot["fixture_source_order"]
        )
        league.round_source_order = tuple(
            int(v) for v in league_snapshot["round_source_order"]
        )
        league.club_ids = tuple(int(v) for v in league_snapshot["club_ids"])
        league.results = {
            int(value["fixture_id"]): MatchResult(
                fixture_id=int(value["fixture_id"]),
                home_goals=int(value["home_goals"]),
                away_goals=int(value["away_goals"]),
            )
            for value in league_snapshot["results"]
        }
        league.round_dates = {
            int(round_index): date.fromisoformat(value)
            for round_index, value in league_snapshot["round_dates"].items()
        }

    state = GameState(
        calendar=GameCalendar(date.fromisoformat(snapshot["calendar_date"])),
        players=players,
        premier_league=league,
        cup_results=_restore_cup_result_registry(snapshot.get("cup_results")),
        domestic_cups=DomesticCupScheduleState.restore(snapshot.get("domestic_cups")),
        european_cups=DomesticCupScheduleState.restore(snapshot.get("european_cups")),
        qualification_cups=DomesticCupScheduleState.restore(
            snapshot.get("qualification_cups")
        ),
        procedural_leagues={
            (
                int(raw["competition_id"]),
                int(raw.get("competition_context", 0)),
            ): LiveProceduralLeagueState.restore(raw)
            for raw in snapshot.get("procedural_leagues", ())
        },
        monthly_player_updates=int(snapshot["monthly_player_updates"]),
        club_roster_order={
            int(club_id): [int(v) for v in values]
            for club_id, values in snapshot["club_roster_order"].items()
        },
        clubs=clubs,
        managers=managers,
        competitions=competitions,
        round_definitions=tuple(getattr(database, "rounds", ())),
        cup_allocation_instructions=tuple(
            getattr(database, "cup_allocation_instructions", ())
        ),
        league_allocation_records=tuple(
            getattr(database, "league_allocation_records", ())
        ),
        club_competition_membership={
            int(club_id): int(competition_id)
            for club_id, competition_id in snapshot.get(
                "club_competition_membership",
                {
                    str(int(club.index)): int(club.competition_id)
                    for club in getattr(database, "clubs", ())
                    if hasattr(club, "competition_id")
                },
            ).items()
        },
        countries=countries,
        source_fixture_identity=tuple(
            (
                int(fixture.id),
                int(fixture.round_index),
                int(fixture.home_club_id),
                int(fixture.away_club_id),
            )
            for fixture in getattr(database, "real_fixtures", ())
        ),
        positions=positions,
        access_fan_bases=access_fan_bases,
        access_skill_financial_values=access_skill_financial_values,
        ai_transfer_startup_roster_count=startup_roster_count,
        ai_transfer_buy_counter={
            int(club_id): int(value)
            for club_id, value in snapshot["ai_transfer_buy_counter"].items()
        },
        country_transfer_window_open={
            int(country_id): bool(value)
            for country_id, value in snapshot["country_transfer_window_open"].items()
        },
        user_controlled_club_id=(
            None
            if snapshot["user_controlled_club_id"] is None
            else int(snapshot["user_controlled_club_id"])
        ),
        user_youth=_restore_youth_state(snapshot.get("user_youth")),
        user_sacking_reason=(
            None
            if snapshot.get("user_sacking_reason") is None
            else int(snapshot["user_sacking_reason"])
        ),
        user_training_recovery_threshold=(
            None
            if snapshot.get("user_training_calendar") is None
            else int(snapshot["user_training_calendar"]["recovery_threshold"])
        ),
        user_training_quality_multiplier=(
            None
            if snapshot.get("user_training_calendar") is None
            else float(snapshot["user_training_calendar"]["quality_multiplier"])
        ),
        user_commercial_timers=(
            None
            if snapshot.get("user_commercial_timers") is None
            else UserCommercialTimerState(
                concession_wait_days=int(
                    snapshot["user_commercial_timers"]["concession_wait_days"]
                ),
                concession_elapsed_days=int(
                    snapshot["user_commercial_timers"]["concession_elapsed_days"]
                ),
                sponsor_wait_days=int(
                    snapshot["user_commercial_timers"]["sponsor_wait_days"]
                ),
                sponsor_elapsed_days=int(
                    snapshot["user_commercial_timers"]["sponsor_elapsed_days"]
                ),
            )
        ),
        user_concession_source=(
            None
            if snapshot.get("user_concession_source") is None
            else ConcessionRuntimeSource(
                selector_capacities=tuple(
                    int(value)
                    for value in snapshot["user_concession_source"]["selector_capacities"]
                ),
                stadium_total=int(snapshot["user_concession_source"]["stadium_total"]),
                club_metric=int(snapshot["user_concession_source"]["club_metric"]),
                access_metric=int(snapshot["user_concession_source"]["access_metric"]),
                adjustment_percent=float(
                    snapshot["user_concession_source"]["adjustment_percent"]
                ),
            )
        ),
        team_tactics={
            int(club_id): TeamTacticalState(
                play_style=int(value["play_style"]),
                without_ball_style=int(value["without_ball_style"]),
                with_ball_style=int(value["with_ball_style"]),
                aggression=int(value["aggression"]),
            )
            for club_id, value in snapshot["team_tactics"].items()
        },
        pitch_wear={
            int(club_id): int(value)
            for club_id, value in snapshot["pitch_wear"].items()
        },
        prepared_match_environments={
            int(fixture_id): MatchEnvironment(
                temperature_c=int(value["temperature_c"]),
                weather_code=int(value["weather_code"]),
                weekday_evening=bool(value["weekday_evening"]),
            )
            for fixture_id, value in snapshot["prepared_match_environments"].items()
        },
        premier_league_scheduler_order={
            int(round_index): tuple(int(v) for v in values)
            for round_index, values in snapshot["premier_league_scheduler_order"].items()
        },
        primary_schedule_shadow=PrimaryScheduleShadowState.restore(
            snapshot.get("primary_schedule_shadow", {})
        ),
        primary_matchday_order={
            date.fromisoformat(on_date): tuple(
                (
                    str(entry[0]),
                    int(entry[1])
                    if entry[0] == "premier_league"
                    else tuple(entry[1]),
                )
                for entry in entries
            )
            for on_date, entries in snapshot.get("primary_matchday_order", {}).items()
        },
        transfers=_restore_transfer_state(snapshot.get("transfers")),
        contract_renewal_suggestions=[
            ContractRenewalSuggestion(
                player_id=int(value["player_id"]),
                queued_on=date.fromisoformat(value["queued_on"]),
                kind=ContractRenewalSuggestionKind(str(value["kind"])),
            )
            for value in snapshot.get("contract_renewal_suggestions", ())
        ],
        player_transfer_requests=[
            PlayerTransferRequest(
                player_id=int(value["player_id"]),
                queued_on=date.fromisoformat(value["queued_on"]),
                due_on=date.fromisoformat(value["due_on"]),
            )
            for value in snapshot.get("player_transfer_requests", ())
        ],
        finance_balances={
            int(club_id): BalanceRuntimeState(
                current_cash=value["current_cash"],
                financial_objective=(
                    None
                    if value.get("financial_objective") is None
                    else FinancialObjectiveState(
                        base_cash=value["financial_objective"]["base_cash"],
                        candidate_ids=tuple(
                            int(candidate_id)
                            for candidate_id in value["financial_objective"]["candidate_ids"]
                        ),
                        selected_objective_id=int(
                            value["financial_objective"]["selected_objective_id"]
                        ),
                        starting_funds=value["financial_objective"]["starting_funds"],
                        target_cash=value["financial_objective"]["target_cash"],
                        starting_funds_snapshot=(
                            value["financial_objective"]["starting_funds_snapshot"]
                        ),
                        selected_on=_date(value["financial_objective"]["selected_on"]),
                        deadline=_date(value["financial_objective"]["deadline"]),
                        active=bool(value["financial_objective"]["active"]),
                        progression_gate_reached=bool(
                            value["financial_objective"]["progression_gate_reached"]
                        ),
                        progression_state=int(
                            value["financial_objective"]["progression_state"]
                        ),
                    )
                ),
                ledger=[
                    FinancePosting(
                        amount=posting["amount"],
                        category=int(posting["category"]),
                        posting_date=date.fromisoformat(posting["posting_date"]),
                    )
                    for posting in value["ledger"]
                ],
            )
            for club_id, value in snapshot["finance_balances"].items()
        },
        rng=(
            None
            if snapshot["rng_state"] is None
            else MsvcCrtRng(int(snapshot["rng_state"]))
        ),
    )
    state.calendar.daily_hooks.append(state._run_daily_injury_returns)
    state.calendar.daily_hooks.append(state._run_daily_ai_pitch_recovery)
    state.calendar.monthly_hooks.append(state._run_monthly_player_development)
    state.calendar.monthly_hooks.append(state._run_monthly_contract_maintenance)
    return state


def _snapshot_primary_entry(entry: tuple | None):
    if entry is None:
        return None
    entry = tuple(entry)
    if entry[0] == "premier_league":
        return ["premier_league", int(entry[1])]
    if entry[0] in (
        "domestic_cup",
        "european_cup",
        "qualification_cup",
        "procedural_league",
    ):
        return [str(entry[0]), list(entry[1])]
    raise ValueError(f"unsupported primary match entry {entry!r}")


def _restore_primary_entry(value):
    if value is None:
        return None
    if value[0] == "premier_league":
        return ("premier_league", int(value[1]))
    if value[0] in (
        "domestic_cup",
        "european_cup",
        "qualification_cup",
        "procedural_league",
    ):
        return (str(value[0]), tuple(value[1]))
    raise ValueError(f"unsupported saved primary match entry {value!r}")


def snapshot_human_gameplay(controller: HumanGameplayController) -> dict[str, Any]:
    rng_state = getattr(controller.match_rng, "state", None)
    if rng_state is None:
        raise TypeError("internal save requires a match RNG with serializable state")

    human = controller.human
    human_snapshot = None
    if human is not None:
        human_snapshot = {
            "club_id": int(human.club_id),
            "formation_id": int(human.formation_id),
            "starter_ids": [int(v) for v in human.starter_ids],
            "substitute_ids": [int(v) for v in human.substitute_ids],
            "team_orders": {
                "captain": [int(v) for v in human.team_orders.captain],
                "penalty": [int(v) for v in human.team_orders.penalty],
                "corner": [int(v) for v in human.team_orders.corner],
                "free_kick": [int(v) for v in human.team_orders.free_kick],
            },
        }

    return {
        "format": SAVE_FORMAT,
        "schema_version": SAVE_SCHEMA_VERSION,
        "source": _source_descriptor_from_state(controller.state),
        "game_state": snapshot_game_state(controller.state),
        "controller": {
            "human": human_snapshot,
            "pending_fixture_id": controller.pending_fixture_id,
            "pending_prior_results": [
                {
                    "fixture_id": int(fixture_id),
                    "result": _snapshot_normal_match_result(result),
                }
                for fixture_id, result in controller._pending_prior_results
            ],
            "pending_after_fixture_ids": [
                int(v) for v in controller._pending_after_fixture_ids
            ],
            "pending_primary_entry": _snapshot_primary_entry(
                controller.pending_primary_entry
            ),
            "pending_prior_primary_results": [
                {
                    "entry": _snapshot_primary_entry(entry),
                    "result": _snapshot_normal_match_result(result),
                }
                for entry, result in controller._pending_prior_primary_results
            ],
            "pending_after_primary_entries": [
                _snapshot_primary_entry(entry)
                for entry in controller._pending_after_primary_entries
            ],
            "match_rng_state": int(rng_state),
        },
    }


def restore_human_gameplay(
    database,
    attack_matrix,
    defence_matrix,
    snapshot: dict[str, Any],
) -> HumanGameplayController:
    if snapshot.get("format") != SAVE_FORMAT:
        raise ValueError("not an FM2001 modern internal save")
    version = int(snapshot.get("schema_version", -1))
    if version != SAVE_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported internal save schema {version}; expected {SAVE_SCHEMA_VERSION}"
        )

    _assert_database_matches(database, snapshot["source"])
    state = restore_game_state(database, snapshot["game_state"])
    control = snapshot["controller"]
    controller = HumanGameplayController(
        state,
        attack_matrix,
        defence_matrix,
        MsvcCrtRng(int(control["match_rng_state"])),
    )

    human = control["human"]
    if human is not None:
        orders = human["team_orders"]
        controller.human = HumanManagerState(
            club_id=int(human["club_id"]),
            formation_id=int(human["formation_id"]),
            starter_ids=tuple(int(v) for v in human["starter_ids"]),
            substitute_ids=tuple(int(v) for v in human["substitute_ids"]),
            team_orders=TeamOrderPriorities(
                captain=tuple(int(v) for v in orders["captain"]),
                penalty=tuple(int(v) for v in orders["penalty"]),
                corner=tuple(int(v) for v in orders["corner"]),
                free_kick=tuple(int(v) for v in orders["free_kick"]),
            ),
        )
        controller.state.user_controlled_club_id = int(human["club_id"])

    pending = control["pending_fixture_id"]
    controller.pending_fixture_id = None if pending is None else int(pending)
    controller._pending_prior_results = tuple(
        (
            int(value["fixture_id"]),
            _restore_normal_match_result(value["result"]),
        )
        for value in control["pending_prior_results"]
    )
    controller._pending_after_fixture_ids = tuple(
        int(v) for v in control["pending_after_fixture_ids"]
    )
    controller.pending_primary_entry = _restore_primary_entry(
        control.get("pending_primary_entry")
    )
    controller._pending_prior_primary_results = tuple(
        (
            _restore_primary_entry(value["entry"]),
            _restore_normal_match_result(value["result"]),
        )
        for value in control.get("pending_prior_primary_results", ())
    )
    controller._pending_after_primary_entries = tuple(
        _restore_primary_entry(value)
        for value in control.get("pending_after_primary_entries", ())
    )
    return controller


def dumps_human_gameplay(controller: HumanGameplayController) -> str:
    return json.dumps(
        snapshot_human_gameplay(controller),
        sort_keys=True,
        separators=(",", ":"),
    )


def loads_human_gameplay(
    database,
    attack_matrix,
    defence_matrix,
    text: str,
) -> HumanGameplayController:
    return restore_human_gameplay(
        database,
        attack_matrix,
        defence_matrix,
        json.loads(text),
    )


def save_human_gameplay(
    controller: HumanGameplayController,
    path: str | Path,
    *,
    compress: bool = True,
) -> Path:
    """Write one internal save.

    The logical format is UTF-8 JSON. File saves default to gzip compression
    because the complete runtime snapshot is highly compressible;
    load_human_gameplay also accepts uncompressed JSON for transparency and
    debugging.
    """
    path = Path(path)
    payload = dumps_human_gameplay(controller).encode("utf-8")
    path.write_bytes(gzip.compress(payload) if compress else payload)
    return path


def load_human_gameplay(
    database,
    attack_matrix,
    defence_matrix,
    path: str | Path,
) -> HumanGameplayController:
    payload = Path(path).read_bytes()
    if payload.startswith(b"\x1f\x8b"):
        payload = gzip.decompress(payload)
    return loads_human_gameplay(
        database,
        attack_matrix,
        defence_matrix,
        payload.decode("utf-8"),
    )

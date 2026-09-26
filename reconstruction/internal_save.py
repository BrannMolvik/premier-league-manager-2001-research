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

from competition_state import MatchResult, PremierLeagueState
from game_state import GameCalendar, GameState
from human_gameplay import HumanGameplayController, HumanManagerState
from match_environment import MatchEnvironment
from match_events import (
    BoundaryRecord,
    ChanceRecord,
    IncidentRecord,
    PossessionRecord,
    SubstitutionRecord,
)
from match_orders import TeamOrderPriorities
from match_schedule import MsvcCrtRng
from match_simulation import NormalMatchResult, SegmentPossession, TimedMatchEvent
from match_team_setup import TeamTacticalState
from player_development import DevelopmentState, PeakAges
from runtime_state import RuntimePlayer


SAVE_FORMAT = "fm2001-modern-internal-save"
SAVE_SCHEMA_VERSION = 2


def _iso(value: date | None) -> str | None:
    return None if value is None else value.isoformat()


def _date(value: str | None) -> date | None:
    return None if value is None else date.fromisoformat(str(value))


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
    league = state.premier_league
    return _source_payload(
        tuple(state.players.values()),
        tuple(state.clubs.values()),
        tuple(state.managers.values()),
        tuple(state.competitions.values()),
        () if league is None else tuple(league.fixtures.values()),
    )


def _source_signature(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return sha256(blob).hexdigest()


def _source_descriptor_from_state(state: GameState) -> dict[str, Any]:
    payload = _source_payload_from_state(state)
    return {
        "signature_sha256": _source_signature(payload),
        "player_count": len(payload["players"]),
        "club_count": len(payload["club_ids"]),
        "manager_count": len(payload["manager_ids"]),
        "competition_count": len(payload["competition_ids"]),
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
        first_name=str(source.first_name),
        surname=str(source.surname),
        club_id=int(value[1]),
        nationality_id=int(source.nationality_id),
        date_of_birth=source.date_of_birth,
        shirt_number=int(value[2]),
        height_cm=int(source.height_cm),
        weight_kg=int(source.weight_kg),
        positions=tuple(int(v) for v in source.positions),
        current_raw=[int(v) for v in value[3]],
        target_raw=tuple(int(v) for v in source.target_raw),
        development=_restore_development(value[4], source.target_raw),
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
        non_eu=bool(flags & _PLAYER_FLAG_NON_EU),
        eu_status_code=int(getattr(source, "eu_status_code", 2)),
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
        return {"type": "boundary", "kind": int(event.kind)}
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
        return BoundaryRecord(kind=int(value["kind"]))
    if kind == "possession":
        return PossessionRecord(
            territory=int(value["territory"]),
            side0_percent=int(value["side0_percent"]),
            neutral_percent=int(value["neutral_percent"]),
        )
    raise ValueError(f"unknown saved match event type {kind!r}")


def _snapshot_normal_match_result(result: NormalMatchResult) -> dict[str, Any]:
    return {
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


def _restore_normal_match_result(value: dict[str, Any]) -> NormalMatchResult:
    return NormalMatchResult(
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
        "premier_league": league_snapshot,
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
        monthly_player_updates=int(snapshot["monthly_player_updates"]),
        club_roster_order={
            int(club_id): [int(v) for v in values]
            for club_id, values in snapshot["club_roster_order"].items()
        },
        clubs=clubs,
        managers=managers,
        competitions=competitions,
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
        rng=(
            None
            if snapshot["rng_state"] is None
            else MsvcCrtRng(int(snapshot["rng_state"]))
        ),
    )
    state.calendar.daily_hooks.append(state._run_daily_injury_returns)
    state.calendar.daily_hooks.append(state._run_daily_ai_pitch_recovery)
    state.calendar.monthly_hooks.append(state._run_monthly_player_development)
    return state


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

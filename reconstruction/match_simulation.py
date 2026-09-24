from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from match_condition import (
    ConditionInjurySettings,
    ConditionInjuryState,
    apply_sequence_condition_and_injuries,
)
from match_discipline import DisciplineState, apply_sequence_discipline
from match_calculator import (
    BoundedRng,
    MatchSkillPlayer,
    build_positional_pools,
    resolve_corner,
    resolve_free_kick,
    resolve_open_play_attempt,
    resolve_penalty,
)
from match_clock import build_match_phase_plan
from match_events import (
    BoundaryRecord,
    BoundaryType,
    ChanceRecord,
    ChanceSource,
    IncidentKind,
    MatchEvent,
    PossessionRecord,
)
from match_orders import TeamOrderCategory, select_set_piece_taker
from match_statistics import SegmentCounters, normalize_segment_statistics
from match_substitution import apply_ai_substitution, apply_injury_substitution
from match_strength import (
    TeamStrengthContext,
    TeamStrengthPlayer,
    attack_team_strength,
    attack_weights,
    defence_team_strength,
    schedule_segment_attacks,
)


@dataclass
class PreparedMatchPlayer:
    """Evidence-backed player state required by the reconstructed calculator.

    Match-day state that is not present in Master.dat (assigned role, Condition,
    Form and availability) must be supplied by the caller rather than guessed.
    """

    side: int
    player_index: int
    condition: int
    form_state: int
    current_position: int
    balance_position_code: int
    preferred_positions: tuple[int, int, int]
    skills: tuple[int, ...]
    minimum_strength_override: bool = False
    active: bool = True
    substitution_available: bool = False
    position_aux_code: int = 0

    def __post_init__(self) -> None:
        if self.side not in (0, 1):
            raise ValueError("side must be 0 or 1")
        if self.player_index < 0:
            raise ValueError("player_index must be non-negative")
        if not 0 <= int(self.condition) <= 255:
            raise ValueError("condition must be in 0..255")
        if not 0 <= int(self.form_state) <= 4:
            raise ValueError("form_state must be in 0..4")
        if not 0 <= int(self.current_position) <= 19:
            raise ValueError("current_position must be in 0..19")
        if not 0 <= int(self.balance_position_code) <= 31:
            raise ValueError("balance_position_code must be in 0..31")
        if not 0 <= int(self.position_aux_code) <= 15:
            raise ValueError("position_aux_code must be in 0..15")
        if self.active and self.substitution_available:
            raise ValueError("a player cannot be active and substitute-available simultaneously")
        if len(self.preferred_positions) != 3:
            raise ValueError("preferred_positions must contain exactly three entries")
        if len(self.skills) != 17:
            raise ValueError("skills must contain exactly 17 raw skill bytes")
        if any(not 0 <= int(value) <= 255 for value in self.skills):
            raise ValueError("skills must be in 0..255")

    def chance_player(self) -> MatchSkillPlayer:
        return MatchSkillPlayer(
            side=self.side,
            player_index=self.player_index,
            condition=self.condition,
            form_state=self.form_state,
            current_position=self.current_position,
            preferred_positions=self.preferred_positions,
            passing=self.skills[5],
            shooting=self.skills[6],
            tackling=self.skills[7],
            heading=self.skills[8],
            control=self.skills[9],
            goalkeeping=self.skills[13],
            set_piece=self.skills[16],
            minimum_strength_override=self.minimum_strength_override,
        )

    def strength_player(self) -> TeamStrengthPlayer:
        return TeamStrengthPlayer(
            side=self.side,
            player_index=self.player_index,
            condition=self.condition,
            form_state=self.form_state,
            current_position=self.current_position,
            balance_position_code=self.balance_position_code,
            preferred_positions=self.preferred_positions,
            skills=self.skills,
            minimum_strength_override=self.minimum_strength_override,
        )


@dataclass(frozen=True)
class PreparedMatchSide:
    players: tuple[PreparedMatchPlayer, ...]
    attack_context: TeamStrengthContext
    defence_context: TeamStrengthContext
    penalty_taker_priority: tuple[int, ...]
    corner_taker_priority: tuple[int, ...]
    free_kick_taker_priority: tuple[int, ...]
    starting_player_indices: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if not self.players:
            raise ValueError("prepared match side requires active players")
        sides = {player.side for player in self.players}
        if len(sides) != 1:
            raise ValueError("all prepared players must belong to the same side")
        indices = {player.player_index for player in self.players}
        if len(indices) != len(self.players):
            raise ValueError("prepared player indices must be unique within a side")
        if self.attack_context.aggression != self.defence_context.aggression:
            raise ValueError("a prepared side must use one team Aggression value")

        if not self.starting_player_indices:
            starters = tuple(
                int(player.player_index)
                for player in self.players
                if player.active
            )
            object.__setattr__(self, "starting_player_indices", starters)

        if len(self.starting_player_indices) > 11:
            raise ValueError("starting_player_indices cannot contain more than 11 players")
        if len(set(self.starting_player_indices)) != len(self.starting_player_indices):
            raise ValueError("starting_player_indices must be unique")
        if any(int(index) not in indices for index in self.starting_player_indices):
            raise ValueError("starting_player_indices must reference prepared players")


    @property
    def side(self) -> int:
        return self.players[0].side

    def chance_players(self) -> tuple[MatchSkillPlayer, ...]:
        return tuple(
            player.chance_player()
            for player in self.players
            if player.active
        )

    def strength_players(self) -> tuple[TeamStrengthPlayer, ...]:
        return tuple(
            player.strength_player()
            for player in self.players
            if player.active
        )

    def active_prepared_players(self) -> tuple[PreparedMatchPlayer, ...]:
        return tuple(player for player in self.players if player.active)

    def deactivate(self, player_index: int) -> None:
        for player in self.players:
            if player.player_index == player_index:
                player.active = False
                player.substitution_available = False
                player.current_position = int(player.preferred_positions[0])
                player.position_aux_code = 0
                return
        raise KeyError(player_index)


@dataclass(frozen=True)
class TimedMatchEvent:
    minute: int
    event: MatchEvent


@dataclass(frozen=True)
class SegmentPossession:
    calculation_minute: int
    record: PossessionRecord


@dataclass(frozen=True)
class NormalMatchResult:
    events: tuple[TimedMatchEvent, ...]
    possession_segments: tuple[SegmentPossession, ...] = ()

    @property
    def score(self) -> tuple[int, int]:
        scores = [0, 0]
        for timed in self.events:
            event = timed.event
            if isinstance(event, ChanceRecord):
                side = event.credited_side
                if side is not None:
                    scores[side] += 1
        return scores[0], scores[1]


def _append_chance(
    events: list[TimedMatchEvent],
    minute: int,
    event: ChanceRecord | None,
    scores: list[int],
) -> None:
    if event is None:
        return
    events.append(TimedMatchEvent(minute, event))
    credited = event.credited_side
    if credited is not None:
        scores[credited] += 1


def _resolve_set_piece_chain(
    source: ChanceSource,
    minute: int,
    attacking: PreparedMatchSide,
    defending: PreparedMatchSide,
    scores: list[int],
    rng: BoundedRng,
    events: list[TimedMatchEvent],
) -> int:
    attack_players = attacking.chance_players()
    defend_players = defending.chance_players()
    possession_increment = 0
    current_source: ChanceSource | None = source

    while current_source is not None:
        if current_source is ChanceSource.PENALTY:
            taker = select_set_piece_taker(
                attack_players,
                TeamOrderCategory.PENALTY,
                attacking.attack_context.user_controlled,
                attacking.penalty_taker_priority,
                rng,
            )
            goalkeeper = build_positional_pools(defend_players).goalkeeper
            if taker is None:
                return possession_increment
            if goalkeeper is None:
                raise ValueError("penalty resolution requires a defending goalkeeper")
            event = resolve_penalty(
                taker,
                goalkeeper,
                scores[attacking.side],
                rng,
            )
            _append_chance(events, minute, event, scores)
            return possession_increment

        if current_source is ChanceSource.FREE_KICK:
            taker = select_set_piece_taker(
                attack_players,
                TeamOrderCategory.FREE_KICK,
                attacking.attack_context.user_controlled,
                attacking.free_kick_taker_priority,
                rng,
            )
            if taker is None:
                return possession_increment
            resolution = resolve_free_kick(
                taker,
                attack_players,
                defend_players,
                scores[attacking.side],
                rng,
            )
        elif current_source is ChanceSource.CORNER:
            taker = select_set_piece_taker(
                attack_players,
                TeamOrderCategory.CORNER,
                attacking.attack_context.user_controlled,
                attacking.corner_taker_priority,
                rng,
            )
            if taker is None:
                return possession_increment
            resolution = resolve_corner(
                taker,
                attack_players,
                defend_players,
                scores[attacking.side],
                rng,
            )
        else:
            raise ValueError(f"unsupported set-piece transition {current_source!r}")

        possession_increment += resolution.attacking_possession_increment
        _append_chance(events, minute, resolution.event, scores)
        current_source = resolution.transition

    return possession_increment


def resolve_attacking_sequence(
    minute: int,
    attacking: PreparedMatchSide,
    defending: PreparedMatchSide,
    scores: list[int],
    rng: BoundedRng,
    counters: SegmentCounters | None = None,
) -> tuple[TimedMatchEvent, ...]:
    """Run one scheduler-selected 0x62C740 sequence plus exact set-piece handoffs."""
    if attacking.side == defending.side:
        raise ValueError("attacking and defending sides must differ")
    if len(scores) != 2:
        raise ValueError("scores must contain exactly two side scores")

    events: list[TimedMatchEvent] = []
    resolution = resolve_open_play_attempt(
        attacking.chance_players(),
        defending.chance_players(),
        int(minute),
        scores[attacking.side],
        rng,
    )
    if counters is not None:
        counters.neutral += resolution.neutral_increment
        counters.add_attacking(
            attacking.side,
            resolution.attacking_possession_increment,
        )

    _append_chance(events, minute, resolution.event, scores)

    if resolution.transition is not None:
        extra_possession = _resolve_set_piece_chain(
            resolution.transition,
            minute,
            attacking,
            defending,
            scores,
            rng,
            events,
        )
        if counters is not None:
            counters.add_attacking(attacking.side, extra_possession)

    return tuple(events)


def simulate_normal_match(
    side0: PreparedMatchSide,
    side1: PreparedMatchSide,
    attack_matrix: Sequence[Sequence[Sequence[float]]],
    defence_matrix: Sequence[Sequence[Sequence[float]]],
    rng: BoundedRng,
    condition_injury_settings: ConditionInjurySettings | None = None,
    discipline_enabled: bool = True,
    match_mode_code: int | None = None,
) -> NormalMatchResult:
    """Run the verified normal-time scoring/chance backbone through minute 90.

    This runs the recovered strength builders, 0x62B1A0 attack scheduler,
    type-1/2/3/4 chance resolvers, the exact RNG(7)-gated AI substitution path,
    exact per-segment territory/possession normalization, HalfTime and FullTime
    boundaries. When condition_injury_settings is supplied, it also runs the
    exact mapped 0x62E6F0 Condition loop and 0x62EAE0 injury-incidence gate.
    The exact 0x62E130 discipline path runs after every attacking sequence;
    sending-off events remove that player from later active chance and strength
    pools. Successful injuries immediately enter the recovered 0x409950 /
    0x409AC0 replacement path when allowed. AI teams always permit that injury
    replacement; user-controlled teams require raw MatchCalculator +0xD3C mode
    1 or 3, exposed here as match_mode_code. The scheduler then consumes RNG(7),
    and on a zero invokes 0x62E2F0 for the side opposite the scheduler-selected
    attacker, preserving the original per-sequence call order.
    """
    if side0.side != 0 or side1.side != 1:
        raise ValueError("simulate_normal_match requires side0.side=0 and side1.side=1")

    sides = (side0, side1)
    events: list[TimedMatchEvent] = []
    possession_segments: list[SegmentPossession] = []
    scores = [0, 0]
    condition_state = ConditionInjuryState()
    discipline_state = DisciplineState()
    plan = build_match_phase_plan(extra_time=False, penalties=False)
    boundaries = {boundary.minute: boundary.kind for boundary in plan.boundaries}

    for segment_start in plan.segment_minutes:
        strengths = []
        for side in sides:
            strength_players = side.strength_players()
            strengths.append((
                attack_team_strength(
                    strength_players,
                    attack_matrix,
                    side.attack_context,
                ),
                defence_team_strength(
                    strength_players,
                    defence_matrix,
                    side.defence_context,
                ),
            ))

        weights = attack_weights(
            strengths[0][0],
            strengths[0][1],
            strengths[1][0],
            strengths[1][1],
        )

        scheduled_attacks = schedule_segment_attacks(segment_start, weights, rng)
        counters = SegmentCounters()
        side0_attack_count = sum(1 for item in scheduled_attacks if item.side == 0)

        for scheduled in scheduled_attacks:
            attacking = sides[scheduled.side]
            defending = sides[1 - scheduled.side]
            events.extend(resolve_attacking_sequence(
                scheduled.minute,
                attacking,
                defending,
                scores,
                rng,
                counters,
            ))

            if condition_injury_settings is not None:
                def replace_injured_player(incident):
                    team = sides[incident.player_side]
                    return apply_injury_substitution(
                        incident.player_side,
                        incident.player_index,
                        team.players,
                        team.attack_context.user_controlled,
                        match_mode_code=match_mode_code,
                        enabled=discipline_enabled,
                    )

                incidents = apply_sequence_condition_and_injuries(
                    scheduled.side,
                    side0.players,
                    side1.players,
                    side0.attack_context.aggression,
                    side1.attack_context.aggression,
                    scheduled.minute,
                    condition_injury_settings,
                    condition_state,
                    rng,
                    injury_enabled=discipline_enabled,
                    injury_substitution_handler=replace_injured_player,
                )
                events.extend(
                    TimedMatchEvent(scheduled.minute, incident)
                    for incident in incidents
                )

            discipline = apply_sequence_discipline(
                scheduled.side,
                side0.active_prepared_players(),
                side1.active_prepared_players(),
                side0.attack_context.aggression,
                side1.attack_context.aggression,
                discipline_state,
                rng,
                enabled=discipline_enabled,
            )
            if discipline is not None:
                events.append(TimedMatchEvent(scheduled.minute, discipline))
                if discipline.kind is IncidentKind.SENT_OFF:
                    sides[discipline.player_side].deactivate(
                        discipline.player_index
                    )

            # Original 0x62B1A0 consumes this roll after chance,
            # Condition/injury and discipline. A zero calls 0x62E2F0 for the
            # side opposite the scheduler-selected attacker.
            if rng.randbelow(7) == 0:
                substitution_side = 1 - scheduled.side
                substitution_team = sides[substitution_side]
                substitution = apply_ai_substitution(
                    substitution_side,
                    scheduled.minute,
                    scores,
                    substitution_team.players,
                    substitution_team.starting_player_indices,
                    substitution_team.attack_context.user_controlled,
                    enabled=discipline_enabled,
                )
                if substitution is not None:
                    events.append(TimedMatchEvent(
                        scheduled.minute,
                        substitution,
                    ))

        possession_segments.append(SegmentPossession(
            calculation_minute=segment_start,
            record=normalize_segment_statistics(
                side0_attack_count,
                len(scheduled_attacks),
                counters,
                rng,
            ),
        ))

        boundary_minute = segment_start + 5
        kind = boundaries.get(boundary_minute)
        if kind is not None:
            events.append(TimedMatchEvent(
                boundary_minute,
                BoundaryRecord(kind),
            ))

    return NormalMatchResult(tuple(events), tuple(possession_segments))

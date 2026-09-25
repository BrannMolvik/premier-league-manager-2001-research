from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, Sequence, TypeVar

from match_availability import base_lineup_eligible
from match_lineup import AiLineupCoreResult, AiLineupPlayer, select_ai_lineup_core
from match_orders import TeamOrderPriorities
from match_participants import collect_match_participants
from match_simulation import PreparedMatchPlayer, PreparedMatchSide
from match_strength import TeamStrengthContext
from match_team_setup import (
    FormationSelectionClass,
    TeamTacticalState,
    formation_selection_class_from_score,
    game_strategy_score,
    manager_formation_for_selection_class,
    play_style_to_strategy_code,
    premier_league_strategy_bias,
    resolved_substitute_quota,
    strategy_team_rating,
)


class MutableAiMatchPlayer(AiLineupPlayer, Protocol):
    club_id: int
    match_active: bool
    match_substitute_available: bool
    injured: bool
    suspended: bool
    selection_excluded: bool
    non_eu: bool
    condition: int
    current_position: int
    position_aux_code: int
    balance_position_code: int

    def assign_match_position(self, role: int, auxiliary_code: int) -> None: ...
    def set_match_active(self) -> None: ...
    def set_match_substitute_available(self) -> None: ...
    def clear_match_selection(self, *, reset_position: bool = False) -> None: ...


PlayerT = TypeVar("PlayerT", bound=MutableAiMatchPlayer)

class ManagerFormationInput(Protocol):
    formation_default: int
    formation_class3: int
    formation_class1: int


class CompetitionSelectionInput(Protocol):
    substitute_quota: int
    max_non_eu_players: int


class LeagueTableInput(Protocol):
    club_id: int
    played: int
    points: int



@dataclass(frozen=True)
class PreparedPremierLeagueAiSelection:
    """Autonomous Premier League AI team-selection result."""

    strategy_score: int
    selection_class: FormationSelectionClass
    formation_id: int
    substitute_quota: int
    selection: "PreparedAiMatchSelection"

@dataclass(frozen=True)
class PreparedPremierLeagueAiSide:
    """Autonomous Premier League AI selection plus calculator-ready side."""

    preparation: PreparedPremierLeagueAiSelection
    tactical_state: TeamTacticalState
    match_side: PreparedMatchSide

@dataclass(frozen=True)
class PreparedAiMatchSelection:
    """Result of the proven AI selection core plus exact participant filtering."""

    lineup: AiLineupCoreResult
    participants: tuple[MutableAiMatchPlayer, ...]
    non_eu_restriction_relaxed: bool = False


def prepare_ai_match_selection(
    team_club_id: int,
    ordered_roster: Sequence[PlayerT],
    formation_id: int,
    substitute_quota: int,
    *,
    additional_eligible: Callable[[PlayerT], bool] | None = None,
    starter_allowed: Callable[[PlayerT, Sequence[PlayerT]], bool] | None = None,
    preserve_existing_selection: Callable[[PlayerT], bool] | None = None,
    require_complete_xi: bool = True,
    non_eu_limit: int | None = None,
    enforce_non_eu_restriction: bool = True,
    non_eu_counting_enabled: bool = True,
) -> PreparedAiMatchSelection:
    """Apply the proven pre-match AI selection/mutation pipeline.

    This composes:
    - the proven first-stage 0x418050 club/injury/suspension/bit-2 filter;
    - the exact formation/rating/bench core of 0x409C90;
    - the confirmed role/auxiliary and first-team selection mutations;
    - participant collection behavior of 0x510CD0.

    Competition-specific registration/cup-tie checks that remain outside the
    proven base filter are still supplied through additional_eligible.

    The former bit-11 callback boundary is now internalized as the proven Non-EU
    restriction. non_eu_limit is DBRCompetition +0x2B / Static.dat competition
    +34. When enforcement/counting is active, selected Non-EU players increment
    the running count. If an AI XI cannot be completed while the original
    enforcement flag is set, 0x409C90 retries the entire XI exactly once with
    that counter disabled; the candidate limit comparison itself remains active.

    The unusual 0x41FA50 secondary-team exception in the original clear loop is
    represented by preserve_existing_selection until that secondary team field
    is named.
    """
    club_id = int(team_club_id)
    extra = additional_eligible or (lambda _player: True)

    def eligible(player: PlayerT) -> bool:
        return base_lineup_eligible(player, club_id) and bool(extra(player))

    result = select_ai_lineup_core(
        ordered_roster,
        formation_id,
        substitute_quota,
        eligible=eligible,
        starter_allowed=starter_allowed,
        non_eu_limit=non_eu_limit,
        count_non_eu=bool(
            enforce_non_eu_restriction and non_eu_counting_enabled
        ),
    )

    non_eu_restriction_relaxed = False
    if result.unfilled_slot_indices and bool(enforce_non_eu_restriction):
        # Exact 0x409C90 AI failure path: one restart with its local
        # restriction-enforcement flag cleared. The Non-EU candidate comparison
        # remains, but the running count no longer increments.
        result = select_ai_lineup_core(
            ordered_roster,
            formation_id,
            substitute_quota,
            eligible=eligible,
            starter_allowed=starter_allowed,
            non_eu_limit=non_eu_limit,
            count_non_eu=False,
        )
        non_eu_restriction_relaxed = True

    if require_complete_xi and result.unfilled_slot_indices:
        raise ValueError(
            "AI lineup core could not fill all 11 formation slots after the "
            "original one-time restriction-relaxation retry"
        )

    preserve = preserve_existing_selection or (lambda _player: False)

    # 0x409C90 clears old first-team selection state before committing the
    # newly chosen XI/bench, except for the separately-tested 0x41FA50 case.
    for player in ordered_roster:
        if preserve(player):
            continue
        player.clear_match_selection(reset_position=True)

    by_index = {int(player.player_index): player for player in ordered_roster}

    for assignment in result.starters:
        player = by_index[int(assignment.player_index)]
        player.assign_match_position(
            int(assignment.role),
            int(assignment.auxiliary_code),
        )
        player.set_match_active()

    for player_index in result.substitutes:
        player = by_index[int(player_index)]
        player.set_match_substitute_available()

    participants = collect_match_participants(club_id, ordered_roster)

    return PreparedAiMatchSelection(
        lineup=result,
        participants=tuple(participants),
        non_eu_restriction_relaxed=non_eu_restriction_relaxed,
    )

def _translate_team_orders_to_participant_indices(
    team_orders: TeamOrderPriorities,
    participant_index_by_player_id: dict[int, int],
) -> TeamOrderPriorities:
    """Translate persistent Team Orders player IDs to side-local match indices.

    The original user profile stores DBRPlayer IDs. MatchCalculator semantic
    records identify players by their index inside the side participant array.
    The clean-room bridge therefore resolves priorities at preparation time.
    Missing IDs are omitted because they cannot resolve to a match participant.
    """
    def translate(values: Sequence[int]) -> tuple[int, ...]:
        return tuple(
            participant_index_by_player_id[int(player_id)]
            for player_id in values
            if int(player_id) in participant_index_by_player_id
        )

    return TeamOrderPriorities(
        captain=translate(team_orders.captain),
        penalty=translate(team_orders.penalty),
        corner=translate(team_orders.corner),
        free_kick=translate(team_orders.free_kick),
    )


def build_prepared_match_side_from_selection(
    selection: PreparedAiMatchSelection,
    side: int,
    tactical_state: TeamTacticalState,
    *,
    user_controlled: bool = False,
    team_orders: TeamOrderPriorities | None = None,
) -> PreparedMatchSide:
    """Bridge selected runtime participants into the reconstructed calculator.

    Participant array order defines side-local match player indices. Current
    Condition/Form/assigned role/auxiliary/balance state is copied. Live team
    With Ball and Without Ball styles feed attack/defence coefficient contexts;
    Play style supplies the initial match bias; Aggression feeds both contexts.
    Persistent human Team Orders IDs are translated to participant indices.
    """
    side = int(side)
    if side not in (0, 1):
        raise ValueError("side must be 0 or 1")

    participants = tuple(selection.participants)
    if not participants:
        raise ValueError("selection has no match participants")

    player_id_to_local = {
        int(player.player_index): local_index
        for local_index, player in enumerate(participants)
    }
    if len(player_id_to_local) != len(participants):
        raise ValueError("match participants must have unique persistent player IDs")

    prepared_players = tuple(
        PreparedMatchPlayer(
            side=side,
            player_index=local_index,
            condition=int(player.condition),
            form_state=int(player.form_state),
            current_position=int(player.current_position),
            balance_position_code=int(player.balance_position_code),
            preferred_positions=tuple(
                int(role) for role in player.preferred_positions[:3]
            ),
            skills=tuple(int(value) for value in player.skills),
            active=bool(player.match_active),
            substitution_available=bool(player.match_substitute_available),
            position_aux_code=int(player.position_aux_code),
        )
        for local_index, player in enumerate(participants)
    )

    match_bias = play_style_to_strategy_code(tactical_state.play_style)
    attack_context = TeamStrengthContext(
        tactic_style=int(tactical_state.with_ball_style),
        match_bias=match_bias,
        user_controlled=bool(user_controlled),
        aggression=int(tactical_state.aggression),
    )
    defence_context = TeamStrengthContext(
        tactic_style=int(tactical_state.without_ball_style),
        match_bias=match_bias,
        user_controlled=bool(user_controlled),
        aggression=int(tactical_state.aggression),
    )

    persistent_orders = team_orders or TeamOrderPriorities()
    local_orders = _translate_team_orders_to_participant_indices(
        persistent_orders,
        player_id_to_local,
    )

    starting_player_indices = tuple(
        player_id_to_local[int(assignment.player_index)]
        for assignment in selection.lineup.starters
        if int(assignment.player_index) in player_id_to_local
    )

    return PreparedMatchSide.from_team_orders(
        players=prepared_players,
        attack_context=attack_context,
        defence_context=defence_context,
        team_orders=local_orders,
        starting_player_indices=starting_player_indices,
    )

def prepare_premier_league_ai_selection(
    team_club_id: int,
    ordered_roster: Sequence[PlayerT],
    opponent_roster: Sequence[PlayerT],
    manager: ManagerFormationInput,
    competition: CompetitionSelectionInput,
    table_rows: Sequence[LeagueTableInput],
    *,
    is_home: bool,
    additional_eligible: Callable[[PlayerT], bool] | None = None,
    preserve_existing_selection: Callable[[PlayerT], bool] | None = None,
    require_complete_xi: bool = True,
) -> PreparedPremierLeagueAiSelection:
    """Prepare an AI Premier League XI without caller-supplied formation/quota.

    The formation path mirrors 0x409500 -> 0x409B50: home/away base, exact
    first-eleven roster rating, live late-season Premier League table pressure,
    then the manager attacking/normal/defensive formation preference. The
    substitute quota and Non-EU limit come directly from DBRCompetition fields
    parsed from Static.dat (+17 and +34 respectively).
    """
    current_rating = strategy_team_rating(ordered_roster)
    opponent_rating = strategy_team_rating(opponent_roster)
    league_bias = premier_league_strategy_bias(table_rows, team_club_id)
    strategy_score = game_strategy_score(
        is_home=bool(is_home),
        current_rating=current_rating,
        opponent_rating=opponent_rating,
        competition_context_bias=league_bias,
    )
    selection_class = formation_selection_class_from_score(strategy_score)
    formation_id = manager_formation_for_selection_class(
        manager,
        selection_class,
    )
    substitute_quota = resolved_substitute_quota(
        int(competition.substitute_quota)
    )

    selection = prepare_ai_match_selection(
        int(team_club_id),
        ordered_roster,
        formation_id=formation_id,
        substitute_quota=substitute_quota,
        additional_eligible=additional_eligible,
        preserve_existing_selection=preserve_existing_selection,
        require_complete_xi=require_complete_xi,
        non_eu_limit=int(competition.max_non_eu_players),
    )

    return PreparedPremierLeagueAiSelection(
        strategy_score=strategy_score,
        selection_class=selection_class,
        formation_id=formation_id,
        substitute_quota=substitute_quota,
        selection=selection,
    )

def prepare_premier_league_ai_match_side(
    team_club_id: int,
    ordered_roster: Sequence[PlayerT],
    opponent_roster: Sequence[PlayerT],
    manager: ManagerFormationInput,
    competition: CompetitionSelectionInput,
    table_rows: Sequence[LeagueTableInput],
    *,
    side: int,
    is_home: bool,
    tactical_state: TeamTacticalState | None = None,
    additional_eligible: Callable[[PlayerT], bool] | None = None,
    preserve_existing_selection: Callable[[PlayerT], bool] | None = None,
    require_complete_xi: bool = True,
) -> PreparedPremierLeagueAiSide:
    """Prepare a calculator-ready Premier League AI side autonomously.

    A normally constructed AI DBRTeam retains the authoritative backend
    defaults: Normal Play, Normal Without Ball, Normal With Ball and
    Aggression 5. Manager tactical preference bytes belong to the separate
    MatchEngine-side snapshot and are intentionally not substituted here.

    Pass tactical_state when copied/preserved live DBRTeam state already has
    non-default values; that exact runtime state is then used unchanged.
    """
    preparation = prepare_premier_league_ai_selection(
        team_club_id,
        ordered_roster,
        opponent_roster,
        manager,
        competition,
        table_rows,
        is_home=is_home,
        additional_eligible=additional_eligible,
        preserve_existing_selection=preserve_existing_selection,
        require_complete_xi=require_complete_xi,
    )
    live_tactics = tactical_state or TeamTacticalState()
    match_side = build_prepared_match_side_from_selection(
        preparation.selection,
        side,
        live_tactics,
        user_controlled=False,
        team_orders=TeamOrderPriorities(),
    )
    return PreparedPremierLeagueAiSide(
        preparation=preparation,
        tactical_state=live_tactics,
        match_side=match_side,
    )

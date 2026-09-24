from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, Sequence, TypeVar

from match_availability import base_lineup_eligible
from match_lineup import AiLineupCoreResult, AiLineupPlayer, select_ai_lineup_core
from match_orders import TeamOrderPriorities
from match_participants import collect_match_participants
from match_simulation import PreparedMatchPlayer, PreparedMatchSide
from match_strength import TeamStrengthContext
from match_team_setup import TeamTacticalState, play_style_to_strategy_code


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

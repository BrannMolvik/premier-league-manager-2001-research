from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, Sequence, TypeVar

from match_availability import base_lineup_eligible
from match_lineup import AiLineupCoreResult, AiLineupPlayer, select_ai_lineup_core
from match_participants import collect_match_participants


class MutableAiMatchPlayer(AiLineupPlayer, Protocol):
    club_id: int
    match_active: bool
    match_substitute_available: bool
    injured: bool
    suspended: bool
    selection_excluded: bool
    non_eu: bool

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

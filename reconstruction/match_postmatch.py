from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from match_events import IncidentKind, IncidentRecord, SubstitutionRecord
from match_simulation import NormalMatchResult, PreparedMatchSide


DEFAULT_FORM_CHANGE_PROB = 5
DEFAULT_IN_FORM_CHANGE_PROB = 20
DEFAULT_OUT_OF_FORM_CHANGE_PROB = 20
DEFAULT_FORM_INCREASE_PROB = 50


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


class MutablePostMatchPlayer(Protocol):
    condition: int
    form_state: int
    injured: bool


@dataclass(frozen=True)
class FormTransitionSettings:
    """Shipped defaults loaded for DBRPlayer Form updater 0x41B870."""

    form_change_prob: int = DEFAULT_FORM_CHANGE_PROB
    in_form_change_prob: int = DEFAULT_IN_FORM_CHANGE_PROB
    out_of_form_change_prob: int = DEFAULT_OUT_OF_FORM_CHANGE_PROB
    form_increase_prob: int = DEFAULT_FORM_INCREASE_PROB

    def __post_init__(self) -> None:
        for name in (
            "form_change_prob",
            "in_form_change_prob",
            "out_of_form_change_prob",
            "form_increase_prob",
        ):
            value = int(getattr(self, name))
            if not 0 <= value <= 100:
                raise ValueError(f"{name} must be in 0..100")


def update_post_match_form(
    form_state: int,
    rng: BoundedRng,
    settings: FormTransitionSettings = FormTransitionSettings(),
) -> int:
    """Exact 0x41B870 five-state post-match Form transition.

    The first RNG(100) uses a state-dependent trigger probability. A failed
    trigger returns immediately and consumes no second draw. A successful
    trigger consumes RNG(100) against FormIncreaseProb; increase/decrease is
    clamped at the 0/4 state boundaries exactly as in the executable.
    """
    state = int(form_state)
    if not 0 <= state <= 4:
        raise ValueError("form_state must be in 0..4")

    if state <= 1:
        trigger = int(settings.out_of_form_change_prob)
    elif state == 2:
        trigger = int(settings.form_change_prob)
    else:
        trigger = int(settings.in_form_change_prob)

    if rng.randbelow(100) >= trigger:
        return state

    if rng.randbelow(100) < int(settings.form_increase_prob):
        return min(4, state + 1)
    return max(0, state - 1)


def appeared_player_indices(
    side: PreparedMatchSide,
    result: NormalMatchResult,
) -> frozenset[int]:
    """Return side-local players who appeared, matching the post-match scope.

    Every original starter counts as an appearance. A bench player joins the
    appeared set when a type-10 substitution record names them as incoming.
    """
    appeared = {int(index) for index in side.starting_player_indices}
    side_id = int(side.side)

    for timed in result.events:
        event = timed.event
        if (
            isinstance(event, SubstitutionRecord)
            and int(event.player_side) == side_id
        ):
            appeared.add(int(event.incoming_player_index))

    return frozenset(appeared)


@dataclass(frozen=True)
class PostMatchPersistenceSummary:
    appeared_player_indices: frozenset[int]
    injured_player_indices: frozenset[int]


def persist_post_match_side(
    side: PreparedMatchSide,
    runtime_participants: Sequence[MutablePostMatchPlayer],
    result: NormalMatchResult,
    rng: BoundedRng,
    *,
    form_settings: FormTransitionSettings = FormTransitionSettings(),
) -> PostMatchPersistenceSummary:
    """Persist the proven post-match player state for one side.

    Original MatchCalculator Condition processing mutates DBRPlayer+0x77
    directly, so the clean-room copy must be written back for every participant.

    Match-local injury flags are converted to persistent injury state during
    0x5127A0/0x41A5B0. Form update 0x41B870 is then run once for every player
    who actually appeared, in participant/roster order.

    Suspension/card counters are deliberately not handled here until the
    0x419490/0x4197C0/0x419680 competition-specific persistence path is fully
    reconstructed.
    """
    prepared = tuple(side.players)
    runtime = tuple(runtime_participants)
    if len(prepared) != len(runtime):
        raise ValueError(
            "runtime participant count must match prepared participant count"
        )

    for local_index, player in enumerate(prepared):
        if int(player.player_index) != local_index:
            raise ValueError(
                "prepared participants must use contiguous side-local indices"
            )
        runtime[local_index].condition = int(player.condition)

    side_id = int(side.side)
    injured: set[int] = set()
    for timed in result.events:
        event = timed.event
        if (
            isinstance(event, IncidentRecord)
            and event.kind is IncidentKind.INJURED
            and int(event.player_side) == side_id
        ):
            local_index = int(event.player_index)
            if not 0 <= local_index < len(runtime):
                raise IndexError(
                    f"injury player index {local_index} outside participant array"
                )
            runtime[local_index].injured = True
            injured.add(local_index)

    appeared = appeared_player_indices(side, result)
    for local_index, player in enumerate(runtime):
        if local_index in appeared:
            player.form_state = update_post_match_form(
                int(player.form_state),
                rng,
                form_settings,
            )

    return PostMatchPersistenceSummary(
        appeared_player_indices=appeared,
        injured_player_indices=frozenset(injured),
    )

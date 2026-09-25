"""Recovered pre-schedule startup RNG primitives.

Only behavior with proven executable ordering/bounds is modeled here.
"""

from typing import Iterable, Protocol


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


class PlayerSource(Protocol):
    index: int
    club_id: int
    initial_flags: int


def startup_youth_target_count(option_mode: int | None, rng: BoundedRng) -> int:
    """Reproduce 0x42C3A0 followed by the +4 in 0x61DF90."""
    if option_mode is None:
        return 4
    option_mode = int(option_mode)
    if option_mode == 0:
        return 4 + rng.randbelow(2)
    if option_mode == 1:
        return 5 + rng.randbelow(2)
    if option_mode == 2:
        return 6 + rng.randbelow(3)
    return 4


def startup_youth_candidate_ids(
    players: Iterable[PlayerSource],
    source_club_id: int,
) -> tuple[int, ...]:
    """Reproduce the 0x61DF90 club/bit-3 candidate filter in table order."""
    source_club_id = int(source_club_id)
    return tuple(
        int(player.index)
        for player in players
        if int(player.club_id) == source_club_id
        and not (int(player.initial_flags) & 0x08)
    )


def select_startup_youth_candidate(candidates: list[int], rng: BoundedRng) -> int:
    """Select one candidate and apply the executable swap-delete mutation."""
    if not candidates:
        raise ValueError("candidate list must not be empty")
    selected_index = rng.randbelow(len(candidates))
    selected = int(candidates[selected_index])
    candidates[selected_index] = candidates[-1]
    candidates.pop()
    return selected

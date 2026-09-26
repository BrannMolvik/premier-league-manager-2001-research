"""Exact procedural-League round-robin generator recovered from FOOTBAL.EXE.

The legacy builder at 0x6170F0 constructs one randomized single round-robin
pairing matrix before emitting one or more schedule cycles.  Its recursive
solver is 0x616F20 -> 0x616EA0 -> 0x616CE0.  Candidate selection in 0x616CE0
uses the shared MSVC bounded RNG and can backtrack, so its call stream is not a
simple Fisher-Yates sequence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol, TypeVar


T = TypeVar("T")


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


@dataclass(frozen=True)
class ProceduralLeagueRoundRobin:
    rounds: tuple[tuple[tuple[T, T], ...], ...]
    bounds: tuple[int, ...]
    state_after: int | None

    @property
    def pairing_count(self) -> int:
        return sum(len(round_pairs) for round_pairs in self.rounds)


@dataclass(frozen=True)
class ProceduralLeagueMatchEmission:
    """One LeagueMatch call emitted by 0x6172C3..0x61735D.

    schedule_index addresses League+0x60's sorted week/weekday array.
    home_team and away_team are passed to the same 0x5104F0 LeagueMatch
    constructor positions used by fixed home/away fixtures.
    """

    round_index: int
    pair_index: int
    cycle_index: int
    schedule_index: int
    home_team: object
    away_team: object


def procedural_league_cycle_count(
    team_count: int,
    scheduled_matchday_count: int,
) -> int:
    """Reproduce 0x616F40's ceiling division.

    The executable divides the competition's scheduled-matchday byte by
    team_count - 1 and increments the quotient when there is a remainder.
    Generic canonical procedural Leagues use complete cycles; the special
    ScotPremierLeague override handles its partial final cycle separately.
    """
    team_count = int(team_count)
    scheduled_matchday_count = int(scheduled_matchday_count)
    if team_count <= 1:
        raise ValueError("procedural League cycle count requires at least two teams")
    if scheduled_matchday_count < 0:
        raise ValueError("scheduled matchday count must not be negative")
    quotient, remainder = divmod(scheduled_matchday_count, team_count - 1)
    return quotient + int(remainder != 0)


def materialize_procedural_league_match_emissions(
    round_robin: ProceduralLeagueRoundRobin,
    scheduled_matchday_count: int,
) -> tuple[ProceduralLeagueMatchEmission, ...]:
    """Reproduce generic 0x6170F0 LeagueMatch emission order.

    0x6170F0 iterates pairing rounds first, then adjacent pairs, then schedule
    cycles for that pair. It reuses the same randomized one-cycle matrix and
    swaps the two participant pointers after every emitted cycle, so odd cycles
    reverse home/away direction. 0x616FC0 selects the date-array entry as
    (team_count - 1) * cycle_index + round_index.

    This helper models the generic League vtable path. ScotPremierLeague uses
    its 0x6170A0 override for the final partial cycle and is intentionally not
    folded into this generic routine.
    """
    rounds = tuple(round_robin.rounds)
    if not rounds:
        return ()

    round_count = len(rounds)
    team_count = round_count + 1
    cycle_count = procedural_league_cycle_count(
        team_count,
        scheduled_matchday_count,
    )

    emissions: list[ProceduralLeagueMatchEmission] = []
    for round_index, round_pairs in enumerate(rounds):
        for pair_index, (left, right) in enumerate(round_pairs):
            for cycle_index in range(cycle_count):
                if cycle_index & 1:
                    home_team, away_team = right, left
                else:
                    home_team, away_team = left, right
                emissions.append(
                    ProceduralLeagueMatchEmission(
                        round_index=round_index,
                        pair_index=pair_index,
                        cycle_index=cycle_index,
                        schedule_index=round_count * cycle_index + round_index,
                        home_team=home_team,
                        away_team=away_team,
                    )
                )
    return tuple(emissions)

@dataclass
class _Slot:
    team: object | None
    capacity: int
    cursor: int
    candidates: list["_Slot"]


class _TracingRng:
    def __init__(self, delegate: BoundedRng):
        self.delegate = delegate
        self.bounds: list[int] = []

    def randbelow(self, bound: int) -> int:
        bound = int(bound)
        if bound <= 0:
            raise ValueError("legacy round-robin RNG bound must be positive")
        self.bounds.append(bound)
        return int(self.delegate.randbelow(bound))

    @property
    def state(self) -> int | None:
        value = getattr(self.delegate, "state", None)
        return None if value is None else int(value) & 0xFFFFFFFF


class _RoundRobinSolver:
    """High-level transliteration of 0x616BF0..0x616F20.

    Each row contains N slot objects.  Row r has candidate-vector capacity
    N-1-r.  Once one perfect matching is chosen, 0x616B60 copies the row into
    the next row while dropping the paired opponent that was moved to the end
    of each candidate vector.
    """

    def __init__(self, teams: tuple[T, ...], rng: _TracingRng):
        self.teams = teams
        self.team_count = len(teams)
        self.rng = rng
        self.row_index = 0
        self.rows: list[list[_Slot]] = []

        for row_index in range(max(0, self.team_count - 1)):
            capacity = self.team_count - 1 - row_index
            self.rows.append(
                [
                    _Slot(
                        team=None,
                        capacity=capacity,
                        cursor=0,
                        candidates=[None] * capacity,  # type: ignore[list-item]
                    )
                    for _ in range(self.team_count)
                ]
            )

        if self.rows:
            first = self.rows[0]
            for index, slot in enumerate(first):
                slot.team = teams[index]
                slot.candidates = [
                    first[other]
                    for other in range(self.team_count)
                    if other != index
                ]

    @staticmethod
    def _swap(values: list, left: int, right: int) -> None:
        values[left], values[right] = values[right], values[left]

    def _commit_slot(self, slot: _Slot) -> None:
        """Reproduce 0x616C60: remove this slot from active opponents."""
        for candidate_index in range(slot.cursor, slot.capacity):
            candidate = slot.candidates[candidate_index]
            found = None
            for index in range(candidate.cursor, candidate.capacity):
                if candidate.candidates[index] is slot:
                    found = index
                    break
            if found is None:
                raise RuntimeError("legacy round-robin candidate graph desynchronized")
            old_cursor = candidate.cursor
            candidate.cursor += 1
            self._swap(candidate.candidates, old_cursor, found)

    def _undo_slot(self, slot: _Slot) -> None:
        """Reproduce 0x616CB0's cursor-only backtracking undo."""
        for candidate_index in range(slot.cursor, slot.capacity):
            candidate = slot.candidates[candidate_index]
            candidate.cursor -= 1
            if candidate.cursor < 0:
                raise RuntimeError("legacy round-robin cursor underflow")

    def _copy_row_to_next(self) -> None:
        """Reproduce 0x616B60/0x616BA0 pointer remapping."""
        source = self.rows[self.row_index]
        destination = self.rows[self.row_index + 1]
        source_index = {id(slot): index for index, slot in enumerate(source)}

        for index, destination_slot in enumerate(destination):
            source_slot = source[index]
            destination_slot.team = source_slot.team
            destination_slot.cursor = 0
            destination_slot.candidates = [
                destination[source_index[id(candidate)]]
                for candidate in source_slot.candidates[: destination_slot.capacity]
            ]

    def _solve_active_prefix(self, active_count: int) -> bool:
        """Reproduce 0x616EA0."""
        row = self.rows[self.row_index]
        forced_index = 0

        for index in range(active_count):
            slot = row[index]
            remaining = slot.capacity - slot.cursor
            if remaining == 1:
                forced_index = index
            elif remaining == 0:
                return False

        # 0x616EA0 moves the last forced slot, or slot zero when none is
        # forced, to the end of the active prefix.
        self._swap(row, forced_index, active_count - 1)
        remaining_active = active_count - 2
        pivot = row[remaining_active + 1]
        return self._solve_pivot(pivot, remaining_active)

    def _solve_pivot(self, pivot: _Slot, remaining_active: int) -> bool:
        """Reproduce 0x616CE0 including retries and cross-round recursion."""
        if pivot.capacity - pivot.cursor == 0:
            return False

        self._commit_slot(pivot)
        attempts = 0

        while True:
            bound = pivot.capacity - pivot.cursor - attempts
            if bound <= 0:
                self._undo_slot(pivot)
                return False

            selected = self.rng.randbelow(bound)
            candidate_index = pivot.cursor + selected
            candidate = pivot.candidates[candidate_index]

            self._commit_slot(candidate)

            # Move the selected edge to the end of both candidate vectors.
            pivot_position = next(
                index
                for index in range(pivot.cursor, pivot.capacity)
                if pivot.candidates[index] is candidate
            )
            self._swap(pivot.candidates, pivot_position, pivot.capacity - 1)
            self._swap(
                candidate.candidates,
                candidate.cursor - 1,
                candidate.capacity - 1,
            )

            if remaining_active != 0:
                row = self.rows[self.row_index]
                row_position = next(
                    index for index, slot in enumerate(row) if slot is candidate
                )
                self._swap(row, row_position, remaining_active)

                if self._solve_active_prefix(remaining_active):
                    return True
            else:
                if pivot.capacity == 1:
                    return True

                self._copy_row_to_next()
                self.row_index += 1
                if self._solve_active_prefix(self.team_count):
                    return True
                self.row_index -= 1

            # Backtrack candidate-specific changes.
            attempts += 1
            self._swap(
                candidate.candidates,
                candidate.cursor - 1,
                candidate.capacity - 1,
            )
            self._undo_slot(candidate)

            remaining_choices = pivot.capacity - pivot.cursor
            if attempts >= remaining_choices:
                self._undo_slot(pivot)
                return False

            pivot_position = next(
                index
                for index in range(pivot.cursor, pivot.capacity)
                if pivot.candidates[index] is candidate
            )
            self._swap(
                pivot.candidates,
                pivot_position,
                pivot.capacity - attempts,
            )

    def solve(self) -> bool:
        if self.team_count <= 1:
            return True
        return self._solve_active_prefix(self.team_count)

    def materialized_rounds(self) -> tuple[tuple[tuple[T, T], ...], ...]:
        result: list[tuple[tuple[T, T], ...]] = []
        for row in self.rows:
            pairs: list[tuple[T, T]] = []
            for index in range(0, self.team_count, 2):
                left = row[index].team
                right = row[index + 1].team
                if left is None or right is None:
                    raise RuntimeError("legacy round-robin row was not fully assigned")
                pairs.append((left, right))  # type: ignore[arg-type]
            result.append(tuple(pairs))
        return tuple(result)


def generate_procedural_league_round_robin(
    teams: Iterable[T],
    rng: BoundedRng,
) -> ProceduralLeagueRoundRobin:
    """Reproduce 0x6170F0's randomized one-cycle pairing matrix.

    Canonical FM2001 procedural Leagues all enter this solver with an even
    participant count.  The executable has no bye-team branch in this path,
    so reject odd synthetic inputs rather than inventing behavior.

    The returned round order is the order consumed by 0x6172C3..0x61735D.
    Within each round, adjacent slots are emitted as match pairs in order.
    Later home/away cycles reuse this same matrix and do not regenerate it.
    """
    team_tuple = tuple(teams)
    if len(team_tuple) < 2:
        return ProceduralLeagueRoundRobin(
            rounds=(),
            bounds=(),
            state_after=(
                None
                if getattr(rng, "state", None) is None
                else int(getattr(rng, "state")) & 0xFFFFFFFF
            ),
        )
    if len(team_tuple) % 2:
        raise ValueError("canonical procedural League path requires an even team count")

    tracing_rng = _TracingRng(rng)
    solver = _RoundRobinSolver(team_tuple, tracing_rng)
    if not solver.solve():
        raise RuntimeError("legacy procedural League round-robin solver failed")

    rounds = solver.materialized_rounds()

    # Strong structural invariant: one single round-robin cycle contains every
    # unordered team pair exactly once.
    identity = {id(team): index for index, team in enumerate(team_tuple)}
    pairs = []
    for round_pairs in rounds:
        for left, right in round_pairs:
            left_index = identity.get(id(left))
            right_index = identity.get(id(right))
            if left_index is None or right_index is None:
                # Immutable scalar team IDs do not preserve object identity.
                left_index = team_tuple.index(left)
                right_index = team_tuple.index(right)
            pairs.append(tuple(sorted((left_index, right_index))))

    expected_pair_count = len(team_tuple) * (len(team_tuple) - 1) // 2
    if len(pairs) != expected_pair_count or len(set(pairs)) != expected_pair_count:
        raise RuntimeError("legacy procedural League output is not a full round robin")

    return ProceduralLeagueRoundRobin(
        rounds=rounds,
        bounds=tuple(tracing_rng.bounds),
        state_after=tracing_rng.state,
    )

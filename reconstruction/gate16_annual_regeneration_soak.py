"""Bounded destructive soak audit for repeated annual primary regeneration.

Gate 16 eventually requires genuine multi-season automatic play. This audit is
a narrower cloud-safe foundation: repeatedly exercise the already recovered
annual replacement boundary and prove that each new primary season replaces,
rather than accumulates, prior fixture/result/prepared-match runtime state.

The caller must prepare valid completed-season qualification evidence before
each rollover. The audit never synthesizes qualification, standings, results,
or RNG draws and therefore cannot be used to claim that multiple seasons were
actually played.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


class AnnualRegenerationSoakError(RuntimeError):
    """Repeated season replacement violated a destructive-state invariant."""


@dataclass(frozen=True)
class AnnualRegenerationSoakSnapshot:
    cycle: int
    season_year: int
    fixture_count: int
    scheduler_fixture_count: int
    primary_matchday_date_count: int
    result_count_after: int
    prepared_environment_count_after: int
    rng_state_before: int
    rng_state_after: int
    runtime_object_replaced: bool


PrepareCompletedSeason = Callable[[object, int, int], None]


def _scheduler_fixture_ids(state) -> tuple[int, ...]:
    order = getattr(state, "premier_league_scheduler_order", {})
    return tuple(
        int(fixture_id)
        for round_index in sorted(order)
        for fixture_id in order[round_index]
    )


def audit_repeated_annual_regeneration(
    controller,
    season_years: Iterable[int],
    *,
    prepare_completed_season: PrepareCompletedSeason,
    procedural_league_ids: Iterable[int] = (),
) -> tuple[AnnualRegenerationSoakSnapshot, ...]:
    """Repeat the atomic annual replacement and check stale-state destruction.

    prepare_completed_season is intentionally explicit. Canonical callers
    should let actual completed competitions publish qualification evidence;
    synthetic destructive tests may install their own bounded fixture evidence.
    """
    years = tuple(int(year) for year in season_years)
    if not years:
        raise ValueError("annual regeneration soak requires at least one season year")
    if len(set(years)) != len(years):
        raise ValueError("annual regeneration soak season years must be unique")
    if any(later <= earlier for earlier, later in zip(years, years[1:])):
        raise ValueError("annual regeneration soak season years must increase")

    procedural = tuple(int(value) for value in procedural_league_ids)
    snapshots: list[AnnualRegenerationSoakSnapshot] = []
    retained_old_runtimes: list[object] = []
    expected_fixture_count: int | None = None

    for cycle, season_year in enumerate(years):
        prepare_completed_season(controller, cycle, season_year)
        state = controller.state
        old_runtime = state.premier_league
        retained_old_runtimes.append(old_runtime)

        rng_before = getattr(controller.match_rng, "state", None)
        if rng_before is None:
            raise AnnualRegenerationSoakError(
                "annual regeneration soak requires serializable controller RNG state"
            )

        regeneration = controller.regenerate_annual_primary_season(
            season_year=season_year,
            procedural_league_ids=procedural,
        )
        state = controller.state
        new_runtime = state.premier_league

        if new_runtime is old_runtime:
            raise AnnualRegenerationSoakError(
                f"cycle {cycle}: annual regeneration reused the prior Premier League runtime"
            )
        if any(new_runtime is previous for previous in retained_old_runtimes):
            raise AnnualRegenerationSoakError(
                f"cycle {cycle}: annual regeneration revived a retained old runtime object"
            )
        if state.premier_league.results:
            raise AnnualRegenerationSoakError(
                f"cycle {cycle}: prior-season Premier League results survived regeneration"
            )
        if state.prepared_match_environments:
            raise AnnualRegenerationSoakError(
                f"cycle {cycle}: prepared match environments survived regeneration"
            )

        fixture_ids = tuple(sorted(int(value) for value in new_runtime.fixtures))
        if not fixture_ids:
            raise AnnualRegenerationSoakError(
                f"cycle {cycle}: regenerated Premier League has no fixtures"
            )
        if expected_fixture_count is None:
            expected_fixture_count = len(fixture_ids)
        elif len(fixture_ids) != expected_fixture_count:
            raise AnnualRegenerationSoakError(
                f"cycle {cycle}: Premier League fixture count changed "
                f"{expected_fixture_count} -> {len(fixture_ids)}"
            )

        scheduler_ids = _scheduler_fixture_ids(state)
        if len(scheduler_ids) != len(set(scheduler_ids)):
            raise AnnualRegenerationSoakError(
                f"cycle {cycle}: scheduler contains duplicate Premier League fixtures"
            )
        if set(scheduler_ids) != set(fixture_ids):
            raise AnnualRegenerationSoakError(
                f"cycle {cycle}: scheduler fixture set differs from regenerated league"
            )

        rng_after = getattr(controller.match_rng, "state", None)
        if rng_after is None or int(rng_after) != int(regeneration.state_after):
            raise AnnualRegenerationSoakError(
                f"cycle {cycle}: controller RNG did not commit regeneration state atomically"
            )

        snapshots.append(
            AnnualRegenerationSoakSnapshot(
                cycle=cycle,
                season_year=season_year,
                fixture_count=len(fixture_ids),
                scheduler_fixture_count=len(scheduler_ids),
                primary_matchday_date_count=len(state.primary_matchday_order),
                result_count_after=len(state.premier_league.results),
                prepared_environment_count_after=len(state.prepared_match_environments),
                rng_state_before=int(rng_before) & 0xFFFFFFFF,
                rng_state_after=int(rng_after) & 0xFFFFFFFF,
                runtime_object_replaced=True,
            )
        )

    return tuple(snapshots)

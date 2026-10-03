"""Fail-closed multi-seed wrapper for the canonical Gate-16 audit.

The existing canonical_multiseason_audit runner proves one shipped-data seed at
a time. This module orchestrates multiple independent canonical seeds against
the same authorized game directory and returns one evidence envelope only when
every requested seed completes successfully.

It does not synthesize a source database, standings, qualification state, RNG
state, or season results. Each seed delegates to the existing canonical runner.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable, Iterable

from canonical_multiseason_audit import run_canonical_multiseason_audit


DEFAULT_CANONICAL_SEEDS = (
    1,
    2,
    0x12345678,
)


class CanonicalMultiSeedAuditError(RuntimeError):
    """One requested canonical shipped-data seed failed its audit."""


CanonicalRunner = Callable[..., dict]


def _normalized_seeds(player_seeds: Iterable[int]) -> tuple[int, ...]:
    raw = tuple(player_seeds)
    if any(type(seed) is not int for seed in raw):
        raise ValueError("canonical multi-seed audit seeds must be exact integers")
    seeds = tuple(seed & 0xFFFFFFFF for seed in raw)
    if len(seeds) < 2:
        raise ValueError("canonical multi-seed audit requires at least two seeds")
    if len(set(seeds)) != len(seeds):
        raise ValueError("canonical multi-seed audit seeds must be unique")
    return seeds


def run_canonical_multiseed_audit(
    game_dir: str | Path,
    *,
    player_seeds: Iterable[int] = DEFAULT_CANONICAL_SEEDS,
    rollover_count: int = 3,
    max_days_per_season: int = 420,
    canonical_runner: CanonicalRunner = run_canonical_multiseason_audit,
) -> dict:
    """Run the existing canonical multi-season audit once per requested seed.

    The wrapper fails immediately on the first failing seed and therefore never
    emits a misleading combined success report containing a failed seed.
    """
    seeds = _normalized_seeds(player_seeds)
    if type(rollover_count) is not int or rollover_count < 2:
        raise ValueError(
            "canonical multi-seed audit rollover_count must be an integer >= 2"
        )
    if type(max_days_per_season) is not int or max_days_per_season <= 0:
        raise ValueError("max_days_per_season must be a positive integer")

    reports: list[dict] = []
    for seed in seeds:
        try:
            report = canonical_runner(
                game_dir,
                player_seed=seed,
                rollover_count=rollover_count,
                max_days_per_season=max_days_per_season,
            )
        except Exception as exc:
            raise CanonicalMultiSeedAuditError(
                f"canonical shipped-data audit failed for player seed 0x{seed:08X}"
            ) from exc

        reported_seed = int(report.get("player_seed", -1)) & 0xFFFFFFFF
        if reported_seed != seed:
            raise CanonicalMultiSeedAuditError(
                "canonical runner returned a mismatched player seed: "
                f"requested 0x{seed:08X}, got 0x{reported_seed:08X}"
            )
        if report.get("rollover_count") != rollover_count:
            raise CanonicalMultiSeedAuditError(
                f"canonical runner returned unexpected rollover count for "
                f"seed 0x{seed:08X}"
            )
        snapshots = report.get("snapshots")
        if not isinstance(snapshots, list) or len(snapshots) != rollover_count:
            raise CanonicalMultiSeedAuditError(
                f"canonical runner returned incomplete snapshots for "
                f"seed 0x{seed:08X}"
            )
        reports.append(report)

    return {
        "schema_version": 1,
        "audit": "gate16_canonical_multiseed",
        "player_seeds": list(seeds),
        "seed_count": len(seeds),
        "rollover_count_per_seed": rollover_count,
        "max_days_per_season": max_days_per_season,
        "all_seeds_passed": True,
        "reports": reports,
    }


def _parse_seed(value: str) -> int:
    return int(value, 0)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the canonical Gate-16 multi-season shipped-data audit across "
            "multiple independent player seeds."
        )
    )
    parser.add_argument("game_dir", type=Path)
    parser.add_argument(
        "--player-seed",
        action="append",
        type=_parse_seed,
        dest="player_seeds",
        help=(
            "Repeat for each canonical seed. Accepts decimal or 0x-prefixed "
            "values. Defaults to 1, 2 and 0x12345678."
        ),
    )
    parser.add_argument("--rollovers", type=int, default=3)
    parser.add_argument("--max-days-per-season", type=int, default=420)
    args = parser.parse_args()

    report = run_canonical_multiseed_audit(
        args.game_dir,
        player_seeds=(
            DEFAULT_CANONICAL_SEEDS
            if args.player_seeds is None
            else tuple(args.player_seeds)
        ),
        rollover_count=args.rollovers,
        max_days_per_season=args.max_days_per_season,
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

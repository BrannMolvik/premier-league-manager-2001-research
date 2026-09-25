from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import IntEnum
from typing import Protocol, Sequence


CONDITION_INJURY_INDUCING_LEVEL = 75
MIN_PLAYERS_AVAILABLE_FOR_INJURY = 14


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


class MutablePersistentInjuryPlayer(Protocol):
    condition: int
    injured: bool
    suspended: bool
    selection_excluded: bool
    injury_return_date: date | None
    injury_source_mode: int | None
    injury_severity_code: int | None
    injury_history_weight: int


class MatchInjuryBucket(IntEnum):
    """Internal 0x605F90 match-injury generator buckets.

    The persistent 12-byte injury object does not retain this anatomical
    bucket, so it is exposed only for deterministic reconstruction/testing.
    """

    BROKEN_TOE = 0
    ANKLE = 1
    ACHILLES = 2
    SHIN = 3
    CALF = 4
    THIGH = 5
    KNEE = 6
    HAMSTRING = 7
    GROIN = 8
    HERNIA = 9
    ABDOMEN = 10
    RIBS = 11
    COLLAR_BONE = 12
    SPECIAL = 13
    BROKEN_LEG = 14


@dataclass(frozen=True)
class GeneratedPersistentInjury:
    source_mode: int
    bucket: MatchInjuryBucket
    severity_code: int
    recovery_weeks: int
    condition_drop: int
    return_date: date


def count_available_for_persistent_injury(
    roster: Sequence[MutablePersistentInjuryPlayer],
) -> int:
    """Approximate the proven availability inputs of team helper 0x405080.

    The reconstructed runtime currently models the exact low-three-bit
    unavailable states relevant here: injury, suspension and selection
    exclusion. Newly created injuries therefore reduce the count immediately
    for later participants in the same post-match loop.
    """
    return sum(
        1
        for player in roster
        if not bool(player.injured)
        and not bool(player.suspended)
        and not bool(player.selection_excluded)
    )


def _select_match_injury_bucket(source_mode: int, rng: BoundedRng) -> MatchInjuryBucket:
    roll = int(rng.randbelow(100))
    mode = int(source_mode)

    if mode == 0:
        if roll < 3:
            return MatchInjuryBucket.BROKEN_TOE
        if roll < 6:
            return MatchInjuryBucket.ANKLE
        if roll < 12:
            return MatchInjuryBucket.ACHILLES
        if roll < 18:
            return MatchInjuryBucket.SHIN
        if roll < 26:
            return MatchInjuryBucket.CALF
        if roll < 34:
            return MatchInjuryBucket.THIGH
        if roll < 40:
            return MatchInjuryBucket.KNEE
        if roll < 50:
            return MatchInjuryBucket.HAMSTRING
        if roll < 60:
            return MatchInjuryBucket.GROIN
        if roll < 69:
            return MatchInjuryBucket.HERNIA
        if roll < 78:
            return MatchInjuryBucket.ABDOMEN
        if roll < 84:
            return MatchInjuryBucket.RIBS
        if roll < 88:
            return MatchInjuryBucket.COLLAR_BONE
        if roll < 96:
            return MatchInjuryBucket.SPECIAL
        return MatchInjuryBucket.BROKEN_LEG

    if mode == 1:
        if roll < 10:
            return MatchInjuryBucket.ANKLE
        if roll < 20:
            return MatchInjuryBucket.ACHILLES
        if roll < 30:
            return MatchInjuryBucket.CALF
        if roll < 40:
            return MatchInjuryBucket.THIGH
        if roll < 50:
            return MatchInjuryBucket.KNEE
        if roll < 60:
            return MatchInjuryBucket.HAMSTRING
        if roll < 70:
            return MatchInjuryBucket.GROIN
        if roll < 80:
            return MatchInjuryBucket.HERNIA
        return MatchInjuryBucket.ABDOMEN

    raise ValueError("post-match persistent injury source mode must be 0 or 1")


def _severity_and_recovery(
    bucket: MatchInjuryBucket,
    rng: BoundedRng,
) -> tuple[int, int, int]:
    """Return exact (severity_code, recovery_weeks, Condition drop)."""
    if bucket is MatchInjuryBucket.BROKEN_TOE:
        return 4, int(rng.randbelow(4)) + 3, 40

    roll = int(rng.randbelow(100))

    if bucket is MatchInjuryBucket.ANKLE:
        if roll < 50:
            return 0, 1, 10
        if roll < 80:
            return 1, int(rng.randbelow(4)) + 3, 35
        if roll < 95:
            return 2, int(rng.randbelow(4)) + 11, 60
        return 3, int(rng.randbelow(4)) + 11, 60

    if bucket is MatchInjuryBucket.ACHILLES:
        # Executable compares the first threshold against the Ankle 80% global.
        if roll < 80:
            return 1, int(rng.randbelow(4)) + 3, 35
        if roll < 95:
            return 2, int(rng.randbelow(12)) + 12, 60
        return 3, int(rng.randbelow(12)) + 12, 60

    if bucket is MatchInjuryBucket.SHIN:
        return 1, int(rng.randbelow(4)) + 3, 35

    if bucket in (
        MatchInjuryBucket.CALF,
        MatchInjuryBucket.THIGH,
        MatchInjuryBucket.HAMSTRING,
        MatchInjuryBucket.GROIN,
    ):
        if roll < 50:
            return 0, 1, 10
        if roll < 80:
            return 1, int(rng.randbelow(4)) + 3, 35
        if roll < 95:
            return 2, int(rng.randbelow(4)) + 11, 60
        return 3, int(rng.randbelow(4)) + 11, 60

    if bucket is MatchInjuryBucket.KNEE:
        if roll < 50:
            return 0, int(rng.randbelow(2)) + 1, 10
        if roll < 80:
            return 1, int(rng.randbelow(4)) + 3, 35
        if roll < 95:
            return 2, int(rng.randbelow(4)) + 12, 60
        return 3, int(rng.randbelow(4)) + 11, 60

    if bucket is MatchInjuryBucket.HERNIA:
        return 1, int(rng.randbelow(3)) + 4, 35

    if bucket is MatchInjuryBucket.ABDOMEN:
        return 0, int(rng.randbelow(2)) + 1, 10

    if bucket is MatchInjuryBucket.RIBS:
        if roll < 50:
            return 0, 1, 10
        return 1, int(rng.randbelow(4)) + 3, 35

    if bucket is MatchInjuryBucket.COLLAR_BONE:
        return 1, int(rng.randbelow(4)) + 3, 35

    if bucket is MatchInjuryBucket.SPECIAL:
        # 0x60A3D0 consumes its RNG(100) above, then uses literal six weeks
        # and the Knee-moderate Condition-drop global (35).
        return 1, 6, 35

    if bucket is MatchInjuryBucket.BROKEN_LEG:
        if roll < 60:
            return 1, 12, 35
        if roll < 90:
            return 2, 26, 60
        return 3, 26, 60

    raise AssertionError(bucket)


def generate_persistent_match_injury(
    player: MutablePersistentInjuryPlayer,
    roster: Sequence[MutablePersistentInjuryPlayer],
    fixture_date: date,
    rng: BoundedRng,
    *,
    user_controlled: bool = False,
    min_available_players: int = MIN_PLAYERS_AVAILABLE_FOR_INJURY,
    condition_split: int = CONDITION_INJURY_INDUCING_LEVEL,
) -> GeneratedPersistentInjury | None:
    """Reconstruct post-match 0x41A5B0 -> 0x605F90 for match injuries.

    AI/non-user teams suppress creation when fewer than 14 players are
    currently available. Existing persistent injuries are not replaced.
    Mode 0 is selected at Condition >=75; Mode 1 below 75.
    """
    if not bool(user_controlled):
        if count_available_for_persistent_injury(roster) < int(min_available_players):
            return None

    if bool(player.injured) or player.injury_return_date is not None:
        return None

    source_mode = 1 if int(player.condition) < int(condition_split) else 0
    bucket = _select_match_injury_bucket(source_mode, rng)
    severity, weeks, condition_drop = _severity_and_recovery(bucket, rng)

    return_date = fixture_date + timedelta(days=7 * int(weeks))
    player.injured = True
    player.injury_return_date = return_date
    player.injury_source_mode = int(source_mode)
    player.injury_severity_code = int(severity)

    history_increment = 0
    if severity == 0:
        history_increment = 1
    elif severity == 1:
        history_increment = 4
    elif severity in (2, 3):
        history_increment = 8
    player.injury_history_weight = (
        int(player.injury_history_weight) + history_increment
    ) & 0xFF

    condition = int(player.condition)
    player.condition = condition - condition_drop if condition > condition_drop else 1

    return GeneratedPersistentInjury(
        source_mode=source_mode,
        bucket=bucket,
        severity_code=severity,
        recovery_weeks=weeks,
        condition_drop=condition_drop,
        return_date=return_date,
    )


def clear_expired_persistent_injury(
    player: MutablePersistentInjuryPlayer,
    on_date: date,
) -> bool:
    """Mirror the scheduled return handler's 0x418AD0 state clear."""
    return_date = player.injury_return_date
    if return_date is None or on_date < return_date:
        return False

    player.injured = False
    player.injury_return_date = None
    player.injury_source_mode = None
    player.injury_severity_code = None
    return True

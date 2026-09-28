"""Source-backed FM2001 monthly player-contract maintenance.

This module reconstructs the non-user-club branch of DBRPlayer::0x41ABC0.
The separate user-controlled 0x41BEE0 expiry/event path is intentionally not
collapsed into this routine.
"""

from __future__ import annotations

from datetime import date, timedelta
from enum import Enum

from match_role_rating import best_preferred_role_rating
from player_contract import contract_expiry_from_month_span


CONTRACT_DECISION_WINDOW_DAYS = 30
LOW_RATING_BOUNDARY = 50
LOW_RATING_RELEASE_ROLL = 8
HIGH_RATING_RELEASE_ROLL = 2
RELEASE_MIN_ROSTER_EXCLUSIVE = 18
RELEASE_MIN_TENURE_WEEKS_EXCLUSIVE = 104
RELEASE_MIN_AGE_EXCLUSIVE = 23
AI_RENEWAL_MONTHS = 12


class AiContractMaintenanceOutcome(str, Enum):
    NOT_DUE = "not_due"
    RENEWED = "renewed"
    OUT_OF_CONTRACT = "out_of_contract"


def completed_club_weeks(player, on_date: date) -> int:
    """Return the 0x419390 completed-week tenure used by 0x41ABC0."""
    joined = player.current_club_join_date
    if joined is None or joined > on_date:
        return 0
    return (on_date - joined).days // 7


def _release_eligibility_passes(player, on_date: date, roster_count: int) -> bool:
    """Reproduce the non-random release gates after 0x41ABC0 selects release."""
    if int(roster_count) <= RELEASE_MIN_ROSTER_EXCLUSIVE:
        return False
    if completed_club_weeks(player, on_date) <= RELEASE_MIN_TENURE_WEEKS_EXCLUSIVE:
        return False

    age = player.age(on_date)
    if age is None or int(age) <= RELEASE_MIN_AGE_EXCLUSIVE:
        return False

    # 0x417580 succeeds only when 0x417460 is false and the two club IDs
    # match. 0x417460 is exactly signed player+0x64 > -1. RuntimePlayer's
    # loan_club_id models the unequal temporary/current-club state.
    if int(player.ai_transfer_block_value_64) > -1:
        return False
    if player.loan_club_id is not None:
        return False
    return True


def run_ai_monthly_contract_maintenance(
    player,
    *,
    on_date: date,
    roster_count: int,
    rng,
) -> AiContractMaintenanceOutcome:
    """Reproduce the non-user branch of DBRPlayer::0x41ABC0.

    More than 30 days before expiry this consumes no RNG. Inside the decision
    window it preserves the exact one/two shared-CRT RNG(100) call pattern.

    A successful release branch sets the source-backed states materialized by
    the clean-room runtime: transfer-listed, Out of contract and +0xC0 = 0.
    The player is not detached from club IDs here because 0x41ABC0 itself does
    not perform the explicit 0x4177C0 free-player detachment.

    Every other due branch renews from the existing expiry by exactly 12
    calendar months through the recovered 0x419190 path and applies the mapped
    0x419210 clears.
    """
    expiry = player.contract_expiry_date
    if expiry is None:
        return AiContractMaintenanceOutcome.NOT_DUE
    if on_date + timedelta(days=CONTRACT_DECISION_WINDOW_DAYS) < expiry:
        return AiContractMaintenanceOutcome.NOT_DUE
    if not hasattr(rng, "randbelow"):
        raise TypeError("rng must provide randbelow(bound)")

    rating = best_preferred_role_rating(
        player.current_raw,
        player.positions,
    )

    first_roll = int(rng.randbelow(100))
    release_candidate = bool(
        first_roll < LOW_RATING_RELEASE_ROLL
        and int(rating) < LOW_RATING_BOUNDARY
    )

    if not release_candidate:
        second_roll = int(rng.randbelow(100))
        release_candidate = bool(
            second_roll < HIGH_RATING_RELEASE_ROLL
            and int(rating) >= LOW_RATING_BOUNDARY
        )

    if release_candidate and _release_eligibility_passes(
        player,
        on_date,
        int(roster_count),
    ):
        # 0x41B530 precedes the bit-7 set on this path.
        player.transfer_listed = True
        player.out_of_contract = True
        # 0x41AC7E zeros the neutral DBRPlayer+0xC0 byte.
        player.startup_month_span = 0
        return AiContractMaintenanceOutcome.OUT_OF_CONTRACT

    player.contract_expiry_date = contract_expiry_from_month_span(
        expiry,
        AI_RENEWAL_MONTHS,
    )
    # 0x419190 converges on 0x419210.
    player.out_of_contract = False
    player.signed_for_other_club = False
    return AiContractMaintenanceOutcome.RENEWED

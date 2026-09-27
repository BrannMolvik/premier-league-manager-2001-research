"""Evidence-backed selling-club transfer decision primitives.

This module intentionally separates the recovered decision itself from two
still-partially reconstructed inputs:
- DBRPlayer::0x4205A0 transfer valuation;
- DBRClub::0x405080 transfer-availability squad count.

Callers must supply those values explicitly until their adapters are promoted.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from match_role_rating import best_preferred_role_rating


class SellingClubDecision(str, Enum):
    ACCEPTED = "accepted"
    TOO_CHEAP = "too_cheap"
    SQUAD_TOO_SMALL = "squad_too_small"


@dataclass(frozen=True)
class SellingClubBidInputs:
    proposal_total_value: float
    player_value: float
    target_age: int
    higher_rated_squadmates: int
    eligible_squad_count: int


def protected_young_first_team_player(
    *,
    target_age: int,
    higher_rated_squadmates: int,
) -> bool:
    """Reproduce player helper 0x4212F0.

    0x4212F0 returns true exactly when:
    - fewer than 11 players in the current club have a strictly higher
      0x41E1D0 max-preferred-role rating; and
    - the target player's age from 0x4173B0 is below 30.
    """

    return int(higher_rated_squadmates) < 11 and int(target_age) < 30


def evaluate_selling_club_bid(
    inputs: SellingClubBidInputs,
) -> SellingClubDecision:
    """Reproduce the seller-chairman branch at proposal routine 0x4EF940.

    Exact recovered order:

    1. If 0x4212F0 is true, compare proposal total value (0x4EFA20) against
       0.6 * player transfer value (0x4205A0). A strict shortfall routes to
       0x4F01A0 and the Too Cheap chairman events.
    2. Otherwise/after passing price, 0x405080 is compared with 17. Values
       below 17 route to 0x4EFF30 and the Too Small Squad chairman events.
    3. The remaining path calls 0x4F0EA0, which emits Offer Accepted /
       Approach Player events depending on control context.

    Equality at exactly 60 percent passes the cheap-bid check because the
    original branch rejects only when threshold > offer.
    """

    offer = float(inputs.proposal_total_value)
    player_value = float(inputs.player_value)
    if offer < 0 or player_value < 0:
        raise ValueError("proposal/player values must not be negative")
    if int(inputs.higher_rated_squadmates) < 0:
        raise ValueError("higher_rated_squadmates must not be negative")
    if int(inputs.eligible_squad_count) < 0:
        raise ValueError("eligible_squad_count must not be negative")

    if protected_young_first_team_player(
        target_age=int(inputs.target_age),
        higher_rated_squadmates=int(inputs.higher_rated_squadmates),
    ):
        if offer < player_value * 0.6:
            return SellingClubDecision.TOO_CHEAP

    if int(inputs.eligible_squad_count) < 17:
        return SellingClubDecision.SQUAD_TOO_SMALL

    return SellingClubDecision.ACCEPTED


def higher_rated_squadmate_count(state, player_id: int) -> int:
    """Reproduce club helper 0x408860 used by player predicate 0x4212F0."""

    player_id = int(player_id)
    target = state.players[player_id]
    target_rating = best_preferred_role_rating(
        target.current_raw,
        target.positions,
    )
    count = 0
    for squadmate in state.ordered_club_roster(int(target.club_id)):
        if int(squadmate.index) == player_id:
            continue
        rating = best_preferred_role_rating(
            squadmate.current_raw,
            squadmate.positions,
        )
        if rating > target_rating:
            count += 1
    return count


def eligible_selling_squad_count(state, club_id: int) -> int:
    """Reproduce DBRClub helper 0x405080.

    The original starts from the club roster count and excludes players with
    DBRPlayer+0x14 bit 8, 0, 6, or 1 respectively:
    transfer-listed, injured, loaned out, or suspended.
    """

    return sum(
        not player.selling_squad_count_excluded
        for player in state.ordered_club_roster(int(club_id))
    )

"""Recovered weekly autonomous club acquisition path for Gate 9.

This module implements the evidence-backed 0x40DD70 -> 0x40DC90 -> 0x40DBB0
-> 0x41EFB0 slice. It deliberately does not invent transfer budgets or other
Gate-10 finance behavior.

Two still-neutrally named DBRPlayer inputs are represented by optional runtime
attributes:
- ai_transfer_block_value_64, fresh-game default -1;
- ai_transfer_status_bit_9, fresh-game default False.
GameState/RuntimePlayer integration supplies those defaults explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from competition_startup import country_league_root_storage_order
from player_contract import (
    initial_weekly_wage,
    signing_fee_doubling_eligible,
)
from player_valuation import live_player_transfer_value
from transfer_state import ContractTerms, PlayerMovement, TransferProposal
from transfer_workflow import _complete_ordinary_cash_transfer


BIG_CLUB_FAN_BASE = 21
BIG_CLUB_BUY_CHANCE = 50
MAX_PLAYERS_BUY_MONTHLY = 3
MAX_PLAYERS_BUY_SEASON = 8

# 0x406950 / 0x4087E0.
POSITION_COVERAGE_EQUIVALENCE = (
    0, 1, 2, 3, 4, 4, 2, 3, 4, 6,
    7, 8, 9, 7, 8, 6, 0, 0, 10, 10,
)
POSITION_COVERAGE_MINIMUM = (
    0, 2, 1, 1, 4, 4, 2, 2, 4, 3,
    2, 2, 3, 2, 2, 3, 0, 0, 3, 3,
)

# 0x423340, rows = competition/category 0..4, columns = age bands
# <=18, 19-21, 22-25, 26-28, 29-31, >31. The executable truncates toward
# zero and applies the result as calendar months.
AUTONOMOUS_CONTRACT_MONTHS = (
    (7.0, 5.0, 4.0, 4.0, 3.0, 2.5),
    (4.5, 4.0, 4.0, 3.0, 2.5, 2.0),
    (3.5, 3.0, 3.0, 2.5, 2.0, 2.0),
    (3.0, 2.5, 2.5, 2.0, 2.0, 2.0),
    (2.0, 3.0, 3.0, 2.0, 2.0, 1.0),
)


@dataclass(frozen=True)
class AutonomousTransferResult:
    buyer_club_id: int
    seller_club_id: int
    player_id: int
    consideration: int
    weekly_wage: int
    contract_length_months: int
    movement: PlayerMovement


def is_weekly_ai_transfer_day(on_date: date) -> bool:
    """Return the recovered 0x40DD70 weekly phase.

    The executable tests (serial_date + 5) % 7 == 0. The recovered serial-date
    mapping puts that phase on Saturday in the 2000/01 calendar.
    """
    return on_date.weekday() == 5


def _active_club_id(player) -> int:
    loan = getattr(player, "loan_club_id", None)
    return int(player.club_id if loan is None else loan)


def _valid_manager_for_club(state, club_id: int) -> bool:
    club_id = int(club_id)
    club = state.clubs.get(club_id)
    if club is None:
        return False
    manager_id = int(getattr(club, "manager_id", -1))
    manager = state.managers.get(manager_id)
    if manager is None:
        return False
    manager_club = getattr(manager, "club_id", None)
    return manager_club is not None and int(manager_club) == club_id


def _country_transfer_gate_open(state, club) -> bool:
    gates = getattr(state, "country_transfer_window_open", None)
    if gates is None:
        # 0x4117C6 initializes every freshly constructed runtime country to 1.
        return True
    return bool(gates.get(int(club.country_id), True))


def _buy_counter(state, club_id: int) -> int:
    counters = getattr(state, "ai_transfer_buy_counter", None)
    if counters is None:
        return 0
    return int(counters.get(int(club_id), 0))


def _startup_roster_count(state, club_id: int) -> int:
    baselines = getattr(state, "ai_transfer_startup_roster_count", None)
    if baselines is None:
        return len(state.club_roster_order.get(int(club_id), ()))
    return int(
        baselines.get(
            int(club_id),
            len(state.club_roster_order.get(int(club_id), ())),
        )
    )


def _club_related_ids(club) -> tuple[int, ...]:
    return tuple(
        int(value)
        for value in (
            getattr(club, "related_club_id_0", -1),
            getattr(club, "related_club_id_1", -1),
            getattr(club, "related_club_id_2", -1),
        )
        if int(value) >= 0
    )


def club_is_big(club) -> bool:
    return int(getattr(club, "fan_base_index", -1)) > BIG_CLUB_FAN_BASE


def buyer_club_eligible(
    state,
    club_id: int,
    *,
    user_controlled_club_id: int | None = None,
) -> bool:
    """Implement the non-random 0x40DC90 / 0x403E70 buyer predicates."""
    club_id = int(club_id)
    club = state.clubs.get(club_id)
    if club is None:
        return False
    if user_controlled_club_id is not None and club_id == int(user_controlled_club_id):
        return False
    if not club_is_big(club):
        return False

    name = str(getattr(club, "name", ""))
    if name == "FREE TRANSFER" or name.startswith("!"):
        return False
    if int(getattr(club, "team_category_code", 0)) in (2, 3):
        return False
    if not _country_transfer_gate_open(state, club):
        return False
    if not _valid_manager_for_club(state, club_id):
        return False

    roster_count = len(state.club_roster_order.get(club_id, ()))
    if roster_count > 28:
        counter = _buy_counter(state, club_id)
        if counter > MAX_PLAYERS_BUY_MONTHLY or counter > MAX_PLAYERS_BUY_SEASON:
            return False
    return True


def buyer_random_gate_passes(state, club_id: int, rng) -> bool:
    """Implement the two-draw BigClubBuyChance gate in 0x40DC90."""
    first = int(rng.randbelow(BIG_CLUB_BUY_CHANCE))
    if first == 3:
        return True

    current_count = len(state.club_roster_order.get(int(club_id), ()))
    if current_count >= _startup_roster_count(state, club_id) - 2:
        return False
    return int(rng.randbelow(BIG_CLUB_BUY_CHANCE)) < 10


def _seller_threshold(state, club_id: int) -> int | None:
    club = state.clubs.get(int(club_id))
    if club is None:
        return None
    index = int(getattr(club, "fan_base_index", -1))
    rows = tuple(getattr(state, "access_fan_bases", ()))
    if not 0 <= index < len(rows):
        return None
    return int(rows[index].field_48) - 4


def seller_has_spare_roster(state, club_id: int) -> bool:
    """Implement 0x40C7D0's retained-roster test."""
    club_id = int(club_id)
    threshold = _seller_threshold(state, club_id)
    if threshold is None:
        return False
    roster_ids = tuple(state.club_roster_order.get(club_id, ()))
    if len(roster_ids) <= threshold:
        return False

    effective = len(roster_ids)
    for player_id in roster_ids:
        player = state.players.get(int(player_id))
        if player is None:
            effective -= 1
        elif (
            int(player.club_id) != club_id
            or _active_club_id(player) != club_id
            or bool(getattr(player, "ai_transfer_status_bit_9", False))
        ):
            effective -= 1
        if effective <= threshold:
            return False
    return True


def seller_club_eligible(
    state,
    club_id: int,
    *,
    user_controlled_club_id: int | None = None,
) -> bool:
    """Implement the seller-wide 0x40DBB0 predicates."""
    club_id = int(club_id)
    if user_controlled_club_id is not None and club_id == int(user_controlled_club_id):
        return False
    if not _valid_manager_for_club(state, club_id):
        return False
    threshold = _seller_threshold(state, club_id)
    if threshold is None:
        return False
    if len(state.club_roster_order.get(club_id, ())) <= threshold:
        return False
    return seller_has_spare_roster(state, club_id)


def _raw_lineup_group(state, player) -> int | None:
    position = state.positions.get(int(player.current_position))
    if position is None:
        return None
    value = int(getattr(position, "lineup_group", -1))
    if not 0 <= value < len(POSITION_COVERAGE_EQUIVALENCE):
        return None
    return value


def candidate_has_spare_position_coverage(state, player_id: int, seller_club_id: int) -> bool:
    """Implement the recovered 0x4088E0 positional spare-player gate."""
    player = state.players.get(int(player_id))
    seller_club_id = int(seller_club_id)
    if player is None:
        return False
    if int(getattr(player, "ai_transfer_block_value_64", -1)) > -1:
        return False
    if _active_club_id(player) != int(player.club_id):
        return False

    raw_group = _raw_lineup_group(state, player)
    if raw_group is None:
        return False
    normalized = POSITION_COVERAGE_EQUIVALENCE[raw_group]

    count = 0
    for other_id in state.club_roster_order.get(seller_club_id, ()):
        other = state.players.get(int(other_id))
        if other is None:
            continue
        other_group = _raw_lineup_group(state, other)
        if other_group is None:
            continue
        if POSITION_COVERAGE_EQUIVALENCE[other_group] == normalized:
            count += 1

    return count > POSITION_COVERAGE_MINIMUM[raw_group]


def _weeks_at_current_club(state, player) -> int:
    joined = getattr(player, "current_club_join_date", None)
    if joined is None or joined > state.calendar.current_date:
        return 0
    return (state.calendar.current_date - joined).days // 7


def select_seller_target(
    state,
    seller_club_id: int,
    rng,
    *,
    user_controlled_club_id: int | None = None,
):
    """Reproduce 0x40DBB0's random roster rejection-sampling selection."""
    seller_club_id = int(seller_club_id)
    if not seller_club_eligible(
        state,
        seller_club_id,
        user_controlled_club_id=user_controlled_club_id,
    ):
        return None

    roster_ids = tuple(state.club_roster_order.get(seller_club_id, ()))
    eligible = {
        int(player_id)
        for player_id in roster_ids
        if candidate_has_spare_position_coverage(state, int(player_id), seller_club_id)
        and _weeks_at_current_club(state, state.players[int(player_id)]) > 26
    }
    if not eligible:
        return None

    while True:
        player_id = int(roster_ids[int(rng.randbelow(len(roster_ids)))])
        if player_id in eligible:
            return state.players[player_id]


def _random_big_seller_id(state, buyer_club_id: int, rng) -> int | None:
    club_ids = tuple(sorted(int(club_id) for club_id in state.clubs))
    eligible_other = tuple(
        club_id
        for club_id in club_ids
        if club_id != int(buyer_club_id) and club_is_big(state.clubs[club_id])
    )
    if not club_ids or not eligible_other:
        return None

    while True:
        club_id = club_ids[int(rng.randbelow(len(club_ids)))]
        if club_id != int(buyer_club_id) and club_is_big(state.clubs[club_id]):
            return club_id


def related_club_suppression_passes(state, buyer_club_id: int, seller_club_id: int, rng) -> bool:
    """Apply both directional 0x4079A0 relationship checks and RNG(100) draws."""
    buyer_club_id = int(buyer_club_id)
    seller_club_id = int(seller_club_id)
    buyer = state.clubs[buyer_club_id]
    seller = state.clubs[seller_club_id]

    if seller_club_id in _club_related_ids(buyer):
        if int(rng.randbelow(100)) > 10:
            return False
    if buyer_club_id in _club_related_ids(seller):
        if int(rng.randbelow(100)) > 10:
            return False
    return True


def _autonomous_contract_category(state, buyer_club_id: int) -> int:
    """Return 0x4FA510's exact country League/DummyLeague root index."""
    buyer_club_id = int(buyer_club_id)
    club = state.clubs.get(buyer_club_id)
    if club is None:
        raise KeyError(f"unknown buying club {buyer_club_id}")

    competition_id = int(club.competition_id)
    competition = state.competitions.get(competition_id)
    if competition is None:
        raise RuntimeError(
            f"buying club {buyer_club_id} competition {competition_id} is not loaded"
        )

    country_region_id = int(getattr(competition, "country_region_id"))
    ordered = country_league_root_storage_order(
        tuple(state.competitions.values()),
        country_region_id,
    )
    try:
        category = next(
            index
            for index, candidate in enumerate(ordered)
            if int(candidate.id) == competition_id
        )
    except StopIteration as exc:
        raise RuntimeError(
            f"competition {competition_id} is not in country {country_region_id} "
            "League/DummyLeague root subset"
        ) from exc

    # 0x423340 contains exactly five playable rows. Canonical England maps
    # Premier League/Division 1/Division 2/Division 3/Conference to 0..4;
    # Conference 2 is the trailing DummyLeague at index 5 and is not a valid
    # autonomous buyer-league category.
    if not 0 <= category < len(AUTONOMOUS_CONTRACT_MONTHS):
        raise RuntimeError(
            f"competition {competition_id} contract category {category} is "
            "outside the 0x423340 playable table"
        )
    return category


def autonomous_contract_length_months(state, player_id: int, buyer_club_id: int) -> int:
    player = state.players[int(player_id)]
    age = player.age(state.calendar.current_date)
    if age is None:
        raise ValueError(f"player {player_id} has no usable date of birth")
    if age <= 18:
        band = 0
    elif age <= 21:
        band = 1
    elif age <= 25:
        band = 2
    elif age <= 28:
        band = 3
    elif age <= 31:
        band = 4
    else:
        band = 5
    category = _autonomous_contract_category(state, int(buyer_club_id))
    return int(AUTONOMOUS_CONTRACT_MONTHS[category][band])


def _autonomous_consideration(state, player_id: int, rng) -> int:
    player = state.players[int(player_id)]
    if int(player.club_id) < 0:
        return 1
    if signing_fee_doubling_eligible(state, int(player_id)):
        return 2

    value = float(live_player_transfer_value(state, int(player_id)))
    if value < 500_000.0:
        random_bound = int(0.30 * value)
        random_add = 0 if random_bound <= 0 else int(rng.randbelow(random_bound))
        return int(0.98 * value + random_add)

    random_bound = int(0.20 * value)
    random_add = 0 if random_bound <= 0 else int(rng.randbelow(random_bound))
    return int(1.10 * value + random_add)


def _autonomous_weekly_wage(state, player_id: int, buyer_club_id: int, rng) -> int:
    player = state.players[int(player_id)]
    club = state.clubs[int(buyer_club_id)]
    country = state.countries.get(int(club.country_id))
    if country is None:
        raise ValueError(f"buying club {buyer_club_id} has no resolved country")
    return int(
        initial_weekly_wage(
            player.current_raw,
            player.positions,
            state.access_skill_financial_values,
            int(getattr(country, "financial_multiplier_percent", 100)),
            rng,
        )
    )


def complete_autonomous_acquisition(state, player_id: int, buyer_club_id: int, rng):
    """Apply 0x41EFB0's direct acquisition guard, terms, and club switch."""
    player_id = int(player_id)
    buyer_club_id = int(buyer_club_id)
    player = state.players[player_id]
    seller_club_id = int(player.club_id)

    if seller_club_id == buyer_club_id:
        return None
    if player_id in state.transfers.deals:
        return None
    if any(int(key[0]) == player_id for key in state.transfers.proposals):
        return None
    if bool(player.signed_for_other_club):
        return None
    if _weeks_at_current_club(state, player) < 12:
        return None

    consideration = _autonomous_consideration(state, player_id, rng)
    weekly_wage = _autonomous_weekly_wage(
        state, player_id, buyer_club_id, rng
    )
    months = autonomous_contract_length_months(
        state, player_id, buyer_club_id
    )
    proposal = TransferProposal(
        target_player_id=player_id,
        buying_club_id=buyer_club_id,
        cash_fee=int(consideration),
        contract_terms=ContractTerms(
            weekly_wage=int(weekly_wage),
            contract_length_months=int(months),
        ),
    )
    # 0x41EFB0 funnels the successful autonomous acquisition through
    # 0x422B80 -> 0x422F40 -> 0x422F70, so it reaches the same final
    # signed-contract morale RNG(2) as an ordinary human transfer.
    movement = _complete_ordinary_cash_transfer(state, proposal, rng)

    counters = getattr(state, "ai_transfer_buy_counter", None)
    if counters is not None:
        counters[buyer_club_id] = int(counters.get(buyer_club_id, 0)) + 1

    return AutonomousTransferResult(
        buyer_club_id=buyer_club_id,
        seller_club_id=seller_club_id,
        player_id=player_id,
        consideration=int(consideration),
        weekly_wage=int(weekly_wage),
        contract_length_months=int(months),
        movement=movement,
    )


def attempt_autonomous_acquisition(
    state,
    buyer_club_id: int,
    rng,
    *,
    user_controlled_club_id: int | None = None,
):
    """Run one 0x40DC90 buyer attempt."""
    buyer_club_id = int(buyer_club_id)
    if not buyer_club_eligible(
        state,
        buyer_club_id,
        user_controlled_club_id=user_controlled_club_id,
    ):
        return None
    if not buyer_random_gate_passes(state, buyer_club_id, rng):
        return None

    seller_club_id = _random_big_seller_id(state, buyer_club_id, rng)
    if seller_club_id is None:
        return None
    if not related_club_suppression_passes(
        state, buyer_club_id, seller_club_id, rng
    ):
        return None

    target = select_seller_target(
        state,
        seller_club_id,
        rng,
        user_controlled_club_id=user_controlled_club_id,
    )
    if target is None:
        return None
    return complete_autonomous_acquisition(
        state,
        int(target.index),
        buyer_club_id,
        rng,
    )


def run_weekly_ai_acquisitions(
    state,
    rng,
    *,
    user_controlled_club_id: int | None = None,
) -> tuple[AutonomousTransferResult, ...]:
    """Run the recovered Saturday 0x40DD70 club-table pass."""
    if not is_weekly_ai_transfer_day(state.calendar.current_date):
        return ()

    # Lightweight/synthetic game states used by earlier gates may not carry the
    # source-backed transfer tables. Preserve those callers without pretending
    # that an acquisition was evaluated.
    if (
        not getattr(state, "clubs", None)
        or not getattr(state, "managers", None)
        or not getattr(state, "positions", None)
        or not getattr(state, "access_fan_bases", None)
        or not getattr(state, "access_skill_financial_values", None)
    ):
        return ()

    if user_controlled_club_id is None:
        user_controlled_club_id = getattr(state, "user_controlled_club_id", None)

    results = []
    for club_id in sorted(int(value) for value in state.clubs):
        result = attempt_autonomous_acquisition(
            state,
            club_id,
            rng,
            user_controlled_club_id=user_controlled_club_id,
        )
        if result is not None:
            results.append(result)
    return tuple(results)

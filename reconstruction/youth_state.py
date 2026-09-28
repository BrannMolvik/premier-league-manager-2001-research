"""Source-backed Gate-11 human youth workflow.

This module materializes the separate DBRUser youth list reached by
0x413980 -> 0x61DF90. It deliberately keeps the record's still-unnamed scalar
fields neutral and does not treat youth-list membership as first-team roster
membership.

Promotion and release are modeled from 0x61E3D0 / 0x417700 and 0x4177C0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Iterable

from player_contract import contract_expiry_from_month_span
from startup_rng import (
    generated_name_source_eligible,
    startup_spare_club_id,
    startup_youth_target_count,
)


YOUTH_LIST_CAP = 20
YOUTH_CANDIDATE_CAP = 0x200
YOUTH_INITIAL_AGE = 15
YOUTH_FINAL_AGE = 17
YOUTH_FINAL_CONTRACT_MONTHS = 12

DEFAULT_TRAINING_METHOD = 5
DEFAULT_TRAINING_COUNTDOWN = 8


@dataclass
class YouthTrainingState:
    """Materialized subset of the 0xA4 object initialized by 0x4EAB80.

    These are the same already-recovered training fields represented on
    RuntimePlayer. The remaining timed-effect/date fields are intentionally
    omitted until a Gate-11 consumer requires them.
    """

    method_id: int = DEFAULT_TRAINING_METHOD
    countdown: int = DEFAULT_TRAINING_COUNTDOWN
    active_count: int = 0
    modifiers: list[int] = field(default_factory=lambda: [0] * 17)
    skill_states: list[int] = field(default_factory=lambda: [1] * 17)
    method_results: list[int] = field(default_factory=lambda: [0] * 7)

    def copy_to_player(self, player) -> None:
        player.training_method_id = int(self.method_id)
        player.training_countdown = int(self.countdown)
        player.training_active_count = int(self.active_count)
        player.training_modifiers[:] = [int(value) & 0xFF for value in self.modifiers]
        player.training_skill_states[:] = [int(value) for value in self.skill_states]
        player.training_method_results[:] = [int(value) for value in self.method_results]


@dataclass
class YouthRecord:
    """Clean-room representation of one original 0x18-byte youth record."""

    player_id: int
    # Modern bookkeeping for the original active/current-club (+0x72) roster
    # that still owns the player until 0x61E3D0 promotion or 0x4177C0 release.
    source_roster_club_id: int
    training: YouthTrainingState = field(default_factory=YouthTrainingState)
    field_08: int = 1
    field_0c: int = 1
    field_10: int = 1
    status_14: bool = False


@dataclass
class YouthTeamState:
    """The separate DBRUser+0x6BC fixed-capacity youth list."""

    records: list[YouthRecord] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.records) > YOUTH_LIST_CAP:
            raise ValueError("FM2001 youth list contains at most 20 records")

    def clear(self) -> None:
        self.records.clear()

    def player_ids(self) -> tuple[int, ...]:
        return tuple(int(record.player_id) for record in self.records)

    def find(self, player_id: int) -> YouthRecord | None:
        player_id = int(player_id)
        for record in self.records:
            if int(record.player_id) == player_id:
                return record
        return None

    def append(self, record: YouthRecord) -> bool:
        if len(self.records) >= YOUTH_LIST_CAP:
            return False
        if self.find(record.player_id) is not None:
            raise ValueError(f"player {int(record.player_id)} is already in youth list")
        self.records.append(record)
        return True

    def remove_player(self, player_id: int) -> YouthRecord | None:
        """Mirror 0x61E170 + 0x61E100 compaction."""
        player_id = int(player_id)
        for index, record in enumerate(self.records):
            if int(record.player_id) == player_id:
                return self.records.pop(index)
        return None

    def set_status_14(self, player_id: int) -> bool:
        """Mirror 0x61E1B0 without inventing the byte's UI label."""
        record = self.find(player_id)
        if record is None:
            return False
        record.status_14 = True
        return True

    def status_14_for(self, player_id: int) -> bool:
        """Mirror 0x61E1F0."""
        record = self.find(player_id)
        return bool(record is not None and record.status_14)


def _birth_date_for_age(player, on_date: date, target_age: int) -> date:
    """Apply the 0x41E510/0x61DD30 year rewrite while preserving month/day."""
    if player.date_of_birth is None:
        raise ValueError(f"player {int(player.index)} has no date of birth")
    current_age = player.age(on_date)
    if current_age is None:
        raise ValueError(f"player {int(player.index)} has no usable age")
    target_year = int(player.date_of_birth.year) + int(current_age) - int(target_age)
    try:
        return player.date_of_birth.replace(year=target_year)
    except ValueError:
        # OLE/EA date conversion normalizes invalid leap-day year changes.
        # Preserve month/day when valid and use the final valid February day
        # for the only Gregorian replacement edge case.
        if player.date_of_birth.month == 2 and player.date_of_birth.day == 29:
            return player.date_of_birth.replace(year=target_year, day=28)
        raise


def _reset_known_generated_youth_status(player) -> None:
    """Materialize the source-backed status portion of 0x4185B0.

    0x4185B0 clears bits 0,1,7,8,9,11 and sets bit 3. It also resets the
    signed-for-other-club secondary bit and match-selection state. Other
    still-neutral DBRPlayer fields remain outside this slice.
    """

    player.injured = False
    player.suspended = False
    player.out_of_contract = False
    player.transfer_listed = False
    player.non_eu = False
    player.signed_for_other_club = False
    player.status_bit_3 = True
    player.match_active = False
    player.match_substitute_available = False
    player.previous_club_id_74 = None
    player.reset_match_position()


def _generated_name_source_table(players: Iterable[object]) -> dict[int, tuple[int, ...]]:
    """Snapshot 0x411A10's nationality pointer vectors before youth mutation."""
    result: dict[int, list[int]] = {}
    for player in players:
        if not generated_name_source_eligible(player.first_name, player.surname):
            continue
        result.setdefault(int(player.nationality_id), []).append(int(player.index))
    return {key: tuple(values) for key, values in result.items()}


def _country_nationality_id(country) -> int:
    value = int(country.nationality_id)
    return 26 if value in (-1, 0xFFFFFFFF) else value


def _select_name_source(
    player_order: tuple[object, ...],
    players_by_id: dict[int, object],
    source_ids_by_nationality: dict[int, tuple[int, ...]],
    nationality_id: int,
    rng,
):
    source_ids = source_ids_by_nationality.get(int(nationality_id), ())
    if len(source_ids) > 10:
        source_id = int(source_ids[int(rng.randbelow(len(source_ids)))])
        return players_by_id[source_id]

    selected_index = int(rng.randbelow(len(player_order)))
    return player_order[selected_index]


def _spare_candidate_ids(state, spare_club_id: int) -> list[int]:
    """Build one 0x61DF90 512-WORD local candidate buffer."""
    result: list[int] = []
    for player in state.players.values():
        if int(player.club_id) != int(spare_club_id):
            continue
        if bool(player.status_bit_3):
            continue
        result.append(int(player.index))
        if len(result) >= YOUTH_CANDIDATE_CAP:
            break
    return result


def generate_fresh_user_youth(
    state,
    *,
    user_club_id: int,
    option_mode: int | None,
    rng,
) -> YouthTeamState:
    """Materialize one fresh 0x61DF90 -> 0x61DD30 human youth pass.

    The exact RNG order is option-size draw (when applicable), then for every
    generated player: candidate draw, first-name source draw, surname source
    draw. Candidate removal uses swap-with-last.

    The selected global RuntimePlayer is rewritten into the final immediately
    post-0x61DD30 state (age 17 and 12 months remaining) but remains in the
    original !Spare roster container until promotion/release.
    """

    user_club_id = int(user_club_id)
    if user_club_id not in state.clubs:
        raise KeyError(f"unknown user club {user_club_id}")
    if not hasattr(rng, "randbelow"):
        raise TypeError("rng must provide randbelow(bound)")

    club_values = tuple(state.clubs.values())
    spare_club_id = int(startup_spare_club_id(club_values))
    user_club = state.clubs[user_club_id]
    country_id = int(user_club.country_id)
    country = state.countries.get(country_id)
    if country is None:
        raise ValueError(f"user club {user_club_id} has no resolved country")

    player_order = tuple(state.players.values())
    players_by_id = {int(player.index): player for player in player_order}
    source_ids_by_nationality = _generated_name_source_table(player_order)
    nationality_id = _country_nationality_id(country)

    candidates = _spare_candidate_ids(state, spare_club_id)
    youth = YouthTeamState()
    target_count = int(startup_youth_target_count(option_mode, rng))
    draw_count = min(target_count, len(candidates), YOUTH_LIST_CAP)

    for _ in range(draw_count):
        selected_index = int(rng.randbelow(len(candidates)))
        player_id = int(candidates[selected_index])
        candidates[selected_index] = candidates[-1]
        candidates.pop()

        first_source = _select_name_source(
            player_order,
            players_by_id,
            source_ids_by_nationality,
            nationality_id,
            rng,
        )
        surname_source = _select_name_source(
            player_order,
            players_by_id,
            source_ids_by_nationality,
            nationality_id,
            rng,
        )

        player = players_by_id[player_id]
        player.date_of_birth = _birth_date_for_age(player, state.calendar.current_date, YOUTH_FINAL_AGE)
        player.shirt_number = 0
        player.nationality_id = country_id
        player.first_name = str(first_source.first_name)
        player.surname = str(surname_source.surname)
        _reset_known_generated_youth_status(player)

        # 0x41E510 writes registered club +0x10 but does not add a first-team
        # roster entry. The existing !Spare roster container therefore remains
        # the source roster until 0x61E3D0/0x4177C0.
        player.club_id = user_club_id
        player.contract_expiry_date = contract_expiry_from_month_span(
            state.calendar.current_date,
            YOUTH_FINAL_CONTRACT_MONTHS,
        )

        youth.append(
            YouthRecord(
                player_id=player_id,
                source_roster_club_id=spare_club_id,
            )
        )

    return youth


def _next_june_30(on_date: date) -> date:
    """Return the common 0x61DE40 player+0x154 date."""
    target_year = int(on_date.year) if int(on_date.month) < 7 else int(on_date.year) + 1
    return date(target_year, 6, 30)


def initialize_user_youth_for_club_activation(
    state,
    youth: YouthTeamState,
    *,
    user_club_id: int,
    option_mode: int | None,
    rng,
) -> YouthTeamState:
    """Materialize the full 0x61DE40 pending-club youth initializer.

    Clearing the youth records deliberately leaves the old generated players'
    status-bit-3 mutations intact. The first 0x61DF90 cohort is then
    post-processed to age 17 by 0x61DD30. The second cohort remains at the
    age-15 state produced by 0x41E510. Finally all records receive the same
    next-30-June player+0x154 date and freshly reset training state.
    """

    youth.clear()

    first = generate_fresh_user_youth(
        state,
        user_club_id=int(user_club_id),
        option_mode=option_mode,
        rng=rng,
    )
    second = generate_fresh_user_youth(
        state,
        user_club_id=int(user_club_id),
        option_mode=option_mode,
        rng=rng,
    )

    # generate_fresh_user_youth materializes the startup path through 0x61DD30,
    # so undo only that post-process for the second 0x61DE40 cohort. The
    # selection/name/status work remains exactly the shared 0x61DF90 behavior.
    for record in second.records:
        player = state.players[int(record.player_id)]
        player.date_of_birth = _birth_date_for_age(
            player,
            state.calendar.current_date,
            YOUTH_INITIAL_AGE,
        )

    combined = [*first.records, *second.records]
    if len(combined) > YOUTH_LIST_CAP:
        combined = combined[:YOUTH_LIST_CAP]

    common_date = _next_june_30(state.calendar.current_date)
    for record in combined:
        player = state.players[int(record.player_id)]
        player.contract_expiry_date = common_date
        record.training = YouthTrainingState()

    youth.records[:] = combined
    return youth


def promote_youth_player(
    state,
    youth: YouthTeamState,
    *,
    player_id: int,
    target_club_id: int,
    weekly_wage: float,
    contract_months: int,
):
    """Reproduce the mapped state effects of 0x61E3D0 -> 0x417700."""

    player_id = int(player_id)
    target_club_id = int(target_club_id)
    record = youth.find(player_id)
    if record is None:
        raise ValueError(f"player {player_id} is not in the youth list")
    player = state.players[player_id]
    if target_club_id not in state.clubs:
        raise KeyError(f"unknown target club {target_club_id}")

    # 0x61E3D0 retains the youth training subobject, removes the record, then
    # performs roster removal/addition before 0x417700 copies training state.
    removed = youth.remove_player(player_id)
    assert removed is not None

    source_roster = state.club_roster_order.setdefault(
        int(record.source_roster_club_id), []
    )
    if player_id in source_roster:
        source_roster.remove(player_id)

    target_roster = state.club_roster_order.setdefault(target_club_id, [])
    if player_id not in target_roster:
        target_roster.append(player_id)

    player.club_id = target_club_id
    player.loan_club_id = None
    player.previous_club_id_74 = None
    player.injured = False
    player.suspended = False
    player.selection_excluded = False
    player.status_bit_3 = False
    player.non_eu = False
    player.transfer_listed = False
    player.out_of_contract = False
    player.loan_listed = False
    player.signed_for_other_club = False
    player.match_active = False
    player.match_substitute_available = False
    player.eu_status_code = 0
    player.weekly_wage = int(float(weekly_wage))
    player.contract_expiry_date = contract_expiry_from_month_span(
        state.calendar.current_date,
        int(contract_months),
    )
    player.reset_match_position()
    record.training.copy_to_player(player)
    return player


def release_youth_player(
    state,
    youth: YouthTeamState,
    *,
    player_id: int,
    user_club_id: int,
):
    """Reproduce youth-list removal plus 0x4177C0 free-player transition."""

    player_id = int(player_id)
    record = youth.remove_player(player_id)
    if record is None:
        return False

    player = state.players[player_id]
    source_roster = state.club_roster_order.setdefault(
        int(record.source_roster_club_id), []
    )
    if player_id in source_roster:
        source_roster.remove(player_id)

    player.previous_club_id_74 = int(user_club_id)
    player.club_id = -1
    player.loan_club_id = None
    player.injured = False
    player.suspended = False
    player.selection_excluded = False
    player.status_bit_3 = False
    player.non_eu = False
    player.transfer_listed = False
    player.out_of_contract = True
    player.loan_listed = False
    player.signed_for_other_club = False
    player.match_active = False
    player.match_substitute_available = False
    return True

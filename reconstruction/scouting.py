"""Source-backed FM2001 scouting search ordering primitives.

This module intentionally keeps unresolved PScouting2K control semantics neutral.
It implements only mechanics proven from FOOTBAL.EXE 0x4AF7F0 and the
0x4AE970/0x4AEAE0 result-vector shuffles.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cmp_to_key
from typing import Callable, Iterable, Sequence, TypeVar

from match_role_rating import best_preferred_role_rating
from match_schedule import MsvcCrtRng


T = TypeVar("T")

SCOUT_ONE_AGE_BIAS = 4
MAX_NUM_USED1 = 80
MAX_NUM_USED2 = 50
MAX_NUM_FOUND = 20


@dataclass(frozen=True)
class ScoutingReseedState:
    """Exact neutral panel fields consumed by PScouting2K::0x4AF7F0."""

    status_control_7738: int = 0
    status_control_76f8: int = 0
    status_control_76b8: int = 0
    value_high_64d0: float = 0.0
    value_low_64c8: float = 0.0
    field_64e4: int = 0
    age_high_64dc: int = 0
    field_64e0: int = 0
    age_low_64d8: int = 0
    class_selector_64c0: int = 0

    def exact_seed(self, caller_argument: int) -> int:
        """Return the 32-bit XOR passed directly to CRT srand at 0x66950F.

        Original helper 0x668350 converts the two doubles with x87 truncation
        toward zero. Python int(float) has the same truncation direction.
        """

        terms = (
            int(self.status_control_7738) & 0xFF,
            int(self.status_control_76f8) & 0xFF,
            int(self.status_control_76b8) & 0xFF,
            int(float(self.value_high_64d0)),
            int(float(self.value_low_64c8)),
            int(self.field_64e4),
            int(self.age_high_64dc),
            int(self.field_64e0),
            int(self.age_low_64d8),
            int(self.class_selector_64c0),
            int(caller_argument),
        )
        seed = 0
        for value in terms:
            seed ^= value & 0xFFFFFFFF
        return seed & 0xFFFFFFFF


def scouting_shuffle(
    items: Iterable[T],
    panel_state: ScoutingReseedState,
    *,
    caller_argument: int,
) -> tuple[T, ...]:
    """Reproduce the PScouting2K reseed followed by descending Fisher-Yates."""

    shuffled = list(items)
    rng = MsvcCrtRng(panel_state.exact_seed(caller_argument))
    for remaining in range(len(shuffled), 1, -1):
        selected = rng.randbelow(remaining)
        last = remaining - 1
        shuffled[selected], shuffled[last] = shuffled[last], shuffled[selected]
    return tuple(shuffled)


def primary_scouting_results(
    candidates: Iterable[T],
    panel_state: ScoutingReseedState,
) -> tuple[T, ...]:
    """Primary 0x4AE970 result ordering. The caller argument is literal -1."""

    return scouting_shuffle(candidates, panel_state, caller_argument=-1)


def secondary_scouting_results(
    ranked_candidates: Sequence[T],
    panel_state: ScoutingReseedState,
    *,
    caller_argument: int,
    max_num_used2: int = MAX_NUM_USED2,
    max_num_found: int = MAX_NUM_FOUND,
) -> tuple[T, ...]:
    """Apply the proven 0x4AEAE0 shortlist cap, reseed/shuffle and final cap.

    The input must already be in the exact score/name order produced by the
    original 0x4AEE00 comparator. Score construction remains a separate
    source-recovery step.
    """

    used = tuple(ranked_candidates[: max(0, int(max_num_used2))])
    shuffled = scouting_shuffle(
        used,
        panel_state,
        caller_argument=caller_argument,
    )
    return shuffled[: max(0, int(max_num_found))]


SCOUTING_SCORE_MODE_AGE_BIAS = 5
SCOUTING_SCORE_MODE_SKILL_BIAS = 15
SCOUTING_SCORE_MODE_PLAIN = 16


def scouting_country_context_passes(
    selector_mode: int,
    *,
    candidate_country_id: int,
    candidate_european_index: int,
    active_club_country_id: int,
) -> bool:
    """Reproduce panel+0x64E0 country-context gating from 0x4AE680.

    Mode 0 requires the active club's country. Mode 1 requires a different
    country whose runtime DBRCountry+0x18 value is nonzero. Any other nonzero
    mode requires a different country whose +0x18 value is zero.
    """

    selector_mode = int(selector_mode)
    same_country = int(candidate_country_id) == int(active_club_country_id)
    if selector_mode == 0:
        return same_country
    if same_country:
        return False
    if selector_mode == 1:
        return int(candidate_european_index) != 0
    return int(candidate_european_index) == 0


def scouting_preferred_position_passes(
    preferred_positions: Sequence[int],
    selected_position_id: int | None,
) -> bool:
    """Reproduce the optional 0x4EA410 three-position membership gate."""

    if selected_position_id is None:
        return True
    return int(selected_position_id) in tuple(
        int(value) for value in tuple(preferred_positions)[:3]
    )


def scouting_loan_list_user_match(
    *,
    transfer_listed: bool,
    non_eu: bool,
    registered_club_competition_id: int,
    active_club_competition_id: int,
) -> bool:
    """Reproduce 0x41E450 after the scouting caller has proven bit 12.

    On this call site the player's loan-list bit is already set, so the
    function's separate bit-4/not-bit-12 rejection is unreachable.
    """

    if int(registered_club_competition_id) == int(active_club_competition_id):
        return False
    if bool(transfer_listed):
        return True
    return not bool(non_eu)


def scouting_rank_score(
    current_raw: Sequence[int],
    preferred_positions: Sequence[int],
    *,
    age: int,
    mode: int,
    age_bias: int = SCOUT_ONE_AGE_BIAS,
) -> int | None:
    """Reproduce the score appended by PScouting2K::0x4AEAE0.

    Only panel mode return codes 5, 15 and 16 append a scored record.
    The mode-15 boosts are byte writes in the original, so values above 255
    intentionally wrap before the temporary rating calculation.
    """

    mode = int(mode)
    if mode not in (
        SCOUTING_SCORE_MODE_AGE_BIAS,
        SCOUTING_SCORE_MODE_SKILL_BIAS,
        SCOUTING_SCORE_MODE_PLAIN,
    ):
        return None

    if len(current_raw) != 17:
        raise ValueError("current_raw must contain exactly 17 raw skill bytes")
    skills = [int(value) for value in current_raw]
    if any(not 0 <= value <= 255 for value in skills):
        raise ValueError("current_raw values must be in 0..255")

    if mode == SCOUTING_SCORE_MODE_SKILL_BIAS:
        for slot, percent in ((1, 120), (2, 130), (3, 120), (9, 120)):
            skills[slot] = (skills[slot] * percent // 100) & 0xFF

    score = best_preferred_role_rating(skills, preferred_positions)

    if mode == SCOUTING_SCORE_MODE_AGE_BIAS:
        age_term = max(0, (int(age) - 31) * int(age_bias))
        score = score * (60 + age_term) // 100

    return int(score)


SCOUTING_SORT_MODE_NAME = 0
SCOUTING_SORT_MODE_AGE = 1
SCOUTING_SORT_MODE_HISTORY_AVERAGE = 2
SCOUTING_SORT_MODE_POSITION_LABEL = 3
SCOUTING_SORT_MODE_CLUB_NAME = 4
SCOUTING_SORT_MODE_VALUE = 5


@dataclass(frozen=True)
class ScoutingSortValues:
    """Neutral values consumed by the six exact 0x4AEEA0 comparators."""

    name_primary: str
    name_secondary: str
    age: int
    history_average: float
    position_label: str
    club_name: str
    valuation: float


def _cmp_scalar(left, right) -> int:
    return (left > right) - (left < right)


def scouting_result_compare(
    left: ScoutingSortValues,
    right: ScoutingSortValues,
    mode: int,
) -> int:
    """Reproduce the sign/order of the six 0x4AEEA0 qsort comparators.

    The neutral name fields correspond, in order, to the strings reached through
    DBRPlayer +0x0C and +0x08. history_average is DBRPlayer::0x41FB60.
    """

    mode = int(mode)
    name_cmp = _cmp_scalar(str(left.name_primary), str(right.name_primary))
    if name_cmp == 0:
        name_cmp = _cmp_scalar(str(left.name_secondary), str(right.name_secondary))

    if mode == SCOUTING_SORT_MODE_NAME:
        return name_cmp
    if mode == SCOUTING_SORT_MODE_AGE:
        primary = _cmp_scalar(int(left.age), int(right.age))
    elif mode == SCOUTING_SORT_MODE_HISTORY_AVERAGE:
        primary = _cmp_scalar(float(right.history_average), float(left.history_average))
    elif mode == SCOUTING_SORT_MODE_POSITION_LABEL:
        primary = _cmp_scalar(str(right.position_label), str(left.position_label))
    elif mode == SCOUTING_SORT_MODE_CLUB_NAME:
        primary = _cmp_scalar(str(left.club_name), str(right.club_name))
    elif mode == SCOUTING_SORT_MODE_VALUE:
        primary = _cmp_scalar(float(right.valuation), float(left.valuation))
    else:
        raise ValueError("scouting sort mode must be in 0..5")

    return primary if primary != 0 else name_cmp


def sort_scouting_results(
    items: Iterable[T],
    mode: int,
    values: Callable[[T], ScoutingSortValues],
) -> tuple[T, ...]:
    """Sort result items with the exact 0x4AEEA0 comparator selected by mode."""

    def compare_items(left: T, right: T) -> int:
        return scouting_result_compare(values(left), values(right), mode)

    return tuple(sorted(items, key=cmp_to_key(compare_items)))


@dataclass(frozen=True)
class ScoutingRankValues:
    """Runtime inputs consumed by the three exact 0x4AEAE0 score modes."""

    current_raw: Sequence[int]
    preferred_positions: Sequence[int]
    age: int


def run_scouting_search(
    candidates: Iterable[T],
    panel_state: ScoutingReseedState,
    *,
    candidate_predicate: Callable[[T], bool],
    sort_mode: int,
    sort_values: Callable[[T], ScoutingSortValues],
    secondary_score_mode: int | None = None,
    secondary_caller_argument: int = 0,
    rank_values: Callable[[T], ScoutingRankValues] | None = None,
) -> tuple[T, ...]:
    """Compose the recovered UI-independent PScouting2K result pipeline.

    candidate_predicate represents the already-instruction-mapped 0x4AE680
    first-stage predicate. It remains explicit because several panel controls
    are not yet safely named in the clean-room runtime.

    When secondary_score_mode is supplied, this reproduces the optional
    0x4AEAE0 stage before the final 0x4AEEA0 result sort.
    """

    filtered = tuple(item for item in candidates if candidate_predicate(item))
    result = primary_scouting_results(filtered, panel_state)

    if secondary_score_mode is not None:
        if rank_values is None:
            raise ValueError(
                "rank_values is required when secondary_score_mode is enabled"
            )

        scored: list[tuple[T, int]] = []
        for item in result:
            values = rank_values(item)
            score = scouting_rank_score(
                values.current_raw,
                values.preferred_positions,
                age=values.age,
                mode=int(secondary_score_mode),
            )
            if score is not None:
                scored.append((item, int(score)))

        def compare_scored(left: tuple[T, int], right: tuple[T, int]) -> int:
            score_cmp = _cmp_scalar(int(right[1]), int(left[1]))
            if score_cmp != 0:
                return score_cmp
            return scouting_result_compare(
                sort_values(left[0]),
                sort_values(right[0]),
                SCOUTING_SORT_MODE_NAME,
            )

        scored.sort(key=cmp_to_key(compare_scored))
        result = secondary_scouting_results(
            tuple(item for item, _score in scored),
            panel_state,
            caller_argument=int(secondary_caller_argument),
        )

    return sort_scouting_results(result, int(sort_mode), sort_values)


SCOUTING_SPECIAL_AGE_MODE = 15
SCOUTING_CLASS_BY_SELECTOR = (3, 0, 1, 2)


@dataclass(frozen=True)
class ScoutingFilterControls:
    """Checked-state inputs for the three final 0x4AE680 status controls."""

    transfer_listed: bool = False
    status_bit_7: bool = False
    loan_listed: bool = False


@dataclass(frozen=True)
class ScoutingFilterValues:
    """Candidate-specific values consumed by the mapped 0x4AE680 gates."""

    age: int
    valuation: float
    player_class: int
    transfer_listed: bool = False
    status_bit_7: bool = False
    loan_listed: bool = False
    loan_list_user_match: bool = False
    team_selector_passes: bool = True
    optional_position_passes: bool = True
    threshold_passes: bool = True


def scouting_first_stage_passes(
    panel_state: ScoutingReseedState,
    values: ScoutingFilterValues,
    *,
    page_mode: int,
    status_controls: ScoutingFilterControls = ScoutingFilterControls(),
) -> bool:
    """Reproduce the source-backed portion of PScouting2K::0x4AE680.

    Registered/current controlled-club exclusion is performed by the caller
    because it depends on the active DBRUser. The still-neutral team selector,
    optional-position list and global threshold gates are represented by exact
    booleans rather than assigned unsupported UI labels.
    """

    if not bool(values.team_selector_passes):
        return False

    age = int(values.age)
    low_age = int(panel_state.age_low_64d8)
    high_age = int(panel_state.age_high_64dc)
    if int(page_mode) == SCOUTING_SPECIAL_AGE_MODE:
        if age < 15 or age < low_age or age > 18 or age > high_age:
            return False
    elif age < low_age or age > high_age:
        return False

    valuation = float(values.valuation)
    if valuation < float(panel_state.value_low_64c8):
        return False
    if valuation > float(panel_state.value_high_64d0):
        return False

    selector = int(panel_state.class_selector_64c0)
    # 0x4AE7FE uses an unsigned "ja 0x4AE831": selector values outside 0..3
    # bypass the four-way class check and continue to the later gates.
    if 0 <= selector < len(SCOUTING_CLASS_BY_SELECTOR):
        if int(values.player_class) != int(SCOUTING_CLASS_BY_SELECTOR[selector]):
            return False

    if not bool(values.optional_position_passes):
        return False
    if not bool(values.threshold_passes):
        return False

    controls = status_controls
    if not (
        bool(controls.transfer_listed)
        or bool(controls.status_bit_7)
        or bool(controls.loan_listed)
    ):
        return True

    if bool(controls.transfer_listed) and bool(values.transfer_listed):
        return True
    if bool(controls.status_bit_7) and bool(values.status_bit_7):
        return True
    if (
        bool(controls.loan_listed)
        and bool(values.loan_listed)
        and bool(values.loan_list_user_match)
    ):
        return True
    return False

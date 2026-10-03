"""Source-closed MatchCalculator histories that feed FastView PlayerProxy.

Fresh canonical-executable tracing (Recovery 211) proves that PlayerProxy does
not display PreparedMatchPlayer.condition or form_state directly.

FastViewPanel calls:
- 0x632FC0 -> 0x6308B0 for EventPlayerUpdateForm;
- 0x633000 -> 0x630910 for EventPlayerUpdateEnergy.

Both are backed by 24 five-minute samples per player. The Condition history is
seeded from DBRPlayer +0x77; the adjacent match-form history is maintained in
the source 1..10 display domain. Persistent DBRPlayer form_state (+0x192,
0..4) is merely one input to the match-form-history writer and is not the
displayed value.

The energy getter consumes one RNG(6) draw every time it is evaluated. This
module therefore requires that roll explicitly rather than importing or
advancing gameplay RNG.
"""
from __future__ import annotations

from dataclasses import dataclass


SOURCE_PLAYER_PROXY_UPDATE_VA = 0x5247A0
SOURCE_FASTVIEW_PLAYER_LOOP_VA = 0x521C9C

SOURCE_FORM_WRAPPER_VA = 0x632FC0
SOURCE_FORM_HISTORY_GETTER_VA = 0x6308B0
SOURCE_ENERGY_WRAPPER_VA = 0x633000
SOURCE_ENERGY_DERIVER_VA = 0x630910

SOURCE_CONDITION_HISTORY_GETTER_VA = 0x630EF0
SOURCE_HISTORY_WRITER_VA = 0x6309D0
SOURCE_FORM_TRAJECTORY_LOOP_VA = 0x630CEC
SOURCE_FORM_TRAJECTORY_RNG_VA = 0x630D46
SOURCE_SEGMENT_HISTORY_UPDATE_VA = 0x62B3F0
SOURCE_PARTICIPANT_SIDE0_CONDITION_SEED_VA = 0x62ACFF
SOURCE_PARTICIPANT_SIDE1_CONDITION_SEED_VA = 0x62AD65
SOURCE_PARTICIPANT_STARTER_FORM_SEED_SIDE0_VA = 0x62ACED
SOURCE_PARTICIPANT_STARTER_FORM_SEED_SIDE1_VA = 0x62AD53
SOURCE_DBRPLAYER_CONDITION_OFFSET = 0x77
SOURCE_DBRPLAYER_FORM_STATE_OFFSET = 0x192

SOURCE_PLAYER_HISTORY_STRIDE = 0x4C
SOURCE_SIDE0_CONDITION_HISTORY_OFFSET = 0x4C
SOURCE_SIDE0_FORM_HISTORY_OFFSET = 0x64
SOURCE_SIDE1_CONDITION_HISTORY_OFFSET = 0x5FC
SOURCE_SIDE1_FORM_HISTORY_OFFSET = 0x614

SOURCE_HISTORY_SAMPLE_COUNT = 24
SOURCE_HISTORY_TICK_CAP = 0x77
SOURCE_HISTORY_TICK_DIVISOR = 5
SOURCE_MATCH_FORM_MIN = 1
SOURCE_MATCH_FORM_MAX = 10
SOURCE_MATCH_FORM_INITIAL = 5
SOURCE_MATCH_FORM_TARGET_MIN = 4
SOURCE_MATCH_FORM_TARGET_MAX = 10
SOURCE_MATCH_FORM_RNG_BOUND = 2

SOURCE_ENERGY_FORM_TREND_STEP = 4
SOURCE_ENERGY_RNG_BOUND = 6
SOURCE_ENERGY_RNG_CENTER = 3
SOURCE_ENERGY_MIN = 1


class FastViewPlayerHistoryError(ValueError):
    pass


def player_history_sample_index(global_tick: int) -> int:
    """Mirror the source min(tick, 119) / 5 history index."""
    if type(global_tick) is not int or global_tick < 0:
        raise FastViewPlayerHistoryError(
            "FastView player-history tick must be a non-negative integer"
        )
    return min(global_tick, SOURCE_HISTORY_TICK_CAP) // SOURCE_HISTORY_TICK_DIVISOR



def match_form_trajectory_rng_draw_count(elapsed_sample_count: int) -> int:
    """Return exact 0x630CEC-loop RNG(2) draw count for an active player."""
    if (
        type(elapsed_sample_count) is not int
        or not 0 <= elapsed_sample_count <= SOURCE_HISTORY_SAMPLE_COUNT
    ):
        raise FastViewPlayerHistoryError(
            "elapsed_sample_count must be an integer in 0..24"
        )
    return max(0, elapsed_sample_count - 1)


def materialize_fastview_match_form_history(
    target_rating: int,
    elapsed_sample_count: int,
    rng2_rolls,
    *,
    active_for_club: bool,
) -> tuple[int, ...]:
    """Mirror the active-player 0x630CEC..0x630D9E form trajectory.

    The source resets sample 0 to 5, then visits samples 1..23. Samples before
    MatchCalculator +0xFF8 each consume one MatchEngine RNG(2) result. A nonzero
    roll moves one point toward participant target byte +0x30. If already equal
    to the target and 0x417F50 says the player is active for this club, values
    <=5 rise one point while values >5 fall one point. Samples at/after +0xFF8
    hold the previous clamped value without consuming RNG.

    rng2_rolls must contain exactly the draws the source would consume, so a
    caller cannot accidentally desynchronize the separate MatchEngine stream.
    """
    if (
        type(target_rating) is not int
        or not SOURCE_MATCH_FORM_TARGET_MIN
        <= target_rating
        <= SOURCE_MATCH_FORM_TARGET_MAX
    ):
        raise FastViewPlayerHistoryError(
            "target_rating must be an integer in source range 4..10"
        )
    if type(active_for_club) is not bool:
        raise FastViewPlayerHistoryError("active_for_club must be a bool")

    expected_draws = match_form_trajectory_rng_draw_count(elapsed_sample_count)
    try:
        rolls = tuple(rng2_rolls)
    except TypeError as exc:
        raise FastViewPlayerHistoryError("rng2_rolls must be iterable") from exc
    if len(rolls) != expected_draws or any(
        type(value) is not int or not 0 <= value < SOURCE_MATCH_FORM_RNG_BOUND
        for value in rolls
    ):
        raise FastViewPlayerHistoryError(
            f"rng2_rolls must contain exactly {expected_draws} source RNG(2) results"
        )

    history = [SOURCE_MATCH_FORM_INITIAL]
    roll_index = 0
    for sample_index in range(1, SOURCE_HISTORY_SAMPLE_COUNT):
        previous = history[-1]
        if sample_index >= elapsed_sample_count:
            current = min(
                SOURCE_MATCH_FORM_MAX,
                max(SOURCE_MATCH_FORM_MIN, previous),
            )
        else:
            roll = rolls[roll_index]
            roll_index += 1
            current = previous
            if roll != 0:
                if current < target_rating:
                    current += 1
                elif current > target_rating:
                    current -= 1
                elif active_for_club:
                    current += 1 if current <= 5 else -1
            current = min(
                SOURCE_MATCH_FORM_MAX,
                max(SOURCE_MATCH_FORM_MIN, current),
            )
        history.append(current)

    return tuple(history)


def condition_history_retained_prefix_count(elapsed_sample_count: int) -> int:
    """Return Condition bytes that survive 0x630D12 future-fill."""
    if (
        type(elapsed_sample_count) is not int
        or not 0 <= elapsed_sample_count <= SOURCE_HISTORY_SAMPLE_COUNT
    ):
        raise FastViewPlayerHistoryError(
            "elapsed_sample_count must be an integer in 0..24"
        )
    return max(1, min(elapsed_sample_count, SOURCE_HISTORY_SAMPLE_COUNT))


def materialize_fastview_condition_history(
    captured_prefix,
    elapsed_sample_count: int,
    final_condition: int,
) -> tuple[int, ...]:
    """Complete the exact 24-byte Condition history after match finalization.

    captured_prefix is the source-visible prefix that survives finalization:
    sample 0 from participant setup plus the segment-boundary samples below
    MatchCalculator +0xFF8. 0x630D12..0x630D3D fills every remaining history
    byte with the player's final DBRPlayer Condition.
    """
    retained = condition_history_retained_prefix_count(elapsed_sample_count)
    try:
        prefix = tuple(captured_prefix)
    except TypeError as exc:
        raise FastViewPlayerHistoryError("captured_prefix must be iterable") from exc
    if len(prefix) != retained or any(
        type(value) is not int or not 0 <= value <= 0xFF for value in prefix
    ):
        raise FastViewPlayerHistoryError(
            f"captured_prefix must contain exactly {retained} source-byte samples"
        )
    if type(final_condition) is not int or not 0 <= final_condition <= 0xFF:
        raise FastViewPlayerHistoryError(
            "final_condition must be an unsigned source byte"
        )
    return prefix + (final_condition,) * (
        SOURCE_HISTORY_SAMPLE_COUNT - retained
    )


@dataclass(frozen=True)
class FastViewPlayerHistories:
    """Exact source-domain histories required by PlayerProxy form/energy output."""

    condition: tuple[int, ...]
    match_form: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.condition) != SOURCE_HISTORY_SAMPLE_COUNT:
            raise FastViewPlayerHistoryError(
                "Condition history must contain exactly 24 five-minute samples"
            )
        if len(self.match_form) != SOURCE_HISTORY_SAMPLE_COUNT:
            raise FastViewPlayerHistoryError(
                "Match-form history must contain exactly 24 five-minute samples"
            )
        if any(type(value) is not int or not 0 <= value <= 0xFF for value in self.condition):
            raise FastViewPlayerHistoryError(
                "Condition history samples must be unsigned source bytes"
            )
        if any(
            type(value) is not int
            or not SOURCE_MATCH_FORM_MIN <= value <= SOURCE_MATCH_FORM_MAX
            for value in self.match_form
        ):
            raise FastViewPlayerHistoryError(
                "Match-form history samples must remain in source range 1..10"
            )

    def condition_at_tick(self, global_tick: int) -> int:
        return self.condition[player_history_sample_index(global_tick)]

    def form_at_tick(self, global_tick: int) -> int:
        """Mirror 0x632FC0 -> 0x6308B0."""
        return self.match_form[player_history_sample_index(global_tick)]


def derive_fastview_energy(
    histories: FastViewPlayerHistories,
    global_tick: int,
    rng6_roll: int,
) -> int:
    """Mirror 0x633000 -> 0x630910 for one PlayerProxy energy evaluation.

    Source algorithm:
    1. start from Condition history at tick 0;
    2. for 5,10,... strictly below the requested tick, compare current vs
       previous match-form sample; rising form subtracts 4, otherwise add 4;
    3. consume RNG(6) and add roll-3;
    4. clamp the result to at least 1;
    5. cap it by Condition at the first five-minute boundary >= tick
       (with the getter's own 119-tick cap).

    The caller must supply the exact source-order RNG(6) result. This function
    never consumes gameplay RNG itself.
    """
    if type(global_tick) is not int or global_tick < 0:
        raise FastViewPlayerHistoryError(
            "FastView energy tick must be a non-negative integer"
        )
    if type(rng6_roll) is not int or not 0 <= rng6_roll < SOURCE_ENERGY_RNG_BOUND:
        raise FastViewPlayerHistoryError(
            "FastView energy RNG result must be an integer in 0..5"
        )

    value = histories.condition_at_tick(0)
    sample_tick = SOURCE_HISTORY_TICK_DIVISOR
    while sample_tick < global_tick:
        current_form = histories.form_at_tick(sample_tick)
        previous_form = histories.form_at_tick(
            sample_tick - SOURCE_HISTORY_TICK_DIVISOR
        )
        if current_form > previous_form:
            value -= SOURCE_ENERGY_FORM_TREND_STEP
        else:
            value += SOURCE_ENERGY_FORM_TREND_STEP
        sample_tick += SOURCE_HISTORY_TICK_DIVISOR

    value += rng6_roll - SOURCE_ENERGY_RNG_CENTER
    if value < SOURCE_ENERGY_MIN:
        return SOURCE_ENERGY_MIN

    condition_cap = histories.condition_at_tick(sample_tick)
    return condition_cap if value > condition_cap else value


def source_history_byte_offset(
    side_index: int,
    player_index: int,
    global_tick: int,
    *,
    form: bool,
) -> int:
    """Return the exact MatchRecord byte offset used by the source getters."""
    if type(side_index) is not int or side_index not in (0, 1):
        raise FastViewPlayerHistoryError("side_index must be 0 or 1")
    if type(player_index) is not int or player_index < 0:
        raise FastViewPlayerHistoryError("player_index must be non-negative")
    sample = player_history_sample_index(global_tick)
    if side_index == 0:
        base = (
            SOURCE_SIDE0_FORM_HISTORY_OFFSET
            if form
            else SOURCE_SIDE0_CONDITION_HISTORY_OFFSET
        )
    else:
        base = (
            SOURCE_SIDE1_FORM_HISTORY_OFFSET
            if form
            else SOURCE_SIDE1_CONDITION_HISTORY_OFFSET
        )
    return base + player_index * SOURCE_PLAYER_HISTORY_STRIDE + sample

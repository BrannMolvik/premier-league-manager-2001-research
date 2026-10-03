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

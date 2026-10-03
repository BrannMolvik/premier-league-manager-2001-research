"""Native +E8 bit 9 / +130 lifecycle; unknown allocation bytes stay unknown."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ClubAttendanceCounter:
    initialized: bool
    count: int | None

    def __post_init__(self):
        if type(self.initialized) is not bool:
            raise ValueError('Attendance bit-9 state must be explicit')
        if self.count is not None and (type(self.count) is not int or not 0 <= self.count <= 255):
            raise ValueError('Attendance counter is a native byte')
        if self.initialized and self.count is None:
            raise ValueError('Initialized attendance counter requires its producer value')

    @classmethod
    def fresh(cls):
        # 405A6E/405AA7 explicitly zero E8, not the unwritten +130 byte.
        return cls(False, None)

    def completed_home_gate(self):
        # 5DB97F writes 1 when bit 9 is clear, ignoring the allocation byte.
        # Otherwise 5DB9B5/C1 increments AL, including native byte wrap.
        return type(self)(True, 1 if not self.initialized else (self.count + 1) & 255)


def ordinary_human_adjustment(counter, native_zero_based_rank):
    """408191/4081E8 guards only; never invent the boost branch or its draws."""
    if counter is not None and counter.count is not None and counter.count < 2:
        return 5
    if (type(native_zero_based_rank) is int and native_zero_based_rank >= 4):
        return 5
    return None


def initialize_top_four_opponent_condition(players, rng):
    """4081FB..4082E4, shipped tuning; called only after proven native guards.

    This is the second roster pass, AFTER 4080F0. Two ran1 RNG(6) draws
    per roster slot, including non-selected players, precede the byte store.
    The scale uses SETL's boolean 1, not the zero-based rank itself.
    """
    minimum, mean, maximum, base = 100, 105, 110, 90
    lower_span, upper_span = mean - minimum + 1, maximum - mean + 1
    scale = 100 - (100 - 0) // 4
    for player in players:
        upper_draw = int(rng.randbelow(upper_span))
        lower_draw = int(rng.randbelow(lower_span))
        product = scale * (minimum + upper_draw + lower_draw - base)
        # Native signed division truncates toward zero, not floor division.
        quotient = (abs(product) // 100) * (-1 if product < 0 else 1)
        player.condition = (quotient + base) & 0xFF
    return (upper_span + lower_span) // 2 + minimum - base


def produce_human_opponent_condition(counter, native_rank, players, match_engine_rng):
    """Retain D48 only with its actual producer side effects or proven guard."""
    guarded = ordinary_human_adjustment(counter, native_rank)
    if guarded is not None:
        return guarded
    if (counter is not None and counter.count is not None and counter.count >= 2
            and type(native_rank) is int and 0 <= native_rank < 4
            and match_engine_rng is not None):
        return initialize_top_four_opponent_condition(players, match_engine_rng)
    return None

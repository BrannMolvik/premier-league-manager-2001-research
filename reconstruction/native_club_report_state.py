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

"""Source-closed FastView clock / GlobalTick bridge.

The same EventGlobalTick first dword consumed by MatchIterator is consumed by
ClockControl and rendered numerically. This module records that identity and the
exact five-tick array-index transform without assigning an unverified localized
suffix or inventing host scheduling beyond the separately recovered throttle.
"""
from __future__ import annotations


SOURCE_CLOCK_CONSTRUCTOR_VA = 0x51EB90
SOURCE_CLOCK_RECEIVER_VA = 0x51EDB0
SOURCE_CLOCK_RENDER_VA = 0x51EDD0
SOURCE_CLOCK_FORMAT_VA = 0x8292F4
SOURCE_CLOCK_FORMAT = "%u %s"
SOURCE_CLOCK_TEXT_RECT = (439, 44, 621, 64)
SOURCE_CLOCK_FIRST_DWORD_OFFSET = 0x00
SOURCE_CLOCK_FIRST_HALF_SWITCH_VALUE = 46
SOURCE_CLOCK_SECOND_HALF_SWITCH_VALUE = 91

SOURCE_POSSESSION_ARRAY_LOOKUP_VA = 0x631240
SOURCE_POSSESSION_TICK_DIVISOR = 5


class FastViewClockError(ValueError):
    pass


def fastview_clock_numeric_value(global_tick_value: int) -> int:
    """Return the exact unsigned value ClockControl passes to its formatter."""
    if type(global_tick_value) is not int or global_tick_value < 0:
        raise FastViewClockError(
            "EventGlobalTick numeric value must be a non-negative integer"
        )
    return global_tick_value


def possession_array_index_for_global_tick(global_tick_value: int) -> int:
    """Return the exact MatchIterator quotient used for the possession arrays.

    MatchIterator only enters the EventPossession branch when the incoming
    EventGlobalTick value is divisible by five. The quotient is then passed to
    the source statistics lookup at 0x631240.
    """
    value = fastview_clock_numeric_value(global_tick_value)
    if value % SOURCE_POSSESSION_TICK_DIVISOR:
        raise FastViewClockError(
            "EventPossession array lookup requires a GlobalTick divisible by five"
        )
    return value // SOURCE_POSSESSION_TICK_DIVISOR

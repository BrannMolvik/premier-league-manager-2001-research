"""Bounded original PBg NEXT/MATCH target, not a substitute match workflow.

Canonical 4A83F0/4A84D2 target arithmetic and 5155B0 default. Callers must
provide the actual 615D10 selector result; unavailable evidence is not None.
Queued-user warnings, pre-match UI and annual rollover are not inferred here.
"""
from dataclasses import dataclass
from datetime import date, timedelta


NATIVE_DEFAULT_TURN_LENGTH = 7
NATIVE_TURN_LENGTH_CHOICES = (1, 2, 3, 7, 14)


def original_pitch_event_season_matches(
    native_calendar: tuple[int, int, int], event_mask: int,
) -> bool:
    """Exact 5E3CC0 predicate; not a pitch-event or wrapper-link producer.

    5E3B20 supplies zero-extended event byte+8. The explicit tuple comes from
    64CCD0 (year offset, 1-based month/day), not inferred weather or Gregorian
    quarters. In January/early February the original retains the input mask,
    accepting ANY nonzero mask; it does not select winter bit16 there.
    """
    if (type(native_calendar) is not tuple or len(native_calendar) != 3
            or any(type(value) is not int for value in native_calendar)):
        raise ValueError('Pitch-event season requires the explicit native calendar tuple')
    year, month, day = native_calendar
    if not 0 <= year <= 8099:
        raise ValueError('Pitch-event native year is outside the supported range')
    # Preserve the native four-year cycle, including its post-1900 leap
    # centuries; host Gregorian validation would reject valid source tuples.
    month_lengths = (31, 29 if year >= 4 and year % 4 == 0 else 28,
                     31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    if not 1 <= month <= 12 or not 1 <= day <= month_lengths[month - 1]:
        raise ValueError('Pitch-event native month/day is invalid')
    if type(event_mask) is not int or not 0 <= event_mask <= 255:
        raise ValueError('Pitch-event mask must be an explicit source byte')
    selected_mask = event_mask  # 5E3D29, not an invented winter/default bit.
    for lower_month, upper_month, bit in (
        (2, 5, 2), (5, 8, 4), (8, 11, 8), (11, 2, 16),
    ):
        upper_year = year + int(upper_month < lower_month)
        if ((year, lower_month, 22) <= native_calendar
                < (upper_year, upper_month, 22)):
            selected_mask = bit
    return bool(selected_mask & event_mask)


@dataclass(frozen=True)
class OriginalManagementAdvanceTarget:
    current_date: date
    target_date: date
    next_match_date: date | None
    turn_length: int

    @property
    def processing_dates(self) -> tuple[date, ...]:
        # 4A84FD stores each increment before 4A83D0, never processes today.
        return tuple(self.current_date + timedelta(days=i)
                     for i in range(1, (self.target_date - self.current_date).days + 1))


def original_management_advance_target(
    current_date: date, *, next_match_date: date | None,
    selector_source_qualified: bool, container_end_date: date,
    turn_length: int = NATIVE_DEFAULT_TURN_LENGTH,
) -> OriginalManagementAdvanceTarget:
    """Preserve native pre-match stop/cap without fabricating selector state.

    A None result is accepted only when the caller explicitly qualifies native
    null. Unknown/symbolic schedules cannot silently become an end-date turn.
    Settings accept native DWORD values, not merely the five UI choices.
    The annual terminal branch must be handled by its separate producer.
    """
    if selector_source_qualified is not True:
        raise RuntimeError('Original NEXT match selector is not source-qualified')
    if type(current_date) is not date or type(container_end_date) is not date:
        raise ValueError('Original NEXT requires exact calendar dates')
    if next_match_date is not None and type(next_match_date) is not date:
        raise ValueError('Original NEXT match date is invalid')
    if type(turn_length) is not int or not 0 <= turn_length <= 0x7FFFFFFF:
        raise ValueError('Original NEXT turn length is outside the bounded signed range')
    if container_end_date <= current_date:
        raise RuntimeError('Original NEXT annual container transition is not integrated')
    target = container_end_date - timedelta(days=1)
    if next_match_date is not None:
        if not current_date <= next_match_date < container_end_date:
            raise ValueError('Original NEXT selector date is outside its current container')
        target = next_match_date
        if target > current_date + timedelta(days=1):
            target -= timedelta(days=1)
    # Compare the native interval before constructing a Python date: an
    # otherwise legal large DWORD must not overflow host date arithmetic.
    if (target - current_date).days > turn_length:
        target = current_date + timedelta(days=turn_length)
    return OriginalManagementAdvanceTarget(current_date, target,
                                          next_match_date, turn_length)

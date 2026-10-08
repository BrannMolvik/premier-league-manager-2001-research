"""Bounded original PBg NEXT/MATCH target, not a substitute match workflow.

Canonical 4A83F0/4A84D2 target arithmetic and 5155B0 default. Callers must
provide the actual 615D10 selector result; unavailable evidence is not None.
Queued-user warnings, pre-match UI and annual rollover are not inferred here.
"""
from dataclasses import dataclass
from datetime import date, timedelta


NATIVE_DEFAULT_TURN_LENGTH = 7
NATIVE_TURN_LENGTH_CHOICES = (1, 2, 3, 7, 14)


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

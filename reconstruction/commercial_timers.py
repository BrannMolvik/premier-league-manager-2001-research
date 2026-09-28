"""Source-backed fresh DBRUser concession/sponsor wait timers.

This module models only the wait/reset layer that is already instruction-locked.
Concession offer construction remains caller-supplied because its candidate
selection depends on building/resource state that is not yet represented by a
general clean-room runtime object.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


ConcessionAttempt = Callable[[BoundedRng], bool]


FRESH_CONCESSION_WAIT_MIN = 7
FRESH_CONCESSION_WAIT_RANGE = 14
FRESH_SPONSOR_WAIT_MIN = 7
FRESH_SPONSOR_WAIT_RANGE = 7


@dataclass
class UserCommercialTimerState:
    """Minimum recovered DBRUser commercial wait state.

    A newly scheduled wait counts its scheduling day as day 1. This reproduces
    the canonical fresh sequence where an 11-day concession wait drawn on the
    first active DBRUser day expires on day 11, while a 13-day no-sponsor wait
    expires on day 13.
    """

    concession_wait_days: int = 0
    concession_elapsed_days: int = 0
    sponsor_wait_days: int = 0
    sponsor_elapsed_days: int = 0

    def _schedule_concession_wait(self, rng: BoundedRng) -> int:
        self.concession_wait_days = (
            FRESH_CONCESSION_WAIT_MIN + int(rng.randbelow(FRESH_CONCESSION_WAIT_RANGE))
        )
        self.concession_elapsed_days = 1
        return 1

    def _schedule_sponsor_wait(self, rng: BoundedRng) -> int:
        self.sponsor_wait_days = (
            FRESH_SPONSOR_WAIT_MIN + int(rng.randbelow(FRESH_SPONSOR_WAIT_RANGE))
        )
        self.sponsor_elapsed_days = 1
        return 1

    def run_daily(
        self,
        rng: BoundedRng,
        *,
        concession_attempt: ConcessionAttempt | None = None,
    ) -> tuple[int, bool]:
        """Advance the proven wait/reset layer by one DBRUser day.

        Returns (timer_draws, concession_expired). timer_draws counts only the
        wait-scheduling draws owned by this state object; RNG consumed by
        concession_attempt belongs to the caller-supplied offer body.

        When a concession wait expires, a missing concession_attempt leaves
        the timer expired and reports the condition instead of inventing an
        offer result. A failed attempt also leaves the expired wait in place so
        the original retries on the following day. A successful attempt resets
        the wait to zero; a fresh wait is drawn on the next daily call.

        Sponsor expiry itself consumes no RNG and resets its wait to zero. The
        next daily call schedules a new no-sponsor wait.
        """
        if not hasattr(rng, "randbelow"):
            raise TypeError("rng must provide randbelow(bound)")

        timer_draws = 0
        concession_expired = False

        if self.concession_wait_days <= 0:
            timer_draws += self._schedule_concession_wait(rng)
        else:
            if self.concession_elapsed_days < self.concession_wait_days:
                self.concession_elapsed_days += 1
            if self.concession_elapsed_days >= self.concession_wait_days:
                concession_expired = True
                if concession_attempt is not None and bool(concession_attempt(rng)):
                    self.concession_wait_days = 0
                    self.concession_elapsed_days = 0
                    concession_expired = False

        if self.sponsor_wait_days <= 0:
            timer_draws += self._schedule_sponsor_wait(rng)
        else:
            if self.sponsor_elapsed_days < self.sponsor_wait_days:
                self.sponsor_elapsed_days += 1
            if self.sponsor_elapsed_days >= self.sponsor_wait_days:
                self.sponsor_wait_days = 0
                self.sponsor_elapsed_days = 0

        return timer_draws, concession_expired

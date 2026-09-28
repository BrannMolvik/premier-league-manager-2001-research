#!/usr/bin/env python3
"""Replay the canonical fresh Gate-11 post-staff training RNG bridge.

This helper contains no original EA data. It starts from the independently
verified shared CRT state after fixed support-staff creation and replays only
the mandatory RNG-bearing paths before the first active Saturday training
update for the fresh Arsenal user:

* one fresh concession wait draw;
* one fresh no-sponsor wait draw;
* seven daily condition-recovery passes over 37 active training records.

The daily recovery transition mirrors canonical FOOTBAL.EXE 0x61C580.
"""

from __future__ import annotations

from dataclasses import dataclass


POST_FIXED_STAFF_STATE = 0xFA1C595E
FRESH_ACTIVE_TRAINING_RECORDS = 37
FRESH_CONDITION = 80
DAILY_RECOVERY_ITERATIONS = 3
RECOVERY_THRESHOLD = 50

CONCESSION_MIN_WAIT = 7
CONCESSION_MAX_WAIT = 21
NO_SPONSOR_MIN_WAIT = 7
NO_SPONSOR_MAX_WAIT = 14

EXPECTED_CONCESSION_DRAW = 4
EXPECTED_CONCESSION_WAIT = 11
EXPECTED_CONCESSION_STATE = 0xA5A88AA9
EXPECTED_SPONSOR_DRAW = 6
EXPECTED_SPONSOR_WAIT = 13
EXPECTED_SPONSOR_STATE = 0x73FCE2C8

EXPECTED_DAILY = (
    (111, 0, 52, 0xC9A8C159, 80, 83),
    (111, 0, 54, 0xF9743E3E, 81, 85),
    (111, 0, 50, 0x5A4D5407, 82, 87),
    (111, 0, 64, 0x4C9DC084, 83, 89),
    (111, 0, 54, 0x0FDA05C5, 84, 91),
    (126, 15, 62, 0x1111C433, 85, 92),
    (142, 31, 46, 0x216C6081, 86, 93),
)
EXPECTED_PRE_FIRST_TRAINING_STATE = 0x216C6081
EXPECTED_FINAL_CONDITION_SUM = 3342


@dataclass
class MsvcCrtRng:
    state: int

    def rand15(self) -> int:
        self.state = (214013 * self.state + 2531011) & 0xFFFFFFFF
        return (self.state >> 16) & 0x7FFF

    def randbelow(self, bound: int) -> int:
        if bound <= 0:
            raise ValueError("bound must be positive")
        return (self.rand15() * int(bound)) // 32768


def replay() -> tuple[MsvcCrtRng, list[int]]:
    rng = MsvcCrtRng(POST_FIXED_STAFF_STATE)

    concession_draw = rng.randbelow(CONCESSION_MAX_WAIT - CONCESSION_MIN_WAIT)
    concession_wait = CONCESSION_MIN_WAIT + concession_draw
    assert concession_draw == EXPECTED_CONCESSION_DRAW
    assert concession_wait == EXPECTED_CONCESSION_WAIT
    assert rng.state == EXPECTED_CONCESSION_STATE

    sponsor_draw = rng.randbelow(NO_SPONSOR_MAX_WAIT - NO_SPONSOR_MIN_WAIT)
    sponsor_wait = NO_SPONSOR_MIN_WAIT + sponsor_draw
    assert sponsor_draw == EXPECTED_SPONSOR_DRAW
    assert sponsor_wait == EXPECTED_SPONSOR_WAIT
    assert rng.state == EXPECTED_SPONSOR_STATE

    # Both waits exceed the seven daily intervals before first active Saturday
    # training, so neither timer consumes another draw inside this bridge.
    assert concession_wait > 7
    assert sponsor_wait > 7

    conditions = [FRESH_CONDITION] * FRESH_ACTIVE_TRAINING_RECORDS

    for day_index, expected in enumerate(EXPECTED_DAILY, start=1):
        day_draws = 0
        extra_draws = 0
        increments = 0

        for player_index in range(FRESH_ACTIVE_TRAINING_RECORDS):
            for _ in range(DAILY_RECOVERY_ITERATIONS):
                roll = rng.randbelow(100)
                day_draws += 1
                if roll >= RECOVERY_THRESHOLD:
                    continue

                condition = conditions[player_index]
                if condition <= 90:
                    conditions[player_index] = condition + 1
                    increments += 1
                    continue

                first_extra = rng.randbelow(10)
                day_draws += 1
                extra_draws += 1
                if first_extra >= 99 - condition:
                    continue

                second_extra = rng.randbelow(10)
                day_draws += 1
                extra_draws += 1
                if second_extra < 5:
                    continue

                conditions[player_index] = condition + 1
                increments += 1

        actual = (
            day_draws,
            extra_draws,
            increments,
            rng.state,
            min(conditions),
            max(conditions),
        )
        assert actual == expected, (day_index, actual, expected)

    assert rng.state == EXPECTED_PRE_FIRST_TRAINING_STATE
    assert sum(conditions) == EXPECTED_FINAL_CONDITION_SUM
    return rng, conditions


def main() -> None:
    rng, conditions = replay()
    print(f"concession wait: {EXPECTED_CONCESSION_WAIT} days")
    print(f"no-sponsor wait: {EXPECTED_SPONSOR_WAIT} days")
    for day, expected in enumerate(EXPECTED_DAILY, start=1):
        draws, extras, gains, state, lo, hi = expected
        print(
            f"day {day}: draws={draws} extras={extras} gains={gains} "
            f"state=0x{state:08X} condition={lo}..{hi}"
        )
    print(f"condition sum: {sum(conditions)}")
    print(f"pre-first-0x4EACE0 state: 0x{rng.state:08X}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Replay the corrected fresh Arsenal commercial/training RNG stream.

This helper contains no original EA files. Capacity totals and branch outcomes
are independently verified constants from the authorized source analysis.
"""

from __future__ import annotations

from dataclasses import dataclass


POST_FIRST_WEEKLY_STATE = 0xF68CAFEF
SELECTOR_CAPACITIES = (0, 16, 0, 20, 0, 12, 0, 14)

RULES = (
    (1000,1400,1,4),(1000,1400,1,5),(1000,1500,1,8),(1000,1600,1,6),(1000,1650,1,7),
    (1200,1400,2,10),(1100,1450,2,12),(1200,1500,2,10),(1100,1560,2,15),(1200,1650,2,10),
    (1100,1200,5,15),(1200,1300,5,13),(1200,1250,5,15),(1200,1300,5,18),(1200,1350,5,24),
    (850,1200,10,30),(950,1200,10,35),(950,1200,10,35),(950,1200,10,35),(850,1300,10,40),
    (900,1200,20,50),(900,1250,20,50),(900,1350,20,50),(900,1150,20,55),(900,1250,20,60),
)
LOCAL_RANGES = (
    (1,1),(1,1),(2,3),(2,3),(3,3),(1,1),(1,2),(2,3),(3,3),(3,3),
    (1,2),(2,2),(2,2),(2,3),(3,3),(2,2),(2,2),(2,3),(3,3),(3,4),
    (2,2),(2,2),(2,3),(3,4),(4,5),
)

EXPECTED_DAY11_STATE = 0x2D3FF8E7
EXPECTED_DAY12_PRE_CONCESSION_STATE = 0xD4E2341D
EXPECTED_DAY12_POST_CONCESSION_STATE = 0x03CA80A0
EXPECTED_DAY12_POST_RECOVERY_STATE = 0x50CB6921
EXPECTED_DAY13_WAIT_STATE = 0x51142760
EXPECTED_DAY14_SPONSOR_STATE = 0x9533F463
EXPECTED_SECOND_WEEKLY_PRE = 0x509630B6
EXPECTED_SECOND_WEEKLY_POST = 0xA3C5013C
EXPECTED_THIRD_WEEKLY_PRE = 0x7B8D5F58
EXPECTED_THIRD_WEEKLY_POST = 0xE176B24E


@dataclass
class MsvcCrtRng:
    state: int

    def rand15(self) -> int:
        self.state = (214013 * self.state + 2531011) & 0xFFFFFFFF
        return (self.state >> 16) & 0x7FFF

    def randbelow(self, bound: int) -> int:
        return (self.rand15() * int(bound)) // 32768


def recover_day(rng: MsvcCrtRng, conditions: list[int]) -> int:
    draws = 0
    for index in range(37):
        for _ in range(3):
            roll = rng.randbelow(100)
            draws += 1
            if roll >= 50:
                continue
            condition = conditions[index]
            if condition <= 90:
                conditions[index] += 1
                continue
            first = rng.randbelow(10)
            draws += 1
            if first >= 99 - condition:
                continue
            second = rng.randbelow(10)
            draws += 1
            if second < 5:
                continue
            conditions[index] += 1
    return draws


def concession_attempt(rng: MsvcCrtRng) -> tuple[bool, int, int | None]:
    draws = 0
    for capacity in SELECTOR_CAPACITIES:
        if capacity == 0:
            continue
        base = 850 + rng.randbelow(800)
        draws += 1
        value = base + int(base * 0.20)
        chosen = None
        for _ in range(25):
            candidate = rng.randbelow(25)
            draws += 1
            lo, hi, cap_lo, cap_hi = RULES[candidate]
            if cap_lo <= capacity <= cap_hi and lo <= value <= hi:
                chosen = candidate
                break
        if chosen is None:
            continue
        local_lo, local_hi = LOCAL_RANGES[chosen]
        if local_lo != local_hi:
            rng.randbelow(local_hi - local_lo)
            draws += 1
        rng.randbelow(3)
        draws += 1
        return True, draws, chosen
    return False, draws, None


def replay() -> None:
    # Conditions at the first Saturday are independently locked by
    # replay_gate11_training_bridge.py.
    from replay_gate11_training_bridge import replay as replay_first_bridge

    rng, conditions = replay_first_bridge()
    for _ in range(222):
        rng.randbelow(100)
    assert rng.state == POST_FIRST_WEEKLY_STATE

    assert recover_day(rng, conditions) == 174
    assert recover_day(rng, conditions) == 199
    assert recover_day(rng, conditions) == 187
    assert rng.state == 0xDB610BDF

    success, draws, chosen = concession_attempt(rng)
    assert not success and draws == 104 and chosen is None
    assert rng.state == EXPECTED_DAY11_STATE
    assert recover_day(rng, conditions) == 182
    assert rng.state == EXPECTED_DAY12_PRE_CONCESSION_STATE

    success, draws, chosen = concession_attempt(rng)
    assert success and draws == 53 and chosen == 19
    assert rng.state == EXPECTED_DAY12_POST_CONCESSION_STATE
    assert recover_day(rng, conditions) == 191
    assert rng.state == EXPECTED_DAY12_POST_RECOVERY_STATE

    assert rng.randbelow(14) == 8
    assert rng.state == EXPECTED_DAY13_WAIT_STATE
    assert recover_day(rng, conditions) == 192

    assert rng.randbelow(7) == 1
    assert rng.state == EXPECTED_DAY14_SPONSOR_STATE
    assert recover_day(rng, conditions) == 189
    assert rng.state == EXPECTED_SECOND_WEEKLY_PRE
    for _ in range(222):
        rng.randbelow(100)
    assert rng.state == EXPECTED_SECOND_WEEKLY_POST

    for expected in (195, 197, 217, 188, 200, 188, 187):
        assert recover_day(rng, conditions) == expected
    assert rng.state == EXPECTED_THIRD_WEEKLY_PRE
    for _ in range(222):
        rng.randbelow(100)
    assert rng.state == EXPECTED_THIRD_WEEKLY_POST


if __name__ == "__main__":
    replay()
    print("corrected commercial/training replay: ok")

from __future__ import annotations

from dataclasses import dataclass

from match_events import PossessionRecord


@dataclass
class SegmentCounters:
    """Raw counters accumulated by one 0x62B1A0 five-minute segment."""

    side0: int = 0
    neutral: int = 0
    side1: int = 0

    def add_attacking(self, side: int, amount: int) -> None:
        value = int(amount)
        if value < 0:
            raise ValueError("counter increments must be non-negative")
        if side == 0:
            self.side0 += value
        elif side == 1:
            self.side1 += value
        else:
            raise ValueError("side must be 0 or 1")


def _jitter_percentage(value: int, rng) -> int:
    result = int(value)
    if 5 < result < 95:
        result += rng.randbelow(10) - 5
    return min(100, max(0, result))


def normalize_segment_statistics(
    side0_attack_count: int,
    total_attack_count: int,
    counters: SegmentCounters,
    rng,
) -> PossessionRecord:
    """Exact normalization/jitter block at 0x62B4B9..0x62B5E9."""

    side0_attack_count = int(side0_attack_count)
    total_attack_count = int(total_attack_count)
    if side0_attack_count < 0 or total_attack_count < 0:
        raise ValueError("attack counts must be non-negative")
    if side0_attack_count > total_attack_count:
        raise ValueError("side0 attack count cannot exceed total attack count")

    territory = 50
    if total_attack_count > 0:
        territory = (side0_attack_count * 100) // total_attack_count
        territory = _jitter_percentage(territory, rng)

    raw_total = counters.side0 + counters.neutral + counters.side1
    if raw_total > 0:
        side0_percent = (counters.side0 * 100) // raw_total
        neutral_percent = (counters.neutral * 100) // raw_total
    else:
        side0_percent = 33
        neutral_percent = 33

    side0_percent = _jitter_percentage(side0_percent, rng)
    neutral_percent = _jitter_percentage(neutral_percent, rng)

    if side0_percent + neutral_percent > 100:
        side0_percent = 100 - neutral_percent

    return PossessionRecord(
        territory=territory,
        side0_percent=side0_percent,
        neutral_percent=neutral_percent,
    )

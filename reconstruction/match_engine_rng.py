"""FM2001 MatchEngine RNG used by MatchCalculator (0x981BF0).

This is the canonical executable's 0x64D5D0 ran1/Park-Miller generator with
the 32-entry shuffle table. It is deliberately separate from the shared MSVC
CRT stream used by 0x64D540.
"""

from __future__ import annotations

from dataclasses import dataclass, field


IA = 16807
IM = 2147483647
IQ = 127773
IR = 2836
NTAB = 32
NDIV = 1 + (IM - 1) // NTAB
AM = 1.0 / IM
EPS = 1.2e-7
RNMX = 1.0 - EPS


@dataclass
class MatchEngineRng:
    """State-compatible clean-room form of the global object at 0x981BF0."""

    seed_value: int
    state: int = field(init=False)
    shuffle_value: int = 0
    table: list[int] = field(default_factory=lambda: [0] * NTAB)

    def __post_init__(self) -> None:
        seed = int(self.seed_value)
        # 0x64D560 obtains time(), negates positive values, then calls the
        # state setter. A zero state is normalized to one by 0x64D590.
        self.state = -abs(seed) if seed != 0 else -1
        self.shuffle_value = 0
        if len(self.table) != NTAB:
            raise ValueError("MatchEngine RNG shuffle table requires 32 entries")
        self.table[:] = [0] * NTAB

    def random(self) -> float:
        """Return the exact bounded [0,1) ran1 value from 0x64D5D0."""
        if self.state <= 0 or self.shuffle_value == 0:
            self.state = max(-int(self.state), 1)
            for j in range(NTAB + 7, -1, -1):
                k = self.state // IQ
                self.state = IA * (self.state - k * IQ) - IR * k
                if self.state < 0:
                    self.state += IM
                if j < NTAB:
                    self.table[j] = self.state
            self.shuffle_value = self.table[0]

        k = self.state // IQ
        self.state = IA * (self.state - k * IQ) - IR * k
        if self.state < 0:
            self.state += IM

        index = int(self.shuffle_value) // NDIV
        self.shuffle_value = self.table[index]
        self.table[index] = self.state

        value = AM * self.shuffle_value
        return RNMX if value > RNMX else value

    def randbelow(self, bound: int) -> int:
        """Mirror 0x64D5B0: truncate ran1() * bound."""
        bound = int(bound)
        if bound <= 0:
            raise ValueError("bound must be positive")
        return int(self.random() * bound)

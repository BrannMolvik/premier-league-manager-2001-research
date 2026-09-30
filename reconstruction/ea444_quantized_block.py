"""Original EA444 pre-IDCT 8x8 coefficient grid, not a guessed pixel decoder.

Source: actual Loader444 0x7B9040 writes DC and zeros 63 AC entries.
0x7B933D..0x7B9354 maps signed AC amplitudes through the executable's
64-entry zigzag and multiplies by the runtime quantization matrix at
0x9FBD80, writing the low 32-bit product into the 8x8 grid at 0x9FBE80.

The resulting values are fixed-point PRE-INVERSE-TRANSFORM components.
They must not be treated as displayed colors or saved as image files.
"""
from __future__ import annotations

from dataclasses import dataclass

from ea444_coefficients import EA444CoefficientBlock
from ea444_quantization import EA444Quantization


class EA444BlockGridError(ValueError):
    pass


@dataclass(frozen=True)
class EA444QuantizedBlock:
    """One full 8x8 coefficient grid in original zigzag-mapped positions."""
    signed_fixed: tuple[int, ...]

    def __post_init__(self):
        if len(self.signed_fixed) != 64:
            raise EA444BlockGridError("Expected precisely 64 fixed-point coefficients")

    @property
    def nonzero(self) -> tuple[tuple[int, int], ...]:
        return tuple((index, value) for index, value in enumerate(self.signed_fixed)
                     if value)


def make_quantized_block(
    source: EA444CoefficientBlock, quant: EA444Quantization,
) -> EA444QuantizedBlock:
    grid = [0] * 64
    grid[0] = quant.scaled_coefficient(0, source.scale_code)
    seen = {0}
    for position, amplitude in source.coefficients:
        if not 0 <= position < 64 or position in seen:
            raise EA444BlockGridError(
                f"Original AC stream repeats or corrupts grid position {position}"
            )
        seen.add(position)
        grid[position] = quant.scaled_coefficient(position, amplitude)
    return EA444QuantizedBlock(tuple(grid))

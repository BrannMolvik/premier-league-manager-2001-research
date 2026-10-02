"""Source-closed FM2001 FastView possession-diagram primitives.

This module records only behavior proved from the canonical FM2001 executable
and authorized source disc. It does not choose a UI framework, guess update
cadence, or infer which screen direction belongs to the user's team.
"""
from __future__ import annotations

from dataclasses import dataclass


SOURCE_CONSTRUCTOR_VA = 0x5227D0
SOURCE_FASTVIEW_CALLSITE_VA = 0x5206CD
SOURCE_STATE_SETTER_VA = 0x522B40
SOURCE_UPDATE_VA = 0x522BB0
SOURCE_PRESENTATION_RNG_VA = 0x5227A0
SOURCE_OVERLAY_X_TABLE_VA = 0x829328

PROCESS_INITIAL_PRESENTATION_RNG_STATE = 0
MSVC_RAND_MULTIPLIER = 214013
MSVC_RAND_INCREMENT = 2531011
PRESENTATION_ROLL_DIVISOR = 327

PITCH_ORIGIN = (253, 139)
PITCH_SIZE = (294, 78)
PITCH_RECT = (253, 139, 547, 217)
OFFSCREEN_X = 4000
INITIAL_OVERLAY_STATE = 1
OVERLAY_X_OFFSETS = (0, 98, 169)

PITCH_NORMAL_PATH = "FM2001_Art/FastView/pitch_normal.444"
OVERLAY_PATHS = (
    "FM2001_Art/FastView/pitch_left.444",
    "FM2001_Art/FastView/pitch_middle.444",
    "FM2001_Art/FastView/pitch_right.444",
)
OVERLAY_SIZES = ((125, 78), (98, 78), (125, 78))


@dataclass(frozen=True)
class PossessionDiagramStep:
    previous_state: int
    territory: int
    rng_state_before: int
    rng_state_after: int
    rand15: int
    roll_0_to_100: int
    next_state: int


def active_overlay_rect(state: int) -> tuple[int, int, int, int]:
    """Return the exact on-screen rectangle for one overlay state."""
    if state not in (0, 1, 2):
        raise ValueError("PossessionDiagram state must be 0, 1, or 2")
    x = PITCH_ORIGIN[0] + OVERLAY_X_OFFSETS[state]
    y = PITCH_ORIGIN[1]
    width, height = OVERLAY_SIZES[state]
    return (x, y, x + width, y + height)


def presentation_rand_step(rng_state: int) -> tuple[int, int]:
    """Reproduce one call to the private presentation RNG at 0x5227A0."""
    if not 0 <= int(rng_state) <= 0xFFFFFFFF:
        raise ValueError("Presentation RNG state must fit uint32")
    state = (
        MSVC_RAND_MULTIPLIER * int(rng_state) + MSVC_RAND_INCREMENT
    ) & 0xFFFFFFFF
    return state, (state >> 16) & 0x7FFF


def possession_roll(rand15: int) -> int:
    """Reproduce the source quotient used by 0x522BB0 for the territory test."""
    if not 0 <= int(rand15) <= 0x7FFF:
        raise ValueError("Presentation rand output must fit 15 bits")
    return int(rand15) // PRESENTATION_ROLL_DIVISOR


def advance_possession_diagram(
    state: int,
    territory: int,
    rng_state: int,
) -> PossessionDiagramStep:
    """Reproduce one source-proven 0x522BB0 update.

    This is deliberately a one-call primitive. The original caller cadence is
    not yet source-closed, so this function must not be interpreted as a
    per-frame, per-second, or per-possession-segment scheduler.
    """
    if state not in (0, 1, 2):
        raise ValueError("PossessionDiagram state must be 0, 1, or 2")
    territory = int(territory)
    if not 0 <= territory <= 100:
        raise ValueError("Possession territory must be in 0..100")

    next_rng_state, rand15 = presentation_rand_step(rng_state)
    roll = possession_roll(rand15)

    if roll <= territory and state < 2:
        next_state = state + 1
    elif state > 0:
        next_state = state - 1
    else:
        next_state = state

    return PossessionDiagramStep(
        previous_state=state,
        territory=territory,
        rng_state_before=int(rng_state),
        rng_state_after=next_rng_state,
        rand15=rand15,
        roll_0_to_100=roll,
        next_state=next_state,
    )

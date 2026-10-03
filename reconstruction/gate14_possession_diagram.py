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
SOURCE_GOAL_RECEIVER_VA = 0x522C30
SOURCE_GLOBAL_PENALTIES_RECEIVER_VA = 0x522C60
SOURCE_PRESENTATION_RNG_VA = 0x5227A0

SOURCE_PRIMARY_RECEIVER_VFTABLE = 0x7CA87C
SOURCE_GOAL_RECEIVER_VFTABLE = 0x7CA870
SOURCE_GLOBAL_PENALTIES_RECEIVER_VFTABLE = 0x7CA864
SOURCE_PENALTIES_LATCH_OFFSET = 0x20
SOURCE_GOAL_FIELD_OFFSET = 0x0C

SOURCE_MATCH_ITERATOR_TICK_VA = 0x519630
SOURCE_MATCH_ITERATOR_VFTABLE = 0x7CA1DC
SOURCE_EVENT_POSSESSION_CONSTRUCTOR_VA = 0x51A6B0
SOURCE_EVENT_POSSESSION_CONSTRUCT_CALL_VA = 0x5197B8
SOURCE_EVENT_POSSESSION_SENDER_OFFSET = 0x20
SOURCE_GLOBAL_TICK_DIVISOR = 5
SOURCE_MATCH_ITERATOR_GATE_A5_OFFSET = 0xA5
SOURCE_MATCH_ITERATOR_GATE_98_OFFSET = 0x98
SOURCE_MATCH_ITERATOR_GATE_A0_OFFSET = 0xA0
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


@dataclass(frozen=True)
class PossessionDiagramEventResult:
    previous_state: int
    next_state: int
    rng_state_before: int
    rng_state_after: int
    penalties_latched: bool
    event_kind: str
    transition: PossessionDiagramStep | None = None


def apply_possession_event(
    state: int,
    territory: int,
    rng_state: int,
    *,
    penalties_latched: bool,
) -> PossessionDiagramEventResult:
    """Apply the exact EventPossession receiver at 0x522BB0.

    Once EventGlobalPenalties has latched object+0x20, every later
    EventPossession forces the middle state (1) and returns before the private
    presentation RNG is called. Otherwise this delegates to the already
    source-closed one-call territory transition.
    """
    if type(penalties_latched) is not bool:
        raise ValueError("penalties_latched must be boolean")
    if state not in (0, 1, 2):
        raise ValueError("PossessionDiagram state must be 0, 1, or 2")
    if penalties_latched:
        return PossessionDiagramEventResult(
            previous_state=state,
            next_state=1,
            rng_state_before=int(rng_state),
            rng_state_after=int(rng_state),
            penalties_latched=True,
            event_kind="EventPossession",
            transition=None,
        )
    step = advance_possession_diagram(state, territory, rng_state)
    return PossessionDiagramEventResult(
        previous_state=state,
        next_state=step.next_state,
        rng_state_before=int(rng_state),
        rng_state_after=step.rng_state_after,
        penalties_latched=False,
        event_kind="EventPossession",
        transition=step,
    )


def apply_goal_event(
    state: int,
    goal_field_0c: int,
    rng_state: int,
    *,
    penalties_latched: bool,
) -> PossessionDiagramEventResult:
    """Apply Receiver<EventGoal>::0x522C30 without assigning side semantics.

    Source field EventGoal+0x0C value 0 snaps the diagram to state 2; value 1
    snaps it to state 0. Other values leave the current state unchanged.
    This receiver consumes no presentation RNG and does not clear the penalties
    latch.
    """
    if state not in (0, 1, 2):
        raise ValueError("PossessionDiagram state must be 0, 1, or 2")
    if type(goal_field_0c) is not int:
        raise ValueError("goal_field_0c must be an integer source field")
    if type(penalties_latched) is not bool:
        raise ValueError("penalties_latched must be boolean")
    next_state = 2 if goal_field_0c == 0 else 0 if goal_field_0c == 1 else state
    return PossessionDiagramEventResult(
        previous_state=state,
        next_state=next_state,
        rng_state_before=int(rng_state),
        rng_state_after=int(rng_state),
        penalties_latched=penalties_latched,
        event_kind="EventGoal",
        transition=None,
    )


def apply_global_penalties_event(
    state: int,
    rng_state: int,
    *,
    penalties_latched: bool,
) -> PossessionDiagramEventResult:
    """Apply Receiver<EventGlobalPenalties>::0x522C60.

    The source receiver writes one byte at overall object+0x20. It does not
    immediately move the overlay; the *next EventPossession* observes the latch
    and forces state 1 without consuming presentation RNG.
    """
    if state not in (0, 1, 2):
        raise ValueError("PossessionDiagram state must be 0, 1, or 2")
    if type(penalties_latched) is not bool:
        raise ValueError("penalties_latched must be boolean")
    return PossessionDiagramEventResult(
        previous_state=state,
        next_state=state,
        rng_state_before=int(rng_state),
        rng_state_after=int(rng_state),
        penalties_latched=True,
        event_kind="EventGlobalPenalties",
        transition=None,
    )


def should_emit_possession_on_global_tick(
    global_tick_value: int,
    *,
    field_a5: int,
    field_98_present: bool,
    field_a0_present: bool,
) -> bool:
    """Mirror the exact preconditions before 0x5197B8 constructs EventPossession.

    MatchIterator's primary base is Receiver<EventGlobalTick>. Its callback at
    0x519630 exits when source byte +0xA5 is nonzero or pointer +0x98 is null.
    The EventPossession branch additionally requires pointer +0xA0 and only
    executes when the EventGlobalTick first dword is divisible by five.

    This closes cadence in *GlobalTick event counts only*. The wall-clock
    duration represented by one GlobalTick is intentionally not inferred here.
    """
    if type(global_tick_value) is not int or global_tick_value < 0:
        raise ValueError("global_tick_value must be a non-negative integer")
    if type(field_a5) is not int or not 0 <= field_a5 <= 0xFF:
        raise ValueError("field_a5 must be an unsigned source byte")
    if type(field_98_present) is not bool or type(field_a0_present) is not bool:
        raise ValueError("source pointer-presence gates must be boolean")
    return (
        field_a5 == 0
        and field_98_present
        and field_a0_present
        and global_tick_value % SOURCE_GLOBAL_TICK_DIVISOR == 0
    )

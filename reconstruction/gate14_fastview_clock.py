"""Source-closed FastView ClockControl text/state contract.

The same EventGlobalTick first dword consumed by MatchIterator is rendered by
ClockControl. Canonical RTTI also closes ClockControl's phase receivers for
half time, second half, full time, extra time and penalties.

This module preserves those exact text/state transitions and source color
inputs. It deliberately does not invent the modern RGBA result of the
runtime-packed RGB(255,45,45) alert color: that still depends on the active
16-bit masks and the unresolved packed-16 -> modern display expansion.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from gate14_fastview_phase_text import language_entry_for_global


class FastViewClockError(ValueError):
    pass


SOURCE_CLOCK_CONSTRUCTOR_VA = 0x51EB90
SOURCE_CLOCK_TEXT_CONSTRUCTOR_CALLSITE_VA = 0x51EC30
SOURCE_CLOCK_RECEIVER_VA = 0x51EDB0
SOURCE_CLOCK_RENDER_VA = 0x51EDD0
SOURCE_CLOCK_FORMAT_VA = 0x8292F4
SOURCE_CLOCK_FORMAT = "%u %s"
SOURCE_CLOCK_EMPTY_STRING_VA = 0x874BA0
SOURCE_CLOCK_TEXT_RECT = (439, 44, 621, 64)
SOURCE_CLOCK_TEXT_STYLE_INDEX = 1
SOURCE_CLOCK_TEXT_RAW_FLAGS = 0x02
SOURCE_CLOCK_TEXT_RENDER_FLAGS = 0x0A
SOURCE_CLOCK_NATIVE_WHITE_16 = 0xFFFF
SOURCE_CLOCK_ALERT_RGB8 = (255, 45, 45)

SOURCE_CLOCK_FIRST_HALF_SWITCH_VALUE = 46
SOURCE_CLOCK_SECOND_HALF_SWITCH_VALUE = 91

SOURCE_CLOCK_SECOND_HALF_LATCH_OFFSET = 0x6C
SOURCE_CLOCK_POST_90_LATCH_OFFSET = 0x6D
SOURCE_CLOCK_PENALTIES_LATCH_OFFSET = 0x6E
SOURCE_CLOCK_TEXTCONTROL_OFFSET = 0x18

SOURCE_CLOCK_VTABLE_GLOBAL_TICK = 0x7CA468
SOURCE_CLOCK_VTABLE_HALF_TIME = 0x7CA45C
SOURCE_CLOCK_VTABLE_SECOND_HALF = 0x7CA450
SOURCE_CLOCK_VTABLE_FULL_TIME = 0x7CA444
SOURCE_CLOCK_VTABLE_EXTRA_TIME = 0x7CA438
SOURCE_CLOCK_VTABLE_PENALTIES = 0x7CA42C

SOURCE_CLOCK_CALLBACK_GLOBAL_TICK = 0x51EDB0
SOURCE_CLOCK_CALLBACK_HALF_TIME = 0x51EEE0
SOURCE_CLOCK_CALLBACK_SECOND_HALF = 0x51EFB0
SOURCE_CLOCK_CALLBACK_FULL_TIME = 0x51EFD0
SOURCE_CLOCK_CALLBACK_EXTRA_TIME = 0x51F0A0
SOURCE_CLOCK_CALLBACK_PENALTIES = 0x51F170

SOURCE_CLOCK_RECEIVER_OFFSETS = {
    "EventGlobalTick": 0x00,
    "EventGlobalHalfTime": 0x04,
    "EventGlobalSecondHalf": 0x08,
    "EventGlobalFullTime": 0x0C,
    "EventGlobalExtraTime": 0x10,
    "EventGlobalPenalties": 0x14,
}

SOURCE_CLOCK_RECEIVER_VTABLES = {
    "EventGlobalTick": SOURCE_CLOCK_VTABLE_GLOBAL_TICK,
    "EventGlobalHalfTime": SOURCE_CLOCK_VTABLE_HALF_TIME,
    "EventGlobalSecondHalf": SOURCE_CLOCK_VTABLE_SECOND_HALF,
    "EventGlobalFullTime": SOURCE_CLOCK_VTABLE_FULL_TIME,
    "EventGlobalExtraTime": SOURCE_CLOCK_VTABLE_EXTRA_TIME,
    "EventGlobalPenalties": SOURCE_CLOCK_VTABLE_PENALTIES,
}

SOURCE_CLOCK_RECEIVER_CALLBACKS = {
    "EventGlobalTick": SOURCE_CLOCK_CALLBACK_GLOBAL_TICK,
    "EventGlobalHalfTime": SOURCE_CLOCK_CALLBACK_HALF_TIME,
    "EventGlobalSecondHalf": SOURCE_CLOCK_CALLBACK_SECOND_HALF,
    "EventGlobalFullTime": SOURCE_CLOCK_CALLBACK_FULL_TIME,
    "EventGlobalExtraTime": SOURCE_CLOCK_CALLBACK_EXTRA_TIME,
    "EventGlobalPenalties": SOURCE_CLOCK_CALLBACK_PENALTIES,
}

SOURCE_CLOCK_MINS_GLOBAL_VA = 0x982384
SOURCE_CLOCK_HALF_TIME_GLOBAL_VA = 0x98238C
SOURCE_CLOCK_FULL_TIME_GLOBAL_VA = 0x982388
SOURCE_CLOCK_EXTRA_TIME_GLOBAL_VA = 0x9821F4
SOURCE_CLOCK_PENALTIES_GLOBAL_VA = 0x9822D0

SOURCE_CLOCK_LOCALIZED_TEXT = {
    "mins": (SOURCE_CLOCK_MINS_GLOBAL_VA, 2333, 21532, "mins"),
    "half_time": (SOURCE_CLOCK_HALF_TIME_GLOBAL_VA, 2331, 21530, "Half time"),
    "full_time": (SOURCE_CLOCK_FULL_TIME_GLOBAL_VA, 2332, 21531, "Full time"),
    "extra_time": (SOURCE_CLOCK_EXTRA_TIME_GLOBAL_VA, 2433, 21617, "Extra time"),
    "penalties": (SOURCE_CLOCK_PENALTIES_GLOBAL_VA, 2378, 20014, "Penalties"),
}

SOURCE_POSSESSION_ARRAY_LOOKUP_VA = 0x631240
SOURCE_POSSESSION_TICK_DIVISOR = 5


@dataclass(frozen=True)
class FastViewClockColor:
    native_color_16: int | None
    source_rgb8: tuple[int, int, int] | None
    exact_modern_rgba_recovered: bool

    def __post_init__(self) -> None:
        if (self.native_color_16 is None) == (self.source_rgb8 is None):
            raise FastViewClockError(
                "clock color must be either one native endpoint or one RGB8 source"
            )
        if self.native_color_16 is not None:
            if self.native_color_16 != SOURCE_CLOCK_NATIVE_WHITE_16:
                raise FastViewClockError("only source white endpoint is closed directly")
            if not self.exact_modern_rgba_recovered:
                raise FastViewClockError(
                    "native white endpoint must remain exact in the current text path"
                )
        else:
            if self.source_rgb8 != SOURCE_CLOCK_ALERT_RGB8:
                raise FastViewClockError("clock RGB8 alert source drifted")
            if self.exact_modern_rgba_recovered:
                raise FastViewClockError(
                    "runtime-packed alert RGB cannot claim exact modern RGBA yet"
                )


CLOCK_WHITE = FastViewClockColor(
    native_color_16=SOURCE_CLOCK_NATIVE_WHITE_16,
    source_rgb8=None,
    exact_modern_rgba_recovered=True,
)
CLOCK_ALERT = FastViewClockColor(
    native_color_16=None,
    source_rgb8=SOURCE_CLOCK_ALERT_RGB8,
    exact_modern_rgba_recovered=False,
)


@dataclass(frozen=True)
class FastViewClockState:
    text: str
    color: FastViewClockColor
    second_half_latched: bool = False
    post_90_latched: bool = False
    penalties_latched: bool = False
    last_numeric_tick: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise FastViewClockError("clock text must be a string")
        if type(self.color) is not FastViewClockColor:
            raise FastViewClockError("clock color must use exact source record")
        for name in (
            "second_half_latched",
            "post_90_latched",
            "penalties_latched",
        ):
            if type(getattr(self, name)) is not bool:
                raise FastViewClockError(f"{name} must be boolean")
        if self.last_numeric_tick is not None and (
            type(self.last_numeric_tick) is not int or self.last_numeric_tick < 0
        ):
            raise FastViewClockError("last numeric tick must be non-negative or None")


def _localized(label: str) -> str:
    try:
        _global_va, _entry, _string_id, text = SOURCE_CLOCK_LOCALIZED_TEXT[label]
    except KeyError as exc:
        raise FastViewClockError("unknown source clock localized label") from exc
    return text


def initial_fastview_clock_state() -> FastViewClockState:
    """Mirror the constructor's empty source string and native white endpoint."""
    return FastViewClockState(text="", color=CLOCK_WHITE)


def fastview_clock_numeric_value(global_tick_value: int) -> int:
    """Return the exact unsigned value ClockControl passes to its formatter."""
    if type(global_tick_value) is not int or global_tick_value < 0:
        raise FastViewClockError(
            "EventGlobalTick numeric value must be a non-negative integer"
        )
    return global_tick_value


def _render_numeric_tick(
    state: FastViewClockState,
    global_tick_value: int,
) -> FastViewClockState:
    value = fastview_clock_numeric_value(global_tick_value)
    color = state.color
    if (
        value >= SOURCE_CLOCK_FIRST_HALF_SWITCH_VALUE
        and not state.second_half_latched
    ):
        color = CLOCK_ALERT
    if (
        value >= SOURCE_CLOCK_SECOND_HALF_SWITCH_VALUE
        and not state.post_90_latched
    ):
        color = CLOCK_ALERT
    return replace(
        state,
        text=f"{value} {_localized('mins')}",
        color=color,
        last_numeric_tick=value,
    )


def apply_clock_global_tick(
    state: FastViewClockState,
    global_tick_value: int,
) -> FastViewClockState:
    """Mirror EventGlobalTick receiver gating and numeric text update.

    Native receiver 0x51EDB0 ignores tick value 0 and ignores all later ticks
    after the penalties latch is set.
    """
    if type(state) is not FastViewClockState:
        raise FastViewClockError("clock update requires exact source state")
    value = fastview_clock_numeric_value(global_tick_value)
    if value == 0 or state.penalties_latched:
        return state
    return _render_numeric_tick(state, value)


def apply_clock_half_time(state: FastViewClockState) -> FastViewClockState:
    if type(state) is not FastViewClockState:
        raise FastViewClockError("clock update requires exact source state")
    return replace(state, text=_localized("half_time"), color=CLOCK_WHITE)


def apply_clock_second_half(state: FastViewClockState) -> FastViewClockState:
    if type(state) is not FastViewClockState:
        raise FastViewClockError("clock update requires exact source state")
    # 0x51EFB0 sets +0x6C before directly calling 0x51EDD0 with 46.
    latched = replace(state, second_half_latched=True)
    return _render_numeric_tick(latched, SOURCE_CLOCK_FIRST_HALF_SWITCH_VALUE)


def apply_clock_full_time(state: FastViewClockState) -> FastViewClockState:
    if type(state) is not FastViewClockState:
        raise FastViewClockError("clock update requires exact source state")
    return replace(
        state,
        text=_localized("full_time"),
        color=CLOCK_WHITE,
        post_90_latched=True,
    )


def apply_clock_extra_time(state: FastViewClockState) -> FastViewClockState:
    if type(state) is not FastViewClockState:
        raise FastViewClockError("clock update requires exact source state")
    return replace(
        state,
        text=_localized("extra_time"),
        color=CLOCK_ALERT,
        post_90_latched=True,
    )


def apply_clock_penalties(state: FastViewClockState) -> FastViewClockState:
    if type(state) is not FastViewClockState:
        raise FastViewClockError("clock update requires exact source state")
    return replace(
        state,
        text=_localized("penalties"),
        color=CLOCK_ALERT,
        penalties_latched=True,
    )


def possession_array_index_for_global_tick(global_tick_value: int) -> int:
    """Return the exact MatchIterator quotient used for the possession arrays.

    MatchIterator only enters the EventPossession branch when the incoming
    EventGlobalTick value is divisible by five. The quotient is then passed to
    the source statistics lookup at 0x631240.
    """
    value = fastview_clock_numeric_value(global_tick_value)
    if value % SOURCE_POSSESSION_TICK_DIVISOR:
        raise FastViewClockError(
            "EventPossession array lookup requires a GlobalTick divisible by five"
        )
    return value // SOURCE_POSSESSION_TICK_DIVISOR


def fastview_clock_contract() -> dict:
    return {
        "constructor_va": SOURCE_CLOCK_CONSTRUCTOR_VA,
        "text_constructor_callsite_va": SOURCE_CLOCK_TEXT_CONSTRUCTOR_CALLSITE_VA,
        "textcontrol_offset": SOURCE_CLOCK_TEXTCONTROL_OFFSET,
        "text_rect": SOURCE_CLOCK_TEXT_RECT,
        "text_style_index": SOURCE_CLOCK_TEXT_STYLE_INDEX,
        "text_raw_flags": SOURCE_CLOCK_TEXT_RAW_FLAGS,
        "text_render_flags": SOURCE_CLOCK_TEXT_RENDER_FLAGS,
        "native_white_16": SOURCE_CLOCK_NATIVE_WHITE_16,
        "alert_source_rgb8": SOURCE_CLOCK_ALERT_RGB8,
        "receiver_offsets": tuple(SOURCE_CLOCK_RECEIVER_OFFSETS.items()),
        "receiver_vtables": tuple(SOURCE_CLOCK_RECEIVER_VTABLES.items()),
        "receiver_callbacks": tuple(SOURCE_CLOCK_RECEIVER_CALLBACKS.items()),
        "localized_text": tuple(SOURCE_CLOCK_LOCALIZED_TEXT.items()),
        "second_half_latch_offset": SOURCE_CLOCK_SECOND_HALF_LATCH_OFFSET,
        "post_90_latch_offset": SOURCE_CLOCK_POST_90_LATCH_OFFSET,
        "penalties_latch_offset": SOURCE_CLOCK_PENALTIES_LATCH_OFFSET,
        "clock_text_state_machine_recovered": True,
        "alert_packed16_value_recovered": False,
        "alert_modern_rgba_recovered": False,
        "clock_raster_integrated": False,
        "global_fastview_z_order_recovered": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }

"""Source-closed GoalFlash row contract for FM2001 FastView.

GoalFlash owns two identical five-TextControl rows. MSVC RTTI proves three typed
receivers: EventGoal, EventScore and EventPenaltyShootoutShot. This module keeps
the still-unproven EventGoal string/dword labels neutral while preserving exact
formatting, row geometry, style, raw flags and side-highlight behavior.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_possession_figures import (
    SOURCE_TEXT_FONT_BYTE_SIZE,
    SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT,
    SOURCE_TEXT_FONT_PATH,
    SOURCE_TEXT_FONT_SHA256,
    SOURCE_TEXT_STYLE_INDEX,
)


class FastViewGoalFlashError(ValueError):
    pass


GOALFLASH_CONSTRUCTOR_VA = 0x51C700
GOALFLASH_CHILD_CONSTRUCTOR_VA = 0x51BE20
GOALFLASH_CHILD_COUNT = 2
GOALFLASH_RECEIVER_EVENT_GOAL_OFFSET = 0x00
GOALFLASH_RECEIVER_EVENT_SCORE_OFFSET = 0x04
GOALFLASH_RECEIVER_PENALTY_SHOT_OFFSET = 0x08
GOALFLASH_EVENT_GOAL_CALLBACK_VA = 0x51CD70
GOALFLASH_EVENT_SCORE_CALLBACK_VA = 0x51CE80
GOALFLASH_PENALTY_SHOT_CALLBACK_VA = 0x51CEA0

GOALFLASH_RECEIVER_TYPES = (
    "Receiver<EventGoal>",
    "Receiver<EventScore>",
    "Receiver<EventPenaltyShootoutShot>",
)

GOALFLASH_NORMAL_FORMATTER_VA = 0x51C230
GOALFLASH_PENALTY_FORMATTER_VA = 0x51C3F0
GOALFLASH_MOVE_ROW_VA = 0x51C5F0
GOALFLASH_PERCENT_U_FORMAT_VA = 0x828D3C
GOALFLASH_PERCENT_U_FORMAT = "%u"
GOALFLASH_NORMAL_OPEN = " ("
GOALFLASH_NORMAL_SEPARATOR = " "
GOALFLASH_NORMAL_CLOSE = ")"
GOALFLASH_PENALTY_MISSED = " missed"
GOALFLASH_PENALTY_SCORED = " scored"

GOALFLASH_STYLE_INDEX = 1
GOALFLASH_FONT_PATH = SOURCE_TEXT_FONT_PATH
GOALFLASH_FONT_SHA256 = SOURCE_TEXT_FONT_SHA256
GOALFLASH_FONT_BYTE_SIZE = SOURCE_TEXT_FONT_BYTE_SIZE
GOALFLASH_FONT_NATIVE_LINE_HEIGHT = SOURCE_TEXT_FONT_NATIVE_LINE_HEIGHT

ACTIVE_RGB = (255, 255, 255)
INACTIVE_RGB = (0, 0, 0)
ACTIVE_NATIVE_COLOR_GLOBAL_VA = 0x87763C
INACTIVE_NATIVE_COLOR_GLOBAL_VA = 0x877640

# Control storage order is also final left-to-right runtime order.
CONTROL_STORAGE_OFFSETS = (0x04, 0x08, 0x10, 0x0C, 0x14)
CONTROL_X_OFFSETS = (0, 134, 164, 194, 328)
CONTROL_WIDTHS = (134, 30, 30, 134, 160)
CONTROL_HEIGHT = 33
CONTROL_RAW_FLAGS = (0x22, 0x22, 0x21, 0x21, 0x1022)
CONTROL_RENDER_FLAGS = tuple(value | 0x08 for value in CONTROL_RAW_FLAGS)
CONTROL_HORIZONTAL_ALIGNMENT = ("right", "right", "left", "left", "right")
CONTROL_VERTICAL_ALIGNMENT = ("center",) * 5
CONTROL_EXTRA_0X1000_SEMANTIC_RECOVERED = False

EVENT_SCORE_SOURCE_OFFSETS = (0x0C, 0x10, 0x14, 0x18)
EVENT_GOAL_SOURCE_OFFSETS = (0x00, 0x04, 0x08, 0x0C, 0x10)
PENALTY_SHOT_SOURCE_OFFSETS = (0x00, 0x04, 0x08, 0x0C, 0x10, 0x24)


@dataclass(frozen=True)
class GoalFlashCellContract:
    index: int
    storage_offset: int
    x_offset: int
    width: int
    height: int
    raw_flags: int
    render_flags: int
    horizontal_alignment: str
    vertical_alignment: str

    def __post_init__(self) -> None:
        if not 0 <= self.index < 5:
            raise FastViewGoalFlashError("GoalFlash cell index must be 0..4")
        if self.height != CONTROL_HEIGHT or self.width <= 0:
            raise FastViewGoalFlashError("GoalFlash cell geometry drifted")
        if self.render_flags != (self.raw_flags | 0x08):
            raise FastViewGoalFlashError("GoalFlash render flags drifted")


GOALFLASH_CELLS = tuple(
    GoalFlashCellContract(
        index=index,
        storage_offset=CONTROL_STORAGE_OFFSETS[index],
        x_offset=CONTROL_X_OFFSETS[index],
        width=CONTROL_WIDTHS[index],
        height=CONTROL_HEIGHT,
        raw_flags=CONTROL_RAW_FLAGS[index],
        render_flags=CONTROL_RENDER_FLAGS[index],
        horizontal_alignment=CONTROL_HORIZONTAL_ALIGNMENT[index],
        vertical_alignment=CONTROL_VERTICAL_ALIGNMENT[index],
    )
    for index in range(5)
)


def goalflash_row_rects(
    row_x: int,
    row_y: int,
) -> tuple[tuple[int, int, int, int], ...]:
    if type(row_x) is not int or type(row_y) is not int:
        raise FastViewGoalFlashError("GoalFlash row position must be integer")
    return tuple(
        (
            row_x + cell.x_offset,
            row_y,
            row_x + cell.x_offset + cell.width,
            row_y + cell.height,
        )
        for cell in GOALFLASH_CELLS
    )


def normal_goalflash_texts(
    club_a: str,
    score_a: int,
    score_b: int,
    club_b: str,
    event_text: str,
    event_value: int,
) -> tuple[str, str, str, str, str]:
    for label, text in (
        ("club_a", club_a),
        ("club_b", club_b),
        ("event_text", event_text),
    ):
        if not isinstance(text, str):
            raise FastViewGoalFlashError(f"{label} must be string")
    for label, value in (
        ("score_a", score_a),
        ("score_b", score_b),
        ("event_value", event_value),
    ):
        if type(value) is not int or value < 0:
            raise FastViewGoalFlashError(f"{label} must be non-negative integer")
    return (
        club_a,
        f"{score_a}",
        f"{score_b}",
        club_b,
        f" ({event_text} {event_value})",
    )


def penalty_goalflash_texts(
    club_a: str,
    score_a: int,
    score_b: int,
    club_b: str,
    event_text: str,
    *,
    scored: bool,
) -> tuple[str, str, str, str, str]:
    if type(scored) is not bool:
        raise FastViewGoalFlashError("scored must be boolean")
    base = normal_goalflash_texts(
        club_a, score_a, score_b, club_b, event_text, 0
    )
    return base[:4] + (
        event_text + (GOALFLASH_PENALTY_SCORED if scored else GOALFLASH_PENALTY_MISSED),
    )


def normal_goalflash_active_cells(side_flag: bool) -> tuple[int, int]:
    if type(side_flag) is not bool:
        raise FastViewGoalFlashError("side_flag must be boolean")
    return (0, 1) if side_flag else (2, 3)


def penalty_goalflash_active_cells(
    side_flag: bool,
    *,
    scored: bool,
) -> tuple[int, ...]:
    if type(side_flag) is not bool or type(scored) is not bool:
        raise FastViewGoalFlashError("side_flag and scored must be boolean")
    if not scored:
        return ()
    return normal_goalflash_active_cells(side_flag)


def goalflash_source_contract() -> dict:
    return {
        "constructor_va": GOALFLASH_CONSTRUCTOR_VA,
        "child_constructor_va": GOALFLASH_CHILD_CONSTRUCTOR_VA,
        "child_count": GOALFLASH_CHILD_COUNT,
        "receiver_types": GOALFLASH_RECEIVER_TYPES,
        "receiver_offsets": (
            GOALFLASH_RECEIVER_EVENT_GOAL_OFFSET,
            GOALFLASH_RECEIVER_EVENT_SCORE_OFFSET,
            GOALFLASH_RECEIVER_PENALTY_SHOT_OFFSET,
        ),
        "receiver_callbacks": (
            GOALFLASH_EVENT_GOAL_CALLBACK_VA,
            GOALFLASH_EVENT_SCORE_CALLBACK_VA,
            GOALFLASH_PENALTY_SHOT_CALLBACK_VA,
        ),
        "style_index": GOALFLASH_STYLE_INDEX,
        "font_path": GOALFLASH_FONT_PATH,
        "font_sha256": GOALFLASH_FONT_SHA256,
        "font_byte_size": GOALFLASH_FONT_BYTE_SIZE,
        "font_native_line_height": GOALFLASH_FONT_NATIVE_LINE_HEIGHT,
        "cells": GOALFLASH_CELLS,
        "normal_event_string_semantic_recovered": False,
        "normal_event_dword0_semantic_recovered": False,
        "penalty_suffix_semantics_recovered": True,
        "dynamic_row_position_recovered": True,
        "absolute_flash_timing_position_recovered": False,
        "goalflash_pixels_rasterized": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }

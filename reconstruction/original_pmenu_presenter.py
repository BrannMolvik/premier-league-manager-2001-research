"""Source-bounded visible-row presenter for FM2001's PMenu shell.

The original tree walker emits each root in construction order and descends
into the selected/expanded root before continuing to the next root. This module
projects that proven ordering and geometry without inventing text placement or
meanings for the remaining neutral animation bits.
"""
from __future__ import annotations

from dataclasses import dataclass

from original_pmenu_chrome import (
    PMENU_CHILDREN_BY_ARRAY_VA,
    PMENU_CHILD_ARROW_RESOURCE,
    PMENU_CHILD_BOX_RESOURCE,
    PMENU_FONT_SOURCE_PATH,
    PMENU_FRESH_SELECTED_CHILD_ID,
    PMENU_FRESH_SELECTED_ROOT_ID,
    PMENU_LIST_ROW_CAPACITY,
    PMENU_LIST_SCREEN_ORIGIN,
    PMENU_LIST_SIZE,
    PMENU_RESOURCES,
    PMENU_ROOT_NODES,
    PMENU_ROW_HEIGHT,
    PMENU_TITLE_ARROW_RESOURCE,
    PMENU_TITLE_BOX_RESOURCE,
    OriginalPMenuNode,
)


class OriginalPMenuPresentationError(ValueError):
    """The recovered PMenu tree cannot be projected safely."""


@dataclass(frozen=True)
class OriginalPMenuVisibleRow:
    visible_index: int
    y: int
    height: int
    row_kind: str
    menu_id: int
    caption: str
    selected: bool
    expanded: bool
    arrow_source_path: str
    box_source_path: str


@dataclass(frozen=True)
class OriginalPMenuSnapshot:
    list_screen_origin: tuple[int, int]
    list_size: tuple[int, int]
    row_capacity: int
    row_step: int
    selected_root_id: int
    selected_child_id: int
    font_source_path: str
    resource_source_paths: tuple[str, ...]
    rows: tuple[OriginalPMenuVisibleRow, ...]


def _children(root: OriginalPMenuNode) -> tuple[OriginalPMenuNode, ...]:
    if root.children_array_va is None:
        return ()
    try:
        return PMENU_CHILDREN_BY_ARRAY_VA[root.children_array_va]
    except KeyError as exc:
        raise OriginalPMenuPresentationError(
            f"PMenu root {root.menu_id:#x} has no recovered child array"
        ) from exc


def build_pmenu_snapshot(selected_child_id: int) -> OriginalPMenuSnapshot:
    """Project the native one-root-expanded menu for a recovered child ID."""
    if type(selected_child_id) is not int:
        raise OriginalPMenuPresentationError("PMenu child ID must be an integer")

    selected_root = None
    selected_child = None
    for root in PMENU_ROOT_NODES:
        for child in _children(root):
            if child.menu_id == selected_child_id:
                if selected_child is not None:
                    raise OriginalPMenuPresentationError(
                        f"PMenu child ID {selected_child_id:#x} is ambiguous"
                    )
                selected_root = root
                selected_child = child
    if selected_root is None or selected_child is None:
        raise OriginalPMenuPresentationError(
            f"PMenu child ID {selected_child_id:#x} is not source-proven"
        )

    ordered: list[tuple[str, OriginalPMenuNode]] = []
    for root in PMENU_ROOT_NODES:
        ordered.append(("title", root))
        if root is selected_root:
            ordered.extend(("child", child) for child in _children(root))
    if len(ordered) > PMENU_LIST_ROW_CAPACITY:
        raise OriginalPMenuPresentationError(
            "Expanded PMenu tree exceeds the source-proven 16-row list"
        )

    rows = []
    for index, (kind, node) in enumerate(ordered):
        title = kind == "title"
        rows.append(
            OriginalPMenuVisibleRow(
                visible_index=index,
                y=index * PMENU_ROW_HEIGHT,
                height=PMENU_ROW_HEIGHT,
                row_kind=kind,
                menu_id=node.menu_id,
                caption=node.require_original_text(),
                selected=node is selected_child or node is selected_root,
                expanded=node is selected_root,
                arrow_source_path=(
                    PMENU_TITLE_ARROW_RESOURCE.source_path
                    if title
                    else PMENU_CHILD_ARROW_RESOURCE.source_path
                ),
                box_source_path=(
                    PMENU_TITLE_BOX_RESOURCE.source_path
                    if title
                    else PMENU_CHILD_BOX_RESOURCE.source_path
                ),
            )
        )

    return OriginalPMenuSnapshot(
        list_screen_origin=PMENU_LIST_SCREEN_ORIGIN,
        list_size=PMENU_LIST_SIZE,
        row_capacity=PMENU_LIST_ROW_CAPACITY,
        row_step=PMENU_ROW_HEIGHT,
        selected_root_id=selected_root.menu_id,
        selected_child_id=selected_child.menu_id,
        font_source_path=PMENU_FONT_SOURCE_PATH,
        resource_source_paths=tuple(resource.source_path for resource in PMENU_RESOURCES),
        rows=tuple(rows),
    )


def build_fresh_pmenu_snapshot() -> OriginalPMenuSnapshot:
    """Project the executable-proven fresh Team -> Squad selection."""
    snapshot = build_pmenu_snapshot(PMENU_FRESH_SELECTED_CHILD_ID)
    if snapshot.selected_root_id != PMENU_FRESH_SELECTED_ROOT_ID:
        raise OriginalPMenuPresentationError("Fresh PMenu root identity mismatch")
    return snapshot

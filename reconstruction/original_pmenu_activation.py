"""Executable-backed PMenu row action contract for FM2001.

Recovery 173 traces the action callback owned by each concrete PMenu row.
The generic child-control dispatcher calls parent-row virtual slot +0x10 after
the child control accepts its source event. Title rows mutate the static
menu-tree open bit. Child rows call the real management panel factory with the
node's +0x0C menu/panel ID.

This module deliberately starts after source control/event acceptance. It does
not claim that arbitrary rectangle containment, a modern Tk click, or any
particular mouse/keyboard event is equivalent to the original event object.
"""
from __future__ import annotations

from dataclasses import dataclass

from original_pmenu_chrome import (
    PMENU_CHILDREN_BY_ARRAY_VA,
    PMENU_NODE_SELECTED_OR_EXPANDED_BIT,
    PMENU_ROOT_NODES,
    OriginalPMenuNode,
)


class OriginalPMenuActivationError(ValueError):
    """A requested row action is outside the recovered executable contract."""


PMENU_NODE_MENU_ID_OFFSET = 0x0C
PMENU_NODE_CHILD_ARRAY_OFFSET = 0x10
PMENU_NODE_STATE_FLAGS_OFFSET = 0x14
PMENU_SOURCE_GUARD_BIT_1 = 0x2

PMENU_ROW_ACTION_VTABLE_OFFSET = 0x10
PMENU_BASE_ROW_ACTION_PURECALL_VA = 0x668766
PMENU_TITLE_ROW_ACTION_VA = 0x47AC60
PMENU_CHILD_ROW_ACTION_VA = 0x47AD60

PMENU_CHILD_PARENT_OFFSET = 0x24
PMENU_GENERIC_CONTROL_DISPATCH_VA = 0x64FE50
PMENU_GENERIC_PARENT_ACTION_CALL_VA = 0x64FF21

PMENU_TREE_ORDINAL_TRAVERSAL_VA = 0x60CA70
PMENU_MANAGEMENT_PANEL_FACTORY_VA = 0x47AEC0
PMENU_OWNER_REFRESH_VTABLE_OFFSET = 0xA8


@dataclass(frozen=True)
class OriginalPMenuRowAction:
    row_kind: str
    menu_id: int
    source_flags_before: int
    accepted: bool
    action_kind: str
    source_flags_after: int
    clear_open_bit_on_other_expandable_roots: bool
    panel_factory_va: int | None
    panel_factory_arguments: tuple[int, int] | None
    owner_refresh_vtable_offset: int | None
    rejection_reason: str | None


def _children(root: OriginalPMenuNode) -> tuple[OriginalPMenuNode, ...]:
    if root.children_array_va is None:
        return ()
    try:
        return PMENU_CHILDREN_BY_ARRAY_VA[root.children_array_va]
    except KeyError as exc:
        raise OriginalPMenuActivationError(
            f"PMenu root {root.menu_id:#x} has no recovered child array"
        ) from exc


def source_pmenu_node(row_kind: str, menu_id: int) -> OriginalPMenuNode:
    """Resolve one source node without confusing duplicate root/child IDs."""
    if row_kind not in {"title", "child"}:
        raise OriginalPMenuActivationError(
            "PMenu row kind must be 'title' or 'child'"
        )
    if type(menu_id) is not int:
        raise OriginalPMenuActivationError("PMenu menu ID must be an integer")

    if row_kind == "title":
        matches = [node for node in PMENU_ROOT_NODES if node.menu_id == menu_id]
    else:
        matches = [
            child
            for root in PMENU_ROOT_NODES
            for child in _children(root)
            if child.menu_id == menu_id
        ]

    if len(matches) != 1:
        raise OriginalPMenuActivationError(
            f"PMenu {row_kind} ID {menu_id:#x} is not uniquely source-proven"
        )
    node = matches[0]
    has_children = node.children_array_va is not None
    if has_children != (row_kind == "title"):
        raise OriginalPMenuActivationError(
            f"PMenu {row_kind} topology mismatch for ID {menu_id:#x}"
        )
    return node


def _rejected(
    *,
    row_kind: str,
    menu_id: int,
    source_flags: int,
    reason: str,
) -> OriginalPMenuRowAction:
    return OriginalPMenuRowAction(
        row_kind=row_kind,
        menu_id=menu_id,
        source_flags_before=source_flags,
        accepted=False,
        action_kind="no_action",
        source_flags_after=source_flags,
        clear_open_bit_on_other_expandable_roots=False,
        panel_factory_va=None,
        panel_factory_arguments=None,
        owner_refresh_vtable_offset=None,
        rejection_reason=reason,
    )


def resolve_pmenu_row_action(
    row_kind: str,
    menu_id: int,
    source_flags: int,
) -> OriginalPMenuRowAction:
    """Mirror the recovered title/child action after source-event acceptance.

    source_flags is static menu node +0x14. Bit 0 is source-proven as the
    selected/expanded bit. Bit 1 remains a neutral child-action gate because
    its higher-level UI meaning is not needed by this contract.
    """
    source_pmenu_node(row_kind, menu_id)
    if type(source_flags) is not int or source_flags < 0:
        raise OriginalPMenuActivationError(
            "PMenu source flags must be a non-negative integer"
        )

    if source_flags & PMENU_NODE_SELECTED_OR_EXPANDED_BIT:
        return _rejected(
            row_kind=row_kind,
            menu_id=menu_id,
            source_flags=source_flags,
            reason="source_bit0_already_set",
        )

    if row_kind == "title":
        return OriginalPMenuRowAction(
            row_kind=row_kind,
            menu_id=menu_id,
            source_flags_before=source_flags,
            accepted=True,
            action_kind="expand_root",
            source_flags_after=(
                source_flags | PMENU_NODE_SELECTED_OR_EXPANDED_BIT
            ),
            clear_open_bit_on_other_expandable_roots=True,
            panel_factory_va=None,
            panel_factory_arguments=None,
            owner_refresh_vtable_offset=PMENU_OWNER_REFRESH_VTABLE_OFFSET,
            rejection_reason=None,
        )

    if source_flags & PMENU_SOURCE_GUARD_BIT_1:
        return _rejected(
            row_kind=row_kind,
            menu_id=menu_id,
            source_flags=source_flags,
            reason="source_bit1_set",
        )

    return OriginalPMenuRowAction(
        row_kind=row_kind,
        menu_id=menu_id,
        source_flags_before=source_flags,
        accepted=True,
        action_kind="open_panel",
        source_flags_after=(
            source_flags | PMENU_NODE_SELECTED_OR_EXPANDED_BIT
        ),
        clear_open_bit_on_other_expandable_roots=False,
        panel_factory_va=PMENU_MANAGEMENT_PANEL_FACTORY_VA,
        panel_factory_arguments=(menu_id, 0),
        owner_refresh_vtable_offset=PMENU_OWNER_REFRESH_VTABLE_OFFSET,
        rejection_reason=None,
    )

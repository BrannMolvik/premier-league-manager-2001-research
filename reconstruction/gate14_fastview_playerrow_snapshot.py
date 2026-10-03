"""Complete source-backed FastView PlayerRow presentation snapshot.

This composes already source-closed PlayerRow primitives. It does not calculate
match outcomes, update gameplay state, or invent event history. Goal/own-goal
text is optional because the source counters start at zero but their
parenthesized text is written only by the corresponding typed callbacks.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_fastview_player_history import (
    FastViewPlayerHistories,
    derive_fastview_energy,
)
from gate14_fastview_team import (
    FastViewEnergyBarState,
    FastViewPlayerRowPositionState,
    FastViewPlayerRowTextState,
    FastViewTeamError,
    FastViewTeamResource,
    player_row_form_text_state,
    player_row_name_text_state,
    player_row_position_state,
    player_row_shirt_number_text_state,
    side_contract,
    team_row_energy_bar_state,
    team_row_name_resource,
    team_row_rects,
    team_row_text_rect,
)


@dataclass(frozen=True)
class FastViewPlayerRowSnapshot:
    side_index: int
    row_index: int
    name_grid_resource: FastViewTeamResource
    shirt_number: FastViewPlayerRowTextState
    position: FastViewPlayerRowPositionState
    player_name: FastViewPlayerRowTextState
    goal_count: FastViewPlayerRowTextState | None
    own_goal_count: FastViewPlayerRowTextState | None
    form: FastViewPlayerRowTextState
    energy: FastViewEnergyBarState

    @property
    def text_cells(self) -> tuple[
        FastViewPlayerRowTextState | FastViewPlayerRowPositionState | None, ...
    ]:
        """Return the six source-order text cells without filling absent events."""
        return (
            self.shirt_number,
            self.position,
            self.player_name,
            self.goal_count,
            self.own_goal_count,
            self.form,
        )


@dataclass(frozen=True)
class FastViewPlayerRowTextRenderInstruction:
    """One source-owned PlayerRow text control without invented localization."""

    text_cell_index: int
    semantic: str
    rect: tuple[int, int, int, int]
    value_kind: str
    value: str | None
    source_color_update: bool = False

    def __post_init__(self) -> None:
        if type(self.text_cell_index) is not int or not 1 <= self.text_cell_index <= 6:
            raise FastViewTeamError("PlayerRow render text cell must be 1..6")
        if not isinstance(self.semantic, str) or not self.semantic:
            raise FastViewTeamError("PlayerRow render semantic must be non-empty")
        if (
            type(self.rect) is not tuple
            or len(self.rect) != 4
            or any(type(value) is not int for value in self.rect)
        ):
            raise FastViewTeamError("PlayerRow render text rect must be four integers")
        if self.value_kind not in {"literal", "localization_key", "unwritten"}:
            raise FastViewTeamError("PlayerRow render value kind is not source-backed")
        if self.value_kind == "unwritten":
            if self.value is not None:
                raise FastViewTeamError("unwritten PlayerRow text cannot carry a value")
        elif not isinstance(self.value, str):
            raise FastViewTeamError(
                "written PlayerRow render value must remain a source string/key"
            )
        if type(self.source_color_update) is not bool:
            raise FastViewTeamError("PlayerRow source_color_update must be boolean")


@dataclass(frozen=True)
class FastViewPlayerRowRenderPlan:
    """Raster-neutral render instructions for one retained PlayerRow snapshot."""

    side_index: int
    row_index: int
    name_grid_resource: FastViewTeamResource
    name_grid_rect: tuple[int, int, int, int]
    static_energy_resource: FastViewTeamResource
    dynamic_energy_resource: FastViewTeamResource
    energy_full_rect: tuple[int, int, int, int]
    energy_dynamic_rect: tuple[int, int, int, int]
    text_instructions: tuple[FastViewPlayerRowTextRenderInstruction, ...]
    raster_ready: bool = False

    def __post_init__(self) -> None:
        if tuple(item.text_cell_index for item in self.text_instructions) != (
            1, 2, 3, 4, 5, 6
        ):
            raise FastViewTeamError(
                "PlayerRow render instructions must preserve source cell order 1..6"
            )
        if self.raster_ready:
            raise FastViewTeamError(
                "PlayerRow raster output is not source-closed in this adapter"
            )


def _validate_snapshot_text_state(
    snapshot: FastViewPlayerRowSnapshot,
    state: FastViewPlayerRowTextState | FastViewPlayerRowPositionState,
    cell_index: int,
    expected_rect: tuple[int, int, int, int],
) -> None:
    if (
        state.side_index != snapshot.side_index
        or state.row_index != snapshot.row_index
        or state.text_cell_index != cell_index
        or state.rect != expected_rect
    ):
        raise FastViewTeamError(
            f"PlayerRow snapshot text cell {cell_index} drifted from source geometry"
        )


def build_fastview_player_row_render_plan(
    snapshot: FastViewPlayerRowSnapshot,
) -> FastViewPlayerRowRenderPlan:
    """Translate retained presentation state without recomputing gameplay state.

    Literal controls stay literal. Position remains a localization key because
    this adapter does not invent a language-table result. Goal/own-goal controls
    remain explicitly unwritten until their typed source callback supplied text.
    The source energy rectangle is preserved exactly, including its below-anchor
    negative-width arithmetic; this layer is not a rasterizer.
    """
    if type(snapshot) is not FastViewPlayerRowSnapshot:
        raise FastViewTeamError(
            "PlayerRow render plan requires an exact retained snapshot"
        )

    name_rect, bar_rect, text_rects = team_row_rects(
        snapshot.side_index,
        snapshot.row_index,
    )
    expected_name = team_row_name_resource(snapshot.side_index, snapshot.row_index)
    if snapshot.name_grid_resource is not expected_name:
        raise FastViewTeamError(
            "PlayerRow snapshot name-grid resource drifted from source row selection"
        )

    contract = side_contract(snapshot.side_index)
    energy = snapshot.energy
    if (
        energy.side_index != snapshot.side_index
        or energy.row_index != snapshot.row_index
        or energy.full_rect != bar_rect
        or energy.static_resource is not contract.static_energy_bar
        or energy.dynamic_resource is not contract.dynamic_energy_bar
    ):
        raise FastViewTeamError(
            "PlayerRow snapshot energy state drifted from source row geometry"
        )

    required_states = (
        (snapshot.shirt_number, 1),
        (snapshot.position, 2),
        (snapshot.player_name, 3),
        (snapshot.form, 6),
    )
    for state, cell_index in required_states:
        _validate_snapshot_text_state(
            snapshot,
            state,
            cell_index,
            text_rects[cell_index - 1],
        )

    for state, cell_index in (
        (snapshot.goal_count, 4),
        (snapshot.own_goal_count, 5),
    ):
        if state is not None:
            _validate_snapshot_text_state(
                snapshot,
                state,
                cell_index,
                text_rects[cell_index - 1],
            )

    instructions = (
        FastViewPlayerRowTextRenderInstruction(
            1,
            snapshot.shirt_number.semantic,
            text_rects[0],
            "literal",
            snapshot.shirt_number.text,
            snapshot.shirt_number.source_color_update,
        ),
        FastViewPlayerRowTextRenderInstruction(
            2,
            "player_position",
            text_rects[1],
            "localization_key",
            snapshot.position.localization_key,
        ),
        FastViewPlayerRowTextRenderInstruction(
            3,
            snapshot.player_name.semantic,
            text_rects[2],
            "literal",
            snapshot.player_name.text,
            snapshot.player_name.source_color_update,
        ),
        FastViewPlayerRowTextRenderInstruction(
            4,
            "player_goal_count",
            text_rects[3],
            "unwritten" if snapshot.goal_count is None else "literal",
            None if snapshot.goal_count is None else snapshot.goal_count.text,
            False if snapshot.goal_count is None
            else snapshot.goal_count.source_color_update,
        ),
        FastViewPlayerRowTextRenderInstruction(
            5,
            "player_own_goal_count",
            text_rects[4],
            "unwritten" if snapshot.own_goal_count is None else "literal",
            None if snapshot.own_goal_count is None else snapshot.own_goal_count.text,
            False if snapshot.own_goal_count is None
            else snapshot.own_goal_count.source_color_update,
        ),
        FastViewPlayerRowTextRenderInstruction(
            6,
            snapshot.form.semantic,
            text_rects[5],
            "literal",
            snapshot.form.text,
            snapshot.form.source_color_update,
        ),
    )

    return FastViewPlayerRowRenderPlan(
        side_index=snapshot.side_index,
        row_index=snapshot.row_index,
        name_grid_resource=snapshot.name_grid_resource,
        name_grid_rect=name_rect,
        static_energy_resource=energy.static_resource,
        dynamic_energy_resource=energy.dynamic_resource,
        energy_full_rect=energy.full_rect,
        energy_dynamic_rect=energy.dynamic_rect,
        text_instructions=instructions,
    )


def _counter_snapshot(
    side_index: int,
    row_index: int,
    displayed_count: int | None,
    *,
    own_goal: bool,
) -> FastViewPlayerRowTextState | None:
    """Represent already-written counter text, or None before any write.

    The source constructor initializes the local counters to zero. The typed
    EventPlayerGoal/EventPlayerOwnGoal callbacks increment and then write
    "(%u)". Therefore None is the faithful state when the caller has no
    evidence that the text callback has run; an integer means the caller is
    explicitly supplying the already-written source counter value.
    """
    if displayed_count is None:
        return None
    if type(displayed_count) is not int or not 0 <= displayed_count <= 0xFFFFFFFF:
        raise FastViewTeamError(
            "PlayerRow displayed goal counter must fit an unsigned source dword"
        )
    cell = 5 if own_goal else 4
    return FastViewPlayerRowTextState(
        semantic="player_own_goal_count" if own_goal else "player_goal_count",
        side_index=side_index,
        row_index=row_index,
        text_cell_index=cell,
        rect=team_row_text_rect(side_index, row_index, cell),
        text=f"({displayed_count:d})",
        stored_value=displayed_count,
        source_color_update=own_goal,
    )


def build_fastview_player_row_snapshot(
    *,
    side_index: int,
    row_index: int,
    shirt_number: int,
    source_position_code: int,
    surname: str,
    first_name_initial: str,
    form_value: int,
    energy_value: int,
    displayed_goal_count: int | None = None,
    displayed_own_goal_count: int | None = None,
) -> FastViewPlayerRowSnapshot:
    """Compose one complete PlayerRow from already-proven presentation state."""
    shirt = player_row_shirt_number_text_state(
        side_index, row_index, shirt_number
    )
    position = player_row_position_state(
        side_index, row_index, source_position_code
    )
    name = player_row_name_text_state(
        side_index, row_index, surname, first_name_initial
    )
    form = player_row_form_text_state(side_index, row_index, form_value)
    energy = team_row_energy_bar_state(side_index, row_index, energy_value)
    goal = _counter_snapshot(
        side_index,
        row_index,
        displayed_goal_count,
        own_goal=False,
    )
    own_goal = _counter_snapshot(
        side_index,
        row_index,
        displayed_own_goal_count,
        own_goal=True,
    )
    return FastViewPlayerRowSnapshot(
        side_index=side_index,
        row_index=row_index,
        name_grid_resource=team_row_name_resource(side_index, row_index),
        shirt_number=shirt,
        position=position,
        player_name=name,
        goal_count=goal,
        own_goal_count=own_goal,
        form=form,
        energy=energy,
    )


def build_fastview_player_row_snapshot_from_histories(
    *,
    side_index: int,
    row_index: int,
    shirt_number: int,
    source_position_code: int,
    surname: str,
    first_name_initial: str,
    histories: FastViewPlayerHistories,
    global_tick: int,
    energy_rng6_roll: int,
    displayed_goal_count: int | None = None,
    displayed_own_goal_count: int | None = None,
) -> FastViewPlayerRowSnapshot:
    """Compose one PlayerRow from retained source histories without replaying match state.

    Form is the exact 0x632FC0 -> 0x6308B0 sample at global_tick. Energy is the
    exact 0x633000 -> 0x630910 derivation using the caller-supplied source-order
    RNG(6) result. This adapter deliberately accepts a resolved RNG result rather
    than an RNG object, so presentation cannot advance or alias gameplay state.
    """
    return build_fastview_player_row_snapshot(
        side_index=side_index,
        row_index=row_index,
        shirt_number=shirt_number,
        source_position_code=source_position_code,
        surname=surname,
        first_name_initial=first_name_initial,
        form_value=histories.form_at_tick(global_tick),
        energy_value=derive_fastview_energy(
            histories,
            global_tick,
            energy_rng6_roll,
        ),
        displayed_goal_count=displayed_goal_count,
        displayed_own_goal_count=displayed_own_goal_count,
    )

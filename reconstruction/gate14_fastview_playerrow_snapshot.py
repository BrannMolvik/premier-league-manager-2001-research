"""Complete source-backed FastView PlayerRow presentation snapshot.

This composes already source-closed PlayerRow primitives. It does not calculate
match outcomes, update gameplay state, or invent event history. Goal/own-goal
text is optional because the source counters start at zero but their
parenthesized text is written only by the corresponding typed callbacks.
"""
from __future__ import annotations

from dataclasses import dataclass

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
    team_row_energy_bar_state,
    team_row_name_resource,
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

"""Presentation-only bridge from retained FastView histories to PlayerRows.

Completed matches already retain the exact 24-sample Condition and match-form
histories consumed by the original FastView PlayerProxy. This module combines
those retained histories with explicit display metadata and caller-supplied
RNG(6) results to build the already source-closed PlayerRow snapshots.

It deliberately does not import match simulation, gameplay controllers, or an
RNG implementation. Missing/mismatched retained histories fail closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from gate14_fastview_player_history import (
    FastViewPlayerHistories,
    FastViewPlayerHistoryError,
)
from gate14_fastview_playerrow_snapshot import (
    FastViewPlayerRowSnapshot,
    build_fastview_player_row_snapshot_from_histories,
)
from gate14_fastview_team import PLAYER_ROW_POSITION_KEYS


class FastViewRetainedPlayerRowError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewRetainedPlayerRowIdentity:
    """Source identity and visible fields required for one PlayerRow."""

    side_index: int
    player_index: int
    row_index: int
    shirt_number: int
    source_position_code: int
    surname: str
    first_name_initial: str
    displayed_goal_count: int | None = None
    displayed_own_goal_count: int | None = None

    def __post_init__(self) -> None:
        if type(self.side_index) is not int or self.side_index not in (0, 1):
            raise FastViewRetainedPlayerRowError("PlayerRow side_index must be 0 or 1")
        if type(self.player_index) is not int or not 0 <= self.player_index < 18:
            raise FastViewRetainedPlayerRowError(
                "PlayerRow source player_index must be in 0..17"
            )
        if type(self.row_index) is not int or self.row_index < 0:
            raise FastViewRetainedPlayerRowError(
                "PlayerRow visible row_index must be non-negative"
            )
        if type(self.shirt_number) is not int or not 0 <= self.shirt_number <= 0xFF:
            raise FastViewRetainedPlayerRowError(
                "PlayerRow shirt number must fit an unsigned source byte"
            )
        if type(self.source_position_code) is not int or not (
            0 <= self.source_position_code < len(PLAYER_ROW_POSITION_KEYS)
        ):
            raise FastViewRetainedPlayerRowError(
                "PlayerRow source position code must index the 0..19 source table"
            )
        if not isinstance(self.surname, str) or not self.surname:
            raise FastViewRetainedPlayerRowError(
                "PlayerRow surname must be a non-empty source string"
            )
        if (
            not isinstance(self.first_name_initial, str)
            or len(self.first_name_initial) != 1
        ):
            raise FastViewRetainedPlayerRowError(
                "PlayerRow first-name initial must be exactly one character"
            )
        for label, value in (
            ("goal", self.displayed_goal_count),
            ("own-goal", self.displayed_own_goal_count),
        ):
            if value is not None and (
                type(value) is not int or not 0 <= value <= 0xFFFFFFFF
            ):
                raise FastViewRetainedPlayerRowError(
                    f"PlayerRow displayed {label} count must fit uint32"
                )

    @property
    def source_key(self) -> tuple[int, int]:
        return (self.side_index, self.player_index)

    @property
    def row_key(self) -> tuple[int, int]:
        return (self.side_index, self.row_index)


def _retained_history_map(
    values: object,
    *,
    label: str,
) -> dict[tuple[int, int], tuple[int, ...]]:
    if type(values) is not tuple:
        raise FastViewRetainedPlayerRowError(
            f"retained FastView {label} histories must be a tuple"
        )

    result: dict[tuple[int, int], tuple[int, ...]] = {}
    for item in values:
        try:
            side_index = getattr(item, "side_index")
            player_index = getattr(item, "player_index")
            samples = getattr(item, "samples")
        except AttributeError as exc:
            raise FastViewRetainedPlayerRowError(
                f"retained FastView {label} history lacks source identity/samples"
            ) from exc

        if type(side_index) is not int or side_index not in (0, 1):
            raise FastViewRetainedPlayerRowError(
                f"retained FastView {label} history side_index is invalid"
            )
        if type(player_index) is not int or not 0 <= player_index < 18:
            raise FastViewRetainedPlayerRowError(
                f"retained FastView {label} history player_index is invalid"
            )
        if type(samples) is not tuple:
            raise FastViewRetainedPlayerRowError(
                f"retained FastView {label} samples must remain a tuple"
            )

        key = (side_index, player_index)
        if key in result:
            raise FastViewRetainedPlayerRowError(
                f"duplicate retained FastView {label} history identity {key}"
            )
        result[key] = samples

    return result


def build_fastview_player_rows_from_retained_histories(
    result,
    rows: tuple[FastViewRetainedPlayerRowIdentity, ...],
    *,
    global_tick: int,
    energy_rng6_rolls: Mapping[tuple[int, int], int],
) -> tuple[FastViewPlayerRowSnapshot, ...]:
    """Build PlayerRows without replaying simulation or consuming RNG.

    The result object is intentionally structural. The presentation layer
    requires only fastview_condition_histories and fastview_form_histories,
    keeping this adapter independent from the match-simulation implementation.

    Every requested player requires exactly one explicit source RNG(6) result.
    Extra or missing rolls are rejected so a caller cannot silently misalign
    the presentation RNG sequence.
    """
    if type(rows) is not tuple or any(
        type(row) is not FastViewRetainedPlayerRowIdentity for row in rows
    ):
        raise FastViewRetainedPlayerRowError(
            "rows must be an explicit tuple of retained PlayerRow identities"
        )
    if type(global_tick) is not int or global_tick < 0:
        raise FastViewRetainedPlayerRowError(
            "FastView global_tick must be a non-negative integer"
        )
    if not isinstance(energy_rng6_rolls, Mapping):
        raise FastViewRetainedPlayerRowError(
            "energy_rng6_rolls must be an explicit source-identity mapping"
        )

    source_keys = tuple(row.source_key for row in rows)
    row_keys = tuple(row.row_key for row in rows)
    if len(set(source_keys)) != len(source_keys):
        raise FastViewRetainedPlayerRowError(
            "one retained source player cannot occupy multiple requested rows"
        )
    if len(set(row_keys)) != len(row_keys):
        raise FastViewRetainedPlayerRowError(
            "duplicate FastView PlayerRow visible slot is not allowed"
        )

    try:
        condition_values = getattr(result, "fastview_condition_histories")
        form_values = getattr(result, "fastview_form_histories")
    except AttributeError as exc:
        raise FastViewRetainedPlayerRowError(
            "completed result does not retain FastView histories"
        ) from exc

    conditions = _retained_history_map(condition_values, label="Condition")
    forms = _retained_history_map(form_values, label="form")
    if set(conditions) != set(forms):
        raise FastViewRetainedPlayerRowError(
            "retained FastView Condition/form history identities differ"
        )

    roll_keys = set(energy_rng6_rolls)
    expected_keys = set(source_keys)
    if roll_keys != expected_keys:
        raise FastViewRetainedPlayerRowError(
            "energy RNG(6) results must exactly cover requested source players"
        )
    if any(
        type(key) is not tuple
        or len(key) != 2
        or type(key[0]) is not int
        or type(key[1]) is not int
        for key in roll_keys
    ):
        raise FastViewRetainedPlayerRowError(
            "energy RNG(6) keys must be (side_index, player_index) tuples"
        )

    output: list[FastViewPlayerRowSnapshot] = []
    for row in rows:
        key = row.source_key
        if key not in conditions:
            raise FastViewRetainedPlayerRowError(
                f"requested PlayerRow source identity {key} has no retained histories"
            )

        try:
            histories = FastViewPlayerHistories(
                condition=conditions[key],
                match_form=forms[key],
            )
        except FastViewPlayerHistoryError as exc:
            raise FastViewRetainedPlayerRowError(
                f"retained FastView histories for {key} are invalid"
            ) from exc

        roll = energy_rng6_rolls[key]
        if type(roll) is not int or not 0 <= roll < 6:
            raise FastViewRetainedPlayerRowError(
                f"energy RNG(6) result for {key} must be in 0..5"
            )

        output.append(
            build_fastview_player_row_snapshot_from_histories(
                side_index=row.side_index,
                row_index=row.row_index,
                shirt_number=row.shirt_number,
                source_position_code=row.source_position_code,
                surname=row.surname,
                first_name_initial=row.first_name_initial,
                histories=histories,
                global_tick=global_tick,
                energy_rng6_roll=roll,
                displayed_goal_count=row.displayed_goal_count,
                displayed_own_goal_count=row.displayed_own_goal_count,
            )
        )

    return tuple(output)

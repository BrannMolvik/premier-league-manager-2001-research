"""Bounded source-backed shell for FM2001 semantic FastView output.

This module is intentionally smaller than the final Gate-14 match presentation.
Persisted executable evidence proves a FastViewPanel layer, a ScoreComposite,
and PossessionFigures that prints the three EventPossession percentages. Exact
panel geometry, team screen orientation, commentary, sound cues and 3D
choreography are not yet source-closed, so this shell exposes none of them.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_fastview_clock import possession_array_index_for_global_tick
from gate14_fastview_playerrow_snapshot import FastViewPlayerRowSnapshot
from human_match_presentation import HumanMatchPresentation
from match_events import MatchEvent, PossessionRecord


SOURCE_BACKED_COMPONENTS = (
    "FastViewPanel",
    "ScoreComposite",
    "PossessionFigures",
    "PossessionDiagram",
)


@dataclass(frozen=True)
class FastViewShellEvent:
    """One existing match event exposed through recovered FastView semantics."""

    sequence: int
    minute: int
    score_after: tuple[int, int]
    sender_name: str | None
    event: MatchEvent


@dataclass(frozen=True)
class PossessionFiguresState:
    """The exact three printed percentages plus unresolved territory orientation."""

    sequence: int
    calculation_minute: int
    source_global_tick: int
    source_possession_array_index: int
    side0_percent_text: str
    neutral_percent_text: str
    side1_percent_text: str
    territory_raw: int
    record: PossessionRecord


@dataclass(frozen=True)
class FastViewSemanticShell:
    """Read-only match presentation shell with explicit fidelity boundaries."""

    match_reference: object
    events: tuple[FastViewShellEvent, ...]
    possession_figures: tuple[PossessionFiguresState, ...]
    final_score: tuple[int, int]
    player_rows: tuple[FastViewPlayerRowSnapshot, ...] = ()
    source_backed_components: tuple[str, ...] = SOURCE_BACKED_COMPONENTS
    original_layout_recovered: bool = False
    audio_mapping_recovered: bool = False
    choreography_3d_recovered: bool = False


def _percent_text(value: int) -> str:
    # PossessionFigures.cpp receiver 0x51EA80 formats each value as "%u%%".
    return f"{int(value)}%"


def build_fastview_semantic_shell(
    presentation: HumanMatchPresentation,
) -> FastViewSemanticShell:
    """Expose only semantics already carried by a completed human match.

    Event rows retain the exact source match-event objects. An event without a
    recovered FastView sender remains sender_name=None. Possession keeps the
    original EventPossession record and formats only the three percentages
    proven by PossessionFigures; territory orientation remains raw.
    """
    feed = presentation.feed

    events = tuple(
        FastViewShellEvent(
            sequence=item.sequence,
            minute=item.minute,
            score_after=item.score_after,
            sender_name=(
                item.fastview_event.value
                if item.fastview_event is not None
                else None
            ),
            event=item.event,
        )
        for item in feed.events
    )

    possession = tuple(
        PossessionFiguresState(
            sequence=item.sequence,
            calculation_minute=item.calculation_minute,
            source_global_tick=item.calculation_minute,
            source_possession_array_index=possession_array_index_for_global_tick(
                item.calculation_minute
            ),
            side0_percent_text=_percent_text(item.record.side0_percent),
            neutral_percent_text=_percent_text(item.record.neutral_percent),
            side1_percent_text=_percent_text(item.record.side1_percent),
            territory_raw=item.record.territory,
            record=item.record,
        )
        for item in feed.possession_segments
    )

    return FastViewSemanticShell(
        match_reference=presentation.match_reference,
        events=events,
        possession_figures=possession,
        final_score=feed.final_score,
        player_rows=presentation.player_rows,
    )

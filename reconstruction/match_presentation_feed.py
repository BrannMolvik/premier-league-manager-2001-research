"""Read-only presentation projection over reconstructed FM2001 match events.

Gate 14 presentation must consume the established MatchCalculator event stream
rather than reproduce simulation decisions.  This module therefore accepts the
already-created timed events and possession segments, preserves their exact
record objects/order, and adds only presentation bookkeeping such as running
score.

It intentionally contains no RNG, chance generation, commentary text, sound
mapping, animation selection or original visual semantics.  Those require
separate source evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from match_events import ChanceRecord, MatchEvent, PossessionRecord


class MatchPresentationFeedError(ValueError):
    """An input timeline cannot be projected without inventing state."""


class TimedMatchEventLike(Protocol):
    minute: int
    event: MatchEvent


class PossessionSegmentLike(Protocol):
    calculation_minute: int
    record: PossessionRecord


@dataclass(frozen=True)
class MatchPresentationEvent:
    sequence: int
    minute: int
    score_after: tuple[int, int]
    event: MatchEvent


@dataclass(frozen=True)
class MatchPresentationPossession:
    sequence: int
    calculation_minute: int
    record: PossessionRecord


@dataclass(frozen=True)
class MatchPresentationFeed:
    events: tuple[MatchPresentationEvent, ...]
    possession_segments: tuple[MatchPresentationPossession, ...]
    final_score: tuple[int, int]


def build_match_presentation_feed(
    timed_events: Iterable[TimedMatchEventLike],
    possession_segments: Iterable[PossessionSegmentLike] = (),
) -> MatchPresentationFeed:
    """Project existing match output without running any simulation code."""
    score = [0, 0]
    output_events: list[MatchPresentationEvent] = []
    last_minute = -1

    for sequence, timed in enumerate(timed_events):
        minute = int(timed.minute)
        if minute < 0:
            raise MatchPresentationFeedError("Match event minute cannot be negative")
        if minute < last_minute:
            raise MatchPresentationFeedError(
                "Presentation input must preserve reconstructed chronological order"
            )
        last_minute = minute
        event = timed.event
        if isinstance(event, ChanceRecord):
            credited = event.credited_side
            if credited is not None:
                score[credited] += 1
        output_events.append(
            MatchPresentationEvent(
                sequence=sequence,
                minute=minute,
                score_after=(score[0], score[1]),
                event=event,
            )
        )

    output_possession: list[MatchPresentationPossession] = []
    last_segment = -1
    for sequence, segment in enumerate(possession_segments):
        minute = int(segment.calculation_minute)
        if minute < 0:
            raise MatchPresentationFeedError(
                "Possession calculation minute cannot be negative"
            )
        if minute < last_segment:
            raise MatchPresentationFeedError(
                "Possession segments must preserve reconstructed chronological order"
            )
        last_segment = minute
        if not isinstance(segment.record, PossessionRecord):
            raise MatchPresentationFeedError(
                "Presentation possession input must retain the recovered record"
            )
        output_possession.append(
            MatchPresentationPossession(
                sequence=sequence,
                calculation_minute=minute,
                record=segment.record,
            )
        )

    return MatchPresentationFeed(
        events=tuple(output_events),
        possession_segments=tuple(output_possession),
        final_score=(score[0], score[1]),
    )

"""Presentation-only adapter for completed human FM2001 matches.

This layer deliberately accepts an already-completed human-match outcome and
projects its existing NormalMatchResult-shaped payload through
match_presentation_feed. It does not import or invoke simulation, scheduling,
RNG, post-match mutation, or controller code.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from gate14_fastview_playerrow_snapshot import FastViewPlayerRowSnapshot
from match_presentation_feed import MatchPresentationFeed, build_match_presentation_feed


class CompletedMatchResultLike(Protocol):
    events: tuple
    possession_segments: tuple


class HumanMatchOutcomeLike(Protocol):
    user_result: CompletedMatchResultLike


@dataclass(frozen=True)
class HumanMatchPresentation:
    """Read-only presentation projection for one completed human match."""

    match_reference: object
    feed: MatchPresentationFeed
    player_rows: tuple[FastViewPlayerRowSnapshot, ...] = ()


class HumanMatchPresentationError(ValueError):
    """A completed human outcome cannot be projected without guessing state."""


def _match_reference(outcome: HumanMatchOutcomeLike) -> object:
    if hasattr(outcome, "match_entry"):
        return getattr(outcome, "match_entry")
    if hasattr(outcome, "fixture_id"):
        return int(getattr(outcome, "fixture_id"))
    raise HumanMatchPresentationError(
        "human match outcome has no source-backed match reference"
    )


def build_human_match_presentation(
    outcome: HumanMatchOutcomeLike,
) -> HumanMatchPresentation:
    """Project the completed user result without changing gameplay state."""
    if not hasattr(outcome, "user_result"):
        raise HumanMatchPresentationError("human match outcome has no user_result")
    result = outcome.user_result
    if not hasattr(result, "events"):
        raise HumanMatchPresentationError(
            "human match result has no reconstructed event timeline"
        )
    possession = getattr(result, "possession_segments", ())
    feed = build_match_presentation_feed(result.events, possession)
    rows = tuple(getattr(outcome, "fastview_player_rows", ()))
    if any(not isinstance(row, FastViewPlayerRowSnapshot) for row in rows):
        raise HumanMatchPresentationError(
            "human match outcome contains non-source-backed FastView player rows"
        )
    return HumanMatchPresentation(
        match_reference=_match_reference(outcome),
        feed=feed,
        player_rows=rows,
    )

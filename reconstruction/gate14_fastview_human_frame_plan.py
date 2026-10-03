"""One-way Gate-14 adapter from a completed human outcome to a FastView frame plan.

This module only composes already-established presentation layers:
completed outcome -> HumanMatchPresentation -> FastViewSemanticShell ->
FastViewFramePlan. It does not simulate a match, advance RNG, resolve audio,
invent localization, or promote unresolved raster/3D fidelity.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Mapping

from fastview_semantic_shell import build_fastview_semantic_shell
from gate14_fastview_frame_plan import FastViewFramePlan, build_fastview_frame_plan
from gate14_fastview_score_table_static_raster import FastViewScoreTableStaticRasterSet
from gate14_fastview_playerrow_from_result import (
    FastViewRetainedPlayerRowIdentity,
    build_fastview_player_rows_from_retained_histories,
)
from human_match_presentation import HumanMatchOutcomeLike, build_human_match_presentation
from original_fastview_chrome_art import OriginalFastViewChromeArt
from original_fastview_team_art import OriginalFastViewTeamArt
from original_fastview_possession_art import OriginalFastViewPossessionArtFrame
from original_fastview_possession_figures_art import OriginalFastViewPossessionFiguresArt


def build_human_fastview_frame_plan(
    outcome: HumanMatchOutcomeLike,
    chrome: OriginalFastViewChromeArt,
    possession: OriginalFastViewPossessionArtFrame,
    figures: OriginalFastViewPossessionFiguresArt,
    team_art: OriginalFastViewTeamArt,
    score_table_static: FastViewScoreTableStaticRasterSet | None = None,
) -> FastViewFramePlan:
    """Compose the source-bounded FastView renderer input for one completed match.

    The optional score/table bundle must already be source-verified. This
    adapter does not infer fixture counts, table counts, or phase state from
    the completed outcome.
    """
    presentation = build_human_match_presentation(outcome)
    shell = build_fastview_semantic_shell(presentation)
    return build_fastview_frame_plan(
        shell,
        chrome,
        possession,
        figures,
        team_art,
        score_table_static=score_table_static,
    )

def build_human_fastview_frame_plan_from_retained_histories(
    outcome: HumanMatchOutcomeLike,
    chrome: OriginalFastViewChromeArt,
    possession: OriginalFastViewPossessionArtFrame,
    figures: OriginalFastViewPossessionFiguresArt,
    team_art: OriginalFastViewTeamArt,
    *,
    row_identities: tuple[FastViewRetainedPlayerRowIdentity, ...],
    global_tick: int,
    energy_rng6_rolls: Mapping[tuple[int, int], int],
    score_table_static: FastViewScoreTableStaticRasterSet | None = None,
) -> FastViewFramePlan:
    """Compose a frame from retained histories without mutating the outcome.

    The completed result supplies only its already-retained source histories.
    Visible row identity and each presentation RNG(6) result stay explicit
    caller inputs. Existing outcome PlayerRows are rejected rather than merged
    with a second source.
    """
    presentation = build_human_match_presentation(outcome)
    if presentation.player_rows:
        raise ValueError(
            "retained-history frame path requires outcome without attached PlayerRows"
        )

    rows = build_fastview_player_rows_from_retained_histories(
        outcome.user_result,
        row_identities,
        global_tick=global_tick,
        energy_rng6_rolls=energy_rng6_rolls,
    )
    presentation = replace(presentation, player_rows=rows)
    shell = build_fastview_semantic_shell(presentation)
    return build_fastview_frame_plan(
        shell,
        chrome,
        possession,
        figures,
        team_art,
        score_table_static=score_table_static,
    )


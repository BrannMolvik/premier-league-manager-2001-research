"""One-way Gate-14 adapter from a completed human outcome to a FastView frame plan.

This module only composes already-established presentation layers:
completed outcome -> HumanMatchPresentation -> FastViewSemanticShell ->
FastViewFramePlan. It does not simulate a match, advance RNG, resolve audio,
invent localization, or promote unresolved raster/3D fidelity.
"""
from __future__ import annotations

from fastview_semantic_shell import build_fastview_semantic_shell
from gate14_fastview_frame_plan import FastViewFramePlan, build_fastview_frame_plan
from gate14_fastview_score_table_static_raster import FastViewScoreTableStaticRasterSet
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

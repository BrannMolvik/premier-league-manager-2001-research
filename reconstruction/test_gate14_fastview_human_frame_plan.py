"""Tests for the completed-human -> FastView frame-plan composition seam."""
from pathlib import Path
from types import SimpleNamespace
import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_human_frame_plan import (
    build_human_fastview_frame_plan,
    build_human_fastview_frame_plan_from_retained_histories,
)
from gate14_fastview_playerrow_from_result import (
    FastViewRetainedPlayerRowIdentity,
)
from gate14_fastview_playerrow_snapshot import build_fastview_player_row_snapshot
from gate14_possession_figures import possession_figures_text_layout
from human_match_presentation import HumanMatchPresentationError
from match_events import (
    BoundaryRecord,
    BoundaryType,
    ChanceRecord,
    ChanceSource,
    PossessionRecord,
)
from match_simulation import NormalMatchResult, SegmentPossession, TimedMatchEvent
from original_fastview_chrome_art import build_fastview_chrome_art
from original_fastview_possession_art import build_fastview_possession_art
from original_fastview_possession_figures_art import (
    OriginalFastViewPossessionFigureTextArt,
    OriginalFastViewPossessionFiguresArt,
)
from original_fastview_possession_resources import FASTVIEW_POSSESSION_DIAGRAM_RESOURCES
from original_fastview_team_art import (
    FASTVIEW_TEAM_ART_RESOURCES,
    build_fastview_team_art,
)


def image(width, height, value):
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=bytes([value]) * (width * height * 4),
        consumed_bits=0,
        transparent_pixels=0,
    )


def exact_chrome():
    return build_fastview_chrome_art(
        {
            "top_bar": image(800, 95, 1),
            "ticker": image(800, 33, 2),
        }
    )


def exact_possession(state=1):
    decoded = {
        resource.name: image(*resource.size, index + 3)
        for index, resource in enumerate(FASTVIEW_POSSESSION_DIAGRAM_RESOURCES)
    }
    return build_fastview_possession_art(decoded, state)


def exact_figures(side0=45, neutral=20):
    rows = []
    for source in possession_figures_text_layout(side0, neutral):
        rows.append(
            OriginalFastViewPossessionFigureTextArt(
                source=source,
                line_origin=source.rect[:2],
                clip_rect=source.rect,
                native_color_16=0xFFFF,
                glyph_width=1,
                glyph_height=1,
                glyph_rgba=b"\xff\xff\xff\xff",
            )
        )
    return OriginalFastViewPossessionFiguresArt(tuple(rows))



def exact_team_art():
    return build_fastview_team_art(
        {
            resource.name: image(*resource.size, 20 + index)
            for index, resource in enumerate(FASTVIEW_TEAM_ART_RESOURCES)
        }
    )

def completed_outcome(*, match_reference=23):
    goal = ChanceRecord(
        ChanceSource.OPEN_PLAY,
        raw_outcome=0,
        player_side=0,
        player_index=4,
    )
    possession = PossessionRecord(
        territory=55,
        side0_percent=45,
        neutral_percent=20,
    )
    result = NormalMatchResult(
        events=(
            TimedMatchEvent(12, goal),
            TimedMatchEvent(90, BoundaryRecord(BoundaryType.FULL_TIME)),
        ),
        possession_segments=(SegmentPossession(10, possession),),
    )
    row = build_fastview_player_row_snapshot(
        side_index=0,
        row_index=0,
        shirt_number=9,
        source_position_code=19,
        surname="Striker",
        first_name_initial="A",
        form_value=4,
        energy_value=79,
    )
    if isinstance(match_reference, int):
        outcome = SimpleNamespace(
            fixture_id=match_reference,
            user_result=result,
            fastview_player_rows=(row,),
        )
    else:
        outcome = SimpleNamespace(
            match_entry=match_reference,
            user_result=result,
            fastview_player_rows=(row,),
        )
    return outcome, goal, possession, row


def completed_outcome_with_retained_histories():
    outcome, goal, possession, _row = completed_outcome()
    result = SimpleNamespace(
        events=outcome.user_result.events,
        possession_segments=outcome.user_result.possession_segments,
        fastview_condition_histories=(
            SimpleNamespace(
                side_index=0,
                player_index=3,
                samples=(80,) * 24,
            ),
        ),
        fastview_form_histories=(
            SimpleNamespace(
                side_index=0,
                player_index=3,
                samples=(5, 6, 7) + (7,) * 21,
            ),
        ),
    )
    return (
        SimpleNamespace(fixture_id=23, user_result=result),
        goal,
        possession,
    )


def retained_row_identity():
    return FastViewRetainedPlayerRowIdentity(
        side_index=0,
        player_index=3,
        row_index=0,
        shirt_number=9,
        source_position_code=19,
        surname="Striker",
        first_name_initial="A",
    )


class HumanFastViewFramePlanTests(unittest.TestCase):
    def test_composes_completed_outcome_through_existing_presentation_layers(self):
        outcome, goal, possession, row = completed_outcome()

        frame = build_human_fastview_frame_plan(
            outcome,
            exact_chrome(),
            exact_possession(),
            exact_figures(),
            exact_team_art(),
        )

        self.assertEqual(frame.match_reference, 23)
        self.assertEqual(frame.semantic_shell.final_score, (1, 0))
        self.assertIs(frame.semantic_shell.events[0].event, goal)
        self.assertIs(frame.semantic_shell.possession_figures[0].record, possession)
        self.assertIs(frame.semantic_shell.player_rows[0], row)
        self.assertIs(
            frame.player_row_render_plans,
            frame.semantic_shell.player_row_render_plans,
        )
        self.assertEqual(frame.surface_layout.size, (800, 600))
        self.assertEqual(frame.resolved_composite.size, (800, 600))
        self.assertGreater(frame.resolved_composite.resolved_pixel_count, 0)
        self.assertFalse(frame.resolved_composite.cross_component_z_order_recovered)
        self.assertFalse(frame.resolved_composite.flattened_frame_available)
        self.assertFalse(frame.resolved_composite.complete_fastview_frame)
        self.assertIsNotNone(frame.component_rasters.team_table)
        self.assertEqual(
            frame.component_rasters.team_table.component,
            "team_table_static",
        )
        self.assertFalse(frame.complete_raster_frame)
        self.assertFalse(frame.audio_ready)
        self.assertFalse(frame.choreography_3d_ready)

    def test_builds_completed_human_frame_from_retained_histories_without_mutation(self):
        outcome, goal, possession = completed_outcome_with_retained_histories()

        frame = build_human_fastview_frame_plan_from_retained_histories(
            outcome,
            exact_chrome(),
            exact_possession(),
            exact_figures(),
            exact_team_art(),
            row_identities=(retained_row_identity(),),
            global_tick=10,
            energy_rng6_rolls={(0, 3): 3},
        )

        self.assertFalse(hasattr(outcome, "fastview_player_rows"))
        self.assertEqual(frame.match_reference, 23)
        self.assertIs(frame.semantic_shell.events[0].event, goal)
        self.assertIs(frame.semantic_shell.possession_figures[0].record, possession)
        self.assertEqual(len(frame.semantic_shell.player_rows), 1)
        row = frame.semantic_shell.player_rows[0]
        self.assertEqual(row.player_name.text, "A Striker")
        self.assertEqual(row.form.text, "7")
        self.assertEqual(row.energy.energy_value, 76)
        self.assertEqual(len(frame.player_row_render_plans), 1)
        self.assertFalse(frame.complete_raster_frame)
        self.assertFalse(frame.audio_ready)
        self.assertFalse(frame.choreography_3d_ready)

    def test_retained_history_frame_path_rejects_pre_attached_rows(self):
        outcome, *_ = completed_outcome()
        with self.assertRaisesRegex(
            ValueError,
            "requires outcome without attached PlayerRows",
        ):
            build_human_fastview_frame_plan_from_retained_histories(
                outcome,
                exact_chrome(),
                exact_possession(),
                exact_figures(),
                exact_team_art(),
                row_identities=(retained_row_identity(),),
                global_tick=10,
                energy_rng6_rolls={(0, 3): 3},
            )

    def test_preserves_tagged_non_league_match_reference_without_reconstruction(self):
        reference = ("domestic_cup", ("cup_result", 4, 10, 2))
        outcome, *_ = completed_outcome(match_reference=reference)

        frame = build_human_fastview_frame_plan(
            outcome,
            exact_chrome(),
            exact_possession(),
            exact_figures(),
            exact_team_art(),
        )

        self.assertEqual(frame.match_reference, reference)

    def test_propagates_fail_closed_completed_outcome_validation(self):
        with self.assertRaisesRegex(HumanMatchPresentationError, "no user_result"):
            build_human_fastview_frame_plan(
                SimpleNamespace(fixture_id=1),
                exact_chrome(),
                exact_possession(),
                exact_figures(),
                exact_team_art(),
            )

    def test_adapter_does_not_import_simulation_rng_audio_or_controller_layers(self):
        source = Path(__file__).with_name(
            "gate14_fastview_human_frame_plan.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "match_simulation",
            "match_calculator",
            "match_engine_rng",
            "human_gameplay",
            "gameplay_controller",
            "random",
            "sound_effect",
            "commentary_text",
        ):
            self.assertNotIn(f"import {forbidden}", source)
            self.assertNotIn(f"from {forbidden}", source)


if __name__ == "__main__":
    unittest.main()

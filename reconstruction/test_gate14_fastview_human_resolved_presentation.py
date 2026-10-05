"""Tests for completed-human -> resolved FastView -> Tk composition."""
from base64 import b64decode
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from ea444_decoder import EA444DecodedImage
from gate14_fastview_human_resolved_presentation import (
    HumanFastViewResolvedPresentationError,
    build_human_fastview_resolved_presentation,
    build_human_fastview_resolved_presentation_from_retained_histories,
    draw_human_fastview_resolved_presentation,
)
from gate14_fastview_playerrow_from_result import FastViewRetainedPlayerRowIdentity
from gate14_fastview_playerrow_snapshot import build_fastview_player_row_snapshot
from gate14_possession_figures import possession_figures_text_layout
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


def completed_outcome(*, attached_row=True):
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
    data = {
        "fixture_id": 23,
        "user_result": result,
    }
    if attached_row:
        data["fastview_player_rows"] = (
            build_fastview_player_row_snapshot(
                side_index=0,
                row_index=0,
                shirt_number=9,
                source_position_code=19,
                surname="Striker",
                first_name_initial="A",
                form_value=4,
                energy_value=79,
            ),
        )
    return SimpleNamespace(**data)


def retained_history_outcome():
    base = completed_outcome(attached_row=False)
    result = SimpleNamespace(
        events=base.user_result.events,
        possession_segments=base.user_result.possession_segments,
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
    return SimpleNamespace(fixture_id=23, user_result=result)


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


class FakePhotoImage:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeTk:
    NW = "nw"
    PhotoImage = FakePhotoImage


class FakeCanvas:
    def __init__(self):
        self.calls = []

    def create_image(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return 91


class HumanFastViewResolvedPresentationTests(unittest.TestCase):
    def test_builds_integrity_bound_preview_coverage_and_overlap_readiness(self):
        presentation = build_human_fastview_resolved_presentation(
            completed_outcome(),
            exact_chrome(),
            exact_possession(),
            exact_figures(),
            exact_team_art(),
        )

        frame = presentation.frame
        preview = presentation.preview
        coverage = presentation.coverage
        readiness = presentation.overlap_readiness

        self.assertEqual(frame.match_reference, 23)
        self.assertEqual(frame.semantic_shell.final_score, (1, 0))
        self.assertEqual(preview.size, (800, 600))
        self.assertTrue(preview.rgba_png.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertEqual(coverage.total_pixel_count, 800 * 600)
        self.assertEqual(
            coverage.resolved_pixel_count,
            frame.resolved_composite.resolved_pixel_count,
        )
        self.assertEqual(
            preview.source_composite_rgba_sha256,
            frame.resolved_composite.rgba_sha256,
        )
        self.assertEqual(
            coverage.source_composite_rgba_sha256,
            frame.resolved_composite.rgba_sha256,
        )
        self.assertEqual(
            preview.source_overlap_mask_sha256,
            frame.resolved_composite.unresolved_overlap_mask_sha256,
        )
        self.assertEqual(
            coverage.source_overlap_mask_sha256,
            frame.resolved_composite.unresolved_overlap_mask_sha256,
        )
        self.assertEqual(preview.overlap_groups, coverage.unresolved_overlap_groups)
        self.assertEqual(
            readiness.source_composite_rgba_sha256,
            frame.resolved_composite.rgba_sha256,
        )
        self.assertEqual(
            readiness.source_overlap_mask_sha256,
            frame.resolved_composite.unresolved_overlap_mask_sha256,
        )
        self.assertEqual(
            readiness.unresolved_overlap_pixel_count,
            frame.resolved_composite.unresolved_overlap_pixel_count,
        )
        self.assertEqual(
            readiness.draw_order_resolved_overlap_pixel_count
            + readiness.draw_order_unresolved_overlap_pixel_count,
            readiness.unresolved_overlap_pixel_count,
        )
        self.assertEqual(readiness.raster_resolvable_overlap_pixel_count, 0)
        self.assertFalse(readiness.cross_component_blend_rule_recovered)
        self.assertFalse(readiness.all_overlap_pixels_resolvable)
        self.assertFalse(presentation.complete_fastview_frame)
        self.assertFalse(presentation.audio_ready)
        self.assertFalse(presentation.choreography_3d_ready)

    def test_resolved_adapter_forwards_advanced_artifacts_to_frame_builder(self):
        base = build_human_fastview_resolved_presentation(
            completed_outcome(),
            exact_chrome(),
            exact_possession(),
            exact_figures(),
            exact_team_art(),
        )
        advanced = {
            "score_table": object(),
            "score_draw_phases": object(),
            "score_phase_text": object(),
            "clock": object(),
            "direct_header": object(),
            "surfaced": object(),
        }

        with patch(
            "gate14_fastview_human_resolved_presentation.build_human_fastview_frame_plan",
            return_value=base.frame,
        ) as build:
            presentation = build_human_fastview_resolved_presentation(
                completed_outcome(),
                exact_chrome(),
                exact_possession(),
                exact_figures(),
                exact_team_art(),
                score_table_static=advanced["score_table"],
                score_draw_phases=advanced["score_draw_phases"],
                score_phase_text=advanced["score_phase_text"],
                clock=advanced["clock"],
                direct_header=advanced["direct_header"],
                surfaced=advanced["surfaced"],
            )

        self.assertIs(presentation.frame, base.frame)
        _args, kwargs = build.call_args
        self.assertIs(kwargs["score_table_static"], advanced["score_table"])
        self.assertIs(kwargs["score_draw_phases"], advanced["score_draw_phases"])
        self.assertIs(kwargs["score_phase_text"], advanced["score_phase_text"])
        self.assertIs(kwargs["clock"], advanced["clock"])
        self.assertIs(kwargs["direct_header"], advanced["direct_header"])
        self.assertIs(kwargs["surfaced"], advanced["surfaced"])

    def test_draws_exact_canonical_preview_without_hidden_recomposition(self):
        presentation = build_human_fastview_resolved_presentation(
            completed_outcome(),
            exact_chrome(),
            exact_possession(),
            exact_figures(),
            exact_team_art(),
        )
        canvas = FakeCanvas()

        draw = draw_human_fastview_resolved_presentation(
            presentation,
            FakeTk,
            canvas,
        )

        self.assertIs(draw.preview, presentation.preview)
        self.assertEqual(draw.canvas_item_id, 91)
        self.assertEqual(len(canvas.calls), 1)
        args, kwargs = canvas.calls[0]
        self.assertEqual(args, (0, 0))
        self.assertEqual(kwargs["anchor"], "nw")
        self.assertIs(kwargs["image"], draw.photo_image)
        self.assertEqual(
            b64decode(draw.photo_image.kwargs["data"]),
            presentation.preview.rgba_png,
        )
        self.assertFalse(draw.cross_component_z_order_recovered)
        self.assertFalse(draw.complete_fastview_frame)

    def test_retained_history_path_reuses_existing_source_backed_row_adapter(self):
        presentation = (
            build_human_fastview_resolved_presentation_from_retained_histories(
                retained_history_outcome(),
                exact_chrome(),
                exact_possession(),
                exact_figures(),
                exact_team_art(),
                row_identities=(retained_row_identity(),),
                global_tick=10,
                energy_rng6_rolls={(0, 3): 3},
            )
        )

        row = presentation.frame.semantic_shell.player_rows[0]
        self.assertEqual(row.player_name.text, "A Striker")
        self.assertEqual(row.form.text, "7")
        self.assertEqual(row.energy.energy_value, 76)
        self.assertEqual(
            presentation.coverage.total_pixel_count,
            800 * 600,
        )
        self.assertFalse(presentation.complete_fastview_frame)

    def test_rejects_cross_layer_integrity_drift_or_false_promotion(self):
        presentation = build_human_fastview_resolved_presentation(
            completed_outcome(),
            exact_chrome(),
            exact_possession(),
            exact_figures(),
            exact_team_art(),
        )

        drifted_preview = replace(
            presentation.preview,
            source_composite_rgba_sha256="0" * 64,
        )
        with self.assertRaisesRegex(
            HumanFastViewResolvedPresentationError,
            "RGBA source hashes drifted",
        ):
            replace(presentation, preview=drifted_preview)

        drifted_readiness = replace(
            presentation.overlap_readiness,
            source_composite_rgba_sha256="0" * 64,
        )
        with self.assertRaisesRegex(
            HumanFastViewResolvedPresentationError,
            "RGBA source hashes drifted",
        ):
            replace(presentation, overlap_readiness=drifted_readiness)

        with self.assertRaisesRegex(
            HumanFastViewResolvedPresentationError,
            "cannot promote",
        ):
            replace(presentation, complete_fastview_frame=True)

        with self.assertRaisesRegex(
            HumanFastViewResolvedPresentationError,
            "exact human FastView resolved presentation",
        ):
            draw_human_fastview_resolved_presentation(
                object(),
                FakeTk,
                FakeCanvas(),
            )

    def test_bundle_module_does_not_import_gameplay_rng_audio_or_gate13_host(self):
        source = Path(__file__).with_name(
            "gate14_fastview_human_resolved_presentation.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "match_simulation",
            "match_calculator",
            "match_engine_rng",
            "human_gameplay",
            "original_game_host",
            "gate13_",
            "random",
            "sound_effect",
            "commentary_text",
        ):
            self.assertNotIn(f"import {forbidden}", source)
            self.assertNotIn(f"from {forbidden}", source)


if __name__ == "__main__":
    unittest.main()

"""Tests for the source-backed partial PlayerRow text raster."""
from dataclasses import replace
from pathlib import Path
import unittest

from gate14_fastview_playerrow_snapshot import (
    build_fastview_player_row_render_plan,
    build_fastview_player_row_snapshot,
)
from gate14_fastview_team_text_raster import (
    PLAYERROW_TEXT_FONT_ATLAS_SIZE,
    PLAYERROW_TEXT_FONT_BYTE_SIZE,
    PLAYERROW_TEXT_FONT_SHA256,
    PLAYERROW_TEXT_NATIVE_LINE_HEIGHT,
    PLAYERROW_TEXT_NATIVE_COLOR_16,
    PLAYERROW_TEXT_STYLE_INDEX,
    PLAYERROW_OWN_GOAL_RGB,
    PLAYERROW_POSITION_ENGLISH_IDX_BASE,
    PLAYERROW_POSITION_ENGLISH_BY_KEY,
    FastViewTeamTextRasterError,
    _line_origin,
    load_verified_playerrow_text_font,
    rasterize_fastview_playerrow_text,
    resolve_playerrow_position_english,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def render_plan(*, goal=None, own_goal=None):
    snapshot = build_fastview_player_row_snapshot(
        side_index=0,
        row_index=0,
        shirt_number=9,
        source_position_code=19,
        surname="Striker",
        first_name_initial="A",
        form_value=7,
        energy_value=79,
        displayed_goal_count=goal,
        displayed_own_goal_count=own_goal,
    )
    return build_fastview_player_row_render_plan(snapshot)


def pixel(raster, x, y):
    offset = (y * 800 + x) * 4
    return tuple(raster.rgba[offset:offset + 4])


class FastViewTeamTextRasterTests(unittest.TestCase):
    def test_loads_exact_staged_source_font(self):
        path = (
            REPO_ROOT
            / "original_assets"
            / "source"
            / "Fonts"
            / "Zurich_XCn_BT_16pixel.fnt"
        )
        data = path.read_bytes()
        self.assertEqual(len(data), PLAYERROW_TEXT_FONT_BYTE_SIZE)
        import hashlib
        self.assertEqual(hashlib.sha256(data).hexdigest(), PLAYERROW_TEXT_FONT_SHA256)

        font = load_verified_playerrow_text_font(REPO_ROOT)
        self.assertEqual(
            (font.atlas_width, font.atlas_height),
            PLAYERROW_TEXT_FONT_ATLAS_SIZE,
        )
        self.assertEqual(
            font.native_line_height(),
            PLAYERROW_TEXT_NATIVE_LINE_HEIGHT,
        )

    def test_rasterizes_only_default_color_literal_cells(self):
        plan = render_plan()
        raster = rasterize_fastview_playerrow_text(REPO_ROOT, (plan,))

        self.assertEqual(
            raster.rendered_cells,
            ((0, 0, 1), (0, 0, 2), (0, 0, 3), (0, 0, 6)),
        )
        self.assertEqual(raster.unresolved_cells, ())
        self.assertEqual(raster.text_style_index, PLAYERROW_TEXT_STYLE_INDEX)
        self.assertEqual(raster.native_color_16, PLAYERROW_TEXT_NATIVE_COLOR_16)
        self.assertEqual(raster.source_font_sha256, PLAYERROW_TEXT_FONT_SHA256)
        self.assertEqual(raster.source_language, "English")
        self.assertTrue(raster.position_english_localization_recovered)
        self.assertTrue(raster.own_goal_color_recovered)
        self.assertTrue(raster.complete_team_table_text)

    def test_written_goal_and_own_goal_render_with_source_colors(self):
        raster = rasterize_fastview_playerrow_text(
            REPO_ROOT,
            (render_plan(goal=2, own_goal=1),),
        )

        self.assertEqual(
            raster.rendered_cells,
            ((0, 0, 1), (0, 0, 2), (0, 0, 3), (0, 0, 4), (0, 0, 5), (0, 0, 6)),
        )
        self.assertEqual(raster.unresolved_cells, ())
        self.assertEqual(PLAYERROW_OWN_GOAL_RGB, (255, 0, 0))

        font = load_verified_playerrow_text_font(REPO_ROOT)
        own_goal = render_plan(goal=2, own_goal=1).text_instructions[4]
        mask = font.render_text_alpha(own_goal.value)
        origin_x, origin_y = _line_origin(font, own_goal)
        left, top, right, bottom = own_goal.rect
        found = None
        for y in range(mask.height):
            for x in range(mask.width):
                alpha = mask.alpha[y * mask.width + x]
                dst_x = origin_x + x
                dst_y = origin_y + y
                if alpha and left <= dst_x < right and top <= dst_y < bottom:
                    found = (dst_x, dst_y, alpha)
                    break
            if found is not None:
                break
        self.assertIsNotNone(found)
        x, y, alpha = found
        self.assertEqual(pixel(raster, x, y), (255, 0, 0, alpha))

    def test_source_closes_exact_english_position_sequence(self):
        self.assertEqual(PLAYERROW_POSITION_ENGLISH_IDX_BASE, 2305)
        expected = (
            ("PositionGK", "GK"),
            ("PositionRB", "RB"),
            ("PositionLB", "LB"),
            ("PositionCD", "CD"),
            ("PositionSW", "SW"),
            ("PositionRWB", "RWB"),
            ("PositionLWB", "LWB"),
            ("PositionANC", "ANC"),
            ("PositionDM", "DM"),
            ("PositionRM", "RM"),
            ("PositionLM", "LM"),
            ("PositionCM", "CM"),
            ("PositionRW", "RW"),
            ("PositionLW", "LW"),
            ("PositionAM", "AM"),
            ("PositionRF", "RF"),
            ("PositionLF", "LF"),
            ("PositionCF", "CF"),
            ("PositionST", "ST"),
        )
        self.assertEqual(
            tuple(PLAYERROW_POSITION_ENGLISH_BY_KEY.items())[1:],
            expected,
        )
        for key, value in expected:
            self.assertEqual(resolve_playerrow_position_english(key), value)
        self.assertEqual(resolve_playerrow_position_english(""), "")
        with self.assertRaisesRegex(
            FastViewTeamTextRasterError,
            "outside the source-closed English mapping",
        ):
            resolve_playerrow_position_english("PositionInvented")

    def test_center_and_left_alignment_use_native_18px_line_inside_16px_clip(self):
        font = load_verified_playerrow_text_font(REPO_ROOT)
        plan = render_plan()
        shirt = plan.text_instructions[0]
        name = plan.text_instructions[2]

        shirt_width = font.measure_text(shirt.value)
        self.assertEqual(
            _line_origin(font, shirt),
            (
                shirt.rect[0] + (shirt.rect[2] - shirt.rect[0]) // 2
                - shirt_width // 2,
                shirt.rect[1] - 1,
            ),
        )
        self.assertEqual(
            _line_origin(font, name),
            (name.rect[0], name.rect[1] - 1),
        )

    def test_source_alpha_is_clipped_not_scaled_or_shifted_into_control(self):
        font = load_verified_playerrow_text_font(REPO_ROOT)
        plan = render_plan()
        instruction = plan.text_instructions[0]
        raster = rasterize_fastview_playerrow_text(REPO_ROOT, (plan,))
        mask = font.render_text_alpha(instruction.value)
        origin_x, origin_y = _line_origin(font, instruction)
        left, top, right, bottom = instruction.rect

        found = None
        for y in range(mask.height):
            for x in range(mask.width):
                alpha = mask.alpha[y * mask.width + x]
                dst_x = origin_x + x
                dst_y = origin_y + y
                if (
                    alpha
                    and left <= dst_x < right
                    and top <= dst_y < bottom
                ):
                    found = (dst_x, dst_y, alpha)
                    break
            if found is not None:
                break
        self.assertIsNotNone(found)
        x, y, alpha = found
        self.assertEqual(pixel(raster, x, y), (255, 255, 255, alpha))
        # The native centered line starts one pixel above the 16px control;
        # no raster pixel may leak outside the source control clip.
        self.assertEqual(pixel(raster, left, top - 1), (0, 0, 0, 0))

    def test_missing_or_wrong_staged_font_fails_closed(self):
        with self.assertRaisesRegex(
            FastViewTeamTextRasterError,
            "Missing staged PlayerRow font",
        ):
            rasterize_fastview_playerrow_text(
                REPO_ROOT / "not-a-repository",
                (render_plan(),),
            )

    def test_raster_cannot_promote_unresolved_text_fidelity(self):
        raster = rasterize_fastview_playerrow_text(REPO_ROOT, (render_plan(),))
        with self.assertRaisesRegex(
            FastViewTeamTextRasterError,
            "cannot drop source-closed English position strings",
        ):
            replace(raster, position_english_localization_recovered=False)

        for field in (
            "own_goal_color_recovered",
            "complete_team_table_text",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    FastViewTeamTextRasterError,
                    "cannot drop source-closed English text fidelity",
                ):
                    replace(raster, **{field: False})


if __name__ == "__main__":
    unittest.main()

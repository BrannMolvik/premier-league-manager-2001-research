"""Tests for the bounded operator-visible Gate-14 FastView Tk window."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import gate14_fastview_human_tk_window as window_module


class FakePresentation:
    def __init__(self):
        self.preview = object()
        self.complete_fastview_frame = False


class FakeDraw:
    def __init__(self, preview):
        self.preview = preview
        self.complete_fastview_frame = False


class FakeWindow:
    def __init__(self, parent):
        self.parent = parent
        self.title_value = None
        self.resizable_value = None

    def title(self, value):
        self.title_value = value

    def resizable(self, width, height):
        self.resizable_value = (width, height)


class FakeCanvas:
    def __init__(self, window, **kwargs):
        self.window = window
        self.kwargs = kwargs
        self.pack_calls = 0

    def pack(self):
        self.pack_calls += 1


class FakeTk:
    def __init__(self):
        self.windows = []
        self.canvases = []

    def Toplevel(self, parent):
        window = FakeWindow(parent)
        self.windows.append(window)
        return window

    def Canvas(self, window, **kwargs):
        canvas = FakeCanvas(window, **kwargs)
        self.canvases.append(canvas)
        return canvas


class HumanFastViewTkWindowTests(unittest.TestCase):
    def test_opens_native_window_and_forwards_exact_existing_presentation(self):
        presentation = FakePresentation()
        draw = FakeDraw(presentation.preview)
        tk = FakeTk()
        parent = object()

        with (
            patch.object(
                window_module,
                "HumanFastViewResolvedPresentation",
                FakePresentation,
            ),
            patch.object(window_module, "FastViewResolvedTkDraw", FakeDraw),
            patch.object(
                window_module,
                "draw_human_fastview_resolved_presentation",
                return_value=draw,
            ) as render,
        ):
            opened = window_module.open_human_fastview_tk_window(
                presentation,
                tk,
                parent,
            )

        self.assertIs(opened.presentation, presentation)
        self.assertIs(opened.window, tk.windows[0])
        self.assertIs(opened.canvas, tk.canvases[0])
        self.assertIs(opened.draw, draw)
        self.assertEqual(opened.native_size, (800, 600))
        self.assertFalse(opened.source_navigation_trigger_recovered)
        self.assertTrue(opened.unresolved_pixels_remain_transparent)
        self.assertFalse(opened.complete_fastview_frame)

        self.assertIs(tk.windows[0].parent, parent)
        self.assertEqual(
            tk.windows[0].title_value,
            window_module.FASTVIEW_WINDOW_TITLE,
        )
        self.assertEqual(tk.windows[0].resizable_value, (False, False))
        self.assertEqual(
            tk.canvases[0].kwargs,
            {
                "width": 800,
                "height": 600,
                "highlightthickness": 0,
                "borderwidth": 0,
            },
        )
        self.assertEqual(tk.canvases[0].pack_calls, 1)
        render.assert_called_once_with(presentation, tk, tk.canvases[0])

    def test_rejects_wrong_input_missing_parent_or_missing_tk_constructors(self):
        tk = FakeTk()
        with self.assertRaisesRegex(
            window_module.HumanFastViewTkWindowError,
            "exact completed-human presentation",
        ):
            window_module.open_human_fastview_tk_window(object(), tk, object())

        presentation = FakePresentation()
        with patch.object(
            window_module,
            "HumanFastViewResolvedPresentation",
            FakePresentation,
        ):
            with self.assertRaisesRegex(
                window_module.HumanFastViewTkWindowError,
                "caller-owned Tk parent",
            ):
                window_module.open_human_fastview_tk_window(
                    presentation,
                    tk,
                    None,
                )
            with self.assertRaisesRegex(
                window_module.HumanFastViewTkWindowError,
                "Toplevel and Canvas",
            ):
                window_module.open_human_fastview_tk_window(
                    presentation,
                    SimpleNamespace(),
                    object(),
                )

    def test_window_record_rejects_preview_drift_or_fidelity_promotion(self):
        presentation = FakePresentation()
        draw = FakeDraw(presentation.preview)
        with (
            patch.object(
                window_module,
                "HumanFastViewResolvedPresentation",
                FakePresentation,
            ),
            patch.object(window_module, "FastViewResolvedTkDraw", FakeDraw),
        ):
            record = window_module.HumanFastViewTkWindow(
                presentation=presentation,
                window=object(),
                canvas=object(),
                draw=draw,
            )
            with self.assertRaisesRegex(
                window_module.HumanFastViewTkWindowError,
                "canonical preview",
            ):
                replace(record, draw=FakeDraw(object()))
            with self.assertRaisesRegex(
                window_module.HumanFastViewTkWindowError,
                "cannot promote",
            ):
                replace(record, source_navigation_trigger_recovered=True)
            with self.assertRaisesRegex(
                window_module.HumanFastViewTkWindowError,
                "cannot promote",
            ):
                replace(record, complete_fastview_frame=True)

    def test_window_module_does_not_import_gameplay_navigation_or_rng(self):
        source = Path(__file__).with_name(
            "gate14_fastview_human_tk_window.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "human_gameplay",
            "match_simulation",
            "match_calculator",
            "match_engine_rng",
            "original_game_host",
            "front_end_session",
            "front_end_state",
            "random",
        ):
            self.assertNotIn(f"import {forbidden}", source)
            self.assertNotIn(f"from {forbidden}", source)


if __name__ == "__main__":
    unittest.main()

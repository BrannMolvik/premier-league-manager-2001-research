import unittest
from types import SimpleNamespace
from original_front_end_animation import OriginalFirstScreenAnimation
from original_front_end_layout import OriginalRect


def view(screen='menu'):
    return SimpleNamespace(screen=screen, controls=(
        SimpleNamespace(event=1, rect=OriginalRect(0, 0, 10, 10)),
        SimpleNamespace(event=2, rect=OriginalRect(10, 0, 10, 10))))


class FirstScreenAnimationTests(unittest.TestCase):
    def test_half_open_pointer_and_complete_ordered_traversal(self):
        model = OriginalFirstScreenAnimation()
        snapshot = view()
        model.observe(snapshot, (9, 9))
        model.advance(snapshot)
        model.observe(snapshot, (10, 9))
        model.advance(snapshot)
        self.assertEqual(model.frames(snapshot), {1: 0, 2: 1})

    def test_eleven_frames_are_bounded_and_leave_returns_to_zero(self):
        model = OriginalFirstScreenAnimation()
        snapshot = view()
        model.observe(snapshot, (0, 0))
        frames = [model.frames(snapshot)[1]]
        while model.pending(snapshot):
            self.assertTrue(model.advance(snapshot))
            frames.append(model.frames(snapshot)[1])
        self.assertEqual(frames, list(range(11)))
        self.assertFalse(model.advance(snapshot))
        model.observe(snapshot, None)
        for _ in range(10):
            self.assertTrue(model.advance(snapshot))
        self.assertEqual(model.frames(snapshot), {1: 0, 2: 0})

    def test_inactive_panel_state_is_retained_but_not_updated(self):
        model = OriginalFirstScreenAnimation()
        menu, team = view(), view('team')
        model.observe(menu, (0, 0))
        model.advance(menu)
        model.observe(team, (10, 0))
        model.advance(team)
        self.assertEqual(model.frames(menu), {1: 1, 2: 0})
        self.assertEqual(model.frames(team), {1: 0, 2: 1})

    def test_disabled_source_group_is_not_a_synthetic_hover_frame(self):
        model = OriginalFirstScreenAnimation()
        snapshot = view()
        model.observe(snapshot, (0, 0))
        model.states[('menu', 1)].set_enabled(False)
        self.assertTrue(model.pending(snapshot))
        model.advance(snapshot)
        self.assertEqual(model.frames(snapshot)[1], 22)
        self.assertFalse(model.pending(snapshot))

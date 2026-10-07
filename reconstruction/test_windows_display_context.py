from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from windows_display_context import initialize_windows_display_context


class WindowsDisplayContextTests(unittest.TestCase):
    def api(self, states):
        return SimpleNamespace(
            GetThreadDpiAwarenessContext=Mock(return_value=123),
            GetAwarenessFromDpiAwarenessContext=Mock(side_effect=states),
            SetProcessDPIAware=Mock(return_value=1))

    def test_unaware_context_is_initialized_and_verified(self):
        api = self.api([0, 1])
        initialize_windows_display_context(platform_system='Windows', user32_factory=lambda: api)
        api.SetProcessDPIAware.assert_called_once_with()
        self.assertEqual(api.GetThreadDpiAwarenessContext.call_count, 2)

    def test_existing_aware_context_is_not_changed(self):
        for state in (1, 2):
            api = self.api([state])
            initialize_windows_display_context(platform_system='Windows', user32_factory=lambda: api)
            api.SetProcessDPIAware.assert_not_called()

    def test_unsuccessful_or_invalid_context_fails_closed(self):
        for states in ([0, 0], [-1]):
            with self.assertRaisesRegex(RuntimeError, 'DPI context'):
                initialize_windows_display_context(platform_system='Windows',
                    user32_factory=lambda: self.api(states))

    def test_non_windows_does_not_load_native_api(self):
        factory = Mock()
        initialize_windows_display_context(platform_system='Linux', user32_factory=factory)
        factory.assert_not_called()

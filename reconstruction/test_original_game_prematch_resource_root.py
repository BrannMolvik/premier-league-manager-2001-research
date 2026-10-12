"""The ordinary host must not search its bundled subset for installed club art."""
from datetime import date
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch, sentinel

import original_game_host as runtime
from gate14_fastview_surfaced_resource_loader import FastViewSurfacedResourceLoadError


class OriginalGamePrematchResourceRootTests(unittest.TestCase):
    def loader(self):
        root = Mock()
        host_factory = Mock()
        with (
            patch.object(runtime, 'build_original_game_presenter'),
            patch.object(runtime, 'OriginalGameTkHost', host_factory),
            patch.object(runtime, 'play_configured_startup_media'),
            patch.object(runtime, 'install_live_first_screen_audio'),
            patch('windows_display_context.initialize_windows_display_context'),
            patch('tkinter.Tk', return_value=root),
        ):
            runtime.run_original_game_ui('licensed-install', source_root='bundled-subset')
        root.mainloop.assert_called_once_with()
        return host_factory.call_args.kwargs['prematch_resource_loader']

    def gameplay(self, pair=(349, 359)):
        state = SimpleNamespace(calendar=SimpleNamespace(current_date=date(2000, 8, 19)),
                                clubs=sentinel.clubs, countries=sentinel.countries)
        return Mock(state=state, _primary_entry_clubs=Mock(return_value=pair))

    def test_ordinary_prematch_loads_original_installation_not_bundled_subset(self):
        loader = self.loader()
        gameplay = self.gameplay()
        with patch('gate14_prematch_surface.build_verified_prematch_surface_boundary',
                   return_value=sentinel.boundary) as build:
            self.assertIs(loader(gameplay, sentinel.entry), sentinel.boundary)
        build.assert_called_once_with(
            match_date=date(2000, 8, 19), clubs=sentinel.clubs,
            countries=sentinel.countries, home_club_id=349, away_club_id=359,
            background_club_override_id=None, source_root=Path('licensed-install'),
            original_executable=Path('licensed-install/FOOTBAL.EXE'))
        gameplay._primary_entry_clubs.assert_called_once_with(sentinel.entry)

    def test_missing_original_resource_still_fails_closed(self):
        loader = self.loader()
        with patch('gate14_prematch_surface.build_verified_prematch_surface_boundary',
                   side_effect=FastViewSurfacedResourceLoadError('missing original badge')):
            with self.assertRaisesRegex(FastViewSurfacedResourceLoadError, 'missing original badge'):
                loader(self.gameplay(), sentinel.entry)

    def test_unresolved_participants_never_load_resources(self):
        loader = self.loader()
        with patch('gate14_prematch_surface.build_verified_prematch_surface_boundary') as build:
            with self.assertRaisesRegex(runtime.OriginalGameHostError, 'participant ownership'):
                loader(self.gameplay(pair=None), sentinel.entry)
        build.assert_not_called()


if __name__ == '__main__':
    unittest.main()

"""Synthetic boundary inputs only; these tests do not claim native capture production."""
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from front_end_session import FrontEndSession
from front_end_state import FrontEndScreen, StartMenuControl, TeamSelectControl
from gate13_management_source_data import ManagementSourceDataBridge, ManagementPresentationError
from original_fixture_match_info_link import SourceFixtureMatchInfoContext
from original_management_presenter import OriginalManagementPresenter, OriginalManagementPresentationError
from original_game_host import OriginalGameTkHost
from test_original_management_presenter import Backend, Bridge
from test_original_game_host import (
    FakeRoot, FakeTk, presenter, fake_pmatchinfo_snapshot, MatchInfoActionPresenter,
)


class FixtureReportRouteTests(unittest.TestCase):
    def test_bridge_never_uses_scores_or_completion_as_report(self):
        state = SimpleNamespace(premier_league=SimpleNamespace(
            results={700: SimpleNamespace(home_goals=3, away_goals=0)}))
        bridge = ManagementSourceDataBridge(SimpleNamespace(state=state))
        self.assertIsNone(bridge.fixture_match_info_context(700))
        state.captured_match_reports = ()
        state.fixture_match_info_links = {700: 0xFFFF}
        self.assertIsNone(bridge.fixture_match_info_context(700))

    def test_bridge_retains_append_order_and_fixture_identity(self):
        first, second = object(), object()  # synthetic owner payloads
        state = SimpleNamespace(captured_match_reports=(first, second),
                                fixture_match_info_links={700: 1, 701: 0})
        bridge = ManagementSourceDataBridge(SimpleNamespace(state=state))
        context = bridge.fixture_match_info_context(700)
        self.assertEqual((context.fixture_id, context.link_word), (700, 1))
        self.assertIs(context.captured_report, second)
        self.assertIs(bridge.fixture_match_info_context(701).captured_report, first)
        self.assertIsNone(bridge.fixture_match_info_context(702))

    def test_partial_or_invalid_owner_is_not_repaired(self):
        for state in (
            SimpleNamespace(captured_match_reports=()),
            SimpleNamespace(captured_match_reports=[], fixture_match_info_links={}),
            SimpleNamespace(captured_match_reports=(object(),), fixture_match_info_links={700: True}),
        ):
            bridge = ManagementSourceDataBridge(SimpleNamespace(state=state))
            with self.assertRaises(ManagementPresentationError):
                bridge.fixture_match_info_context(700)

    def build_presenter(self, context):
        class ReportBridge(Bridge):
            def fixture_match_info_context(self, fixture_id):
                return context
        session = FrontEndSession(Backend)
        session.dispatch(StartMenuControl.NEW_GAME)
        session.choose_club(12)
        session.dispatch(TeamSelectControl.START_CONTINUE)
        return OriginalManagementPresenter(session, bridge_factory=ReportBridge,
                                            selected_child_id=0x25C)

    def fixture_point(self, live):
        cell = next(c for c in live.snapshot().league_fixtures.cells if c.fixture_id == 700)
        return 378 + cell.column * 29, 235 + cell.row * 14

    def test_presenter_resolves_only_actual_matrix_fixture_context(self):
        context = SourceFixtureMatchInfoContext(700, 1, object())
        live = self.build_presenter(context)
        self.assertIs(live.fixture_report_at_screen_point(*self.fixture_point(live)), context)
        self.assertIsNone(live.fixture_report_at_screen_point(377, 235))
        self.assertIsNone(live.fixture_report_at_screen_point(378, 235))  # self cell
        live.selected_child_id = 0xCE
        self.assertIsNone(live.fixture_report_at_screen_point(407, 235))

    def test_presenter_rejects_wrong_fixture_context(self):
        live = self.build_presenter(SourceFixtureMatchInfoContext(999, 0, object()))
        with self.assertRaises(OriginalManagementPresentationError):
            live.fixture_report_at_screen_point(*self.fixture_point(live))

    def test_uncaptured_matrix_fixture_is_noop(self):
        live = self.build_presenter(None)
        self.assertIsNone(live.fixture_report_at_screen_point(*self.fixture_point(live)))

    def test_real_host_boundary_retains_context_and_closes_it(self):
        live = presenter()
        host = OriginalGameTkHost(live, FakeRoot(), FakeTk,
                                  pmatchinfo_snapshot=fake_pmatchinfo_snapshot())
        live.session.navigation.screen = FrontEndScreen.MANAGEMENT
        context = SourceFixtureMatchInfoContext(700, 0, object())
        class ReportPresenter(MatchInfoActionPresenter):
            def fixture_report_at_screen_point(self, x, y):
                return context
        host.management_presenter = ReportPresenter()
        with patch.object(host, 'redraw'):
            host.on_fixture_report_press(SimpleNamespace(x=400, y=300))
            self.assertIs(host.active_pmatchinfo_context, context)
            self.assertIsNotNone(host.active_pmatchinfo_art)
            host.apply_source_accepted_pmatchinfo_exit()
        self.assertIsNone(host.active_pmatchinfo_context)
        self.assertIsNone(host.active_pmatchinfo_art)

    def test_host_no_report_leaves_modal_absent(self):
        live = presenter()
        host = OriginalGameTkHost(live, FakeRoot(), FakeTk)
        live.session.navigation.screen = FrontEndScreen.MANAGEMENT
        host.management_presenter = SimpleNamespace(fixture_report_at_screen_point=lambda x, y: None)
        host.on_fixture_report_press(SimpleNamespace(x=400, y=300))
        self.assertIsNone(host.active_pmatchinfo_art)
        self.assertIsNone(host.active_pmatchinfo_context)

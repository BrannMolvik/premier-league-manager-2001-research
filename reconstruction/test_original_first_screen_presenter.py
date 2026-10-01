"""End-to-end headless first-screen source-bundle/navigation regressions."""
import struct
from types import SimpleNamespace
import unittest

from ea444_decoder import EA444DecodedImage
from ea_font import EAFont
from ea_language_strings import parse_language_pair
from front_end_session import FrontEndSession
from front_end_state import FrontEndCommand, FrontEndScreen
from original_button_frames import (
    OriginalButtonAtlasError,
    PSTARTMENU_BUTTON_ATLAS,
    TEAMSELECT_BUTTON_ATLAS,
    split_original_button_atlas,
)
from original_first_screen_presenter import (
    OriginalFirstScreenPresenter, OriginalHierarchyInteraction,
)
from original_teamselect_hierarchy_art import (
    HIERARCHY_ANIM_SPEC, HIERARCHY_BARS_SPEC,
    OriginalTeamSelectHierarchyArt, split_hierarchy_source_strip,
)
from original_front_end_layout import (
    PSTARTMENU_ACTIONS,
    TEAMSELECT_BACK_EVENT,
    TEAMSELECT_BACK_RECT,
    TEAMSELECT_HIERARCHY_ROW_ORIGINS,
    TEAMSELECT_START_EVENT,
    TEAMSELECT_START_RECT,
)
from original_pstartmenu_labels import prepare_original_pstartmenu_captions
from original_pstartmenu_resources import assemble_original_pstartmenu_inputs
from original_teamselect_resources import assemble_original_teamselect_inputs
from original_teamselect_native import TeamSelectHierarchyModel
from test_ea_font import build_fixture
from test_ea_language_strings import make_str


def solid(w, h, pixel):
    return EA444DecodedImage(w, h, bytes(pixel) * (w * h), 0, 0)


class StubBackend:
    def __init__(self):
        self.chosen = []

    def select_club(self, club_id):
        self.chosen.append(club_id)
        return ("manager", club_id)


class OriginalFirstScreenPresenterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global_bg = solid(800, 600, (2, 3, 4, 255))
        menu_bg = solid(532, 532, (5, 6, 7, 255))
        team_bg = solid(800, 558, (8, 9, 10, 255))
        menu_spec = PSTARTMENU_BUTTON_ATLAS
        team_spec = TEAMSELECT_BUTTON_ATLAS
        menu_atlas = split_original_button_atlas(
            solid(menu_spec.source_width, menu_spec.source_height, (11, 12, 13, 255)),
            menu_spec,
        )
        team_atlas = split_original_button_atlas(
            solid(team_spec.source_width, team_spec.source_height, (14, 15, 16, 255)),
            team_spec,
        )
        strings, index = parse_language_pair(
            make_str(("B", "AB", "A", "BA")),
            struct.pack("<7H", 1, 3, 2, 0, 0, 2, 0),
        )
        captions = prepare_original_pstartmenu_captions(
            EAFont.from_bytes(build_fixture()), strings, index
        )
        cls.menu = assemble_original_pstartmenu_inputs(
            global_bg, menu_bg, menu_atlas, captions
        )
        anim = split_hierarchy_source_strip(
            solid(HIERARCHY_ANIM_SPEC.frame_width,
                  HIERARCHY_ANIM_SPEC.frame_height,
                  (18, 19, 20, 255)),
            HIERARCHY_ANIM_SPEC,
        )
        bars = split_hierarchy_source_strip(
            solid(HIERARCHY_BARS_SPEC.frame_width,
                  HIERARCHY_BARS_SPEC.frame_height,
                  (21, 22, 23, 255)),
            HIERARCHY_BARS_SPEC,
        )
        cls.team = assemble_original_teamselect_inputs(
            global_bg, team_bg, team_atlas,
            OriginalTeamSelectHierarchyArt(anim, bars),
        )

    def presenter(self):
        built = []

        def factory():
            backend = StubBackend()
            built.append(backend)
            return backend

        presenter = OriginalFirstScreenPresenter(
            FrontEndSession(factory), self.menu, self.team
        )
        return presenter, built

    def test_start_screen_exposes_original_geometry_source_frames_and_font_masks(self):
        presenter, built = self.presenter()
        view = presenter.snapshot()
        self.assertIs(view.screen, FrontEndScreen.START_MENU)
        self.assertIs(view.background_rgba, self.menu.background_rgba)
        self.assertEqual(view.hierarchy_row_origins, ())
        self.assertEqual(tuple(x.event for x in view.controls), (1, 2, 3, 4))
        self.assertEqual(
            tuple(x.rect for x in view.controls),
            tuple(action.rect for action in PSTARTMENU_ACTIONS),
        )
        self.assertEqual(
            tuple(x.caption.original_text for x in view.controls),
            ("AB", "BA", "A", "B"),
        )
        self.assertEqual(view.controls[0].exact_source_frame(0).width, 169)
        self.assertEqual(
            view.controls[0].exact_source_frame(22).height, 25
        )
        with self.assertRaises(OriginalButtonAtlasError):
            view.controls[0].exact_source_frame(23)
        self.assertEqual(built, [])

    def test_pointer_integrates_menu_teamselect_and_manager_start_boundary(self):
        presenter, built = self.presenter()
        for x, y, command in (
            (181, 478, FrontEndCommand.CONTINUE_GAME),
            (355, 478, FrontEndCommand.LOAD_GAME),
            (181, 508, FrontEndCommand.QUIT_TO_WINDOWS),
        ):
            result = presenter.pointer(x, y)
            self.assertIs(result.transition.command, command)
            self.assertIs(presenter.snapshot().screen, FrontEndScreen.START_MENU)
        self.assertEqual(built, [])
        self.assertIsNone(presenter.pointer(0, 0))
        presenter.pointer(7, 478)  # proven event 2: New Game
        self.assertEqual(len(built), 1)
        view = presenter.snapshot()
        self.assertIs(view.screen, FrontEndScreen.TEAM_SELECT)
        self.assertIs(view.background_rgba, self.team.background_rgba)
        self.assertEqual(
            tuple((x.event, x.rect) for x in view.controls),
            ((TEAMSELECT_BACK_EVENT, TEAMSELECT_BACK_RECT),
             (TEAMSELECT_START_EVENT, TEAMSELECT_START_RECT)),
        )
        self.assertEqual(view.hierarchy_row_origins, TEAMSELECT_HIERARCHY_ROW_ORIGINS)
        self.assertIs(view.hierarchy_art, self.team.hierarchy_art)
        self.assertEqual(view.hierarchy_art.animation.source_frame(0).width, 30)
        self.assertEqual(view.hierarchy_art.bars.source_frame(0).width, 168)
        self.assertEqual(view.controls[0].exact_source_frame(22).width, 150)
        self.assertTrue(all(x.caption is None for x in view.controls))
        # Row IDs/content remain unproven. A click does not silently pick a club.
        self.assertIsNone(presenter.pointer(20, 78))
        self.assertIsNone(presenter.session.selected_club_id)
        presenter.choose_club(12)  # separate explicit data selection
        outcome = presenter.pointer(426, 301)
        self.assertIs(outcome.transition.command,
                      FrontEndCommand.TEAMSELECT_START_CONTINUE)
        self.assertEqual(outcome.selected_manager, ("manager", 12))
        self.assertTrue(presenter.session.started)
        self.assertEqual(built[0].chosen, [12])

    def test_native_club_row_toggle_stays_fail_closed_from_backend_id_mapping(self):
        presenter, built = self.presenter()
        presenter.pointer(7, 478)
        countries = {
            key: SimpleNamespace(id=key, name=name)
            for key, name in (
                (26, "England"), (66, "Scotland"), (33, "Germany"),
                (40, "Italy"), (73, "Spain"), (31, "France"),
                (24, "Holland"), (9, "Belgium"),
            )
        }
        competition = SimpleNamespace(
            id=0,
            name="F.A. Premier League",
            initialization_order_value=9,
            country_region_id=26,
            runtime_kind_code=1,
            parent_competition_id=None,
        )
        club = SimpleNamespace(index=0, name="Arsenal", competition_id=0)
        presenter.hierarchy = TeamSelectHierarchyModel(
            countries, (competition,), (club,)
        )

        # The developer-only backend picker uses a gameplay club ID. It must
        # not seed the unresolved native selection-record index by coincidence.
        presenter.choose_club(12)
        self.assertEqual(presenter.session.selected_club_id, 12)
        self.assertIsNone(presenter.hierarchy.selected_club_record_index)
        presenter.session.clear_club_selection()

        result = presenter.pointer(582, 79)
        self.assertIsInstance(result, OriginalHierarchyInteraction)
        self.assertEqual(result.row_kind, "club")
        self.assertEqual(result.source_id, 0)
        self.assertEqual(result.selected_club_record_index, 0)
        self.assertEqual(presenter.hierarchy.selected_club_record_index, 0)
        self.assertIsNone(presenter.session.selected_club_id)
        self.assertEqual(built[0].chosen, [])

        presenter.pointer(582, 79)
        self.assertIsNone(presenter.hierarchy.selected_club_record_index)
        self.assertIsNone(presenter.session.selected_club_id)
        self.assertEqual(built[0].chosen, [])

    def test_back_returns_to_original_menu_without_hidden_backend_reset(self):
        presenter, built = self.presenter()
        presenter.pointer(7, 478)
        original_backend = presenter.session.gameplay
        presenter.choose_club(12)
        outcome = presenter.pointer(225, 301)
        self.assertIs(outcome.transition.screen, FrontEndScreen.START_MENU)
        self.assertIs(presenter.session.gameplay, original_backend)
        self.assertIsNone(presenter.session.selected_club_id)
        self.assertIs(presenter.snapshot().background_rgba, self.menu.background_rgba)
        self.assertEqual(len(built), 1)


if __name__ == "__main__":
    unittest.main()

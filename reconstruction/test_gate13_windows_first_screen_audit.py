"""Synthetic contract tests for the real-Windows first-screen audit harness."""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from front_end_session import FrontEndSession
from front_end_state import FrontEndScreen
from gate13_windows_first_screen_audit import (
    WindowsFirstScreenAuditError,
    _require_private_receipt,
    audit_frame_contract,
    audit_management_host_contract,
    audit_source_accepted_pmenu_transition,
    expected_clean_host_photo_dimensions,
    expected_tk_photo_dimensions,
)
from original_first_screen_presenter import OriginalFirstScreenPresenter
from original_front_end_layout import (
    PSTARTMENU_ACTIONS,
    SCREEN_SIZE,
    TEAMSELECT_HIERARCHY_ROW_ORIGINS,
)
from original_pstartmenu_resources import assemble_original_pstartmenu_inputs
from original_teamselect_hierarchy_art import (
    HIERARCHY_ANIM_SPEC,
    HIERARCHY_BARS_SPEC,
    OriginalTeamSelectHierarchyArt,
    split_hierarchy_source_strip,
)
from original_teamselect_resources import assemble_original_teamselect_inputs
from test_original_pstartmenu_resources import fixture as menu_fixture
from test_original_teamselect_resources import (
    fixture as team_fixture,
    solid as team_solid,
)


class StubBackend:
    def select_club(self, club_id):
        return ("stub-manager", club_id)


def presenter() -> OriginalFirstScreenPresenter:
    base, team, action_atlas = team_fixture()

    def source_strip(spec, color):
        return split_hierarchy_source_strip(
            team_solid(spec.frame_width, spec.frame_height, color), spec
        )

    hierarchy_art = OriginalTeamSelectHierarchyArt(
        source_strip(HIERARCHY_ANIM_SPEC, (9, 8, 7, 255)),
        source_strip(HIERARCHY_BARS_SPEC, (4, 3, 2, 255)),
    )
    return OriginalFirstScreenPresenter(
        FrontEndSession(lambda: StubBackend()),
        assemble_original_pstartmenu_inputs(*menu_fixture()),
        assemble_original_teamselect_inputs(
            base, team, action_atlas, hierarchy_art
        ),
    )


class WindowsFirstScreenAuditContractTests(unittest.TestCase):
    def test_start_menu_contract_uses_only_recovered_actions_and_captions(self):
        live = presenter()
        snapshot = live.snapshot()
        self.assertIs(snapshot.screen, FrontEndScreen.START_MENU)
        record = audit_frame_contract(snapshot, 0)
        self.assertEqual(record["screen"], "START_MENU")
        self.assertEqual(
            [item["event"] for item in record["actions"]],
            [item.event for item in PSTARTMENU_ACTIONS],
        )
        self.assertEqual(len(record["captions"]), 4)
        self.assertEqual(record["hierarchy_row_origins"], [])
        self.assertEqual(
            record["expected_tk_photo_dimensions"][0],
            list(SCREEN_SIZE),
        )
        self.assertEqual(
            len(record["expected_tk_photo_dimensions"]),
            1 + 4 + 4,
        )

    def test_alternate_group_contract_preserves_native_black_caption_endpoint(self):
        live = presenter()
        record = audit_frame_contract(live.snapshot(), 11)
        self.assertTrue(record["captions"])
        self.assertTrue(
            all(item["native_color_16"] == 0x0000 for item in record["captions"])
        )
        self.assertTrue(
            all(item["source_frame_index"] == 11 for item in record["actions"])
        )

    def test_teamselect_contract_keeps_hierarchy_noninteractive_and_uncaptioned(self):
        live = presenter()
        live.session.dispatch(2)
        snapshot = live.snapshot()
        self.assertIs(snapshot.screen, FrontEndScreen.TEAM_SELECT)
        record = audit_frame_contract(snapshot, 0)
        self.assertEqual(
            [item["event"] for item in record["actions"]],
            [0x29, 0x2A],
        )
        self.assertEqual(record["captions"], [])
        self.assertEqual(
            record["hierarchy_row_origins"],
            [list(item) for item in TEAMSELECT_HIERARCHY_ROW_ORIGINS],
        )
        # Background + Back/Start + independent animation/bars source previews.
        self.assertEqual(
            len(record["expected_tk_photo_dimensions"]),
            1 + 2 + 2,
        )

    def test_expected_photo_geometry_is_derived_from_snapshot_source_art(self):
        live = presenter()
        menu_dims = expected_tk_photo_dimensions(live.snapshot(), 0)
        self.assertEqual(menu_dims[0], SCREEN_SIZE)
        self.assertEqual(menu_dims[1:5], ((169, 25),) * 4)
        live.session.dispatch(2)
        team_dims = expected_tk_photo_dimensions(live.snapshot(), 0)
        self.assertEqual(team_dims[0], SCREEN_SIZE)
        self.assertEqual(team_dims[1:3], ((150, 32), (150, 32)))
        self.assertEqual(team_dims[-2:], ((30, 29), (168, 29)))


    def test_clean_host_photo_dimensions_follow_panel_pmenu_and_modal_order(self):
        pmenu_dimensions = [[30, 29], [168, 29]]

        def run_case(panel_class, panel_snapshot, host_fields, expected_panel):
            presenter_stub = object()
            host = SimpleNamespace(
                management_presenter=presenter_stub,
                active_pmatchinfo_art=host_fields.pop(
                    "active_pmatchinfo_art", None
                ),
                **host_fields,
            )
            frame = SimpleNamespace(
                presentation=SimpleNamespace(
                    panel_class=panel_class,
                    squad_view_transition=(
                        SimpleNamespace(control_id=3)
                        if panel_class == "PSquadScreen"
                        else None
                    ),
                    league_fixtures=(
                        panel_snapshot if panel_class == "PLeagueFixtures" else None
                    ),
                    league_tables=(
                        panel_snapshot if panel_class == "PLeagueTables" else None
                    ),
                )
            )
            with (
                patch(
                    "gate13_windows_first_screen_audit.build_management_canvas_frame",
                    return_value=frame,
                ),
                patch(
                    "gate13_windows_first_screen_audit.expected_management_pmenu_photo_dimensions",
                    return_value=pmenu_dimensions,
                ),
                patch(
                    "gate13_windows_first_screen_audit.build_fresh_squad_top_render",
                    return_value=SimpleNamespace(
                        photo_dimensions=((73, 25), (41, 15))
                    ),
                ),
            ):
                return expected_clean_host_photo_dimensions(host, object())

        squad = run_case(
            "PSquadScreen",
            None,
            {
                "squad_top_resources": object(),
                "league_fixtures_grid_art": None,
                "league_tables_header_art": None,
            },
            [[73, 25], [41, 15]],
        )
        self.assertEqual(squad, [[73, 25], [41, 15], *pmenu_dimensions])

        post_transition_host = SimpleNamespace(
            management_presenter=object(),
            active_pmatchinfo_art=None,
            squad_top_resources=object(),
            league_fixtures_grid_art=None,
            league_tables_header_art=None,
        )
        post_transition_frame = SimpleNamespace(
            presentation=SimpleNamespace(
                panel_class="PSquadScreen",
                squad_view_transition=SimpleNamespace(control_id=4),
                league_fixtures=None,
                league_tables=None,
            )
        )
        with (
            patch(
                "gate13_windows_first_screen_audit.build_management_canvas_frame",
                return_value=post_transition_frame,
            ),
            patch(
                "gate13_windows_first_screen_audit.expected_management_pmenu_photo_dimensions",
                return_value=pmenu_dimensions,
            ),
        ):
            self.assertEqual(
                expected_clean_host_photo_dimensions(post_transition_host, object()),
                pmenu_dimensions,
            )

        fixture_art = SimpleNamespace(
            placements=(
                SimpleNamespace(width=5, height=17),
                SimpleNamespace(width=28, height=5),
            )
        )
        fixtures = run_case(
            "PLeagueFixtures",
            SimpleNamespace(exact_art_staged=True),
            {
                "squad_top_resources": None,
                "league_fixtures_grid_art": fixture_art,
                "league_tables_header_art": None,
                "active_pmatchinfo_art": SimpleNamespace(width=760, height=500),
            },
            [[5, 17], [28, 5]],
        )
        self.assertEqual(
            fixtures,
            [[5, 17], [28, 5], *pmenu_dimensions, [760, 500]],
        )

        tables = run_case(
            "PLeagueTables",
            SimpleNamespace(exact_art_staged=True),
            {
                "squad_top_resources": None,
                "league_fixtures_grid_art": None,
                "league_tables_header_art": SimpleNamespace(width=475, height=19),
            },
            [[475, 19]],
        )
        self.assertEqual(tables, [[475, 19], *pmenu_dimensions])

    def test_clean_host_photo_dimensions_fail_closed_on_missing_exact_panel_art(self):
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                panel_class="PLeagueFixtures",
                league_fixtures=SimpleNamespace(exact_art_staged=False),
                league_tables=None,
            )
        )
        host = SimpleNamespace(
            management_presenter=object(),
            squad_top_resources=None,
            league_fixtures_grid_art=object(),
            league_tables_header_art=None,
            active_pmatchinfo_art=None,
        )
        with patch(
            "gate13_windows_first_screen_audit.build_management_canvas_frame",
            return_value=frame,
        ):
            with self.assertRaisesRegex(
                WindowsFirstScreenAuditError,
                "lost exact staged grid art",
            ):
                expected_clean_host_photo_dimensions(host, object())

    def test_clean_host_photo_dimensions_reject_unrecovered_squad_view_control(self):
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                panel_class="PSquadScreen",
                squad_view_transition=SimpleNamespace(control_id=6),
                league_fixtures=None,
                league_tables=None,
            )
        )
        host = SimpleNamespace(
            management_presenter=object(),
            squad_top_resources=object(),
            league_fixtures_grid_art=None,
            league_tables_header_art=None,
            active_pmatchinfo_art=None,
        )
        with patch(
            "gate13_windows_first_screen_audit.build_management_canvas_frame",
            return_value=frame,
        ):
            with self.assertRaisesRegex(
                WindowsFirstScreenAuditError,
                "unrecovered view control",
            ):
                expected_clean_host_photo_dimensions(host, object())

    def test_management_host_contract_preserves_geometry_and_open_pixel_boundaries(self):
        frame = SimpleNamespace(
            screen_size=(800, 600),
            menu_rect=(599, 96, 201, 504),
            panel_rect=(0, 79, 800, 520),
            presentation=SimpleNamespace(
                panel_class="PSquadScreen",
                panel_code=0xCE,
            ),
            surrounding_background_recovered=False,
            pmenu_text_placement_recovered=True,
            complete_source_pixel_frame_available=False,
        )
        record = audit_management_host_contract(
            frame,
            canvas_size=[800, 600],
            photo_dimensions=[],
            status=(
                "Backend selection returned ('manager', 12); "
                "entered source-proven PMenu management host."
            ),
        )
        self.assertEqual(record["screen_size"], [800, 600])
        self.assertEqual(record["pmenu_rect"], [599, 96, 201, 504])
        self.assertEqual(record["panel_rect"], [0, 79, 800, 520])
        self.assertEqual(record["panel_class"], "PSquadScreen")
        self.assertEqual(record["panel_code"], 0xCE)
        self.assertEqual(record["photo_dimensions"], [])
        self.assertFalse(record["surrounding_background_recovered"])
        self.assertTrue(record["pmenu_text_placement_recovered"])
        self.assertFalse(record["pmenu_rows_rendered"])
        self.assertFalse(record["complete_source_pixel_frame_available"])

        source_photos = [[30, 29], [168, 29], [42, 24]]
        clean_record = audit_management_host_contract(
            frame,
            canvas_size=[800, 600],
            photo_dimensions=source_photos,
            status=(
                "Management host active: PSquadScreen; "
                "source PMenu rows rendered; surrounding management background unresolved"
            ),
            required_status_fragment="source PMenu rows rendered",
            expected_pmenu_photo_dimensions=source_photos,
        )
        self.assertEqual(clean_record["panel_code"], 0xCE)
        self.assertEqual(clean_record["photo_dimensions"], source_photos)
        self.assertTrue(clean_record["pmenu_rows_rendered"])

    def test_management_host_contract_fails_closed_on_guessed_pixels_or_geometry(self):
        base = dict(
            screen_size=(800, 600),
            menu_rect=(599, 96, 201, 504),
            panel_rect=(0, 79, 800, 520),
            presentation=SimpleNamespace(
                panel_class="PSquadScreen",
                panel_code=0xCE,
            ),
            surrounding_background_recovered=False,
            pmenu_text_placement_recovered=True,
            complete_source_pixel_frame_available=False,
        )
        status = "entered source-proven PMenu management host."

        bad_cases = (
            ("PMenu rectangle", {"menu_rect": (598, 96, 201, 504)}, [800, 600], []),
            ("PSquadScreen geometry", {"panel_rect": (0, 80, 800, 520)}, [800, 600], []),
            ("surrounding background", {"surrounding_background_recovered": True}, [800, 600], []),
            ("lost recovered PMenu text placement", {"pmenu_text_placement_recovered": False}, [800, 600], []),
            ("fixed 800x600", {}, [801, 600], []),
            ("uncontracted PhotoImages", {}, [800, 600], [[800, 600]]),
        )
        for expected, changes, canvas_size, photos in bad_cases:
            with self.subTest(expected=expected):
                values = dict(base)
                values.update(changes)
                with self.assertRaisesRegex(WindowsFirstScreenAuditError, expected):
                    audit_management_host_contract(
                        SimpleNamespace(**values),
                        canvas_size=canvas_size,
                        photo_dimensions=photos,
                        status=status,
                    )

        with self.assertRaisesRegex(
            WindowsFirstScreenAuditError,
            "Live PMenu PhotoImage geometry",
        ):
            audit_management_host_contract(
                SimpleNamespace(**base),
                canvas_size=[800, 600],
                photo_dimensions=[[30, 29]],
                status="source PMenu rows rendered",
                required_status_fragment="source PMenu rows rendered",
                expected_pmenu_photo_dimensions=[[168, 29]],
            )

        with self.assertRaisesRegex(
            WindowsFirstScreenAuditError,
            "PMenu host transition",
        ):
            audit_management_host_contract(
                SimpleNamespace(**base),
                canvas_size=[800, 600],
                photo_dimensions=[],
                status="wrong status",
            )

    def test_source_accepted_transition_record_keeps_event_equivalence_separate(self):
        title = SimpleNamespace(
            action=SimpleNamespace(
                accepted=True,
                row_kind="title",
                menu_id=0x259,
                action_kind="expand_root",
                panel_factory_arguments=None,
            ),
            presentation=SimpleNamespace(
                menu=SimpleNamespace(
                    selected_root_id=0x259,
                    selected_child_id=0xCE,
                ),
                panel_code=0xCE,
                panel_class="PSquadScreen",
            ),
        )
        record = audit_source_accepted_pmenu_transition(
            title,
            expected_row_kind="title",
            expected_menu_id=0x259,
            expected_action_kind="expand_root",
            expected_root_id=0x259,
            expected_child_id=0xCE,
            expected_panel_code=0xCE,
            expected_panel_class="PSquadScreen",
        )
        self.assertEqual(record["action_kind"], "expand_root")
        self.assertEqual(record["expanded_root_id"], 0x259)
        self.assertEqual(record["selected_child_id"], 0xCE)
        self.assertIsNone(record["panel_factory_arguments"])

        child = SimpleNamespace(
            action=SimpleNamespace(
                accepted=True,
                row_kind="child",
                menu_id=0x25C,
                action_kind="open_panel",
                panel_factory_arguments=(0x25C, 0),
            ),
            presentation=SimpleNamespace(
                menu=SimpleNamespace(
                    selected_root_id=0x259,
                    selected_child_id=0x25C,
                ),
                panel_code=0x25C,
                panel_class="PLeagueFixtures",
            ),
        )
        record = audit_source_accepted_pmenu_transition(
            child,
            expected_row_kind="child",
            expected_menu_id=0x25C,
            expected_action_kind="open_panel",
            expected_root_id=0x259,
            expected_child_id=0x25C,
            expected_panel_code=0x25C,
            expected_panel_class="PLeagueFixtures",
        )
        self.assertEqual(record["panel_factory_arguments"], [0x25C, 0])
        self.assertEqual(record["panel_class"], "PLeagueFixtures")

    def test_source_accepted_transition_record_fails_closed_on_contract_drift(self):
        base_action = dict(
            accepted=True,
            row_kind="child",
            menu_id=0x25A,
            action_kind="open_panel",
            panel_factory_arguments=(0x25A, 0),
        )
        base_presentation = dict(
            menu=SimpleNamespace(selected_root_id=6, selected_child_id=0x25A),
            panel_code=0x25A,
            panel_class="PLeagueTables",
        )
        cases = (
            ("unexpectedly rejected", {"accepted": False}, {}),
            ("identity changed", {"menu_id": 0x25C}, {}),
            ("action kind changed", {"action_kind": "expand_root"}, {}),
            ("panel-factory arguments", {"panel_factory_arguments": (0x25A, 1)}, {}),
            ("wrong expanded root", {}, {"menu": SimpleNamespace(selected_root_id=0x259, selected_child_id=0x25A)}),
            ("wrong selected child", {}, {"menu": SimpleNamespace(selected_root_id=6, selected_child_id=0x25C)}),
            ("wrong panel code", {}, {"panel_code": 0x25C}),
            ("wrong panel class", {}, {"panel_class": "PLeagueFixtures"}),
        )
        for expected, action_changes, presentation_changes in cases:
            with self.subTest(expected=expected):
                action_values = dict(base_action)
                action_values.update(action_changes)
                presentation_values = dict(base_presentation)
                presentation_values.update(presentation_changes)
                result = SimpleNamespace(
                    action=SimpleNamespace(**action_values),
                    presentation=SimpleNamespace(**presentation_values),
                )
                with self.assertRaisesRegex(WindowsFirstScreenAuditError, expected):
                    audit_source_accepted_pmenu_transition(
                        result,
                        expected_row_kind="child",
                        expected_menu_id=0x25A,
                        expected_action_kind="open_panel",
                        expected_root_id=6,
                        expected_child_id=0x25A,
                        expected_panel_code=0x25A,
                        expected_panel_class="PLeagueTables",
                    )
    def test_receipt_must_stay_outside_repository_and_never_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            with self.assertRaisesRegex(
                WindowsFirstScreenAuditError, "outside Git"
            ):
                _require_private_receipt(
                    root / "audit.json", repository_root=root
                )

            outside = Path(temp) / "private" / "audit.json"
            checked = _require_private_receipt(outside, repository_root=root)
            self.assertEqual(checked, outside.resolve())
            checked.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(
                WindowsFirstScreenAuditError, "do not overwrite"
            ):
                _require_private_receipt(outside, repository_root=root)


if __name__ == "__main__":
    unittest.main()

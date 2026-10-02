"""Synthetic contract tests for the real-Windows first-screen audit harness."""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from front_end_session import FrontEndSession
from front_end_state import FrontEndScreen
from gate13_windows_first_screen_audit import (
    WindowsFirstScreenAuditError,
    _require_private_receipt,
    audit_frame_contract,
    audit_management_host_contract,
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


    def test_management_host_contract_requires_exact_geometry_and_incomplete_pixels(self):
        frame = SimpleNamespace(
            menu_rect=(599, 96, 201, 504),
            panel_rect=(0, 79, 800, 520),
            presentation=SimpleNamespace(
                panel_class="PSquadScreen",
                menu=SimpleNamespace(selected_child_id=0xCE),
            ),
            complete_source_pixel_frame_available=False,
            surrounding_background_recovered=False,
            pmenu_text_placement_recovered=False,
        )
        record = audit_management_host_contract(
            frame,
            canvas_size=(800, 600),
            photo_count=0,
        )
        self.assertEqual(record["menu_rect"], [599, 96, 201, 504])
        self.assertEqual(record["panel_rect"], [0, 79, 800, 520])
        self.assertEqual(record["panel_class"], "PSquadScreen")
        self.assertEqual(record["selected_child_id"], 0xCE)
        self.assertFalse(record["complete_source_pixel_frame_available"])

        bad_cases = (
            ("canvas", {"canvas_size": (799, 600), "photo_count": 0}),
            ("photos", {"canvas_size": (800, 600), "photo_count": 1}),
        )
        for _label, kwargs in bad_cases:
            with self.subTest(label=_label):
                with self.assertRaises(WindowsFirstScreenAuditError):
                    audit_management_host_contract(frame, **kwargs)

        for attribute, value in (
            ("menu_rect", (598, 96, 201, 504)),
            ("panel_rect", (0, 80, 800, 520)),
            ("complete_source_pixel_frame_available", True),
            ("surrounding_background_recovered", True),
            ("pmenu_text_placement_recovered", True),
        ):
            broken = SimpleNamespace(**vars(frame))
            setattr(broken, attribute, value)
            with self.subTest(attribute=attribute):
                with self.assertRaises(WindowsFirstScreenAuditError):
                    audit_management_host_contract(
                        broken,
                        canvas_size=(800, 600),
                        photo_count=0,
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

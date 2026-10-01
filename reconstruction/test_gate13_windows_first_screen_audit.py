"""Synthetic contract tests for the real-Windows first-screen audit harness."""
from pathlib import Path
import tempfile
import unittest

from front_end_session import FrontEndSession
from front_end_state import FrontEndScreen
from gate13_windows_first_screen_audit import (
    WindowsFirstScreenAuditError,
    _require_private_receipt,
    audit_frame_contract,
    expected_tk_photo_dimensions,
)
from original_first_screen_presenter import OriginalFirstScreenPresenter
from original_front_end_layout import (
    PSTARTMENU_ACTIONS,
    SCREEN_SIZE,
    TEAMSELECT_HIERARCHY_ROW_ORIGINS,
)
from original_pstartmenu_resources import assemble_original_pstartmenu_inputs
from original_teamselect_resources import assemble_original_teamselect_inputs
from test_original_pstartmenu_resources import fixture as menu_fixture
from test_original_teamselect_resources import fixture as team_fixture


class StubBackend:
    def select_club(self, club_id):
        return ("stub-manager", club_id)


def presenter() -> OriginalFirstScreenPresenter:
    return OriginalFirstScreenPresenter(
        FrontEndSession(lambda: StubBackend()),
        assemble_original_pstartmenu_inputs(*menu_fixture()),
        assemble_original_teamselect_inputs(*team_fixture()),
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

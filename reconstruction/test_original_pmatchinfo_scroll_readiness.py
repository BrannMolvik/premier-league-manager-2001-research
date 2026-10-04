"""Tests for fail-closed PMatchInfo scroll-resource readiness."""
from pathlib import Path
import tempfile
import unittest

from original_pmatchinfo_scroll_readiness import (
    PMATCHINFO_SCROLL_EXACT_PATH_FILE,
    PMATCHINFO_SCROLL_IMPORT_ROOT,
    PMATCHINFO_SCROLL_RESOURCE_LEADS,
    audit_pmatchinfo_scroll_resource_readiness,
    pending_pmatchinfo_scroll_source_paths,
    validate_pmatchinfo_scroll_exact_path_contract,
)


class PMatchInfoScrollReadinessTests(unittest.TestCase):
    def _write_known(self, root: Path, lead, data: bytes):
        path = root / PMATCHINFO_SCROLL_IMPORT_ROOT / lead.source_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def test_missing_resources_stay_explicit_and_behavior_false(self):
        with tempfile.TemporaryDirectory() as temp:
            result = audit_pmatchinfo_scroll_resource_readiness(temp)
        self.assertEqual(result["verified_staged_resource_names"], [])
        self.assertEqual(
            result["missing_resource_names"],
            [lead.name for lead in PMATCHINFO_SCROLL_RESOURCE_LEADS],
        )
        self.assertFalse(result["resource_inventory_complete"])
        self.assertFalse(result["native_scroll_behavior_recovered"])
        self.assertFalse(result["renderer_geometry_recovered"])

    def test_present_unknown_identity_does_not_become_verified(self):
        unknown = next(
            lead for lead in PMATCHINFO_SCROLL_RESOURCE_LEADS
            if not lead.has_staged_identity
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_known(root, unknown, b"candidate")
            result = audit_pmatchinfo_scroll_resource_readiness(root)
        self.assertIn(unknown.name, result["present_resource_names"])
        self.assertIn(
            unknown.name,
            result["present_but_identity_unverified_resource_names"],
        )
        self.assertIn(unknown.name, result["pending_resource_names"])
        self.assertFalse(result["resource_inventory_complete"])

    def test_known_identity_size_mismatch_fails_closed(self):
        known = next(
            lead for lead in PMATCHINFO_SCROLL_RESOURCE_LEADS
            if lead.has_staged_identity
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._write_known(root, known, b"x")
            with self.assertRaisesRegex(ValueError, "size mismatch"):
                audit_pmatchinfo_scroll_resource_readiness(root)

    def test_repository_stages_only_the_two_currently_proven_identities(self):
        repo_root = Path(__file__).resolve().parent.parent
        result = audit_pmatchinfo_scroll_resource_readiness(repo_root)
        self.assertEqual(
            result["verified_staged_resource_names"],
            ["arrow_atlas", "end_vertical"],
        )
        self.assertEqual(
            result["missing_resource_names"],
            ["bar_vertical", "bar_blue", "thumb_blue"],
        )
        self.assertEqual(
            result["pending_resource_names"],
            ["bar_vertical", "bar_blue", "thumb_blue"],
        )
        self.assertFalse(result["resource_inventory_complete"])
        self.assertFalse(result["native_scroll_behavior_recovered"])

    def test_exact_path_file_matches_pending_source_leads(self):
        repo_root = Path(__file__).resolve().parent.parent
        expected = (
            "FM2001_Art/Generic/GenericButtonsAndBars/scroller_bar_vert.444",
            "FM2001_Art/Generic/GenericButtonsAndBars/scroller_blue_bar.444",
            "FM2001_Art/Generic/GenericButtonsAndBars/vscroll_blue_bar.444",
        )
        self.assertEqual(pending_pmatchinfo_scroll_source_paths(), expected)
        self.assertEqual(
            validate_pmatchinfo_scroll_exact_path_contract(repo_root),
            expected,
        )
        self.assertTrue((repo_root / PMATCHINFO_SCROLL_EXACT_PATH_FILE).is_file())

    def test_exact_path_contract_rejects_missing_or_extra_selection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / PMATCHINFO_SCROLL_EXACT_PATH_FILE
            path.parent.mkdir(parents=True)
            path.write_text(
                "FM2001_Art/Generic/GenericButtonsAndBars/scroller_bar_vert.444\n"
                "FM2001_Art/Generic/GenericButtonsAndBars/unproven.444\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError,
                "exact-path staging contract mismatch",
            ):
                validate_pmatchinfo_scroll_exact_path_contract(root)

    def test_source_contract_keeps_exact_loader_order(self):
        self.assertEqual(
            [(lead.name, lead.loader_va) for lead in PMATCHINFO_SCROLL_RESOURCE_LEADS],
            [
                ("arrow_atlas", 0x5F2BC0),
                ("bar_vertical", 0x5F2DA0),
                ("bar_blue", 0x5F2E30),
                ("end_vertical", 0x5F2E80),
                ("thumb_blue", 0x5F2F10),
            ],
        )


if __name__ == "__main__":
    unittest.main()

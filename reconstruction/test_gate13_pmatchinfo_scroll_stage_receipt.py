"""Tests for the private PMatchInfo scroll staging receipt validator."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from gate13_pmatchinfo_scroll_stage_receipt import (
    PMatchInfoScrollStageReceiptError,
    validate_pmatchinfo_scroll_stage_receipt,
)
from original_pmatchinfo_scroll_readiness import (
    PMATCHINFO_SCROLL_EXACT_PATH_FILE,
    pending_pmatchinfo_scroll_source_paths,
)


def _ea444(width: int, height: int, marker: int) -> bytes:
    return (
        int(width).to_bytes(2, "little")
        + int(height).to_bytes(2, "little")
        + bytes.fromhex("64 ff 00 ff")
        + bytes([marker])
    )


class PMatchInfoScrollStageReceiptTests(unittest.TestCase):
    def _fixture(self, root: Path):
        repo = root / "repo"
        stage = root / "stage"
        report = root / "selection.json"
        contract = repo / PMATCHINFO_SCROLL_EXACT_PATH_FILE
        contract.parent.mkdir(parents=True)
        expected = pending_pmatchinfo_scroll_source_paths()
        contract.write_text("\n".join(expected) + "\n", encoding="utf-8")

        candidates = []
        for index, source_path in enumerate(expected, start=1):
            data = _ea444(10 + index, 20 + index, index)
            path = stage.joinpath(*source_path.split("/"))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            candidates.append(
                {
                    "path": source_path,
                    "size": len(data),
                    "sha256": sha256(data).hexdigest(),
                    "source_layer": "iso9660-extracted",
                    "candidate_reason": "explicit-path",
                }
            )
        payload = {
            "schema_version": 1,
            "source_sha256": "a" * 64,
            "only_explicit": True,
            "explicit_paths": list(expected),
            "unresolved_explicit_paths": [],
            "candidates": candidates,
        }
        report.write_text(json.dumps(payload), encoding="utf-8")
        return repo, stage, report, payload

    def test_complete_hashed_exact_selection_produces_identity_only_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, stage, report, _payload = self._fixture(Path(temp))
            receipt = validate_pmatchinfo_scroll_stage_receipt(
                repo_root=repo,
                inventory_report=report,
                staging_root=stage,
            )
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["source_sha256"], "a" * 64)
        self.assertEqual(receipt["asset_count"], 3)
        self.assertEqual(
            [item["source_path"] for item in receipt["assets"]],
            list(pending_pmatchinfo_scroll_source_paths()),
        )
        self.assertEqual(
            [(item["header_width"], item["header_height"]) for item in receipt["assets"]],
            [(11, 21), (12, 22), (13, 23)],
        )
        self.assertTrue(receipt["ready_for_provenance_import"])
        self.assertFalse(receipt["native_scroll_behavior_recovered"])
        self.assertFalse(receipt["renderer_geometry_recovered"])

    def test_unhashed_or_partial_report_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, stage, report, payload = self._fixture(Path(temp))
            payload["source_sha256"] = None
            report.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                PMatchInfoScrollStageReceiptError,
                "requires a hashed source archive",
            ):
                validate_pmatchinfo_scroll_stage_receipt(
                    repo_root=repo,
                    inventory_report=report,
                    staging_root=stage,
                )

            payload["source_sha256"] = "a" * 64
            payload["unresolved_explicit_paths"] = [payload["explicit_paths"][0]]
            report.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                PMatchInfoScrollStageReceiptError,
                "unresolved exact paths",
            ):
                validate_pmatchinfo_scroll_stage_receipt(
                    repo_root=repo,
                    inventory_report=report,
                    staging_root=stage,
                )

    def test_staged_bytes_must_match_inventory_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, stage, report, payload = self._fixture(Path(temp))
            first = payload["explicit_paths"][0]
            stage.joinpath(*first.split("/")).write_bytes(_ea444(99, 99, 9))
            with self.assertRaisesRegex(
                PMatchInfoScrollStageReceiptError,
                "differs from inventory",
            ):
                validate_pmatchinfo_scroll_stage_receipt(
                    repo_root=repo,
                    inventory_report=report,
                    staging_root=stage,
                )

    def test_candidate_set_and_extracted_layer_are_strict(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, stage, report, payload = self._fixture(Path(temp))
            payload["candidates"][0]["source_layer"] = "iso9660-catalog"
            report.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                PMatchInfoScrollStageReceiptError,
                "does not prove extracted source bytes",
            ):
                validate_pmatchinfo_scroll_stage_receipt(
                    repo_root=repo,
                    inventory_report=report,
                    staging_root=stage,
                )


if __name__ == "__main__":
    unittest.main()

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from gate14_audio_catalog import (
    CANONICAL_SOUND_BANK_COUNT,
    build_audio_catalog,
    main,
    selected_paths,
    validate_canonical_audio_catalog,
)


class Gate14AudioCatalogTests(unittest.TestCase):
    def test_reducer_keeps_banks_and_exact_startup_media_only(self):
        report = {
            "source_sha256": "source",
            "disc_file_count": 6,
            "disc_files": [
                {"path": "Sound/UI.BNK", "size": 10, "extent": 1},
                {"path": "Sound/match.bnk", "size": 20, "extent": 2},
                {"path": "FMV/easp.tgq", "size": 30, "extent": 3},
                {"path": "FMV/premintro.tgq", "size": 40, "extent": 4},
                {"path": "Other/not-startup.tgq", "size": 50, "extent": 5},
                {"path": "Other/guess.wav", "size": 60, "extent": 6},
            ],
        }

        catalog = build_audio_catalog(report)

        self.assertEqual(catalog["source_sha256"], "source")
        self.assertEqual(catalog["sound_bank_count"], 2)
        self.assertEqual(
            [item["path"] for item in catalog["sound_banks"]],
            ["Sound/match.bnk", "Sound/UI.BNK"],
        )
        self.assertEqual(
            [item["binding_status"] for item in catalog["sound_banks"]],
            ["unmapped", "unmapped"],
        )
        self.assertEqual(
            [item["path"] for item in catalog["startup_media"]],
            ["FMV/easp.tgq", "FMV/premintro.tgq"],
        )
        self.assertFalse(catalog["bank_semantics_recovered"])
        self.assertFalse(catalog["bank_event_bindings_recovered"])

    def test_candidate_hash_is_reused_without_inventing_missing_hashes(self):
        report = {
            "disc_files": [
                {"path": "Audio/click.bnk", "size": 7, "extent": 11},
                {"path": "Audio/other.bnk", "size": 8, "extent": 12},
            ],
            "candidates": [
                {
                    "path": "audio/CLICK.BNK",
                    "sha256": "a" * 64,
                }
            ],
        }

        catalog = build_audio_catalog(report)

        self.assertEqual(catalog["sound_banks"][0]["sha256"], "a" * 64)
        self.assertIsNone(catalog["sound_banks"][1]["sha256"])

    def test_duplicate_case_insensitive_disc_paths_fail_closed(self):
        report = {
            "disc_files": [
                {"path": "Audio/UI.bnk", "size": 1, "extent": 1},
                {"path": "audio/ui.BNK", "size": 1, "extent": 2},
            ]
        }
        with self.assertRaisesRegex(ValueError, "Duplicate case-insensitive"):
            build_audio_catalog(report)

    def test_conflicting_candidate_hashes_fail_closed(self):
        report = {
            "disc_files": [{"path": "Audio/UI.bnk", "size": 1, "extent": 1}],
            "candidates": [
                {"path": "Audio/UI.bnk", "sha256": "a" * 64},
                {"path": "audio/ui.BNK", "sha256": "b" * 64},
            ],
        }
        with self.assertRaisesRegex(ValueError, "Conflicting source hashes"):
            build_audio_catalog(report)

    def test_canonical_validation_requires_64_unmapped_banks_and_two_tgqs(self):
        disc_files = [
            {
                "path": f"Audio/bank_{index:02d}.bnk",
                "size": index + 1,
                "extent": index + 100,
            }
            for index in range(CANONICAL_SOUND_BANK_COUNT)
        ]
        disc_files.extend(
            [
                {"path": "FMV/easp.tgq", "size": 10, "extent": 1000},
                {"path": "FMV/premintro.tgq", "size": 20, "extent": 1001},
            ]
        )
        catalog = build_audio_catalog({"disc_files": disc_files})
        validate_canonical_audio_catalog(catalog)

        catalog["sound_bank_count"] -= 1
        with self.assertRaisesRegex(ValueError, "exactly 64"):
            validate_canonical_audio_catalog(catalog)

    def test_selected_paths_preserves_bank_sort_and_startup_sequence(self):
        catalog = build_audio_catalog(
            {
                "disc_files": [
                    {"path": "Z/z.bnk", "size": 1, "extent": 1},
                    {"path": "A/a.bnk", "size": 1, "extent": 2},
                    {"path": "FMV/premintro.tgq", "size": 1, "extent": 3},
                    {"path": "FMV/easp.tgq", "size": 1, "extent": 4},
                ]
            }
        )
        self.assertEqual(
            selected_paths(catalog, "all"),
            [
                "A/a.bnk",
                "Z/z.bnk",
                "FMV/easp.tgq",
                "FMV/premintro.tgq",
            ],
        )

    def test_cli_paths_only_can_emit_bank_extraction_list(self):
        report = {
            "disc_files": [
                {"path": "Audio/b.bnk", "size": 2, "extent": 1},
                {"path": "Audio/a.bnk", "size": 1, "extent": 2},
                {"path": "FMV/easp.tgq", "size": 3, "extent": 3},
                {"path": "FMV/premintro.tgq", "size": 4, "extent": 4},
            ]
        }
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "report.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            output = io.StringIO()
            with patch(
                "sys.argv",
                [
                    "gate14_audio_catalog.py",
                    str(path),
                    "--kind",
                    "banks",
                    "--paths-only",
                ],
            ):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(main(), 0)

        self.assertEqual(output.getvalue().splitlines(), ["Audio/a.bnk", "Audio/b.bnk"])


if __name__ == "__main__":
    unittest.main()

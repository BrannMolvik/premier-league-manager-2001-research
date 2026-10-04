"""Tests for exact Gate-14 audio-bank source staging."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from gate14_audio_bank_source_paths import (
    AUDIO_BANK_EXACT_PATH_FILE,
    CANONICAL_AUDIO_SOURCE_ARCHIVE_SHA256,
    CANONICAL_AUDIO_SOURCE_ARCHIVE_SIZE,
    Gate14AudioBankSourcePathError,
    expected_audio_bank_source_paths,
    validate_audio_bank_exact_path_contract,
)
from gate14_audio_bank_stage_receipt import (
    Gate14AudioBankStageReceiptError,
    validate_audio_bank_stage_receipt,
)


EXPECTED = (
    "DATA/AUDIO/SFXS/menus.bnk",
    "DATA/AUDIO/SFXS/game00.bnk",
    "DATA/AUDIO/SFXS/playercalls.bnk",
    "DATA/AUDIO/SFXS/Advice.bnk",
)


def write_contract(root: Path, paths=EXPECTED) -> None:
    target = root / AUDIO_BANK_EXACT_PATH_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "# synthetic exact-path contract\n"
        + "\n".join(paths)
        + "\n",
        encoding="utf-8",
    )


def stage_and_report(root: Path):
    stage = root / "stage"
    candidates = []
    for index, source_path in enumerate(EXPECTED):
        payload = (f"bank-{index}-".encode("ascii") * (index + 2))
        target = stage.joinpath(*source_path.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        candidates.append(
            {
                "path": source_path,
                "size": len(payload),
                "sha256": sha256(payload).hexdigest(),
                "source_layer": "iso9660-extracted",
                "candidate_reason": "explicit-path",
            }
        )
    report = {
        "only_explicit": True,
        "unresolved_explicit_paths": [],
        "source_sha256": CANONICAL_AUDIO_SOURCE_ARCHIVE_SHA256,
        "source_size": CANONICAL_AUDIO_SOURCE_ARCHIVE_SIZE,
        "explicit_paths": list(EXPECTED),
        "candidates": candidates,
    }
    report_path = root / "inventory.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    return stage, report_path, report


class Gate14AudioBankSourcePathTests(unittest.TestCase):
    def test_expected_paths_follow_source_owned_bank_order(self):
        self.assertEqual(expected_audio_bank_source_paths(), EXPECTED)

    def test_checked_in_contract_matches_expected_paths(self):
        repo_root = Path(__file__).resolve().parent.parent
        self.assertEqual(
            validate_audio_bank_exact_path_contract(repo_root),
            EXPECTED,
        )

    def test_contract_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_contract(root, EXPECTED[:-1])
            with self.assertRaisesRegex(
                Gate14AudioBankSourcePathError,
                "differs from source-owned bank order",
            ):
                validate_audio_bank_exact_path_contract(root)


class Gate14AudioBankStageReceiptTests(unittest.TestCase):
    def test_accepts_one_complete_hashed_exact_path_staging_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_contract(root)
            stage, report_path, _report = stage_and_report(root)

            receipt = validate_audio_bank_stage_receipt(
                repo_root=root,
                inventory_report=report_path,
                staging_root=stage,
            )

            self.assertTrue(receipt["passed"])
            self.assertEqual(
                receipt["source_sha256"],
                CANONICAL_AUDIO_SOURCE_ARCHIVE_SHA256,
            )
            self.assertEqual(
                receipt["source_size"],
                CANONICAL_AUDIO_SOURCE_ARCHIVE_SIZE,
            )
            self.assertEqual(receipt["bank_count"], 4)
            self.assertEqual(
                tuple(item["source_path"] for item in receipt["banks"]),
                EXPECTED,
            )
            self.assertTrue(receipt["ready_for_private_format_analysis"])
            for key in (
                "bank_header_layout_recovered",
                "sample_table_layout_recovered",
                "sample_offsets_recovered",
                "sample_codec_recovered",
                "sample_rate_channels_recovered",
                "modern_sample_decode_ready",
                "event_binding_recovered",
            ):
                with self.subTest(key=key):
                    self.assertFalse(receipt[key])

    def test_accepts_case_variant_staged_directory_components(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_contract(root)
            stage, report_path, _report = stage_and_report(root)

            upper_data = stage / "DATA"
            lower_data = stage / "data"
            upper_data.rename(lower_data)
            audio = lower_data / "AUDIO"
            audio.rename(lower_data / "audio")
            sfxs = lower_data / "audio" / "SFXS"
            sfxs.rename(lower_data / "audio" / "sfxs")
            advice = lower_data / "audio" / "sfxs" / "Advice.bnk"
            advice.rename(lower_data / "audio" / "sfxs" / "advice.BNK")

            receipt = validate_audio_bank_stage_receipt(
                repo_root=root,
                inventory_report=report_path,
                staging_root=stage,
            )
            self.assertTrue(receipt["passed"])
            self.assertEqual(receipt["bank_count"], 4)

    def test_rejects_noncanonical_source_archive_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_contract(root)
            stage, report_path, report = stage_and_report(root)

            report["source_sha256"] = "b" * 64
            report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                Gate14AudioBankStageReceiptError,
                "source SHA-256 is not canonical",
            ):
                validate_audio_bank_stage_receipt(
                    repo_root=root,
                    inventory_report=report_path,
                    staging_root=stage,
                )

            report["source_sha256"] = CANONICAL_AUDIO_SOURCE_ARCHIVE_SHA256
            report["source_size"] = CANONICAL_AUDIO_SOURCE_ARCHIVE_SIZE - 1
            report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                Gate14AudioBankStageReceiptError,
                "source size is not canonical",
            ):
                validate_audio_bank_stage_receipt(
                    repo_root=root,
                    inventory_report=report_path,
                    staging_root=stage,
                )

    def test_rejects_unresolved_or_non_exact_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_contract(root)
            stage, report_path, report = stage_and_report(root)

            report["unresolved_explicit_paths"] = [EXPECTED[0]]
            report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                Gate14AudioBankStageReceiptError,
                "unresolved exact paths",
            ):
                validate_audio_bank_stage_receipt(
                    repo_root=root,
                    inventory_report=report_path,
                    staging_root=stage,
                )

            report["unresolved_explicit_paths"] = []
            report["explicit_paths"] = list(EXPECTED[:-1])
            report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                Gate14AudioBankStageReceiptError,
                "exact-path set differs",
            ):
                validate_audio_bank_stage_receipt(
                    repo_root=root,
                    inventory_report=report_path,
                    staging_root=stage,
                )

    def test_rejects_duplicate_or_modified_staged_bank(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_contract(root)
            stage, report_path, report = stage_and_report(root)

            report["candidates"].append(dict(report["candidates"][0]))
            report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                Gate14AudioBankStageReceiptError,
                "duplicate extracted candidate",
            ):
                validate_audio_bank_stage_receipt(
                    repo_root=root,
                    inventory_report=report_path,
                    staging_root=stage,
                )

            report["candidates"].pop()
            report_path.write_text(json.dumps(report), encoding="utf-8")
            stage.joinpath(*EXPECTED[2].split("/")).write_bytes(b"modified")
            with self.assertRaisesRegex(
                Gate14AudioBankStageReceiptError,
                "differs from inventory",
            ):
                validate_audio_bank_stage_receipt(
                    repo_root=root,
                    inventory_report=report_path,
                    staging_root=stage,
                )

    def test_rejects_non_extracted_candidate_layer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_contract(root)
            stage, report_path, report = stage_and_report(root)
            report["candidates"][0]["source_layer"] = "iso9660-listing"
            report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(
                Gate14AudioBankStageReceiptError,
                "does not prove extracted source bytes",
            ):
                validate_audio_bank_stage_receipt(
                    repo_root=root,
                    inventory_report=report_path,
                    staging_root=stage,
                )


if __name__ == "__main__":
    unittest.main()

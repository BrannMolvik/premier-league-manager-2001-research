"""Tests for strict Gate-14 Windows runtime pixel-format receipts."""
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import gate14_windows_pixel_format_receipt as receipt_module
from gate14_windows_pixel_format_receipt import (
    CAPTURE_METHOD,
    SOURCE_ANCHORS,
    Gate14WindowsPixelFormatReceiptError,
    main as receipt_main,
    validate_windows_pixel_format_receipt,
)


SYNTHETIC_EXE = b"synthetic canonical fm2001 executable"


def valid_receipt() -> dict:
    digest = sha256(SYNTHETIC_EXE).hexdigest()
    red = 0xF800
    green = 0x07E0
    blue = 0x001F
    return {
        "schema_version": 1,
        "passed": True,
        "platform_system": "Windows",
        "platform": "Windows-11-test",
        "source_executable": {
            "filename": "footballmanager.exe",
            "size_bytes": len(SYNTHETIC_EXE),
            "sha256": digest,
        },
        "capture_method": CAPTURE_METHOD,
        "source_anchors": dict(SOURCE_ANCHORS),
        "bit_count": 16,
        "red_mask": red,
        "green_mask": green,
        "blue_mask": blue,
        "native_color_key": red | blue,
        "runtime_mask_values_observed": True,
        "original_runtime_surface_observed": True,
        "native_color_channel_layout_recovered": True,
        "cross_component_pixels_resolvable": False,
        "gate14_complete": False,
        "evidence_limit": (
            "Observed from the source-qualified original runtime surface path; "
            "packed-to-modern RGBA remains unresolved."
        ),
    }


class Gate14WindowsPixelFormatReceiptTests(unittest.TestCase):
    def validate(self, receipt: dict):
        with (
            patch.object(
                receipt_module,
                "CANONICAL_EXECUTABLE_SIZE",
                len(SYNTHETIC_EXE),
            ),
            patch.object(
                receipt_module,
                "CANONICAL_EXECUTABLE_SHA256",
                sha256(SYNTHETIC_EXE).hexdigest(),
            ),
        ):
            return validate_windows_pixel_format_receipt(
                receipt,
                SYNTHETIC_EXE,
            )

    def test_accepts_exact_windows_runtime_mask_receipt_without_pixel_promotion(self):
        validation = self.validate(valid_receipt())

        self.assertTrue(validation["passed"])
        self.assertTrue(validation["source_executable_verified"])
        self.assertTrue(validation["source_anchors_verified"])
        self.assertTrue(validation["windows_runtime_surface_observation_accepted"])
        self.assertEqual(validation["bit_count"], 16)
        self.assertEqual(validation["red_mask"], 0xF800)
        self.assertEqual(validation["green_mask"], 0x07E0)
        self.assertEqual(validation["blue_mask"], 0x001F)
        self.assertEqual(validation["native_color_key"], 0xF81F)
        self.assertEqual(validation["font_replacement_color"], 0)
        self.assertTrue(validation["runtime_rgb_mask_values_recovered"])
        self.assertTrue(validation["native_color_channel_layout_recovered"])
        self.assertTrue(validation["font_color_key_applicability_recovered"])
        self.assertFalse(validation["packed16_to_modern_rgba_recovered"])
        self.assertFalse(validation["cross_component_pixels_resolvable"])
        self.assertFalse(validation["complete_fastview_frame_recovered"])
        self.assertFalse(validation["gate14_complete"])

    def test_rejects_non_windows_wrong_method_or_wrong_source_anchor(self):
        cases = []

        item = valid_receipt()
        item["platform_system"] = "Linux"
        cases.append((item, "Windows runtime observation"))

        item = valid_receipt()
        item["capture_method"] = "guessed_rgb565"
        cases.append((item, "capture_method"))

        item = valid_receipt()
        item["source_anchors"] = dict(SOURCE_ANCHORS)
        item["source_anchors"]["surface_format_capture_va"] += 1
        cases.append((item, "source_anchors"))

        for receipt, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    Gate14WindowsPixelFormatReceiptError,
                    message,
                ):
                    self.validate(receipt)

    def test_rejects_32bit_overlapping_noncontiguous_or_wrong_color_key_masks(self):
        cases = []

        item = valid_receipt()
        item["bit_count"] = 32
        cases.append((item, "16-bit pixels"))

        item = valid_receipt()
        item["green_mask"] = 0xF000
        cases.append((item, "disjoint"))

        item = valid_receipt()
        item["green_mask"] = 0x0520
        cases.append((item, "contiguous"))

        item = valid_receipt()
        item["native_color_key"] ^= 1
        cases.append((item, "red_mask \| blue_mask"))

        for receipt, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(
                    Gate14WindowsPixelFormatReceiptError,
                    message,
                ):
                    self.validate(receipt)

    def test_rejects_false_observation_flags_schema_drift_and_wrong_executable(self):
        item = valid_receipt()
        item["runtime_mask_values_observed"] = False
        with self.assertRaisesRegex(
            Gate14WindowsPixelFormatReceiptError,
            "runtime_mask_values_observed",
        ):
            self.validate(item)

        item = valid_receipt()
        item["unexpected"] = True
        with self.assertRaisesRegex(
            Gate14WindowsPixelFormatReceiptError,
            "schema keys differ",
        ):
            self.validate(item)

        with (
            patch.object(receipt_module, "CANONICAL_EXECUTABLE_SIZE", 999),
            patch.object(
                receipt_module,
                "CANONICAL_EXECUTABLE_SHA256",
                "0" * 64,
            ),
        ):
            with self.assertRaisesRegex(
                Gate14WindowsPixelFormatReceiptError,
                "canonical FM2001 identity",
            ):
                validate_windows_pixel_format_receipt(
                    valid_receipt(),
                    SYNTHETIC_EXE,
                )

    def test_cli_writes_private_validation_without_promoting_fastview_pixels(self):
        receipt = valid_receipt()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / "footballmanager.exe"
            source_receipt = root / "pixel-format.json"
            output = root / "validated.json"
            executable.write_bytes(SYNTHETIC_EXE)
            source_receipt.write_text(
                json.dumps(receipt),
                encoding="utf-8",
            )
            argv = [
                "gate14_windows_pixel_format_receipt.py",
                str(executable),
                "--receipt",
                str(source_receipt),
                "--output-validation",
                str(output),
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.object(
                    receipt_module,
                    "CANONICAL_EXECUTABLE_SIZE",
                    len(SYNTHETIC_EXE),
                ),
                patch.object(
                    receipt_module,
                    "CANONICAL_EXECUTABLE_SHA256",
                    sha256(SYNTHETIC_EXE).hexdigest(),
                ),
                patch(
                    "gate14_windows_pixel_format_receipt.require_private_output_path",
                    return_value=None,
                ),
            ):
                self.assertEqual(receipt_main(), 0)

            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(emitted["runtime_rgb_mask_values_recovered"])
            self.assertFalse(emitted["packed16_to_modern_rgba_recovered"])
            self.assertFalse(emitted["cross_component_pixels_resolvable"])
            self.assertFalse(emitted["gate14_complete"])


if __name__ == "__main__":
    unittest.main()

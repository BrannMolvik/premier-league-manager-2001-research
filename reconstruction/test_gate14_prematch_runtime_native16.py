from __future__ import annotations

from hashlib import sha256
import unittest
from unittest.mock import patch

from gate14_prematch_child_rasters import PrematchChildRaster, PrematchChildRasterLedger
from gate14_prematch_runtime_native16 import (
    PrematchObservedNative16Frame,
    PrematchRuntimeNative16Error,
    compose_prematch_native16_from_windows_receipt,
    prematch_runtime_native16_contract,
)
from original_front_end_layout import OriginalRect


def hidden_child(index: int) -> PrematchChildRaster:
    return PrematchChildRaster(
        child_index=index,
        role=f"hidden_{index}",
        visible=False,
        rect=None,
        rgba=None,
        rgba_sha256=None,
        source_identity=None,
    )


def one_red_background_ledger() -> PrematchChildRasterLedger:
    children = [hidden_child(index) for index in range(182)]
    rgba = bytes((255, 0, 0, 255))
    children[0] = PrematchChildRaster(
        child_index=0,
        role="background",
        visible=True,
        rect=OriginalRect(0, 0, 1, 1),
        rgba=rgba,
        rgba_sha256=sha256(rgba).hexdigest(),
        source_identity="synthetic:red",
    )
    return PrematchChildRasterLedger(children=tuple(children))


VALIDATION = {
    "windows_runtime_surface_observation_accepted": True,
    "runtime_rgb_mask_values_recovered": True,
    "native_color_channel_layout_recovered": True,
    "bit_count": 16,
    "red_mask": 0xF800,
    "green_mask": 0x07E0,
    "blue_mask": 0x001F,
    "native_color_key": 0xF81F,
}


class PrematchRuntimeNative16Tests(unittest.TestCase):
    def test_validated_receipt_drives_exact_mask_triplet_into_compositor(self):
        executable = b"canonical"
        with patch(
            "gate14_prematch_runtime_native16.validate_windows_pixel_format_receipt",
            return_value=dict(VALIDATION),
        ) as validate:
            observed = compose_prematch_native16_from_windows_receipt(
                one_red_background_ledger(),
                receipt={"private": "receipt"},
                original_executable=executable,
            )

        validate.assert_called_once_with({"private": "receipt"}, executable)
        self.assertIsInstance(observed, PrematchObservedNative16Frame)
        self.assertEqual(observed.frame.masks.red, 0xF800)
        self.assertEqual(observed.frame.masks.green, 0x07E0)
        self.assertEqual(observed.frame.masks.blue, 0x001F)
        self.assertEqual(observed.native_color_key, 0xF81F)
        self.assertEqual(
            observed.source_executable_sha256,
            sha256(executable).hexdigest(),
        )
        self.assertTrue(observed.windows_runtime_surface_observation_accepted)
        self.assertTrue(observed.runtime_rgb_mask_values_recovered)
        self.assertTrue(observed.native_color_channel_layout_recovered)
        self.assertTrue(observed.flattened_native16_frame_available)
        self.assertFalse(observed.packed16_to_modern_rgba_recovered)
        self.assertFalse(observed.complete_prematch_frame)
        self.assertFalse(observed.gate14_complete)

    def test_receipt_validation_failure_stays_fail_closed(self):
        with patch(
            "gate14_prematch_runtime_native16.validate_windows_pixel_format_receipt",
            side_effect=RuntimeError("invalid receipt"),
        ):
            with self.assertRaisesRegex(
                PrematchRuntimeNative16Error,
                "could not drive PPreMatch",
            ):
                compose_prematch_native16_from_windows_receipt(
                    one_red_background_ledger(),
                    receipt={},
                    original_executable=b"canonical",
                )

    def test_receipt_cannot_claim_observation_without_validator_flag(self):
        invalid = dict(VALIDATION)
        invalid["windows_runtime_surface_observation_accepted"] = False
        with patch(
            "gate14_prematch_runtime_native16.validate_windows_pixel_format_receipt",
            return_value=invalid,
        ):
            with self.assertRaisesRegex(
                PrematchRuntimeNative16Error,
                "did not accept",
            ):
                compose_prematch_native16_from_windows_receipt(
                    one_red_background_ledger(),
                    receipt={},
                    original_executable=b"canonical",
                )

    def test_contract_keeps_modern_display_and_gate_fail_closed(self):
        contract = prematch_runtime_native16_contract()
        self.assertTrue(contract["strict_windows_receipt_reused"])
        self.assertTrue(contract["canonical_executable_required"])
        self.assertTrue(contract["runtime_rgb_masks_feed_native16_compositor"])
        self.assertTrue(contract["flattened_native16_frame_available_after_receipt"])
        self.assertFalse(contract["packed16_to_modern_rgba_recovered"])
        self.assertFalse(contract["complete_prematch_frame"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()

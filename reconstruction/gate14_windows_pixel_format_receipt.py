"""Strict validator for private Gate-14 original-runtime pixel-format receipts.

The canonical executable obtains its 16-bit RGB masks from the active DirectDraw
surface at runtime. Static source therefore cannot honestly choose RGB565,
RGB555, or another 16-bit layout. This module accepts one exact private Windows
observation only when it is tied to the source-qualified capture path and the
canonical executable identity.

A successful receipt closes the runtime mask values/layout and native magenta
key. It does not by itself recover the exact packed-16 -> modern-RGBA expansion
rule, resolve FastView overlap pixels, or complete Gate 14.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from gate13_button_source_trace import require_private_output_path
from gate14_font_blend_source_trace import (
    FONT_PACKED16_REPLACEMENT_COLOR,
    NATIVE_CHANNEL_MASK_METADATA_VA,
    NATIVE_COLOR_KEY_SETUP_VA,
    NATIVE_CONFIG_BLUE_MASK_VA,
    NATIVE_CONFIG_GREEN_MASK_VA,
    NATIVE_CONFIG_RED_MASK_VA,
    NATIVE_PIXEL_FORMAT_CONFIG_BASE_VA,
    NATIVE_SURFACE_FORMAT_CAPTURE_VA,
    NATIVE_SURFACE_FORMAT_COPY_VA,
    Native16PixelMasks,
)


class Gate14WindowsPixelFormatReceiptError(RuntimeError):
    pass


RECEIPT_SCHEMA_VERSION = 1
CANONICAL_EXECUTABLE_FILENAME = "footballmanager.exe"
CANONICAL_EXECUTABLE_SIZE = 4_714_541
CANONICAL_EXECUTABLE_SHA256 = (
    "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"
)
CAPTURE_METHOD = "original_runtime_surface_description"

SOURCE_ANCHORS = {
    "surface_format_capture_va": NATIVE_SURFACE_FORMAT_CAPTURE_VA,
    "surface_format_copy_va": NATIVE_SURFACE_FORMAT_COPY_VA,
    "channel_mask_metadata_va": NATIVE_CHANNEL_MASK_METADATA_VA,
    "pixel_format_config_base_va": NATIVE_PIXEL_FORMAT_CONFIG_BASE_VA,
    "red_mask_config_va": NATIVE_CONFIG_RED_MASK_VA,
    "green_mask_config_va": NATIVE_CONFIG_GREEN_MASK_VA,
    "blue_mask_config_va": NATIVE_CONFIG_BLUE_MASK_VA,
    "color_key_setup_va": NATIVE_COLOR_KEY_SETUP_VA,
}

_EXPECTED_KEYS = frozenset(
    {
        "schema_version",
        "passed",
        "platform_system",
        "platform",
        "source_executable",
        "capture_method",
        "source_anchors",
        "bit_count",
        "red_mask",
        "green_mask",
        "blue_mask",
        "native_color_key",
        "runtime_mask_values_observed",
        "original_runtime_surface_observed",
        "native_color_channel_layout_recovered",
        "cross_component_pixels_resolvable",
        "gate14_complete",
        "evidence_limit",
    }
)


def _require_exact_mapping(
    value: object,
    *,
    label: str,
    expected_keys: frozenset[str],
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise Gate14WindowsPixelFormatReceiptError(f"{label} must be an object")
    actual = set(value.keys())
    if actual != set(expected_keys):
        missing = sorted(set(expected_keys) - actual)
        unexpected = sorted(actual - set(expected_keys))
        raise Gate14WindowsPixelFormatReceiptError(
            f"{label} schema keys differ; missing={missing}, unexpected={unexpected}"
        )
    return value


def _require_bool(
    receipt: Mapping[str, object],
    field: str,
    expected: bool,
) -> None:
    if type(receipt.get(field)) is not bool or receipt[field] is not expected:
        raise Gate14WindowsPixelFormatReceiptError(
            f"{field} must be exactly {str(expected).lower()}"
        )


def _is_contiguous_mask(mask: int) -> bool:
    low_bit = mask & -mask
    normalized = mask // low_bit
    return bool(normalized) and (normalized & (normalized + 1)) == 0


def _canonical_executable_identity(executable: bytes) -> dict:
    if not isinstance(executable, bytes):
        raise Gate14WindowsPixelFormatReceiptError(
            "original executable payload must be bytes"
        )
    digest = sha256(executable).hexdigest()
    if (
        len(executable) != CANONICAL_EXECUTABLE_SIZE
        or digest != CANONICAL_EXECUTABLE_SHA256
    ):
        raise Gate14WindowsPixelFormatReceiptError(
            "original executable does not match the canonical FM2001 identity"
        )
    return {
        "filename": CANONICAL_EXECUTABLE_FILENAME,
        "size_bytes": len(executable),
        "sha256": digest,
    }


def validate_windows_pixel_format_receipt(
    receipt: Mapping[str, object],
    original_executable: bytes,
) -> dict:
    """Validate one private runtime-surface mask observation fail-closed."""
    checked = _require_exact_mapping(
        receipt,
        label="Windows pixel-format receipt",
        expected_keys=_EXPECTED_KEYS,
    )
    if (
        type(checked.get("schema_version")) is not int
        or checked["schema_version"] != RECEIPT_SCHEMA_VERSION
    ):
        raise Gate14WindowsPixelFormatReceiptError(
            "unsupported Windows pixel-format receipt schema version"
        )

    _require_bool(checked, "passed", True)
    _require_bool(checked, "runtime_mask_values_observed", True)
    _require_bool(checked, "original_runtime_surface_observed", True)
    _require_bool(checked, "native_color_channel_layout_recovered", True)
    _require_bool(checked, "cross_component_pixels_resolvable", False)
    _require_bool(checked, "gate14_complete", False)

    if checked.get("platform_system") != "Windows":
        raise Gate14WindowsPixelFormatReceiptError(
            "receipt does not prove Windows runtime observation"
        )
    if not isinstance(checked.get("platform"), str) or not checked["platform"].strip():
        raise Gate14WindowsPixelFormatReceiptError(
            "platform must be a non-empty string"
        )
    if checked.get("capture_method") != CAPTURE_METHOD:
        raise Gate14WindowsPixelFormatReceiptError(
            "receipt capture_method is not the source-qualified runtime surface path"
        )
    if not isinstance(checked.get("evidence_limit"), str) or not checked[
        "evidence_limit"
    ].strip():
        raise Gate14WindowsPixelFormatReceiptError(
            "evidence_limit must be a non-empty string"
        )

    canonical = _canonical_executable_identity(original_executable)
    source_executable = _require_exact_mapping(
        checked.get("source_executable"),
        label="source_executable",
        expected_keys=frozenset({"filename", "size_bytes", "sha256"}),
    )
    if dict(source_executable) != canonical:
        raise Gate14WindowsPixelFormatReceiptError(
            "receipt source_executable differs from canonical executable identity"
        )

    anchors = _require_exact_mapping(
        checked.get("source_anchors"),
        label="source_anchors",
        expected_keys=frozenset(SOURCE_ANCHORS),
    )
    if dict(anchors) != SOURCE_ANCHORS:
        raise Gate14WindowsPixelFormatReceiptError(
            "receipt source_anchors differ from the recovered capture path"
        )

    if type(checked.get("bit_count")) is not int or checked["bit_count"] != 16:
        raise Gate14WindowsPixelFormatReceiptError(
            "original FastView runtime receipt must report 16-bit pixels"
        )

    values = {}
    for field in ("red_mask", "green_mask", "blue_mask"):
        value = checked.get(field)
        if type(value) is not int or not 0 < value <= 0xFFFF:
            raise Gate14WindowsPixelFormatReceiptError(
                f"{field} must be a non-zero uint16"
            )
        if not _is_contiguous_mask(value):
            raise Gate14WindowsPixelFormatReceiptError(
                f"{field} must be a contiguous packed channel mask"
            )
        values[field] = value

    try:
        masks = Native16PixelMasks(
            red=values["red_mask"],
            green=values["green_mask"],
            blue=values["blue_mask"],
        )
    except Exception as exc:
        raise Gate14WindowsPixelFormatReceiptError(
            "runtime RGB masks are not a valid disjoint native layout"
        ) from exc

    color_key = checked.get("native_color_key")
    if type(color_key) is not int or color_key != masks.color_key:
        raise Gate14WindowsPixelFormatReceiptError(
            "native_color_key must equal source-proven red_mask | blue_mask"
        )
    if FONT_PACKED16_REPLACEMENT_COLOR == masks.color_key:
        raise Gate14WindowsPixelFormatReceiptError(
            "font replacement color unexpectedly collides with native color key"
        )

    return {
        "schema_version": 1,
        "passed": True,
        "source_executable_verified": True,
        "source_anchors_verified": True,
        "windows_runtime_surface_observation_accepted": True,
        "bit_count": 16,
        "red_mask": masks.red,
        "green_mask": masks.green,
        "blue_mask": masks.blue,
        "native_color_key": masks.color_key,
        "font_replacement_color": FONT_PACKED16_REPLACEMENT_COLOR,
        "runtime_rgb_mask_values_recovered": True,
        "native_color_channel_layout_recovered": True,
        "font_color_key_applicability_recovered": True,
        "packed16_to_modern_rgba_recovered": False,
        "cross_component_pixels_resolvable": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
        "evidence_limit": (
            "This validator accepts exact RGB mask values only from a strict "
            "private Windows receipt tied to the source-qualified original "
            "runtime surface path and canonical executable. It does not derive "
            "the packed-16 to modern-RGBA expansion rule, resolve overlap "
            "pixels, prove a complete FastView frame, or complete Gate 14."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_executable", type=Path)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output-validation", type=Path, required=True)
    args = parser.parse_args()

    require_private_output_path(args.output_validation)
    try:
        executable = args.original_executable.read_bytes()
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Gate14WindowsPixelFormatReceiptError(
            "could not read executable/receipt evidence"
        ) from exc

    validation = validate_windows_pixel_format_receipt(receipt, executable)
    args.output_validation.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "PASS: private original-runtime Windows pixel-format receipt validated; "
        f"validation written to {args.output_validation}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

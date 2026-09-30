"""Synthetic fail-closed checks for the private ORIGINAL source-byte audit.

These tests DO NOT run the original executable, decode the licensed art or
replace the CLI's physical original-file verification.
"""
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from gate13_original_source_audit import (
    EXPECTED_CAPTIONS,
    OriginalFirsthandAuditError,
    assert_archive_and_receipt_identity,
    describe_loaded_first_screen_bytes,
    firsthand_source_audit,
    require_exact_firsthand_pixel_metrics,
)
from original_button_frames import PSTARTMENU_BUTTON_ATLAS, TEAMSELECT_BUTTON_ATLAS
from original_pstartmenu_resources import COMPOSED_BACKGROUND_RGBA_SHA256
from original_teamselect_hierarchy_art import HIERARCHY_ANIM_SPEC, HIERARCHY_BARS_SPEC
from original_teamselect_resources import TEAMSELECT_COMPOSED_BACKGROUND_RGBA_SHA256


def synthetic_expected_summary():
    """Just a validator test vector, never original-source evidence."""
    return {
        "pstartmenu_background_rgba_sha256": COMPOSED_BACKGROUND_RGBA_SHA256,
        "teamselect_background_rgba_sha256":
            TEAMSELECT_COMPOSED_BACKGROUND_RGBA_SHA256,
        "pstartmenu_atlas_source_sha256":
            PSTARTMENU_BUTTON_ATLAS.source_sha256,
        "teamselect_action_atlas_source_sha256":
            TEAMSELECT_BUTTON_ATLAS.source_sha256,
        "pstartmenu_original_source_frame_count":
            PSTARTMENU_BUTTON_ATLAS.frame_count,
        "teamselect_original_source_frame_count":
            TEAMSELECT_BUTTON_ATLAS.frame_count,
        "captions": [
            {"event": event, "idx": idx, "text": label,
             "alpha_width": width, "alpha_height": height,
             "glyph_alpha_sha256": digest}
            for event, idx, label, width, height, digest in EXPECTED_CAPTIONS
        ],
        "hierarchy_art": {
            "animation_source_sha256": HIERARCHY_ANIM_SPEC.source_sha256,
            "bars_source_sha256": HIERARCHY_BARS_SPEC.source_sha256,
            "animation_source_frame_count": 2,
            "bars_source_frame_count": 3,
        },
        "native_button_frame_state_mapping": None,
        "native_caption_alignment_or_color": None,
        "native_teamselect_hierarchy_item_mapping": None,
    }


class OriginalSourceAuditTests(unittest.TestCase):
    def test_independently_hashes_archive_instead_of_trusting_json_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            zip_path = Path(temp) / "source.zip"
            zip_path.write_bytes(b"synthetic canonical source")
            digest = sha256(zip_path.read_bytes()).hexdigest()
            receipt = {
                "source": str(zip_path.resolve()), "source_sha256": digest,
                "source_size": zip_path.stat().st_size,
            }
            params = {
                "expected_sha": digest,
                "expected_size": zip_path.stat().st_size,
            }
            self.assertEqual(
                assert_archive_and_receipt_identity(zip_path, receipt, **params),
                digest,
            )
            with self.assertRaisesRegex(OriginalFirsthandAuditError, "another ZIP"):
                assert_archive_and_receipt_identity(
                    zip_path, {**receipt, "source": str(Path(temp) / "other.zip")},
                    **params,
                )
            with self.assertRaisesRegex(OriginalFirsthandAuditError, "receipt"):
                assert_archive_and_receipt_identity(
                    zip_path, {**receipt, "source_sha256": "a" * 64},
                    **params,
                )
            with self.assertRaisesRegex(OriginalFirsthandAuditError, "size"):
                assert_archive_and_receipt_identity(
                    zip_path, receipt,
                    expected_sha=digest, expected_size=1,
                )
            zip_path.write_bytes(b"synthetic canonical sourcE")
            with self.assertRaisesRegex(OriginalFirsthandAuditError, "bytes"):
                assert_archive_and_receipt_identity(zip_path, receipt, **params)

    def test_fixture_summary_is_not_a_source_fidelity_claim(self):
        fake_menu = SimpleNamespace(
            background_rgba=b"not FM2001 original pixel bytes",
            button_atlas=SimpleNamespace(
                spec=PSTARTMENU_BUTTON_ATLAS,
                frames=tuple(range(PSTARTMENU_BUTTON_ATLAS.frame_count)),
            ),
            captions=[SimpleNamespace(
                event=1, source_idx_position=0, original_text="synthetic caption",
                glyph_mask=SimpleNamespace(width=1, height=1, alpha=b"\x00"),
            )],
        )
        fake_team = SimpleNamespace(
            background_rgba=b"synthetic team",
            action_atlas=SimpleNamespace(
                spec=TEAMSELECT_BUTTON_ATLAS,
                frames=tuple(range(TEAMSELECT_BUTTON_ATLAS.frame_count)),
            ),
            hierarchy_art=None,
        )
        summary = describe_loaded_first_screen_bytes(fake_menu, fake_team)
        self.assertEqual(
            summary["pstartmenu_background_rgba_sha256"],
            sha256(fake_menu.background_rgba).hexdigest(),
        )
        self.assertIsNone(summary["native_button_frame_state_mapping"])
        self.assertIsNone(summary["native_caption_alignment_or_color"])
        with self.assertRaisesRegex(OriginalFirsthandAuditError, "background"):
            require_exact_firsthand_pixel_metrics(summary)

    def test_pinned_expected_metrics_validation_rejects_every_fidelity_mismatch(self):
        # This tests the comparison layer only. It is not a real-source run.
        baseline = synthetic_expected_summary()
        require_exact_firsthand_pixel_metrics(baseline)
        cases = [
            ("pstartmenu_background_rgba_sha256", "0" * 64, "background"),
            ("teamselect_background_rgba_sha256", "0" * 64, "background"),
            ("pstartmenu_original_source_frame_count", 22, "atlas"),
            ("teamselect_action_atlas_source_sha256", "0" * 64, "atlas"),
            ("captions", baseline["captions"][:-1], "Zurich"),
            ("hierarchy_art", None, "hierarchy"),
            ("native_button_frame_state_mapping", {"idle": 0}, "separate"),
            ("native_caption_alignment_or_color", "synthetic", "separate"),
        ]
        for key, value, expected in cases:
            with self.subTest(field=key):
                damaged = dict(baseline, **{key: value})
                with self.assertRaisesRegex(OriginalFirsthandAuditError, expected):
                    require_exact_firsthand_pixel_metrics(damaged)

    def test_noncanonical_archive_cannot_write_pseudo_firsthand_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "fake-source.zip"
            source.write_bytes(b"not the original game")
            inventory = root / "selection.json"
            inventory.write_text(json.dumps({
                "source": str(source),
                "source_sha256": sha256(source.read_bytes()).hexdigest(),
                "source_size": source.stat().st_size,
            }), encoding="utf-8")
            output = root / "private-should-not-exist.json"
            with self.assertRaisesRegex(OriginalFirsthandAuditError, "size"):
                firsthand_source_audit(
                    original_zip=source,
                    inventory_report_path=inventory,
                    staging_root=root,
                    original_executable=root / "not-the-original.exe",
                    output_receipt=output,
                )
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()

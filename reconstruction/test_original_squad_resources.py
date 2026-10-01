"""Tests for the four exact executable-correlated Squad resources."""
from pathlib import Path
import tempfile
import unittest

from original_squad_resources import (
    OriginalSquadResourceError,
    SQUAD_BUTTONS,
    SQUAD_BUTTON_ORIGINS,
    SQUAD_RESOURCES,
    SQUAD_SCREEN_CLASS,
    SQUAD_SCREEN_SETUP_VA,
    SQUAD_SCREEN_TYPE_DESCRIPTOR_VA,
    SQUAD_SCREEN_VFTABLE_VA,
    validate_imported_original_squad_resources,
    validate_original_squad_button_labels,
)


class OriginalSquadResourceTests(unittest.TestCase):
    def test_imported_bytes_match_hashes_and_header_geometry(self):
        root = Path(__file__).resolve().parent.parent / "original_assets" / "source"
        self.assertEqual(
            validate_imported_original_squad_resources(root), SQUAD_RESOURCES
        )

    def test_native_owner_boundary_does_not_promote_blue_toggle_to_squad_screen(self):
        by_name = {Path(item.source_path).name: item for item in SQUAD_RESOURCES}
        self.assertEqual(
            by_name["squad_but_anim.444"].native_owners,
            (SQUAD_SCREEN_CLASS,),
        )
        self.assertNotIn(
            SQUAD_SCREEN_CLASS, by_name["blue_toggle.444"].native_owners
        )
        self.assertEqual(
            by_name["blue_toggle.444"].native_owners,
            ("PFormation2k", "PSCFTitle", "PTraining", "PYouthTeam"),
        )

    def test_native_squad_screen_identity_and_button_origins_are_locked(self):
        self.assertEqual(SQUAD_SCREEN_TYPE_DESCRIPTOR_VA, 0x819D48)
        self.assertEqual(SQUAD_SCREEN_VFTABLE_VA, 0x7C5CA4)
        self.assertEqual(SQUAD_SCREEN_SETUP_VA, 0x4B5720)
        self.assertEqual(SQUAD_BUTTON_ORIGINS, ((37, 92), (113, 92), (189, 92)))

    def test_native_button_ids_offsets_globals_and_language_bindings_are_locked(self):
        self.assertEqual(
            tuple(
                (
                    item.control_id,
                    item.object_offset,
                    item.label_global_va,
                    item.language_index,
                    item.original_text,
                    item.origin,
                )
                for item in SQUAD_BUTTONS
            ),
            (
                (3, 0x37A4, 0x982110, 2490, "1ST & RES", (37, 92)),
                (4, 0x37F8, 0x98210C, 2491, "1ST FORM", (113, 92)),
                (5, 0x384C, 0x982108, 2492, "RES. FORM", (189, 92)),
            ),
        )

    def test_original_language_pair_resolves_native_squad_labels(self):
        root = Path(__file__).resolve().parent.parent / "original_assets" / "source"
        self.assertEqual(
            validate_original_squad_button_labels(
                root / "English.str", root / "English.idx"
            ),
            SQUAD_BUTTONS,
        )

    def test_wrong_imported_bytes_fail_closed(self):
        source = Path(__file__).resolve().parent.parent / "original_assets" / "source"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for resource in SQUAD_RESOURCES:
                target = root / resource.source_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((source / resource.source_path).read_bytes())
            first = root / SQUAD_RESOURCES[0].source_path
            first.write_bytes(first.read_bytes() + b"corrupt")
            with self.assertRaisesRegex(
                OriginalSquadResourceError, "checksum mismatch"
            ):
                validate_imported_original_squad_resources(root)


if __name__ == "__main__":
    unittest.main()

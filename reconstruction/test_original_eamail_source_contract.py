"""Original PEAMail art/row source-contract regressions; no fake mailbox delivery."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import original_eamail_source_contract as src


class OriginalEAMailSourceContractTests(unittest.TestCase):
    def test_source_panel_list_and_control_identity(self):
        self.assertEqual(src.ORIGINAL_EAMAIL_CLASS, "PEAMail")
        self.assertEqual(src.ORIGINAL_EAMAIL_MENU_CHILD_ID, 0x65)
        self.assertEqual(src.ORIGINAL_EAMAIL_USER_MAILBOX_OFFSET, 0x6B4)
        self.assertEqual(src.ORIGINAL_EAMAIL_FILTERED_ARRAY_OFFSET, 0x68)
        self.assertEqual(src.ORIGINAL_EAMAIL_FILTERED_COUNT_OFFSET, 0x6C)
        self.assertEqual(src.ORIGINAL_EAMAIL_PANEL_RECT, (0, 148, 800, 530))
        self.assertEqual(src.ORIGINAL_EAMAIL_LIST_RECT, (233, 30, 545, 160))
        self.assertEqual(src.ORIGINAL_EAMAIL_LIST_CONTROL_ID, 17)
        self.assertEqual(src.ORIGINAL_EAMAIL_VISIBLE_ROWS, 8)
        self.assertEqual(src.ORIGINAL_EAMAIL_ROW_PITCH, 20)
        self.assertEqual(src.ORIGINAL_EAMAIL_ROW_RECT, (0, 0, 532, 18))
        self.assertEqual(src.ORIGINAL_EAMAIL_TEXT_CHILDREN, (
            (2, (38, 0, 215, 16), 0x174),
            (3, (256, 0, 215, 16), 0x74),
            (0, (474, 0, 71, 16), 0x274),
        ))
        self.assertEqual(src.ORIGINAL_EAMAIL_DECORATIVE_ICON_ORIGINS,
                         ((15, 3), (15, 3), (2, 4)))

    def test_exact_four_original_disc_strip_hashes_and_source_owner_addresses(self):
        assets = src.ORIGINAL_EAMAIL_GRID_RESOURCES
        self.assertEqual([x.name for x in assets],
                         ["normal", "selected", "highlight", "disabled"])
        self.assertEqual([x.byte_size for x in assets],
                         [8124, 7504, 6856, 7184])
        self.assertEqual([x.iso_lba for x in assets],
                         [105652, 105656, 105648, 105644])
        self.assertEqual([x.source_literal_va for x in assets],
                         [0x836024, 0x836050, 0x83607C, 0x8360AC])
        self.assertEqual([x.source_wrapper_va for x in assets],
                         [0x945E30, 0x945DF0, 0x945DB0, 0x945D70])
        self.assertTrue(all(a.dimensions == (532, 18) for a in assets))
        self.assertEqual([a.sha256 for a in assets], [
            "74676dce75532b781551cab6e8598f805fa4698b2e1b828c9f4ef15b3ff0816d",
            "6b6ff7ce36b3c507df2d590ba7ad48b9253409757844acf4ec93204807bad556",
            "a13b413d13b5fa9c5f6a7b36f632c60342898de72bcff2ee73025bc92fdb68c8",
            "cb1fb08a99dfe204ea9b485f5102e808ab758f80aec96f69e17e9537d8eb2f70",
        ])

    def test_committed_original_inbox_row_art_exact_hashes_and_dimensions(self):
        root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        self.assertEqual(
            src.validate_original_eamail_grid_resources(root),
            src.ORIGINAL_EAMAIL_GRID_RESOURCES,
        )

    def test_source_staging_requires_every_verified_byte_and_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = struct.pack("<HH", 532, 18) + bytes.fromhex("64ff00ff") + b"source-test"
            fake_assets = tuple(replace(spec, byte_size=len(raw),
                                        sha256=sha256(raw).hexdigest())
                                for spec in src.ORIGINAL_EAMAIL_GRID_RESOURCES)
            with patch.object(src, "ORIGINAL_EAMAIL_GRID_RESOURCES", fake_assets):
                with self.assertRaisesRegex(src.OriginalEAMailSourceError, "Missing"):
                    src.validate_original_eamail_grid_resources(root)
                for spec in fake_assets:
                    path = root / spec.source_path
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(raw)
                self.assertEqual(src.validate_original_eamail_grid_resources(root),
                                 fake_assets)
                damaged = root / fake_assets[0].source_path
                damaged.write_bytes(raw[:-1])
                with self.assertRaisesRegex(src.OriginalEAMailSourceError, "byte size"):
                    src.validate_original_eamail_grid_resources(root)
                damaged.write_bytes(raw[:-1] + b"!")
                with self.assertRaisesRegex(src.OriginalEAMailSourceError, "SHA-256"):
                    src.validate_original_eamail_grid_resources(root)
                damaged.write_bytes(struct.pack("<HH", 533, 18) + raw[4:])
                patched = tuple(replace(spec, sha256=sha256(
                    (root / spec.source_path).read_bytes()).hexdigest())
                    for spec in fake_assets)
                with patch.object(src, "ORIGINAL_EAMAIL_GRID_RESOURCES", patched):
                    with self.assertRaisesRegex(src.OriginalEAMailSourceError, "geometry"):
                        src.validate_original_eamail_grid_resources(root)
                damaged.write_bytes(raw[:4] + b"ABCD" + raw[8:])
                patched = tuple(replace(spec, sha256=sha256(
                    (root / spec.source_path).read_bytes()).hexdigest())
                    for spec in fake_assets)
                with patch.object(src, "ORIGINAL_EAMAIL_GRID_RESOURCES", patched):
                    with self.assertRaisesRegex(src.OriginalEAMailSourceError, "header"):
                        src.validate_original_eamail_grid_resources(root)

    def test_filtered_viewport_source_eight_row_scroll_bounds_and_order(self):
        nodes = tuple(object() for _ in range(12))
        w = src.original_eamail_filtered_window(
            nodes, 0, native_filtered_array_qualified=True)
        self.assertEqual(w.max_scroll_offset, 4)
        self.assertEqual(w.visible_rows, nodes[:8])
        w = src.original_eamail_filtered_window(
            nodes, 4, native_filtered_array_qualified=True)
        self.assertEqual(w.visible_rows, nodes[4:])
        self.assertTrue(all(a is b for a, b in zip(w.original_filtered_rows, nodes)))
        for count in (0, 1, 8):
            small = tuple(object() for _ in range(count))
            w = src.original_eamail_filtered_window(
                small, 0, native_filtered_array_qualified=True)
            self.assertEqual(w.max_scroll_offset, 0)
            self.assertEqual(w.visible_rows, small)
        for bad in (-1, 5, True, "4"):
            with self.subTest(bad=bad):
                with self.assertRaises(src.OriginalEAMailSourceError):
                    src.original_eamail_filtered_window(
                        nodes, bad, native_filtered_array_qualified=True)
        for bad in (False, None, 1, "yes"):
            with self.subTest(qualified=bad):
                with self.assertRaisesRegex(
                    src.OriginalEAMailSourceError, "not source-qualified"
                ):
                    src.original_eamail_filtered_window(
                        nodes, 0, native_filtered_array_qualified=bad)
        with self.assertRaisesRegex(src.OriginalEAMailSourceError, "immutable"):
            src.original_eamail_filtered_window(
                list(nodes), 0, native_filtered_array_qualified=True)

    def test_neutral_event_first_preview_then_same_control_requests_original_detail(self):
        first = object()
        second = object()
        initial = src.original_eamail_neutral_row_dispatch(
            row_token=first, currently_selected_row_token=None,
            native_event_argument=0)
        self.assertEqual(initial.kind, "select_native_preview")
        self.assertIs(initial.selected_row_token, first)
        self.assertFalse(initial.requires_native_record_action)
        different = src.original_eamail_neutral_row_dispatch(
            row_token=second, currently_selected_row_token=first,
            native_event_argument=0)
        self.assertEqual(different.kind, "select_native_preview")
        repeated = src.original_eamail_neutral_row_dispatch(
            row_token=first, currently_selected_row_token=first,
            native_event_argument=0)
        self.assertEqual(repeated.kind, "request_native_detail")
        self.assertTrue(repeated.requires_native_record_action)
        for bad in (1, 2, 3, None, False):
            with self.subTest(bad=bad):
                with self.assertRaises(src.OriginalEAMailSourceError):
                    src.original_eamail_neutral_row_dispatch(
                        row_token=first, currently_selected_row_token=None,
                        native_event_argument=bad)
        with self.assertRaisesRegex(src.OriginalEAMailSourceError, "identity"):
            src.original_eamail_neutral_row_dispatch(
                row_token=None, currently_selected_row_token=None,
                native_event_argument=0)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from ea444_decoder import EA444DecodedImage
from original_pmatchinfo_presenter import (
    OriginalPMatchInfoPresentationError,
    build_dynamic_incident_art,
    build_staged_pmatchinfo_snapshot,
)
from original_pmatchinfo_resources import (
    PMATCHINFO_RESOURCE_BY_NAME,
    PMATCHINFO_STAGED_PRESENTATION_RESOURCE_NAMES,
)


def image(name: str, marker: int = 7) -> EA444DecodedImage:
    resource = PMATCHINFO_RESOURCE_BY_NAME[name]
    width, height = resource.size
    return EA444DecodedImage(
        width,
        height,
        bytes((marker, marker + 1, marker + 2, 255)) * (width * height),
        consumed_bits=0,
        transparent_pixels=0,
    )


class OriginalPMatchInfoPresenterTests(unittest.TestCase):
    def staged(self):
        return {
            name: image(name, (index * 11) % 240)
            for index, name in enumerate(PMATCHINFO_STAGED_PRESENTATION_RESOURCE_NAMES)
        }

    def test_partial_snapshot_preserves_exact_source_layout_without_popup(self):
        snapshot = build_staged_pmatchinfo_snapshot(self.staged())
        self.assertEqual(snapshot.dialog_size, (760, 500))
        self.assertFalse(snapshot.complete_dialog_background_available)
        self.assertEqual(snapshot.selected_tab_event_id, 1)
        self.assertEqual(
            tuple((tab.event_id, tab.label, tab.panel_class) for tab in snapshot.tabs),
            (
                (1, "MATCH INFO", "PMatchInfoSubPanel"),
                (2, "TEAM INFO", "PTeamInfoSubPanel"),
                (3, "FINANCIAL", "PFinanceSubPanel"),
            ),
        )
        self.assertEqual(len(snapshot.text_slots), 6)
        self.assertEqual(len(snapshot.art), 8)
        self.assertEqual(
            tuple((item.resource_name, item.rect) for item in snapshot.art),
            (
                ("match_name_grid", (0, 0, 185, 36)),
                ("match_incid_grid", (189, 0, 142, 36)),
                ("yellow_card", (191, 11, 14, 14)),
                ("match_name_grid", (0, 0, 185, 36)),
                ("match_incid_grid", (189, 0, 142, 36)),
                ("info_player", (0, 0, 274, 16)),
                ("info_player_disabled", (0, 0, 252, 16)),
                ("pitch_normal", (233, -2, 294, 78)),
            ),
        )

    def test_disabled_player_strip_is_clipped_to_source_proven_control_width(self):
        decoded = self.staged()
        snapshot = build_staged_pmatchinfo_snapshot(decoded)
        strip = next(
            item for item in snapshot.art
            if item.resource_name == "info_player_disabled"
        )
        self.assertEqual(strip.source_size, (274, 16))
        self.assertEqual(strip.rect, (0, 0, 252, 16))
        self.assertEqual(len(strip.rgba), 252 * 16 * 4)
        expected = bytearray()
        source = decoded["info_player_disabled"].rgba
        for row in range(16):
            start = row * 274 * 4
            expected.extend(source[start:start + 252 * 4])
        self.assertEqual(strip.rgba, bytes(expected))

    def test_complete_dialog_fails_closed_without_exact_popup(self):
        with self.assertRaisesRegex(
            OriginalPMatchInfoPresentationError,
            "requires exact info_popup.444",
        ):
            build_staged_pmatchinfo_snapshot(
                self.staged(),
                require_complete_dialog=True,
            )

    def test_exact_popup_unlocks_complete_dialog_background(self):
        decoded = self.staged()
        decoded["info_popup"] = image("info_popup", 31)
        snapshot = build_staged_pmatchinfo_snapshot(
            decoded,
            require_complete_dialog=True,
        )
        self.assertTrue(snapshot.complete_dialog_background_available)
        popup = next(item for item in snapshot.art if item.resource_name == "info_popup")
        self.assertEqual(popup.rect, (0, 0, 760, 500))
        self.assertEqual(len(popup.rgba), 760 * 500 * 4)

    def test_missing_staged_art_fails_before_any_layout_is_invented(self):
        decoded = self.staged()
        decoded.pop("match_name_grid")
        with self.assertRaisesRegex(
            OriginalPMatchInfoPresentationError,
            "Missing decoded staged PMatchInfo art: match_name_grid",
        ):
            build_staged_pmatchinfo_snapshot(decoded)

    def test_selected_tab_must_be_one_of_three_source_events(self):
        with self.assertRaisesRegex(
            OriginalPMatchInfoPresentationError,
            "outside the recovered tab set",
        ):
            build_staged_pmatchinfo_snapshot(
                self.staged(),
                selected_tab_event_id=4,
            )

    def test_dynamic_incident_art_uses_source_predicate_and_exact_rect(self):
        decoded = self.staged()
        item = build_dynamic_incident_art(
            decoded,
            5,
            event_field_18=1,
        )
        self.assertIsNotNone(item)
        self.assertEqual(item.resource_name, "yellow_card")
        self.assertEqual(item.rect, (191, 11, 14, 14))
        self.assertEqual(len(item.rgba), 14 * 14 * 4)

    def test_unmapped_incident_family_remains_empty(self):
        self.assertIsNone(build_dynamic_incident_art(self.staged(), 7))


if __name__ == "__main__":
    unittest.main()

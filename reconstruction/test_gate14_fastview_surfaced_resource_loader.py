"""Tests for fixed-League surfaced adapter and verified source loader."""
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_premier_league_surfaced_adapter import (
    FIXED_LEAGUE_BACKGROUND_OVERRIDE_VALUE,
    FIXED_LEAGUE_BUILDER_VA,
    MATCH_BACKGROUND_OVERRIDE_OFFSET,
    build_premier_league_surfaced_resource_selection,
    premier_league_surfaced_adapter_contract,
)
from gate14_fastview_surfaced_picture_selection import (
    build_fastview_surfaced_resource_selection,
)
from gate14_fastview_surfaced_resource_loader import (
    BADGE_GEOMETRY,
    BACKGROUND_GEOMETRY,
    FastViewSurfacedResourceLoadError,
    load_verified_fastview_surfaced_resources,
    surfaced_resource_loader_contract,
)


def club(country_id, basename, fan_base_index):
    return SimpleNamespace(
        country_id=country_id,
        graphics_basename=basename,
        fan_base_index=fan_base_index,
    )


def decoded(width, height, *, transparent=0):
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=bytes(width * height * 4),
        consumed_bits=123,
        transparent_pixels=transparent,
    )


class FastViewSurfacedResourceLoaderTests(unittest.TestCase):
    def setUp(self):
        self.clubs = {
            10: club(26, "arsenal", 25),
            11: club(26, "chelsea", 14),
        }
        self.countries = {
            26: SimpleNamespace(graphics_directory="England"),
        }

    def selection(self):
        return build_fastview_surfaced_resource_selection(
            match_date=date(2001, 1, 13),
            clubs=self.clubs,
            countries=self.countries,
            home_club_id=10,
            away_club_id=11,
            background_club_override_id=None,
        )

    def test_fixed_premier_league_adapter_uses_source_proven_absent_override(self):
        fixture = SimpleNamespace(
            scheduled_date=date(2001, 1, 13),
            home_club_id=10,
            away_club_id=11,
        )
        selection = build_premier_league_surfaced_resource_selection(
            fixture,
            clubs=self.clubs,
            countries=self.countries,
        )
        self.assertIsNone(selection.background_override_club_id)
        self.assertEqual(selection.background.club_id, 10)
        self.assertEqual(FIXED_LEAGUE_BUILDER_VA, 0x6173D0)
        self.assertEqual(MATCH_BACKGROUND_OVERRIDE_OFFSET, 0x48)
        self.assertEqual(FIXED_LEAGUE_BACKGROUND_OVERRIDE_VALUE, -1)

        contract = premier_league_surfaced_adapter_contract()
        self.assertTrue(contract["selection_override_passed_as_none"])
        self.assertTrue(contract["read_only_adapter"])
        self.assertFalse(contract["source_bytes_loaded"])
        self.assertFalse(contract["ea444_decoded"])
        self.assertFalse(contract["gate14_complete"])

    def test_loader_preserves_candidate_order_and_decodes_exact_native_geometry(self):
        selection = self.selection()
        with TemporaryDirectory() as td:
            root = Path(td)
            # Leave first background and club badge attempts absent so the
            # loader must take the already recovered fallbacks in exact order.
            chosen_background = selection.background_source_candidates[1]
            chosen_home = selection.home_badge_source_candidates[1]
            chosen_away = selection.away_badge_source_candidates[0]

            for rel, payload in (
                (chosen_background, b"background-source"),
                (chosen_home, b"home-badge-source"),
                (chosen_away, b"away-badge-source"),
            ):
                path = root.joinpath(*rel.replace("/", "\\").split("\\"))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)

            exe = root / "footballmanager.exe"
            exe.write_bytes(b"canonical-test-double")

            def fake_decode(raw, *, tables, quant):
                if raw == b"background-source":
                    return decoded(*BACKGROUND_GEOMETRY)
                if raw == b"home-badge-source":
                    return decoded(*BADGE_GEOMETRY, transparent=4)
                if raw == b"away-badge-source":
                    return decoded(*BADGE_GEOMETRY, transparent=7)
                raise AssertionError("unexpected source payload")

            with (
                patch(
                    "gate14_fastview_surfaced_resource_loader.tables_from_original_executable",
                    return_value=object(),
                ) as table_loader,
                patch(
                    "gate14_fastview_surfaced_resource_loader.quantization_from_verified_executable",
                    return_value=object(),
                ) as quant_loader,
                patch(
                    "gate14_fastview_surfaced_resource_loader.decode_ea444",
                    side_effect=fake_decode,
                ),
            ):
                loaded = load_verified_fastview_surfaced_resources(
                    selection,
                    source_root=root,
                    original_executable=exe,
                )

            table_loader.assert_called_once_with(b"canonical-test-double")
            quant_loader.assert_called_once_with(b"canonical-test-double")
            self.assertEqual(loaded.background.source_path, chosen_background)
            self.assertEqual(loaded.home_badge.source_path, chosen_home)
            self.assertEqual(loaded.away_badge.source_path, chosen_away)
            self.assertEqual(loaded.background.geometry, (800, 600))
            self.assertEqual(loaded.home_badge.geometry, (135, 93))
            self.assertEqual(loaded.away_badge.geometry, (135, 93))
            self.assertTrue(loaded.source_bytes_loaded)
            self.assertTrue(loaded.ea444_decoded)
            self.assertFalse(loaded.surfaced_picture_pixels_staged)
            self.assertFalse(loaded.complete_fastview_frame_recovered)

    def test_missing_background_attempts_fail_on_unresolved_terminal_fallback(self):
        selection = self.selection()
        with TemporaryDirectory() as td:
            root = Path(td)
            exe = root / "footballmanager.exe"
            exe.write_bytes(b"canonical-test-double")
            with (
                patch(
                    "gate14_fastview_surfaced_resource_loader.tables_from_original_executable",
                    return_value=object(),
                ),
                patch(
                    "gate14_fastview_surfaced_resource_loader.quantization_from_verified_executable",
                    return_value=object(),
                ),
            ):
                with self.assertRaisesRegex(
                    FastViewSurfacedResourceLoadError,
                    "terminal original background fallback remains unresolved",
                ):
                    load_verified_fastview_surfaced_resources(
                        selection,
                        source_root=root,
                        original_executable=exe,
                    )

    def test_wrong_decoded_geometry_fails_closed(self):
        selection = self.selection()
        with TemporaryDirectory() as td:
            root = Path(td)
            paths = (
                selection.background_source_candidates[0],
                selection.home_badge_source_candidates[0],
                selection.away_badge_source_candidates[0],
            )
            for index, rel in enumerate(paths):
                path = root.joinpath(*rel.replace("/", "\\").split("\\"))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"source-{index}".encode("ascii"))
            exe = root / "footballmanager.exe"
            exe.write_bytes(b"canonical-test-double")

            def bad_decode(raw, *, tables, quant):
                if raw == b"source-0":
                    return decoded(799, 600)
                return decoded(*BADGE_GEOMETRY)

            with (
                patch(
                    "gate14_fastview_surfaced_resource_loader.tables_from_original_executable",
                    return_value=object(),
                ),
                patch(
                    "gate14_fastview_surfaced_resource_loader.quantization_from_verified_executable",
                    return_value=object(),
                ),
                patch(
                    "gate14_fastview_surfaced_resource_loader.decode_ea444",
                    side_effect=bad_decode,
                ),
            ):
                with self.assertRaisesRegex(
                    FastViewSurfacedResourceLoadError,
                    "background decoded geometry",
                ):
                    load_verified_fastview_surfaced_resources(
                        selection,
                        source_root=root,
                        original_executable=exe,
                    )

    def test_loader_contract_keeps_component_and_gate_promotion_false(self):
        contract = surfaced_resource_loader_contract()
        self.assertTrue(contract["selection_only_input"])
        self.assertTrue(contract["background_candidate_order_preserved"])
        self.assertTrue(contract["badge_candidate_order_preserved"])
        self.assertEqual(contract["background_geometry"], (800, 600))
        self.assertEqual(contract["badge_geometry"], (135, 93))
        self.assertTrue(contract["canonical_executable_tables_required"])
        self.assertTrue(contract["canonical_executable_quantization_required"])
        self.assertFalse(contract["terminal_background_fallback_recovered"])
        self.assertTrue(contract["source_bytes_loaded"])
        self.assertTrue(contract["ea444_decoded"])
        self.assertFalse(contract["surfaced_picture_pixels_staged"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()

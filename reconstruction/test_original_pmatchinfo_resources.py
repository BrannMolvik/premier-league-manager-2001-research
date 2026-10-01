"""Regressions for source-backed PMatchInfo Match_report resources."""
from pathlib import Path
import tempfile
import unittest

from original_pmatchinfo_resources import (
    PMATCHINFO_RESOURCE_BY_NAME,
    PMATCHINFO_RESOURCES,
    PMATCHINFO_SUBPANEL_BASE_CLASS,
    PMATCHINFO_SUBPANEL_BASE_COL_VA,
    PMATCHINFO_SUBPANEL_BASE_TYPE_DESCRIPTOR_VA,
    PMATCHINFO_SUBPANEL_BASE_VFTABLE_VA,
    PMATCHINFO_SUBPANEL_CLASS,
    PMATCHINFO_SUBPANEL_COL_VA,
    PMATCHINFO_SUBPANEL_TYPE_DESCRIPTOR_VA,
    PMATCHINFO_SUBPANEL_VFTABLE_VA,
    OriginalPMatchInfoResourceError,
    assert_pmatchinfo_identity_contract,
    validate_original_pmatchinfo_resources,
)


class OriginalPMatchInfoResourceTests(unittest.TestCase):
    def test_twenty_exact_match_report_resources_are_bound(self):
        self.assertEqual(len(PMATCHINFO_RESOURCES), 20)
        self.assertEqual(
            [resource.name for resource in PMATCHINFO_RESOURCES],
            [
                "info_player",
                "info_player_disabled",
                "info_popup",
                "red_card",
                "yellow_card",
                "sub_on",
                "sub_off",
                "injured",
                "score",
                "red_card_single",
                "name_block_1",
                "name_block_2",
                "name_block_3",
                "name_block_4",
                "match_name_grid",
                "poss_back",
                "poss_blue",
                "poss_yellow",
                "pitch_normal",
                "match_incid_grid",
            ],
        )

    def test_static_raw_and_wrapper_handles_form_exact_contiguous_family(self):
        self.assertEqual(
            [resource.raw_handle_va for resource in PMATCHINFO_RESOURCES],
            [0x943570 - 0x40 * index for index in range(20)],
        )
        self.assertEqual(
            [resource.wrapper_va for resource in PMATCHINFO_RESOURCES],
            [0x943550 - 0x40 * index for index in range(20)],
        )
        self.assertTrue(
            all(
                resource.raw_handle_va - resource.wrapper_va == 0x20
                for resource in PMATCHINFO_RESOURCES
            )
        )

    def test_path_literals_are_exact_and_monotonic_source_family(self):
        expected = [
            0x837E9C, 0x837ECC, 0x837F08, 0x837F38, 0x837F68,
            0x837F98, 0x837FC4, 0x837FF0, 0x83801C, 0x838048,
            0x83807C, 0x8380B0, 0x8380E4, 0x838118, 0x83814C,
            0x838180, 0x8381B0, 0x8381E0, 0x838210, 0x838244,
        ]
        self.assertEqual(
            [resource.path_literal_va for resource in PMATCHINFO_RESOURCES],
            expected,
        )
        self.assertTrue(
            all(
                resource.source_path.startswith(
                    "FM2001_Art/Generic/match_report/"
                )
                for resource in PMATCHINFO_RESOURCES
            )
        )

    def test_background_and_core_grid_geometries_match_firsthand_source(self):
        self.assertEqual(PMATCHINFO_RESOURCE_BY_NAME["info_popup"].size, (760, 500))
        self.assertEqual(PMATCHINFO_RESOURCE_BY_NAME["info_player"].size, (274, 16))
        self.assertEqual(
            PMATCHINFO_RESOURCE_BY_NAME["info_player_disabled"].size,
            (274, 16),
        )
        self.assertEqual(PMATCHINFO_RESOURCE_BY_NAME["match_name_grid"].size, (185, 36))
        self.assertEqual(PMATCHINFO_RESOURCE_BY_NAME["match_incid_grid"].size, (142, 36))
        self.assertEqual(PMATCHINFO_RESOURCE_BY_NAME["pitch_normal"].size, (294, 78))

    def test_incident_icon_family_is_exact_fourteen_square_pixels(self):
        for name in (
            "red_card",
            "yellow_card",
            "sub_on",
            "sub_off",
            "injured",
            "score",
            "red_card_single",
        ):
            with self.subTest(name=name):
                self.assertEqual(PMATCHINFO_RESOURCE_BY_NAME[name].size, (14, 14))

    def test_direct_consumers_are_recorded_only_where_source_traced(self):
        expected_direct = {
            "info_player",
            "info_player_disabled",
            "info_popup",
            "red_card",
            "yellow_card",
            "sub_on",
            "sub_off",
            "injured",
            "score",
            "red_card_single",
            "match_name_grid",
            "pitch_normal",
            "match_incid_grid",
        }
        actual_direct = {
            resource.name
            for resource in PMATCHINFO_RESOURCES
            if resource.direct_consumer_vas
        }
        self.assertEqual(actual_direct, expected_direct)
        self.assertEqual(
            PMATCHINFO_RESOURCE_BY_NAME["info_popup"].direct_consumer_handle,
            "raw",
        )
        self.assertEqual(
            PMATCHINFO_RESOURCE_BY_NAME["red_card"].direct_consumer_handle,
            "wrapper",
        )
        self.assertEqual(
            PMATCHINFO_RESOURCE_BY_NAME["name_block_1"].direct_consumer_vas,
            (),
        )

    def test_pmatchinfo_subpanel_rtti_is_source_bound(self):
        self.assertEqual(PMATCHINFO_SUBPANEL_BASE_CLASS, "PMatchInfoSubPanelBase")
        self.assertEqual(PMATCHINFO_SUBPANEL_BASE_TYPE_DESCRIPTOR_VA, 0x81D078)
        self.assertEqual(PMATCHINFO_SUBPANEL_BASE_VFTABLE_VA, 0x7C42B8)
        self.assertEqual(PMATCHINFO_SUBPANEL_BASE_COL_VA, 0x7E4C08)
        self.assertEqual(PMATCHINFO_SUBPANEL_CLASS, "PMatchInfoSubPanel")
        self.assertEqual(PMATCHINFO_SUBPANEL_TYPE_DESCRIPTOR_VA, 0x81D0A0)
        self.assertEqual(PMATCHINFO_SUBPANEL_VFTABLE_VA, 0x7C426C)
        self.assertEqual(PMATCHINFO_SUBPANEL_COL_VA, 0x7E4BD0)

    def test_every_resource_has_canonical_sha_and_positive_source_size(self):
        for resource in PMATCHINFO_RESOURCES:
            with self.subTest(name=resource.name):
                self.assertEqual(len(resource.sha256), 64)
                self.assertTrue(all(c in "0123456789abcdef" for c in resource.sha256))
                self.assertGreater(resource.byte_size, 0)
                self.assertGreater(resource.size[0], 0)
                self.assertGreater(resource.size[1], 0)

    def test_resource_validator_fails_closed_on_synthetic_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for resource in PMATCHINFO_RESOURCES:
                path = root / resource.source_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"x" * resource.byte_size)
            with self.assertRaisesRegex(
                OriginalPMatchInfoResourceError,
                "checksum mismatch",
            ):
                validate_original_pmatchinfo_resources(root)

    def test_pmatchinfo_identity_guard_uses_populated_fixture_contract(self):
        assert_pmatchinfo_identity_contract()


if __name__ == "__main__":
    unittest.main()

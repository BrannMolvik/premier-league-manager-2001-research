"""Tests for exact source-closed FastViewTeam resource validation."""
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from gate14_fastview_resource_catalog import TARGETS
from gate14_fastview_team import FastViewTeamResource
from original_fastview_team_resources import (
    FASTVIEW_TEAM_TABLE_RESOURCES,
    OriginalFastViewTeamResourceError,
    source_resource_path,
    validate_source_fastview_team_resources,
)


class _Digest:
    def __init__(self, value: str):
        self.value = value

    def hexdigest(self) -> str:
        return self.value


class OriginalFastViewTeamResourceTests(unittest.TestCase):
    def test_exact_source_identity_and_catalog_contract_are_locked(self):
        expected = [
            ("team_name_grid", 3496, (259, 16), 0x829424),
            ("team_name_grid_2", 3512, (259, 16), 0x8293F8),
            ("team_name_grid_3", 3512, (259, 16), 0x829384),
            ("team_name_grid_4", 3496, (259, 16), 0x829358),
            ("team_bar_1", 2344, (82, 16), 0x8293D4),
            ("blank_bar", 2776, (82, 16), 0x8293B0),
            ("team_bar_2", 2312, (82, 16), 0x829334),
        ]
        self.assertEqual(
            [
                (item.name, item.byte_size, item.size, item.path_literal_va)
                for item in FASTVIEW_TEAM_TABLE_RESOURCES
            ],
            expected,
        )
        catalog_by_path = {target.source_path: target for target in TARGETS}
        for resource in FASTVIEW_TEAM_TABLE_RESOURCES:
            self.assertFalse(resource.imported)
            self.assertTrue(resource.source_path.startswith("FM2001_Art/FastView/"))
            target = catalog_by_path[resource.source_path]
            self.assertEqual(target.component, "FastViewTeam")
            self.assertEqual(target.size_bytes, resource.byte_size)
            self.assertEqual(target.sha256, resource.sha256)
            self.assertEqual((target.width, target.height), resource.size)
            self.assertEqual(target.executable_string_va, resource.path_literal_va)

    def test_source_path_is_explicit_and_wrong_resource_type_fails(self):
        root = Path("/private/original")
        resource = FASTVIEW_TEAM_TABLE_RESOURCES[0]
        self.assertEqual(
            source_resource_path(root, resource),
            root / "FM2001_Art/FastView/team_name_grid.444",
        )
        with self.assertRaisesRegex(
            OriginalFastViewTeamResourceError,
            "source-backed resource contract",
        ):
            source_resource_path(root, object())

    def test_missing_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(
                OriginalFastViewTeamResourceError,
                "Missing original FastViewTeam resource",
            ):
                validate_source_fastview_team_resources(tmp)

    def test_size_hash_and_header_geometry_are_all_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected_hash_by_marker = {}
            for marker, resource in enumerate(FASTVIEW_TEAM_TABLE_RESOURCES, start=1):
                path = source_resource_path(root, resource)
                path.parent.mkdir(parents=True, exist_ok=True)
                data = bytearray(resource.byte_size)
                struct.pack_into("<HH", data, 0, *resource.size)
                data[8] = marker
                path.write_bytes(data)
                expected_hash_by_marker[marker] = resource.sha256

            def fake_sha256(data: bytes):
                return _Digest(expected_hash_by_marker[data[8]])

            with patch("original_fastview_team_resources.sha256", fake_sha256):
                self.assertEqual(
                    validate_source_fastview_team_resources(root),
                    FASTVIEW_TEAM_TABLE_RESOURCES,
                )

                first = FASTVIEW_TEAM_TABLE_RESOURCES[0]
                first_path = source_resource_path(root, first)
                original = first_path.read_bytes()

                first_path.write_bytes(original[:-1])
                with self.assertRaisesRegex(
                    OriginalFastViewTeamResourceError,
                    "byte-size mismatch",
                ):
                    validate_source_fastview_team_resources(root)

                first_path.write_bytes(original)
                with patch(
                    "original_fastview_team_resources.sha256",
                    lambda _data: _Digest("0" * 64),
                ):
                    with self.assertRaisesRegex(
                        OriginalFastViewTeamResourceError,
                        "checksum mismatch",
                    ):
                        validate_source_fastview_team_resources(root)

                wrong = bytearray(original)
                struct.pack_into("<HH", wrong, 0, first.size[0] - 1, first.size[1])
                first_path.write_bytes(wrong)
                with patch("original_fastview_team_resources.sha256", fake_sha256):
                    with self.assertRaisesRegex(
                        OriginalFastViewTeamResourceError,
                        "geometry mismatch",
                    ):
                        validate_source_fastview_team_resources(root)


if __name__ == "__main__":
    unittest.main()

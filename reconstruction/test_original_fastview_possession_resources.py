import tempfile
import unittest
from pathlib import Path

from original_fastview_possession_resources import (
    FASTVIEW_POSSESSION_DIAGRAM_RESOURCES,
    OriginalFastViewPossessionResourceError,
    PITCH_LEFT,
    PITCH_MIDDLE,
    PITCH_NORMAL,
    PITCH_RIGHT,
    initial_possession_diagram_layers,
    possession_diagram_layers,
    validate_imported_possession_diagram_resources,
)


class OriginalFastViewPossessionResourceTests(unittest.TestCase):
    def test_exact_source_identity_and_geometry_are_locked(self):
        self.assertEqual(
            [
                (r.name, r.byte_size, r.size, r.path_literal_va)
                for r in FASTVIEW_POSSESSION_DIAGRAM_RESOURCES
            ],
            [
                ("pitch_left", 9736, (125, 78), 0x8298D4),
                ("pitch_middle", 7896, (98, 78), 0x8298AC),
                ("pitch_right", 9408, (125, 78), 0x829888),
                ("pitch_normal", 18424, (294, 78), 0x8298F8),
            ],
        )
        for resource in FASTVIEW_POSSESSION_DIAGRAM_RESOURCES:
            self.assertTrue(
                resource.source_path.startswith("FM2001_Art/FastView/")
            )
            self.assertEqual(len(resource.sha256), 64)

    def test_layer_plan_uses_source_proven_rectangles_only(self):
        self.assertEqual(
            [(x.resource, x.rect) for x in possession_diagram_layers(0)],
            [
                (PITCH_NORMAL, (253, 139, 547, 217)),
                (PITCH_LEFT, (253, 139, 378, 217)),
            ],
        )
        self.assertEqual(
            [(x.resource, x.rect) for x in possession_diagram_layers(1)],
            [
                (PITCH_NORMAL, (253, 139, 547, 217)),
                (PITCH_MIDDLE, (351, 139, 449, 217)),
            ],
        )
        self.assertEqual(
            [(x.resource, x.rect) for x in possession_diagram_layers(2)],
            [
                (PITCH_NORMAL, (253, 139, 547, 217)),
                (PITCH_RIGHT, (422, 139, 547, 217)),
            ],
        )
        self.assertEqual(
            initial_possession_diagram_layers(),
            possession_diagram_layers(1),
        )
        for bad in (-1, 3, True, "1"):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalFastViewPossessionResourceError):
                    possession_diagram_layers(bad)

    def test_repository_staged_source_bytes_validate_and_corruption_fails(self):
        repo_root = Path(__file__).resolve().parent.parent
        self.assertEqual(
            validate_imported_possession_diagram_resources(repo_root),
            FASTVIEW_POSSESSION_DIAGRAM_RESOURCES,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for resource in FASTVIEW_POSSESSION_DIAGRAM_RESOURCES:
                source = (
                    repo_root
                    / "original_assets/source"
                    / resource.source_path
                )
                target = (
                    root
                    / "original_assets/source"
                    / resource.source_path
                )
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
            target = (
                root
                / "original_assets/source"
                / PITCH_LEFT.source_path
            )
            data = bytearray(target.read_bytes())
            data[-1] ^= 1
            target.write_bytes(data)
            with self.assertRaisesRegex(
                OriginalFastViewPossessionResourceError,
                "checksum mismatch",
            ):
                validate_imported_possession_diagram_resources(root)


if __name__ == "__main__":
    unittest.main()

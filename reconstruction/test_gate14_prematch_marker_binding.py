"""Regression coverage for supplied-state PPreMatch XI marker binding."""
from types import SimpleNamespace
import unittest

from gate14_prematch_marker_binding import (
    BoundPrematchStartingXIMarkers,
    PrematchMarkerBindingError,
    bind_prematch_starting_xi_markers,
    prematch_marker_binding_contract,
)
from gate14_prematch_shirt_resources import (
    PrematchGoalkeeperShirt,
    PrematchNumberedShirtAtlas,
)


def atlas(club_id, marker_base):
    rgba = bytearray(36 * 1280 * 4)
    for frame in range(40):
        for y in range(frame * 32, frame * 32 + 32):
            for x in range(36):
                off = (y * 36 + x) * 4
                rgba[off:off + 4] = bytes((marker_base + frame, 0, 0, 255))
    return PrematchNumberedShirtAtlas(
        source_kind="custom_ea444",
        source_path=f"club-{club_id}.444",
        source_sha256=f"{club_id:064x}"[-64:],
        rgba=bytes(rgba),
        club_id=club_id,
        use_alternate=False,
    )


def goalkeeper():
    return PrematchGoalkeeperShirt(
        source_path="goalkeeper.444",
        source_sha256="f" * 64,
        rgba=bytes((99, 0, 0, 255)) * (36 * 32),
    )


def player(club_id, number, alternate=None):
    kwargs = dict(club_id=club_id, shirt_number=number)
    if alternate is not None:
        kwargs["alternate_shirt_number"] = alternate
    return SimpleNamespace(**kwargs)


class PrematchMarkerBindingTests(unittest.TestCase):
    def test_contract_preserves_22_native_children_and_fail_closed_frame(self):
        contract = prematch_marker_binding_contract()
        self.assertEqual(contract["marker_count"], 22)
        self.assertEqual(contract["child_range"], (10, 31))
        self.assertEqual(contract["goalkeeper_children"], (10, 21))
        self.assertEqual(
            contract["outfield_children"],
            (tuple(range(11, 21)), tuple(range(22, 32))),
        )
        self.assertEqual(contract["marker_size"], (36, 32))
        self.assertTrue(contract["formation_coordinates_must_be_source_outputs"])
        self.assertTrue(contract["source_shirt_pixels_bound"])
        self.assertFalse(contract["complete_prematch_frame"])
        self.assertFalse(contract["gate14_complete"])

    def test_binds_both_sides_in_exact_child_order_with_goalkeeper_ownership(self):
        side0 = tuple(player(10, index + 1) for index in range(11))
        side1 = tuple(player(11, index + 11) for index in range(11))
        coords = tuple((0.0, 0.0) for _ in range(11))

        bound = bind_prematch_starting_xi_markers(
            side0_players=side0,
            side1_players=side1,
            side0_coordinates=coords,
            side1_coordinates=coords,
            side0_team_club_id=10,
            side1_team_club_id=11,
            side0_atlas=atlas(10, 10),
            side1_atlas=atlas(11, 50),
            goalkeeper=goalkeeper(),
        )

        self.assertIsInstance(bound, BoundPrematchStartingXIMarkers)
        self.assertEqual(tuple(m.child_index for m in bound.markers), tuple(range(10, 32)))
        self.assertTrue(all(m.visible for m in bound.markers))
        self.assertEqual(bound.markers[0].source_kind, "goalkeeper_original")
        self.assertEqual(bound.markers[11].source_kind, "goalkeeper_original")
        self.assertEqual(tuple(bound.markers[0].rgba[:4]), (99, 0, 0, 255))
        self.assertEqual(tuple(bound.markers[11].rgba[:4]), (99, 0, 0, 255))
        self.assertIsNone(bound.markers[0].frame_number)
        self.assertIsNone(bound.markers[11].frame_number)

        # slot 1 uses player shirt #2 on side 0: second 32-pixel frame.
        self.assertEqual(bound.markers[1].frame_number, 2)
        self.assertEqual(tuple(bound.markers[1].rgba[:4]), (11, 0, 0, 255))
        # side 1 slot 1 uses shirt #12: twelfth frame.
        self.assertEqual(bound.markers[12].frame_number, 12)
        self.assertEqual(tuple(bound.markers[12].rgba[:4]), (61, 0, 0, 255))

        # Native zero normalized coordinate transforms remain side-specific.
        self.assertEqual(
            (
                bound.markers[0].rect.x,
                bound.markers[0].rect.y,
                bound.markers[0].rect.width,
                bound.markers[0].rect.height,
            ),
            (252, 316, 36, 32),
        )
        self.assertEqual(
            (
                bound.markers[11].rect.x,
                bound.markers[11].rect.y,
                bound.markers[11].rect.width,
                bound.markers[11].rect.height,
            ),
            (512, 332, 36, 32),
        )

    def test_unresolved_slots_are_hidden_without_substitute_pixels(self):
        coords = ((0.0, 0.0),) * 2
        bound = bind_prematch_starting_xi_markers(
            side0_players=(player(10, 1), player(10, 2)),
            side1_players=(),
            side0_coordinates=coords,
            side1_coordinates=(),
            side0_team_club_id=10,
            side1_team_club_id=11,
            side0_atlas=atlas(10, 10),
            side1_atlas=atlas(11, 50),
            goalkeeper=goalkeeper(),
        )
        self.assertTrue(bound.markers[0].visible)
        self.assertTrue(bound.markers[1].visible)
        self.assertTrue(all(not marker.visible for marker in bound.markers[2:11]))
        self.assertTrue(all(not marker.visible for marker in bound.markers[11:]))
        hidden = bound.markers[2]
        self.assertIsNone(hidden.rect)
        self.assertIsNone(hidden.rgba)
        self.assertIsNone(hidden.source_path)

    def test_mismatched_registered_club_uses_explicit_alternate_number_when_present(self):
        bound = bind_prematch_starting_xi_markers(
            side0_players=(player(10, 1), player(99, 2, alternate=9)),
            side1_players=(),
            side0_coordinates=((0.0, 0.0), (0.0, 0.0)),
            side1_coordinates=(),
            side0_team_club_id=10,
            side1_team_club_id=11,
            side0_atlas=atlas(10, 10),
            side1_atlas=atlas(11, 50),
            goalkeeper=goalkeeper(),
        )
        self.assertEqual(bound.markers[1].frame_number, 9)
        self.assertEqual(tuple(bound.markers[1].rgba[:4]), (18, 0, 0, 255))

    def test_visible_player_without_coordinate_fails_closed(self):
        with self.assertRaisesRegex(PrematchMarkerBindingError, "coordinate"):
            bind_prematch_starting_xi_markers(
                side0_players=(player(10, 1),),
                side1_players=(),
                side0_coordinates=(),
                side1_coordinates=(),
                side0_team_club_id=10,
                side1_team_club_id=11,
                side0_atlas=atlas(10, 10),
                side1_atlas=atlas(11, 50),
                goalkeeper=goalkeeper(),
            )


if __name__ == "__main__":
    unittest.main()

"""Tests for the fail-closed outer FastView embedded-control contract."""
import unittest

from gate14_fastview_embedded_controls_source import (
    FASTVIEW_EMBEDDED_OUTER_CONTROL_COUNT,
    FASTVIEW_EMBEDDED_OUTER_CONTROLS,
    POST_TEAM_EMBEDDED_CONTROLS,
    PRE_GOALFLASH_EMBEDDED_CONTROLS,
    FastViewEmbeddedControlsSourceError,
    embedded_outer_control,
    embedded_outer_controls_source_contract,
)


class FastViewEmbeddedControlsSourceTests(unittest.TestCase):
    def test_exact_four_controls_and_outer_ranks(self):
        self.assertEqual(FASTVIEW_EMBEDDED_OUTER_CONTROL_COUNT, 4)
        self.assertEqual(len(FASTVIEW_EMBEDDED_OUTER_CONTROLS), 4)
        self.assertEqual(
            tuple(control.identity for control in FASTVIEW_EMBEDDED_OUTER_CONTROLS),
            (
                "embedded_button_0",
                "embedded_button_1",
                "post_team_control_0",
                "post_team_control_1",
            ),
        )
        self.assertEqual(
            tuple(control.outer_draw_rank for control in FASTVIEW_EMBEDDED_OUTER_CONTROLS),
            (4, 5, 34, 35),
        )

    def test_pre_goalflash_source_topology_is_exact(self):
        self.assertEqual(
            tuple(
                (
                    c.parent_offset,
                    c.registration_call_va,
                    c.setup_call_va,
                    c.constructor_target_va,
                )
                for c in PRE_GOALFLASH_EMBEDDED_CONTROLS
            ),
            (
                (0x388, 0x51FFE5, 0x520061, 0x652FD0),
                (0x3D4, 0x52000B, 0x52009F, 0x652FD0),
            ),
        )
        self.assertTrue(
            all(c.family == "pre_goalflash" for c in PRE_GOALFLASH_EMBEDDED_CONTROLS)
        )

    def test_post_team_loop_topology_is_exact(self):
        self.assertEqual(
            tuple(
                (
                    c.parent_offset,
                    c.registration_call_va,
                    c.setup_call_va,
                    c.constructor_target_va,
                )
                for c in POST_TEAM_EMBEDDED_CONTROLS
            ),
            (
                (0x424, 0x520F8B, None, 0x652C50),
                (0x478, 0x520F8B, None, 0x652C50),
            ),
        )
        self.assertTrue(all(c.family == "post_team" for c in POST_TEAM_EMBEDDED_CONTROLS))

    def test_lookup_is_exact_and_does_not_infer_other_controls(self):
        self.assertEqual(
            embedded_outer_control("embedded_button_0").parent_offset,
            0x388,
        )
        self.assertEqual(
            embedded_outer_control("post_team_control_1").parent_offset,
            0x478,
        )
        for value in ("", "goal_flash_0_text_0", "embedded_button_2", None, True):
            with self.subTest(value=value):
                with self.assertRaises(FastViewEmbeddedControlsSourceError):
                    embedded_outer_control(value)

    def test_contract_promotes_topology_only(self):
        contract = embedded_outer_controls_source_contract()
        self.assertEqual(contract["control_count"], 4)
        self.assertEqual(
            tuple(row[-1] for row in contract["controls"]),
            (4, 5, 34, 35),
        )
        self.assertFalse(contract["role_semantics_recovered"])
        self.assertFalse(contract["control_geometry_recovered"])
        self.assertFalse(contract["resource_identity_recovered"])
        self.assertFalse(contract["state_behavior_recovered"])
        self.assertFalse(contract["pixels_rasterized"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()

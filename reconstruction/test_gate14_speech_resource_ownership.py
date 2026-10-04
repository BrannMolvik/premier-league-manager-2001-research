"""Tests for source-backed FM2001 speech resource ownership."""
from dataclasses import replace
import unittest

from gate14_speech_resource_ownership import (
    MAIN_AUDIO_INIT_VA,
    PLAYER_STITCHED_SPEECH_INIT_VA,
    SPEECH_INIT_VA,
    SPEECH_PATH_BUILDER_VA,
    SPEECH_PATH_FORMAT_VA,
    SPEECH_RESOURCES,
    TEAM_SPEECH_INIT_VA,
    Gate14SpeechResourceOwnershipError,
    speech_resource,
)


class Gate14SpeechResourceOwnershipTests(unittest.TestCase):
    def test_exact_source_resource_catalog_is_stable(self):
        self.assertEqual(MAIN_AUDIO_INIT_VA, 0x6D0AC0)
        self.assertEqual(SPEECH_INIT_VA, 0x723AD0)
        self.assertEqual(SPEECH_PATH_BUILDER_VA, 0x723E20)
        self.assertEqual(TEAM_SPEECH_INIT_VA, 0x723E70)
        self.assertEqual(PLAYER_STITCHED_SPEECH_INIT_VA, 0x724080)
        self.assertEqual(SPEECH_PATH_FORMAT_VA, 0x8663F0)

        expected = {
            "Data/Audio/Speech/NewSpeech.inf": (
                26879,
                "b0d0be607f669051a2b4ee884578f8da277f9cd912baf72849c56cec4ee89a25",
                0x86638C,
                0x723CAF,
                SPEECH_INIT_VA,
            ),
            "Data/Audio/Speech/NewSpeech.str": (
                86879932,
                "fd0d511c1482080e49cd49b2baa7396ea53e2866bacebfd0dac6515ab6211c1e",
                0x8663AC,
                0x723C84,
                SPEECH_INIT_VA,
            ),
            "Data/Audio/Speech/Stitched.str": (
                500960,
                "c3fd52af55b6abf1270fb9cd0cd496702bf3c1068ca6274080e64813c98c0c00",
                0x86639C,
                0x723C93,
                SPEECH_INIT_VA,
            ),
            "Data/Audio/Speech/Teams.off": (
                2244,
                "a16c7df782db703e5c3d284bdbf1ff35653f65bc5e2b730e8a17518e7828f54f",
                0x866408,
                0x723EC5,
                TEAM_SPEECH_INIT_VA,
            ),
            "Data/Audio/Speech/Teams.str": (
                1812912,
                "57e04f874806174b6af16ae2dcbf586cf68807eb71707ab5dc01010b6246a18a",
                0x866414,
                0x723EB0,
                TEAM_SPEECH_INIT_VA,
            ),
            "Data/Audio/Speech/Stitched.off": (
                1036,
                "37954be2c825b712215959356ec0940946406e47c30c5aca395cdcf59106a96e",
                0x866420,
                0x7241F2,
                PLAYER_STITCHED_SPEECH_INIT_VA,
            ),
            "Data/Audio/Speech/Players.str": (
                11392368,
                "bd1fabdbebe7aae37fe8878f5a794a069cf6954064a4a450df454b3d9e6ae6c1",
                0x866430,
                0x724100,
                PLAYER_STITCHED_SPEECH_INIT_VA,
            ),
            "Data/Audio/Speech/Players.off": (
                25692,
                "228f53d810e998e8bdb02c610905e28c80780e920ef677635591d9375a728b65",
                0x86643C,
                0x7240C8,
                PLAYER_STITCHED_SPEECH_INIT_VA,
            ),
        }
        self.assertEqual(len(SPEECH_RESOURCES), len(expected))
        for item in SPEECH_RESOURCES:
            with self.subTest(path=item.path):
                self.assertEqual(
                    (
                        item.size_bytes,
                        item.sha256,
                        item.string_va,
                        item.reference_va,
                        item.owner_init_va,
                    ),
                    expected[item.path],
                )

    def test_lookup_is_path_separator_and_case_tolerant_only(self):
        item = speech_resource(r"data\audio\speech\players.str")
        self.assertEqual(item.path, "Data/Audio/Speech/Players.str")
        with self.assertRaisesRegex(
            Gate14SpeechResourceOwnershipError,
            "unknown source-backed",
        ):
            speech_resource("Data/Audio/Speech/Unknown.str")

    def test_resource_identity_does_not_promote_commentary_semantics(self):
        for item in SPEECH_RESOURCES:
            with self.subTest(path=item.path):
                self.assertFalse(item.phrase_mapping_recovered)
                self.assertFalse(item.event_binding_recovered)
                self.assertFalse(item.playback_timing_recovered)
                self.assertFalse(item.commentary_ready)
                for field in (
                    "phrase_mapping_recovered",
                    "event_binding_recovered",
                    "playback_timing_recovered",
                    "commentary_ready",
                ):
                    with self.assertRaisesRegex(
                        Gate14SpeechResourceOwnershipError,
                        "cannot promote",
                    ):
                        replace(item, **{field: True})


if __name__ == "__main__":
    unittest.main()

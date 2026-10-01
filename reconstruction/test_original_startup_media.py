"""Tests for the source-backed FM2001 startup-media contract."""
from hashlib import sha256
import os
from pathlib import Path
import tempfile
import unittest

from original_startup_media import (
    EA_SPORTS_STARTUP_MEDIA,
    ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    PREMIER_LEAGUE_INTRO_MEDIA,
    OriginalStartupMediaError,
    OriginalStartupMediaSpec,
    validate_original_startup_media,
)


class OriginalStartupMediaTests(unittest.TestCase):
    def test_verified_startup_sequence_and_media_measurements_are_locked(self):
        self.assertEqual(
            ORIGINAL_STARTUP_MEDIA_SEQUENCE,
            (EA_SPORTS_STARTUP_MEDIA, PREMIER_LEAGUE_INTRO_MEDIA),
        )
        self.assertEqual(EA_SPORTS_STARTUP_MEDIA.source_path, "FMV/easp.tgq")
        self.assertEqual(EA_SPORTS_STARTUP_MEDIA.size_bytes, 1_383_304)
        self.assertEqual(EA_SPORTS_STARTUP_MEDIA.startup_callsite_va, 0x530FAE)
        self.assertFalse(EA_SPORTS_STARTUP_MEDIA.playback_flag_bit0)
        self.assertEqual(PREMIER_LEAGUE_INTRO_MEDIA.source_path, "FMV/premintro.tgq")
        self.assertEqual(PREMIER_LEAGUE_INTRO_MEDIA.size_bytes, 28_434_180)
        self.assertEqual(PREMIER_LEAGUE_INTRO_MEDIA.startup_callsite_va, 0x531175)
        self.assertTrue(PREMIER_LEAGUE_INTRO_MEDIA.playback_flag_bit0)
        for spec in ORIGINAL_STARTUP_MEDIA_SEQUENCE:
            self.assertEqual(spec.playback_wrapper_va, 0x461E20)
            self.assertEqual((spec.video_width, spec.video_height), (320, 480))
            self.assertEqual(spec.frame_rate, 25)
            self.assertEqual(spec.audio_sample_rate, 22_050)
            self.assertEqual(spec.audio_channels, 2)
        self.assertEqual(EA_SPORTS_STARTUP_MEDIA.decoded_video_frames, 97)
        self.assertEqual(PREMIER_LEAGUE_INTRO_MEDIA.decoded_video_frames, 1_275)

    def test_validator_can_prove_a_deliberately_supplied_source_without_special_cases(self):
        payload = b"synthetic tgq fixture"
        spec = OriginalStartupMediaSpec(
            source_path="FMV/test.tgq",
            source_sha256=sha256(payload).hexdigest(),
            size_bytes=len(payload),
            startup_callsite_va=0x1000,
            playback_wrapper_va=0x2000,
            playback_flag_bit0=False,
            video_width=320,
            video_height=480,
            frame_rate=25,
            decoded_video_frames=1,
            audio_sample_rate=22_050,
            audio_channels=2,
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / spec.source_path
            target.parent.mkdir(parents=True)
            target.write_bytes(payload)
            self.assertEqual(
                validate_original_startup_media(root, specs=(spec,)),
                (spec,),
            )
            target.write_bytes(payload + b"x")
            with self.assertRaisesRegex(
                OriginalStartupMediaError, "size mismatch"
            ):
                validate_original_startup_media(root, specs=(spec,))

    def test_playback_flag_is_kept_neutral_not_renamed_as_confirmed_skip_semantics(self):
        names = set(OriginalStartupMediaSpec.__dataclass_fields__)
        self.assertIn("playback_flag_bit0", names)
        self.assertNotIn("skippable", names)
        self.assertNotIn("skip_input", names)

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_GAME_ROOT"),
        "Original licensed startup media intentionally absent from hosted CI",
    )
    def test_opt_in_original_tgq_files_match_the_source_contract(self):
        root = Path(os.environ["FM2001_ORIGINAL_GAME_ROOT"])
        self.assertEqual(
            validate_original_startup_media(root),
            ORIGINAL_STARTUP_MEDIA_SEQUENCE,
        )


if __name__ == "__main__":
    unittest.main()

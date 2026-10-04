"""Tests for the Windows in-memory WAV menu PCM backend."""
from hashlib import sha256
from io import BytesIO
import struct
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import wave

from gate14_audiohooks_menu_pcm import DecodedMenuPcmDispatch
from gate14_audiohooks_menu_playback import play_audiohooks_menu_pcm
from gate14_windows_menu_pcm_backend import (
    Gate14WindowsMenuPcmBackendError,
    SOURCE_SAMPLE_RATE,
    WindowsMemoryWaveMenuPcmBackend,
    decoded_menu_pcm_to_wav_bytes,
)


def decoded_item() -> DecodedMenuPcmDispatch:
    samples = (1000, -1000, 32767, -32768)
    raw = struct.pack("<hhhh", *samples)
    return DecodedMenuPcmDispatch(
        event_id=17,
        state_value=0,
        sample_slot=6,
        sample_rate=SOURCE_SAMPLE_RATE,
        channels=1,
        pcm_samples=samples,
        pcm_sha256=sha256(raw).hexdigest(),
    )


class Gate14WindowsMenuPcmBackendTests(unittest.TestCase):
    def test_wav_wrapper_preserves_exact_pcm_rate_channels_width_and_frame_count(self):
        item = decoded_item()
        wav_bytes = decoded_menu_pcm_to_wav_bytes(item)

        with wave.open(BytesIO(wav_bytes), "rb") as input_wave:
            self.assertEqual(input_wave.getnchannels(), 1)
            self.assertEqual(input_wave.getsampwidth(), 2)
            self.assertEqual(input_wave.getframerate(), SOURCE_SAMPLE_RATE)
            self.assertEqual(input_wave.getnframes(), len(item.pcm_samples))
            self.assertEqual(
                input_wave.readframes(input_wave.getnframes()),
                struct.pack("<hhhh", *item.pcm_samples),
            )

    def test_backend_calls_injected_memory_player_synchronously_and_returns_true(self):
        player = Mock(return_value=None)
        backend = WindowsMemoryWaveMenuPcmBackend(player=player, memory_flag=4)
        item = decoded_item()

        self.assertIs(backend.play(item), True)
        player.assert_called_once()
        wav_bytes, flag = player.call_args.args
        self.assertEqual(flag, 4)
        self.assertEqual(backend.memory_flag, 4)
        with wave.open(BytesIO(wav_bytes), "rb") as input_wave:
            self.assertEqual(input_wave.getframerate(), SOURCE_SAMPLE_RATE)

    def test_default_backend_uses_winsound_playsound_and_snd_memory(self):
        player = Mock(return_value=None)
        fake = SimpleNamespace(PlaySound=player, SND_MEMORY=1234)
        with patch.dict(sys.modules, {"winsound": fake}):
            backend = WindowsMemoryWaveMenuPcmBackend()
            self.assertEqual(backend.memory_flag, 1234)
            self.assertTrue(backend.play(decoded_item()))

        player.assert_called_once()
        self.assertEqual(player.call_args.args[1], 1234)

    def test_integrity_mismatch_fails_before_platform_player(self):
        item = decoded_item()
        bad = DecodedMenuPcmDispatch(
            event_id=item.event_id,
            state_value=item.state_value,
            sample_slot=item.sample_slot,
            sample_rate=item.sample_rate,
            channels=item.channels,
            pcm_samples=item.pcm_samples,
            pcm_sha256="0" * 64,
        )
        player = Mock()
        backend = WindowsMemoryWaveMenuPcmBackend(player=player, memory_flag=4)

        with self.assertRaisesRegex(
            Gate14WindowsMenuPcmBackendError,
            "SHA-256 identity",
        ):
            backend.play(bad)
        player.assert_not_called()

    def test_backend_rejects_silent_or_malformed_configuration_without_playing(self):
        silent = DecodedMenuPcmDispatch(
            event_id=7,
            state_value=0,
            sample_slot=None,
            sample_rate=None,
            channels=None,
            pcm_samples=None,
            pcm_sha256=None,
        )
        player = Mock()
        backend = WindowsMemoryWaveMenuPcmBackend(player=player, memory_flag=4)
        self.assertFalse(backend.play(silent))
        self.assertFalse(backend.play(object()))
        player.assert_not_called()

        with self.assertRaisesRegex(
            Gate14WindowsMenuPcmBackendError,
            "supplied together",
        ):
            WindowsMemoryWaveMenuPcmBackend(player=player)
        with self.assertRaisesRegex(
            Gate14WindowsMenuPcmBackendError,
            "supplied together",
        ):
            WindowsMemoryWaveMenuPcmBackend(memory_flag=4)
        with self.assertRaisesRegex(
            Gate14WindowsMenuPcmBackendError,
            "must be callable",
        ):
            WindowsMemoryWaveMenuPcmBackend(player=object(), memory_flag=4)

    @patch("gate14_audiohooks_menu_playback.decode_audiohooks_menu_pcm")
    def test_windows_backend_composes_with_synchronous_playback_seam_without_audible_claim(
        self,
        decode,
    ):
        item = decoded_item()
        decode.return_value = item
        player = Mock(return_value=None)
        backend = WindowsMemoryWaveMenuPcmBackend(player=player, memory_flag=4)

        summary = play_audiohooks_menu_pcm(
            b"canonical-placeholder",
            item.event_id,
            item.state_value,
            backend,
        )

        self.assertTrue(summary.adapter_delivery_completed)
        self.assertFalse(summary.audible_windows_verified)
        self.assertFalse(summary.login_menu_audio_integrated)
        self.assertFalse(summary.semantic_event_binding_recovered)
        player.assert_called_once()


if __name__ == "__main__":
    unittest.main()

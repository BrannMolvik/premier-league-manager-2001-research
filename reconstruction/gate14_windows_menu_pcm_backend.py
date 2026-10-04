"""Windows in-memory WAV backend for verified decoded FM2001 menu PCM.

The adapter is deliberately below the numeric AudioHooks playback seam. It
accepts only a non-silent DecodedMenuPcmDispatch, re-verifies the decoded PCM
SHA-256, wraps the exact mono 16-bit 22050 Hz samples in a standard WAV image,
and calls a synchronous Windows memory-wave player.

The default platform path uses winsound.PlaySound(..., winsound.SND_MEMORY).
Tests may inject the player and flag, so hosted non-Windows CI verifies the WAV
contract without claiming real Windows audio-device output.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import wave
from typing import Callable

from gate14_audio_bank_format import pcm16le_bytes
from gate14_audiohooks_menu_pcm import DecodedMenuPcmDispatch


class Gate14WindowsMenuPcmBackendError(RuntimeError):
    pass


SOURCE_SAMPLE_RATE = 22050
SOURCE_CHANNELS = 1
PCM_SAMPLE_WIDTH_BYTES = 2


def decoded_menu_pcm_to_wav_bytes(item: DecodedMenuPcmDispatch) -> bytes:
    """Create a standard PCM WAV image from one verified non-silent dispatch."""
    if type(item) is not DecodedMenuPcmDispatch:
        raise Gate14WindowsMenuPcmBackendError(
            "Windows menu PCM backend requires exact DecodedMenuPcmDispatch"
        )
    if item.sample_slot is None or item.pcm_samples is None:
        raise Gate14WindowsMenuPcmBackendError(
            "silent numeric menu route has no PCM to wrap"
        )
    if (
        item.sample_rate != SOURCE_SAMPLE_RATE
        or item.channels != SOURCE_CHANNELS
    ):
        raise Gate14WindowsMenuPcmBackendError(
            "FM2001 menu PCM must remain mono 22050 Hz"
        )

    try:
        pcm = pcm16le_bytes(item.pcm_samples)
    except Exception as exc:
        raise Gate14WindowsMenuPcmBackendError(
            "decoded menu PCM could not be serialized as int16"
        ) from exc

    if sha256(pcm).hexdigest() != item.pcm_sha256:
        raise Gate14WindowsMenuPcmBackendError(
            "decoded menu PCM SHA-256 identity does not match samples"
        )

    buffer = BytesIO()
    with wave.open(buffer, "wb") as output:
        output.setnchannels(SOURCE_CHANNELS)
        output.setsampwidth(PCM_SAMPLE_WIDTH_BYTES)
        output.setframerate(SOURCE_SAMPLE_RATE)
        output.writeframes(pcm)
    return buffer.getvalue()


class WindowsMemoryWaveMenuPcmBackend:
    """Synchronous winsound-compatible backend for in-memory verified WAV data."""

    def __init__(
        self,
        *,
        player: Callable[[bytes, int], object] | None = None,
        memory_flag: int | None = None,
    ):
        if (player is None) != (memory_flag is None):
            raise Gate14WindowsMenuPcmBackendError(
                "player and memory_flag must be supplied together"
            )

        if player is None:
            try:
                import winsound
            except ImportError as exc:
                raise Gate14WindowsMenuPcmBackendError(
                    "default menu PCM backend requires Windows winsound"
                ) from exc
            player = winsound.PlaySound
            memory_flag = winsound.SND_MEMORY

        if not callable(player):
            raise Gate14WindowsMenuPcmBackendError(
                "menu PCM platform player must be callable"
            )
        if type(memory_flag) is not int or memory_flag < 0:
            raise Gate14WindowsMenuPcmBackendError(
                "winsound memory flag must be a nonnegative integer"
            )

        self._player = player
        self._memory_flag = memory_flag

    @property
    def memory_flag(self) -> int:
        return self._memory_flag

    def play(self, item: DecodedMenuPcmDispatch) -> bool:
        """Synchronously submit one verified WAV memory image.

        Normal return from the player means only that the platform adapter call
        completed. Audible output is verified elsewhere.
        """
        if type(item) is not DecodedMenuPcmDispatch or item.sample_slot is None:
            return False
        wav_bytes = decoded_menu_pcm_to_wav_bytes(item)
        self._player(wav_bytes, self._memory_flag)
        return True

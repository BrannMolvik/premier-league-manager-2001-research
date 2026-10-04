# Gate 14 Windows in-memory menu PCM backend

_Status: Windows adapter implementation only. Audible verification remains open._

## Result

`gate14_windows_menu_pcm_backend.py` provides the first dependency-free Windows
adapter behind the verified synchronous numeric menu PCM seam.

For each non-silent `DecodedMenuPcmDispatch` it:

1. requires the source-backed mono 22,050 Hz format;
2. serializes the already decoded samples as signed PCM16LE;
3. recomputes and verifies the decoded PCM SHA-256 identity;
4. wraps those exact bytes in a standard mono 16-bit 22,050 Hz WAV image;
5. synchronously calls a memory-wave player.

The default platform player is Python's Windows
`winsound.PlaySound(wav_bytes, winsound.SND_MEMORY)`. The player callable and
memory flag are injectable so hosted Linux CI can validate the exact WAV
contract without importing or simulating a Windows audio device.

## Fail-closed boundary

Normal return from the platform player means only that the adapter call
completed. It does not prove:

- audible output reached a real device;
- speaker/headphone configuration was correct;
- numeric event IDs have human-readable original meanings;
- reconstructed UI events are equivalent to original native senders;
- login/menu audio is integrated;
- Gate 14 is complete.

A decoded PCM hash mismatch fails before the platform player is invoked.

## Exact next private Windows step

Add a Windows 11 audit harness/receipt that:

- loads the exact canonical private `menus.bnk`;
- accepts an explicit numeric AudioHooks event/state pair rather than a guessed
  semantic name;
- runs the canonical decode -> synchronous seam -> real winsound backend;
- records OS/Python/audio-adapter completion evidence outside Git;
- requires explicit human confirmation that the expected sample was audible
  before any audible verification flag is promoted.

Semantic event binding remains separately blocked on the canonical executable
caller/source trace. No sample is named by ear and no proprietary PCM/BNK bytes
are committed to Git.

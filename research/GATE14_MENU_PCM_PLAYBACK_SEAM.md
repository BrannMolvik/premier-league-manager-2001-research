# Gate 14 synchronous numeric menu PCM playback seam

_Status: platform-adapter delivery only. Gate 13 remains Codex-owned._

## Result

The canonical numeric `AudioHooks -> menus.bnk -> PCM` bridge can now be
handed to a caller-supplied synchronous playback backend through
`gate14_audiohooks_menu_playback.py`.

The seam follows the same narrow orchestration pattern already used by verified
startup media:

- source identity, numeric routing, and PCM decode happen before platform
  delivery;
- original numeric no-sound routes return without requiring or invoking a
  backend;
- non-silent routes require a `play(decoded_item)` backend;
- only an **exact `True`** return counts as synchronous adapter completion;
- backend exceptions or any other return value fail closed.

## Evidence boundary

A successful backend call proves only that the configured adapter accepted the
verified decoded packet and reported synchronous completion.

It does **not** prove:

- which human-readable original event the numeric ID represents;
- what the sample should be called;
- that a reconstructed modern UI action is the same original event;
- that Windows produced audible output;
- that login/menu audio is integrated;
- that Gate 14 is complete.

Those flags are structurally forbidden in the playback summary.

## Exact next step

Add a Windows-only backend behind this seam. A suitable dependency-free path is
Python's standard-library `winsound.PlaySound` with `SND_MEMORY`, using a
standard in-memory PCM WAV wrapper around the already decoded mono 22,050 Hz
samples. The adapter must remain synchronously testable with an injected player
function.

Even after that adapter passes synthetic/host tests, the real Windows 11 audible
receipt remains required before `audible_windows_verified` or
`login_menu_audio_integrated` can be promoted.

Separately, the private canonical executable caller trace still owns semantic
event binding. No sound should be named by ear.

No proprietary BNK bytes or decoded PCM are committed to Git.

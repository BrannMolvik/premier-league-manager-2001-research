# Gate 14 real-Windows bound first-screen audio acceptance

_Status: fail-closed acceptance tooling. No private Windows receipt is canonical yet._

## Purpose

The production source-backed host already installs the recovered PStartMenu /
TeamSelect Button press-audio route on Windows. The bounded source contract is:

- accepted captioned first-screen Button press;
- numeric AudioHooks event/state `(10, 0)`;
- canonical `menus.bnk` sample slot 2;
- decoded PCM delivered synchronously by
  `WindowsMemoryWaveMenuPcmBackend`;
- gameplay click delegation occurs even when expected audio delivery fails.

That is stronger than an isolated numeric playback CLI, but hosted tests still
cannot prove that Daniel's Windows 11 machine actually produced audible output
through the bound application path.

`reconstruction/gate14_windows_bound_first_screen_audio_audit.py` supplies
that missing acceptance boundary without assigning any new sound/event meaning.

## Production-host seam

`run_original_game_ui(...)` now accepts an optional
`host_ready_callback`. Normal launches leave it as `None`.

When supplied for this audit only, the callback receives:

1. the actual `OriginalGameTkHost`; and
2. the exact `Gate14FirstScreenAudioHostBinding` returned by the normal
   Windows installation path.

The callback runs after the audio binding is installed and before
`root.mainloop()`. The audit schedules its probe with Tk `after(0, ...)`,
so the generated input is delivered only after the real event loop starts.

## Acceptance transaction

A passing run must:

1. execute on an external Windows 11 client workstation, never GitHub Actions
   or Windows Server;
2. begin on the production START_MENU;
3. generate a real Tk `<Button-1>` at the source-backed **Start New Game**
   rectangle;
4. delegate through the normal host handler into TEAM_SELECT;
5. observe exactly one audio attempt and exactly one successful adapter
   delivery;
6. retain the exact canonical `menus.bnk` size/SHA-256;
7. retain an exact `MenuPcmPlaybackSummary` for event 10, state 0, slot 2,
   with the Windows memory-wave backend invoked and synchronously completed;
8. use the exact `WindowsMemoryWaveMenuPcmBackend`; and
9. after delivery, require the human operator to type `YES-HEARD` exactly if
   the sound was personally heard.

Any audio delivery failure remains fail-soft for gameplay, as the live binding
already requires, but the acceptance transaction itself fails closed.

## Private receipt

The CLI is:

```text
python reconstruction/gate14_windows_bound_first_screen_audio_audit.py ^
  --game-dir "C:\Games\FM2001" ^
  --output-receipt "<private-folder-outside-Git>\gate14-bound-first-screen-audio.json"
```

Use `--source-root` only when the normal source-backed host itself needs that
existing override.

The receipt must be new and outside the repository. Do not commit it or any
original bank/decoded audio bytes.

A passing receipt may record:

- `bound_application_press_audio_verified = true`;
- `audible_windows_verified = true` for this bounded application press.

It deliberately keeps all of these false:

- broader semantic/application-wide AudioHooks event binding;
- human-readable sample meaning;
- hover-audio integration;
- full login/menu audio integration;
- Gate 14 completion.

The transaction also records that it invokes the production host runner rather
than the top-level `app.py` CLI and that startup media is not part of this
receipt. The startup-FMV Windows receipt remains a separate acceptance proof.

## Evidence boundary

This acceptance does not source-close the remaining AudioHooks callers, chants,
FastView omissions, 3D choreography, source navigation into FastView, startup
FMV skip/fade/display fidelity, or a recognizable complete original match
workflow. It is one bounded real-Windows proof for an already integrated
source-backed first-screen sound route.

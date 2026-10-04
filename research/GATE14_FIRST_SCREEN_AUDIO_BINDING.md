# Gate 14 first-screen press-audio host binding

_Status: dependent work-ahead on the source-closed first-screen Button audio route._

## Purpose

The production `OriginalGameTkHost` already renders START_MENU and TEAM_SELECT
from original source frame index **0** and binds Tk `<Button-1>` to its
existing `on_click` path. It does not retain a native Button animation-state
machine.

This checkpoint therefore integrates only the bounded behavior the host can
represent exactly: the source group-0 **press** route for recovered
PStartMenu/TeamSelect action rectangles.

## Binding

`gate14_first_screen_audio_binding.py` wraps an already-created host without
editing Gate-13-owned presentation code.

For START_MENU / TEAM_SELECT:

1. it uses the already recovered original action rectangles through
   `candidate_original_event`;
2. only a rectangle-backed action candidate attempts audio;
3. the host's fixed source frame 0 is verified as native group 0/subframe 0;
4. the wrapper calls the source-closed first-screen Button route, which delivers
   numeric AudioHooks `(10,0,0x40)` -> `menus.bnk` slot 2;
5. it then delegates to the original host click handler.

This preserves the native ordering established at `0x64F7A0`: audio is sent
before the later Button state/action path.

The PStartMenu and TeamSelect owner pre-audio gates are already source-closed as
unconditional acceptance methods. A later gameplay/session action may still
fail; that does not retroactively cancel the earlier native Button sound.

## Presentation must not block management

If the existing PCM transport raises the expected
`Gate14MenuPcmPlaybackError`, the wrapper records the audio failure and still
delegates the click to the original host. This preserves the roadmap requirement
that presentation fidelity work must not block core management play.

Unexpected programming errors are not swallowed.

## Deliberate limits

The current host does not track native hover/capture/group state and has no
`<Motion>` binding. Therefore this wrapper does **not** yet integrate the
source-closed pointer-enter slot-3 route from the preceding checkpoint.

It also keeps these false:

- human-readable event/sample meaning;
- hover audio integration;
- real-Windows audibility verification;
- full login/menu audio integration;
- Gate 14 completion.

A strict Windows run through this bound application path is still required
before audibility/integration readiness can advance.

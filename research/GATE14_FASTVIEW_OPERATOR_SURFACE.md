# Gate 14 FastView operator-visible Tk surface

_Status: bounded cloud-safe integration; source navigation trigger intentionally unrecovered._

## Purpose

The completed-human Gate-14 pipeline already produces an integrity-bound
`HumanFastViewResolvedPresentation` containing the canonical resolved-only
800x600 preview, frame-coverage audit, and unresolved-overlap audit. PR #452
also forwards every already source-verified optional component plane through
that completed-human path.

The production `OriginalGameTkHost` did not previously expose any FastView
surface. This checkpoint adds the smallest presentation-only bridge needed to
make those already-verified pixels operator-visible without inventing a new
gameplay or navigation route.

## Runtime boundary

`reconstruction/gate14_fastview_human_tk_window.py`:

- requires an already-built exact `HumanFastViewResolvedPresentation`;
- creates an 800x600 Tk child window on an existing caller-owned Tk root;
- draws only the presentation's canonical resolved-preview PNG through the
  existing `draw_human_fastview_resolved_presentation()` seam;
- keeps unresolved overlap pixels transparent;
- does not call `mainloop()`, fullscreen/focus/grab APIs, simulation, RNG,
  gameplay controllers, front-end navigation, or source resource selectors;
- labels the surrounding Tk window as compatibility chrome rather than original
  FM2001 pixels.

`OriginalGameTkHost.present_completed_match_fastview(...)` exposes that
surface to the source-backed runtime host but is deliberately not called from
`on_click()`, PMenu actions, or any other navigation transition. A source
runtime trigger must be recovered separately before ordinary play may invoke it
automatically.

## Fidelity boundary

This checkpoint does **not** claim:

- a complete FastView frame;
- recovered cross-component z-order or blend behavior;
- recovered omitted TeamTable/ScoreCompositeMain/GoalFlash/embedded-control
  pixels;
- audio or chant semantics;
- 3D choreography;
- an original source navigation trigger into FastView;
- Gate 14 completion.

The surrounding Tk canvas/window is not part of the claimed FM2001 frame. Only
the canonical resolved preview bytes are presentation evidence.

## Verification

Regression coverage requires:

1. native 800x600 window/canvas geometry;
2. exact forwarding of the existing completed-human presentation object;
3. exact reuse of the presentation's canonical preview;
4. fail-closed rejection of false complete-frame/navigation promotion;
5. no imports of gameplay, match simulation/calculation, front-end navigation,
   RNG, or the source host from the standalone surface module;
6. host exposure with no hidden gameplay/navigation trigger.

The full reconstruction workflow includes the new surface tests.

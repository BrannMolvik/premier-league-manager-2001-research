# Gate 13 Recovery 406 — verifying actual startup-FMV transport receipts

_Status: diagnostic hardening only, not an original-pixel correction or Windows acceptance._

## Evidence and compatibility problem

The existing source-verified FMV geometry remains: coded TGQ 320×480, horizontal 2× repeat to 640×480, game-owned child requested at (80,60) of the original 800×600 field. Prior real Windows observation found cropped or displaced content. PR #551 added a **private, opt-in** production-WPF HWND/DPI probe, but a JSON report containing rectangles was previously accepted without checking the algebraic consistency of its reported rectangles and origins.

The minimal Windows 11 compatibility work here changes **only diagnostic receipt validation and comparison**. The Win32 `GetClientRect` API returns a rectangle relative to client (0,0) and `RECT` fields expose bottom-right-exclusive bounds; `GetWindowRect` returns screen coordinates but is DPI virtualized. `GetAwarenessFromDpiAwarenessContext` may return an invalid enum for a bad context. Consult Microsoft documentation:

- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getclientrect
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowrect
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getawarenessfromdpiawarenesscontext

## Guarded diagnostic contract

The existing explicit opt-in receipt parser now rejects:

1. Rectangles where `right-left != width` or `bottom-top != height`.
2. `GetClientRect` results whose left/top are not zero.
3. Child offsets inconsistent with measured child window origin minus measured parent client origin.
4. Invalid awareness enumerations; 0/1/2 remain accepted.

All checks are source-neutral Win32 measurement identities, not guesses about native FM2001 rendering. The parser deliberately **does not** reject a child whose measured size/offset differs from the requested size/offset: a coherent mismatch is the evidence the probe exists to collect. It adds mechanically calculated `transport_comparison` flags for offset, child-window size, child-client size, and parent-vs-child DPI, always setting `visual_equivalence_assessed=false`. No real Windows capture has been received.

The default startup-media path is unchanged because receipt capture remains explicitly opt-in. Validation does **not** set or imply `startup_media_real_windows_verified`, `exact_display_treatment_recovered`, or Gate-13/Gate-17 acceptance. It does not establish WPF `MediaElement` inner pixels or the original fade/skip semantics.

## Next actual evidence required

Execute the already documented `--transport-probe-only` audit using a qualifying private Windows 11 client with the authorized installed game and save the JSON output outside Git. Review each sequence entry’s `transport_comparison` flags and original raw HWND/client/DPI fields. Even all-true geometry flags cannot prove the movie *contents* are visually equivalent. A separate human visual inspection and actual menu/Squad responsiveness acceptance remain necessary. Do not tune WPF movie geometry by eye or treat hosted CI as that receipt.

# Issue #482: Windows WPF child startup timeout

Investigated on Daniel's Windows machine, 7 October 2026. Branch:
`codex/gate13-wpf-startup-fix`, based on current-main
`bf91dc0338de7c9b31486d1d3ff50c6e5251f743`. This is a Gate-13-only
diagnosis/fix, not Gate-14 work or a Gate-13 completion claim.

## Confirmed cause

The owning Tk thread stops processing Windows messages while waiting in
`subprocess.run()` for the WPF player, before `root.mainloop()` starts.
The cross-process `HwndSource` child constructor consequently stalls **before
MediaElement creation**. The timeout is not evidence of a corrupt clip or a
missing MediaEnded event after playback: the blocked run never reaches Loaded,
Play, MediaOpened, MediaEnded, or MediaFailed.

The identical child script, cache bytes, parent-binding method and geometry
complete when the Tk owner services events during the wait. This establishes
the parent-thread starvation boundary; no specific Windows message ID or
native stack was captured, so those are not claimed.

## Media validation

Private cache: `%LOCALAPPDATA%/FM2001-Windows11/startup-media/easp.mp4`.
Size: 410,656 bytes. SHA-256:
`de76c6cdeb88ea4eec1541dd2708c12d99f633629302b6bc2bf696269c6d3b70`.
Size/hash match the existing conversion receipt.

FFprobe reports H.264 High, yuv420p, 640x480, 25 fps, **97 decoded frames**,
3.880000 s; AAC LC, 22,050 Hz, stereo, 3.879002 s. Full video **and** audio
decode with the release-bundled FFmpeg 7.1, `-xerror`, both stream maps and a
null output exits 0, no error stderr, frame=97 and progress=end. FFprobe was
the already installed 9.0.2 binary; no tools or media were downloaded.

## Controlled WPF observations

Times below are seconds since the private PowerShell diagnostic started.
Only event/timing logging was inserted into the production WPF script for
the child comparisons. C-blocked and C-pumped used the same instrumented
script SHA-256:
`10d19cd1edd731b72d0a5690a6bb9d3fd33c344c8e2790163c9cceee38806fbf`.

| Case | HwndSource before / after | Loaded | MediaOpened | MediaEnded | Result |
| --- | --- | --- | --- | --- | --- |
| A: simple top-level WPF Window, diagnostic only | not applicable | 2.152 | 3.563 | 7.290 | completes |
| B: child of Tk canvas HWND, Tk pumped | 0.603 / 1.087 | 1.492 | 2.714 | 6.482 | completes |
| C: production root-HWND binding, owner blocked | 0.514 / never | never | never | never | existing 33.88 s timeout |
| C: same production root binding, owner pumped | 0.304 / 0.815 | 1.204 | 2.339 | 6.124 | completes |

Blocked C records ProcessStarted, WpfLoaded and BeforeHwndSource only; Tk
heartbeat count is zero. Pumped C records 733 Tk heartbeats, correct 640x480
MediaElement size, Loaded/Play/MediaOpened/MediaEnded. B records 782 Tk
heartbeats and the same size. No MediaFailed or Unloaded event was observed
in these receipts. A has ordinary window chrome and is only a decoder/WPF
control experiment; it is **not** a proposed production presentation.

The working child comparisons retain ParentWindow, WS_CHILD|WS_VISIBLE,
80/60 origin, 640x480 size, LoadedBehavior=Manual, UnloadedBehavior=Stop and
Play-on-Loaded. Thus neither a new parent/geometry nor a LoadedBehavior
change is needed to resolve this demonstrated failure.

## Smallest compatible fix

The host binds its owning-thread event pump before starting the verified
startup sequence. The backend uses its own Popen with short communicate
waits, pumping Tk between waits. The **existing duration-derived deadline
is unchanged**; 20 ms is a message-service wait, not a media/frame timer.
Timeout or parent/pump failure kills and drains only the owned player.
Hidden-menu pointer actions and redraws are rejected during startup so
servicing the owner cannot activate unseen menu controls or remove the
black movie field.

The production PowerShell WPF script itself is unchanged. Game-owned child
presentation, native 640x480 at 80/60, existing display transform, ordered
verified source clips, normal audio volume, MediaEnded success requirement,
MediaFailed handling and all cache/source validation remain intact. No
top-level fallback, startup bypass, timeout increase or game-original
execution is introduced.

## Actual production-host sequence verification

`run_original_game_ui` was exercised with the actual default presenter,
Tk host, backend, verified cache and original source files from the existing
authorized installation. `prepare_runtime_startup_media` rechecked the
original TGQ identities and existing derivative hashes. A private diagnostic
selected windowed presentation to avoid disrupting the desktop and added
WPF event logging; it did not alter the sequence or player behavior.

Both clips use the same game parent HWND. The existing 1.6 display scale
maps native 80/60/640/480 to 128/96/1024/768; the compatibility transform
was not changed by this fix.

- easp: Loaded 0.715, MediaOpened 1.498, MediaEnded 5.415.
- premintro: Loaded 0.304, MediaOpened 0.603, MediaEnded 54.347.
  Its decoder reports 51 s of source video; WPF NaturalDuration is 53 s.
  Playback is not cut to video duration and the existing timeout is sufficient.
- Sequence finishes in 61.936 s; 1,955 Tk pumps. The host-ready callback
  is reached only after both clips, menu screen is `pstartmenu`, the black
  backdrop is cleared and mainloop starts.
- A separate opt-in real-Windows regression completes easp using the
  **unmodified** production WPF script, eliminating diagnostic logging as
  the explanation for successful playback.

## Regression and remaining acceptance

Focused Windows tests: **88 passed** (18.970 s), including the opt-in real
WPF/Tk test. Tests cover pre-mainloop pump binding, child-before-completion,
unchanged bounded timeout, owned-process cleanup, MediaFailed, parent close
and hidden-menu input/redraw suppression. Existing verification/order tests
remain in the run. Asset policy and `git diff --check` pass.

Full reconstruction suite: **2,839 tests run, OK (23 expected skips)**,
198.193 s, using the existing private Capstone runtime. The opt-in real-media
test is separately included in the 88-test focused Windows pass above.
The previously downloaded frozen artifact is unchanged: a newly built
package and Daniel's normal packaged-launch acceptance remain unverified.
The successful production-host source run does not replace that acceptance,
an independent audible/visual human review, or the Gate-13 closure audit.

## Private evidence location

Receipts, hashes, scripts and raw logs remain outside Git, under:
`C:/Users/Brann/Documents/Codex/2026-10-01/referenced-chatgpt-conversation-this-is-an/work/`.

- `issue482-decode-verified-20261007/decode.json`
- `issue482-A-top-20261007/{result.json,events.log}`
- `issue482-B-pumped-20261007/{result.json,events.log}`
- `issue482-C-blocked-20261007/{result.json,events.log}`
- `issue482-C-pumped-20261007/{result.json,events.log}`
- `issue482-normal-startup-fixed-20261007/{result.json,easp.log,premintro.log}`
- `issue482-focused-final-20261007.log`
- `issue482-full-suite-20261007.log`

Reproduce the bounded real-WPF regression, with normal clip audio, by setting
`FM2001_WPF_TEST_CACHE` to the existing verified private cache and running
`python -m unittest -v test_startup_media_tk_integration` in `reconstruction`.
Without that explicit Windows opt-in the proprietary-media test is skipped.
No original executable, archive or raw media is committed.

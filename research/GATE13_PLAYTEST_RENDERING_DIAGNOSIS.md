# Local packaged play-test: Squad names and menu owner coordinates

7 October 2026, integration branch only; main is not merged or modified.

## Reproduced defects

The frozen `fe5543ff` build reaches Southport management without an exception,
but draws role/numeric columns over the original background with no player
names. This is not successful normal-play acceptance. The presenter discards
every unselected name because reserve flags are missing, even though the
source name and font are available. The main-menu action group is also offset
left/up because its owner-local rectangles were used as screen coordinates.

## Source-qualified repairs

Canonical executable SHA-256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Bounded disassembly and diagnostic logs remain outside Git in the private
`work/southport-render-trace*.txt` receipts.

- `DBTPlayers::0x416FC0` constructs its array through `0x4234D0`.
  That constructor sets EDI=0 and explicitly writes it to player `+0x174`
  at `0x423528`, before installing DBRPlayer vtable `0x7BDEDC` and calling
  `0x4178D0`. This is a literal field initialization, not inferred allocation
  contents. `0x417EA0/0x417EC0` test current-club identity and bits 0/1 of
  that independent word. The runtime now retains those booleans, carries them
  through the management bridge, and persists them in unused bits 12/13 of
  the existing internal player flags word. The record shape/schema is unchanged;
  older port saves did not implement reserve selection and restore cleared bits.
  The existing color helper keeps its native predicate precedence and still
  fails closed when a bounded adapter genuinely supplies unknown reserve state.
  This does not implement untraced reserve-selection interaction/lifecycles.
- `0x5312A8 -> 0x653320` registers PStartMenu at `(134,34,532,532)`.
  Its four controls register PStartMenu as their owner and receive local
  `(181,478)`, `(7,478)`, `(355,478)`, `(181,508)` origins through `0x652FD0`.
  Shared owner draw `0x6533A0` adds owner `+0x0C/+0x10`; pointer dispatcher
  `0x653480` subtracts those origins before child hit testing. Live art, captions,
  clipping, hover and pointer candidates must therefore use screen origins
  `(315,512)`, `(141,512)`, `(489,512)`, `(315,542)` respectively.
  Derivative caption metadata stays owner-local and its verified manifest is
  unchanged. No settings button or aesthetic substitute is introduced.

## Outstanding external acceptance

These targeted changes are not a claim that the full Squad surface is complete.
The reproduced screen also lacks additional management/roster presentation;
existing fail-closed rendering boundaries must be completed from original
evidence before calling the whole build playable or closing Gate 13.

## Both intro clips: confirmed mixed-DPI defect and compatibility fix

The frozen PyInstaller executable has no DPI-awareness manifest declaration.
Its default Tk parent is DPI-unaware; loading WPF makes the player thread
system-aware. A same-clip A/B test on Daniel's 150% DPI display established:

| Parent setup | Parent/child DPI | WPF content units | Device transform |
| --- | --- | --- | --- |
| Default unaware parent | 96/96; child awareness 0, thread awareness 1 | 800x600 | 1.5 |
| System-aware parent before Tk creation | 144/144; child/thread awareness 1 | 533.333x400 | 1.5 |

The first path applies the device scale to an already full-sized layout,
explaining cropped content inside a correctly centered outer child rectangle.
Both tests used the same verified EA derivative and both reached MediaEnded;
this was a framing error, not another timeout. Private event receipts:
`work/wpf-inner-dpi-{unaware,aligned}-proof1/events.log`.

`windows_display_context.py` now initializes and verifies process-local DPI
awareness before any application Tk root. Existing awareness is not downgraded;
an unsuccessful context qualification fails closed. Desktop settings, source
media, cache checks, source order, audio and duration-plus-30 timeout are unchanged.
The rebuilt frozen executable completed both ordinary intros and restored the
menu. The Premier League circular content was visibly centered and uncropped.
The separate short EA A/B tests both completed. No subjective audio confirmation
or cross-monitor/per-monitor-DPI acceptance is claimed.

The compatibility viewport now scales down as well as up when the actual game
client changes size. It retains the original 800x600 coordinates and 640x480
movie rectangle at (80,60), with nearest-neighbour game art. The backend resizes
only its PID-qualified direct game child using NOACTIVATE/NOZORDER, without
restarting playback. A real two-clip resize test exercised 1000x750, 640x480 and
400x300 clients, verified child client dimensions, reached both MediaEnded events
and restored the menu. Its private receipt is `work/intro-resize-check/passed.json`.
The 50ms resize coalescing is modern transport handling, not original game timing.
F11/Alt+Enter/Escape remain rejected while startup media is active.

## Explicit remaining playability boundary

The corrected frozen build was operated through Start New Game -> Conference ->
Southport -> Start in an ordinary window. Twenty visible names now render with
roles and source-qualified numeric fields, and no startup exception appeared.
However, the blank management header and incomplete roster controls are real
missing presentation, not fixed by DPI initialization. The source-backed host
also lacks the ordinary advance/play binding. Existing backend tests can calculate
a Conference fixture and save/reload it, but are not ordinary UI play acceptance.
The earlier development notebook (`--prototype-ui`) is a distinct host, not a
substitute production solution. Gate 13 is not closed by this checkpoint.

Validation for this checkpoint: 81 focused host/DPI/startup tests passed with
one licensed-media opt-in skip; 22 final DPI/owned-child tests passed; full
reconstruction suite passed 2,859 tests with 24 expected skips (381.983s), using
the existing private Capstone dependency. Asset policy and whitespace checks
passed. The actual rebuilt frozen executable passed package-smoke and PStartMenu
manifest verification, both normal intros, windowed menu input and ordinary
Conference/Southport selection. Private logs: `work/dpi-final-focused.log`,
`work/dpi-ownership-final.log`, `work/dpi-final-full.log`, and
`work/issue482-dpi-build-smoke.log`. These results do not certify missing normal
management interaction, subjective audio, or final release acceptance.

## Follow-on: restored first-roster title and row picture strips

Canonical static source rehash remained
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
`PSquadList::4B4FE0` supplies First Team global `984560` when discriminator
`+98C` is zero (Reserves global `984558` otherwise). The sequential language
reader maps those globals to English.idx 166/168, resolving exactly to
`First Team` / `Reserves`; the existing 982110 -> index 2490 mapping was the
calibration. The current fresh first-roster slice uses First Team only.

`4B506D -> 5D6050 -> 5D5EB0 -> 651E30/651BA0` qualifies title wrapper 946B70,
font 9197E0 (existing verified Zurich BdXCn 18pixel), raw flags 2001, white,
six-pixel X inset and zero Y inset. Its original file is title_bar_7.444:
`5F3754` path literal 8354B0 -> raw 946B90; `5F37A0` constructs wrapper
946B70 with source origin (0,0), 226x20. Native 651F80/6520C0 supply default
vertical centering and owner clipping. The live title rectangle is (37,205,226,20).

The twenty picture controls at 4B520F..4B5670 use wrapper 942FD0 at
list-local (0,154+17*i), i=0..19. `5FBEF4` loads stats_grid_disabled.444
into raw 942FF0; 5FBF40 constructs its wrapper at source (0,0), 328x16.
The original image is 729x16: the runtime must crop its first 328 columns,
not shrink/stretch the entire image. The screen rectangles are (37,233+17*i,328,16).
They render before player/SCF text. Both asset identities and byte sizes were
independently extracted using existing inventory tooling from the canonical
ZIP hash and now appear in original_assets/MANIFEST.md. Masked source pixels
retain the existing EA444 decoder's color-key alpha behavior.

Private evidence: `work/squad-required-chrome-trace.txt`,
`work/squad-required-chrome-inventory.json`, `work/squad-chrome-loader-check.json`.
The production-loader check decodes actual originals entirely offline and
returns 28 overlays (title/caption, 20 strips, six existing button layers).
83 focused Squad/host/style/presenter tests passed (20.292s). No new Windows
visual acceptance is claimed. This is not full roster selection, reserves,
column-title/sort interaction, management-header text or match-start integration.

Final offline regression: 2,861 tests passed, 24 expected skips, in 359.642s
(`work/squad-chrome-full.log`). The subsequent atlas-validation guard passed
all five focused Squad-control tests. Asset policy and staged whitespace checks
passed. Daniel requested a pause for usage reserve; no further executable
launch or native investigation is scheduled by this checkpoint.

## New extracted-package Windows policy blocker

The local-2dc760e1 release ZIP was generated through the normal release tool;
all 1,205 extracted payload hashes match PACKAGE-MANIFEST.json. Its relocated
executable nevertheless cannot start: Windows Code Integrity events 3033/3077
at 16:33:35..37 KST on 7 October 2026 state that it fails Enterprise signing
requirements under policy `{0283ac0f-fff1-49ae-ada1-8a933130cad6}`.
Read-only Authenticode inspection reports NotSigned. Executable SHA-256:
`8359b9a74729b6959648cd09e6294b4d3b6ed3a6e657466367443926040d4a42`.

This is an operating-system trust failure, not a package-manifest failure or
another WPF timeout. The earlier normal frozen run succeeded before extraction;
that does not qualify the blocked redistributed copy. No retry through a
different execution route, unblock operation, signing infrastructure, security
setting, certificate or App Control modification is attempted. Subsequent
work is offline source/rendering tests only. An approved executable trust /
distribution route is required before further packaged Windows acceptance;
Daniel's rejection of paid signing infrastructure remains respected.

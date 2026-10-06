# Startup FMV pixel pipeline

_Last verified: 6 October 2026_

## Scope and correction

This note records the source-backed startup-video pixel path in the canonical
FM2001 executable:

`footballmanager.exe` / disc `FOOTBAL.EXE`

SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

No original executable or EA media bytes are stored in Git.

An earlier Recovery 330 checkpoint correctly established the 320x480 coded
geometry and the flag-0x40 640x480 logical geometry, but stopped one layer too
early and tentatively attributed the horizontal expansion to a DirectDraw
stretch. Deeper writer analysis, independently rechecked before merging PR
#487, supersedes that interpretation: the startup 16-bpp TQI writer itself
duplicates every coded horizontal pixel into two identical display pixels.
There is therefore a source-backed nearest-neighbor 2x horizontal treatment.

The detailed adjudication also lives in
`research/GATE13_STARTUP_FMV_PRESENTATION_SOURCE_TRACE.md`.

## Proven pipeline

```text
TGQ pIQT coded frame
320 x 480
    |
    | TQI decode / packed color tables
    | startup flag 0x40 selects doubled 16-bpp writer
    | each coded pixel -> two identical adjacent 16-bit pixels
    v
640 x 480 game-owned movie surface
    |
    | 1:1 DirectDraw Blt
    v
active game display
640 x 480 at (0,0) in mode 0
640 x 480 at (80,60) inside 800 x 600 in mode 1
```

The old modern presentation that treated the 320x480 derivative as an
aspect-preserved `Uniform` image was not faithful.

## 1. Coded source geometry is 320 x 480

The `pIQT` payload stores little-endian width 320 and height 480. The video
header parser around `0x69CD10` preserves those coded dimensions in the movie
base object:

```text
base + 0x64 = width  = 320
base + 0x60 = height = 480
```

## 2. Startup explicitly requests double-width output

The shared wrapper at `0x461E20` calls `0x461900` with literal flag
`0x40`:

```text
0x461F2E  push 0x40
0x461F30  push path
0x461F31  call 0x461900
```

Rectangle/output setup at `0x69D5C0` starts from the coded width and height.
Flag `0x40` doubles only the logical/output width. The separate `0x30`
vertical-doubling bits are not supplied by this wrapper.

The startup logical movie geometry is therefore 640x480.

## 3. The ordinary game display is initialized to 16 bpp

The ordinary graphics initialization sets the game BPP global
`0x8547A8` to `0x10` at `0x615256`.

The display-mode machinery subsequently carries the selected mode's actual BPP
through the same global. This is also consistent with the game's user-facing
requirement for 16-bit color or higher and with the decoder querying the actual
destination surface pixel format before selecting/initializing its packer.

The 640x480 movie surface creation at `0x461A37` uses helper `0x6555D0`
with BPP argument `-1`, so the surface follows the active game display format
rather than forcing an unrelated private surface format.

## 4. Flag 0x40 selects the doubled 16-bpp writer

At `0x69D289`, the TQI output path checks startup flag `0x40`.

For the ordinary <=16-bpp path without that flag it calls `0x69DC20`.
For the startup path with `0x40` it calls `0x69DCC0`.

The distinction is exact:

- `0x69DC20` advances the destination by `0x20` bytes for every 16 coded
  horizontal samples, which is 16 x 2-byte display pixels.
- `0x69DCC0` advances by `0x40` bytes for the same 16 coded samples, which
  is 32 x 2-byte display pixels.

So the startup path emits two 16-bit display pixels per coded horizontal
sample.

## 5. Those two pixels are identical

The ordinary row packer `0x69F904` and doubled row packer `0x69F679` use the
same packed-color lookup tables.

- `0x69F904` stores lookup results as 16-bit WORD pixels.
- `0x69F679` stores them as 32-bit DWORD values.

Lookup-table builder `0x69C040` calls helper `0x69C1A0`. That helper places
each packed channel contribution both at its ordinary bit offset and at the
same offset +16. Its correction mask is likewise symmetric
`0x80008000`.

For the 16-bpp startup mode, the resulting table value is therefore:

```text
packed16 | (packed16 << 16)
```

Each DWORD store writes two adjacent identical 16-bit pixels. This is exact 2x
horizontal pixel repetition, not bilinear or other interpolated scaling.

## 6. YUY2-capable intermediate/fallback evidence

Video-output setup at `0x69DE00` explicitly requests FourCC
`0x32595559` (`YUY2`) using the coded 320x480 dimensions and includes a
`width * height * 2` fallback allocation.

That evidence describes an available packed intermediate/fallback boundary. It
does not override the separately recovered startup output writer or the active
game-display pixel format.

## 7. Final presentation is 1:1

The game-level callback at `0x461CD0` presents the completed 640x480 movie
surface with a same-size destination rectangle using DirectDraw
`DDBLT_WAIT`.

Recovered placement:

- 640x480 display mode: `(0,0)-(640,480)`
- ordinary 800x600 display mode: `(80,60)-(720,540)`

There is no final source/destination size mismatch and therefore no final
aspect-fit stretch.

## Modern Windows 11 contract

PR #487, merged as main commit
`421a3e1c34e007c1e9550aea892678fa95dde261`, applies the recovered contract:

1. exact TGQ identity remains fail-closed;
2. compatibility derivatives are 640x480;
3. FFmpeg conversion uses `scale=640:480:flags=neighbor`, matching the exact
   recovered horizontal duplicate treatment;
4. runtime receipts/cache identity include that presentation geometry;
5. WPF startup playback is attached as a child HWND of the game-owned
   fullscreen Tk host rather than a separate maximized top-level player;
6. the ordinary 800x600 logical movie rectangle remains centered at (80,60).

This is a repository-side candidate, not human-visible Windows acceptance.
Skip input, fade/transition semantics, and final Windows 11 visible/audible
acceptance remain open until separately verified.

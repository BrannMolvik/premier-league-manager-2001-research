# Startup FMV pixel pipeline

_Last verified: 6 October 2026_

## Scope

This note closes the previously unresolved geometry boundary between the
original FM2001 startup TGQs and the game-owned movie surface. It is based on
private disassembly of the authorized canonical executable:

`footballmanager.exe` / disc `FOOTBAL.EXE`

SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

No original executable or EA media bytes are stored in Git.

## Proven pipeline

The original startup path is now source-backed as:

```text
TGQ pIQT frame
320 x 480
    |
    | decoder/header geometry
    v
320 x 480 video intermediate
YUY2-capable / 2-byte-per-pixel fallback path
    |
    | DirectDraw Blt stretch
    | startup playback flag 0x40 doubles destination width only
    v
640 x 480 game-owned movie surface
    |
    | 1:1 DirectDraw Blt
    v
active game display
640 x 480 at (0,0) in mode 0
640 x 480 at (80,60) inside 800 x 600 in mode 1
```

The old interpretation that the 320 x 480 derivative should be shown with
aspect-preserving `Uniform` presentation is therefore incorrect.

## 1. TGQ dimensions remain 320 x 480 inside the decoder

The `pIQT` payload stores little-endian width 320 and height 480.

The video-header parser around `0x69CD10` copies those values into the movie
base object:

```text
base + 0x64 = width  = 320
base + 0x60 = height = 480
```

These fields remain the source-frame geometry used by the later blit path.

## 2. The wrapper deliberately supplies playback flag 0x40

The shared wrapper at `0x461E20` calls `0x461900` with literal `0x40` as
its second argument:

```text
0x461F2E  push 0x40
0x461F30  push path
0x461F31  call 0x461900
```

At `0x461A68` the lower player ORs that caller value with its fixed movie
configuration bits and stores the result in the decoder base object.

## 3. Flag 0x40 doubles destination width, not source width

Rectangle builder `0x69D5C0` starts from the parsed TGQ geometry:

```text
worker.width  = base.width
worker.height = base.height
```

It then tests the low byte of the movie flags:

```text
test flags, 0x40
if set:
    worker.width <<= 1

test flags, 0x30
if set:
    worker.height <<= 1
```

The startup wrapper supplies `0x40`, but not `0x30`. Therefore the normal
startup destination rectangle becomes exactly:

```text
x = 0
y = 0
width  = 640
height = 480
```

This is an explicit original-code instruction to double the movie horizontally.

## 4. Normal state-1 presentation performs the 320 -> 640 stretch

The normal worker state in `0x69BA40` constructs two rectangles.

Source rectangle:

```text
(0, 0) - (base.width, base.height)
= (0, 0) - (320, 480)
```

Destination rectangle:

```text
(worker.x, worker.y)
    -
(worker.x + worker.width, worker.y + worker.height)
= (0, 0) - (640, 480)
```

It then invokes the DirectDraw surface blit with the decoder/intermediate
surface as source and the configured output surface as destination. The blit
flags include `0x01000000` (the synchronous/wait-style path used throughout
this movie code).

Therefore the 2x horizontal expansion occurs at the DirectDraw blit boundary.
It is not a later 640 x 480 -> display stretch and it is not an inferred
modern aspect-ratio correction.

## 5. Intermediate video path is YUY2-capable

Video-output setup at `0x69DE00` explicitly pushes FourCC:

`0x32595559` = `YUY2`

using the parsed 320 x 480 width/height.

The same setup contains a fallback allocation sized:

```text
width * height * 2
```

and the state-2 fallback row writer copies `width * 2` bytes for each of
`height` rows.

This establishes a 16-bit packed 320 x 480 intermediate path. It does not mean
the final 640 x 480 movie surface is permanently fixed to YUY2.

## 6. Final movie surface follows the active DirectDraw display format

The game creates the 640 x 480 movie surface at `0x461A37` through
`0x6555D0` with the explicit BPP argument `-1`.

In `0x6555D0`, `-1` bypasses the helper's forced 8/16/32-bit pixel-format
descriptors. The surface therefore uses the active/default DirectDraw format.

The movie decoder subsequently queries the actual destination surface pixel
format around `0x69C640` and derives RGB mask widths/offsets from the returned
masks. It has an explicit 8-bit/paletted branch and otherwise adapts to the
queried RGB layout.

So there is no source basis for hard-coding one final FMV display BPP in the
modern port. The original movie path adapts to the game's active DirectDraw
surface format.

## 7. Final display blit remains 1:1

Separately, the game-level callback at `0x461CD0` presents the completed movie
surface with a fixed 640 x 480 source rectangle and a same-size destination
rectangle.

Recovered placement remains:

- 640 x 480 display mode: `(0,0)-(640,480)`
- 800 x 600 display mode: `(80,60)-(720,540)`

This confirms the second blit is not responsible for correcting the TGQ aspect
ratio. The correction has already occurred inside the movie decoder/output
path.

## Interpolation boundary

The executable proves that DirectDraw is asked to stretch 320 x 480 to
640 x 480. It does **not** encode a unique software resampling kernel in the
game code.

The exact filter may depend on the DirectDraw implementation/driver path.
Accordingly:

- 2x horizontal presentation is source-backed;
- 640 x 480 destination geometry is source-backed;
- nearest-neighbor, bilinear, bicubic, or another specific filtering claim is
  **not** source-backed and must not be presented as recovered original
  behavior.

A modern implementation may choose a deterministic filter for compatibility,
but that choice must be labelled as a port implementation decision rather than
an original-code fact.

## Consequence for the Windows 11 port

The current WPF backend's literal 320 x 480 `MediaElement.Stretch=Uniform`
presentation is not faithful.

The port should preserve the proven display contract:

1. derive media from the exact verified TGQ source;
2. present it with a 2:1 horizontal pixel/display treatment so the movie is
   640 x 480 in game coordinates;
3. place that 640 x 480 movie rectangle at the source-backed game-display
   location;
4. keep the presentation integrated with the game-owned startup surface rather
   than accepting a visually separate top-level player as final;
5. do not claim a source-backed interpolation method unless new evidence
   appears.

This closes the earlier 320 x 480 -> 640 x 480 geometry uncertainty. The
remaining startup presentation work is implementation/integration and external
Windows acceptance, not discovery of whether the original intentionally
doubled the TGQ width.

# Gate 13 startup FMV presentation source trace

_Last updated: 6 October 2026 KST._

## Result

The original startup TGQs are coded at **320x480**, but FM2001 does not aspect
fit or bilinearly stretch them. The canonical executable requests a special
TQI output path that performs **exact horizontal 2x pixel duplication** into a
**640x480, 16-bpp** movie surface. The final DirectDraw presentation blit is
1:1. In ordinary 800x600 mode the movie rectangle is
**(80,60)-(720,540)**.

Therefore the modern compatibility derivative may source-faithfully bake:

`scale=640:480:flags=neighbor`

There is no vertical scaling and no final aspect-fit interpolation.

## First-hand source evidence

Canonical executable SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

Canonical EA Sports startup TGQ SHA-256:

`73dc078ee8fe7e1d7412b4bcba072c3f8ec85546d5e5b94f90be9732498af97c`

The exact TGQ was re-extracted from ISO extent 156024 of the authorized
MODE1/2352 track. Its `pIQT` frame header contains width `0x0140` (320) and
height `0x01E0` (480). FFmpeg independently reads the coded stream as
320x480.

### Startup requests the double-width decoder path

The startup wrapper at `0x461E20` calls lower player `0x461900` with a
literal `0x40` flag at `0x461F2E..0x461F31`.

The `pIQT` handler state 4 at `0x69CEE0` stores the packet width and height
into the decoder owner. During output setup `0x69D5C0` copies the coded width
to the logical-width field and tests flag `0x40`. When set, it executes a
one-bit left shift on logical width. For a coded width of 320 this produces
640; height remains 480.

### The game movie surface is 640x480 at 16 bpp

`0x461900` creates the movie DirectDraw surface through `0x6555D0` with
640x480 dimensions and stores it at `0x876648`.

The game's ordinary graphics initialization uses 16 bits per pixel:
the recovered global bit depth is initialized to `0x10`, and the multimedia
decoder also queries the actual DirectDraw surface pixel format before choosing
its TQI writer.

### Flag 0x40 selects the doubled 16-bpp writer

At `0x69D289`, state-4 TQI output tests flag `0x40`.

- without the flag, the 16-bpp path calls ordinary writer `0x69DC20`;
- with the startup flag, it routes through alternate writer `0x69DCC0`.

The ordinary path advances 0x20 bytes for a 16-pixel horizontal macroblock:
16 x 2-byte pixels.

The startup/doubled path advances **0x40 bytes** for the same 16 coded
horizontal samples: **32 x 2-byte display pixels**.

### The two pixels are identical, not interpolated

The doubled per-row packer `0x69F679` reads the same color lookup tables as the
ordinary `0x69F904` packer. The difference is the store width:

- `0x69F904` stores `WORD` values at +0,+2,+4,...;
- `0x69F679` stores `DWORD` values at +0,+4,+8,...

The lookup-table initializer `0x69C040` calls packing helper `0x69C1A0`.
That helper builds each channel contribution twice: once at its normal 16-bit
bit position and once again at the same position **+16**. Its sign/high-bit
correction is likewise symmetric `0x80008000`.

Thus each lookup result is:

`packed16 | (packed16 << 16)`

The doubled writer therefore stores two adjacent, identical 16-bit pixels for
each coded horizontal sample. This proves nearest-neighbor horizontal
duplication rather than filtering/interpolation.

### Final presentation does not scale

Frame callback `0x461CD0` calls DirectDraw Surface::Blt using a full
640x480 source rectangle and a 640x480 destination rectangle with
`DDBLT_WAIT`. There is no source/destination size mismatch and therefore no
final DirectDraw stretch.

Mode getter `0x615600` yields:

- 640x480 mode: destination origin (0,0);
- ordinary 800x600 mode: destination origin (80,60).

The ordinary display rectangle is therefore exactly:

`(80,60)-(720,540)`

## Modern implementation boundary

The source-backed presentation contract is now represented by
`reconstruction/startup_fmv_presentation.py`.

For compatibility conversion:

1. verify exact original TGQ identity;
2. decode the coded 320x480 frame;
3. apply only horizontal 2x nearest-neighbor duplication to 640x480;
4. preserve 480 vertical lines unchanged;
5. encode the compatibility MP4 at 640x480;
6. validate that derivative geometry and frame/audio counts fail closed.

The remaining transport task is to make Windows playback occupy the
game-owned 640x480 rectangle rather than a separate maximized WPF top-level
window. Skip input and fade/transition semantics remain separate evidence
questions and are not inferred here.

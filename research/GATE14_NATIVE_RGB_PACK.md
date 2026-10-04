# Gate 14 native RGB8 to packed-16 conversion

_Status: independent Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Scope

The original FastView font blend operates on packed 16-bit destination pixels.
PR #348 deliberately left the actual mask values to a strict Windows runtime
receipt because the canonical executable queries its active DirectDraw surface
rather than hard-coding RGB565 or RGB555.

This checkpoint closes the other half of the input conversion: once a runtime
mask set is known, how the original game converts an 8-bit RGB source color into
that packed 16-bit layout.

## Source metadata builder

Runtime channel masks are retained through source helper `0x653120`.

For each mask it stores:

- the original mask at metadata offset `+0`;
- the number of trailing zero bits at `+4`;
- the 8-bit quantization shift at `+8`.

For one contiguous channel width `n <= 8`, that final shift is exactly
`8 - n`.

Examples:

| Mask | Channel bits | Placement shift | Quantization shift |
| --- | ---: | ---: | ---: |
| `0xF800` | 5 | 11 | 3 |
| `0x07E0` | 6 | 5 | 2 |
| `0x001F` | 5 | 0 | 3 |
| `0x7C00` | 5 | 10 | 3 |

These examples validate the generic source algorithm; they do **not** select
RGB565 or RGB555 for the target Windows runtime.

## One-channel pack

Source routine `0x443E00` takes one 8-bit channel and one retained metadata
record.

Its compiled operation is:

`packed = (value >> quantization_shift) << placement_shift`

The 8-bit value is truncated, not rounded.

For a 5-bit channel:

- 0..7 -> 0;
- 8..15 -> 1;
- ...
- 248..255 -> 31.

## Three-channel pack

Source routine `0x443E20` applies the retained blue metadata to its third
argument, green metadata to its second argument, and red metadata to its first
argument, then ORs the three packed values.

The recovered source contract is therefore:

`packed16 = pack(red8, red_mask) | pack(green8, green_mask) | pack(blue8, blue_mask)`

where every channel uses the same truncation/placement rule above.

## Reconstruction contract

`reconstruction/gate14_native_rgb_pack.py` provides:

- `Native16ChannelPacking`;
- `native_channel_packing(mask)`;
- `pack_native_channel8(value, packing)`;
- `pack_native_rgb16(red, green, blue, masks)`.

The implementation accepts only contiguous channels of at most eight bits.
It remains parameterized by `Native16PixelMasks` and therefore cannot silently
choose a runtime layout.

Synthetic regressions exercise both common 565 and 555-shaped mask sets only as
calibration examples and lock the exact truncation behavior.

## Fidelity boundary

This checkpoint closes:

- source mask -> placement/quantization metadata;
- RGB8 -> packed-16 conversion.

It does **not** close:

- the actual target-Windows runtime mask values;
- packed-16 -> modern RGBA display expansion;
- final cross-component overlap pixels;
- complete FastView frame;
- Gate 14.

The runtime mask values remain an explicit private Windows receipt requirement
under `GATE14_WINDOWS_PIXEL_FORMAT_RECEIPT.md`.

The next static source task is to look for an original packed-16 readback or
surface-to-RGB conversion path that defines the display-side expansion. If no
software expansion exists because DirectDraw/display hardware owns that step,
record that exact boundary and use a Windows graphical receipt rather than
inventing a software inverse.

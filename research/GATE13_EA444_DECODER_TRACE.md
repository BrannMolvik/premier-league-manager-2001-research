# Gate 13: original EAUK `.444` compressed graphics decoder trace

_30 September 2026. Direct disassembly of the actual authorized `footballmanager.exe` whose SHA-256 matches `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`; original on-disc graphic bytes independently verified. This trace does **not** claim that final pixels have been decoded or visually validated._

## Actual source header and census

All **1,354** source-disc `.444` files use an 8-byte header:

- +0/+2: little-endian uint16 image width/height.
- +4..+7: bytes `64 FF 00 FF` on all original images. The original executable references +5/+6/+7 for destination RGB-component packing, while +4's high and low bits control conditional decoder/output branches. Do not assume every byte is a color key.
- +8: dword-aligned compressed payload. The full original Joliet catalog confirms **1,354 / 1,354** image payload lengths satisfy `(file_size-8) % 4 == 0`.

Representative exact source geometries, verified from actual extracted file bytes: `Generic/bground.444` 800×600; `main_menu/main_menu_bground.444` 532×532; `team_choice/background.444` 800×558; `choice_start_anim.444` **150×736**. The earlier inventory note's 150×224 value was a transcription error and has been corrected.

Two independently SHA-256-verified original decoder fixtures are imported, including **byte-for-byte identical 12-byte compressed payloads** despite opposite geometry:

- `GenericButtonsAndBars/hscroll_end.444`: 1×18, 20 total bytes.
- `GenericButtonsAndBars/vscroll_end.444`: 18×1, 20 total bytes.
- Common payload: `08 20 80 00 10 40 00 01 20 80 00 02`.

Their equal 8×8-padded cell counts (**three cells** in both orientations) make these useful differential tests but not proof of how their final pixels look.

## Recovered bit ordering and executable decoder boundary

The actual Loader444 entry at `0x68598A` invokes `0x6864A0` to prepare quantization/display tables, then the screen-format-specific `0x6868E0` image conversion. That conversion:

- uses `0x7B9000` to initialize a compressed-bitstream pointer at source +8;
- rounds width and height up to multiples of eight;
- for 16-bit output calls `0x7B95D0` per 8×8 tile, with a separate `0x7BB960` branch for an alternative output format;
- preserves the previously proved **259 + 1 = 260** raw CRT RNG startup consumption: 259 on first quant/dither table creation and one per first image conversion.

Both original tile routines access native **little-endian dwords**, reading the **most-significant bit first** within each dword:

```asm
EDX = EDI >> 5                    ; source dword index
EAX = [bitstream + EDX*4]
EDX = [bitstream + EDX*4 + 4]
SHLD EAX, EDX, CL                 ; CL = bit position low 5 bits
SHR  EAX, 24                      ; initial 8-bit scale/DC symbol
EDI += 8
CALL 0x7B9040
```

The source's 12-byte differential payload above therefore yields sequential 8-bit reads `00 80 20 08 01 00 40 10 02 00 80 20`, **not** its physical byte order. `reconstruction/ea444_bits.py` implements this exact bit order with bounds checks. Four local tests passed, including original-byte fixtures, bit reads crossing word boundaries, and all 1,354 private-catalog alignment checks (the latter optional and skipped on standard CI).

## Exact original Huffman and coefficient permutation tables recovered

The canonical executable has a **raw, initialized, named `TQIA_DAT` section** at virtual address `0xADB000` (file raw offset `0x475000`, length `0x420`). This is critical: the decoder tables are original preinitialized source bytes, *not* uninitialized globals or tables to guess from generic EA video formats.

- `0xADB0A0` through `0xADB19F`: 64 `uint32le` source-specific coefficient permutation entries, proven to be exactly a permutation of `0..63`. The first four are `0,63,55,62`, last four `9,2,1,8`.
- `0xADB1A0` through `0xADB41F`: **160 packed Huffman entries**, including 113 unique values, indexed by the actual tiered decoder at `0x7B91E3..0x7B92C7`. Each `uint32` packs low byte amplitude, next byte run/control code, high word bit length. All code lengths in the original data lie in `2..16`. There are four lookup slots each for `0x41` (end-of-block) and `0x42` (escape) control codes.
- SHA-256 of the canonical original `0x420`-byte `TQIA_DAT` section:
  `c62a13efbb812fb2157c067aaa3eae8afbbb52283dc5dc3eaf6cb86c5a11e8da`.
- A lookup prefix below `0x20` branches immediately to end-of-block without reading a table entry; larger 17-bit prefixes select one of eight documented lookup-address tiers.

`reconstruction/ea444_tables.py` locates the **exact canonical PE32 `TQIA_DAT` section**, verifies the complete executable SHA before trusting its table, requires the expected virtual address and byte extent, recovers both original tables, and reproduces all eight lookup tiers. The licensed executable is **not** added to Git. Three local tests passed, including a private-source opt-in test of **all applicable 17-bit prefixes**; the private-source test skips without `FM2001_ORIGINAL_EXE` in standard CI.

### First actual compressed-symbol observation

The first 8-bit symbol of the actual original `hscroll_end.444` image is `0` under the executable's dword/MSB ordering. The next 17-bit prefix is `0x10040`; the tiered lookup selects `TQIA_DAT` entry `0xADB1B0`, whose packed `uint32` is `0x00024100`, i.e. a **2-bit end-of-block symbol**. This is a directly reproducible original-data trace of the first coefficient block, not a guessed decoded pixel color.

## Verified partial sparse coefficients and original quantization

The canonical original `0x7B9040` writes the leading eight-bit
scale/DC code into coefficient grid element 0, multiplied (signed low DWORD)
by quantization table element 0, and zeroes the other 63 grid slots.
The decoder `0x7B91C7..0x7B9354` then parses the original Huffman
run-length, signed amplitude and 14-bit escape codes, remaps decoded
positions through the original coefficient permutation at `0xADB0A0`,
and multiplies each AC amplitude by the corresponding original
`0x9FBD80` quantization value before storing it into its 8×8 grid.

Source-backed `reconstruction/ea444_coefficients.py` has regression
coverage for signed and extended escape codes and end markers. All
**17** independently hashed first-slice `.444` assets successfully
yielded their first sparse coefficient blocks. The actual original
`Generic/main_menu/main_menu_bground.444` first component has eight-bit
scale code **15**, **14 nonzero AC entries** and consumed exactly
**93 compressed bits**; its signed sparse coefficient data and end
marker are test-asserted in `test_ea444_coefficients.py`.

### Exact `0x7DABF0` quantization matrix

The actual canonical executable's `.rdata` stores **64 little-endian
signed 32-bit values at VA `0x7DABF0` (raw file offset `0x3DABF0`)**.
The original image initialization loop
`0x6864CF..0x6864FE` converts each source entry to live quantization
`0x9FBD80`, using:

```asm
MOV EAX, [0x7DABF0 + i*4]
MOV EDX, 0x80000
IMUL EDX
SHL EDX, 16
SHR EAX, 16
ADC EAX, EDX
MOV [0x9FBD80 + i*4], EAX
```

The shift-out carry from `SHR` is explicitly reproduced. All 64
**actual source values are positive integers**, making the resulting
16.16 fixed-point coefficient simply `source_value * 8`; signed
32-bit arithmetic and wrap are retained in the reconstructed helper
for exact x86 behavior.

- Directly SHA-256-verified original 256-byte source matrix:
  `6fb2af66cb6a51e4b3fa7da9bacab417fa40f180aa0c18c85adb2550c04c89eb`.
- First eight original values:
  `8192, 5906, 6270, 6967, 8192, 10426, 15137, 29692`.
- First eight live values:
  `65536, 47248, 50160, 55736, 65536, 83408, 121096, 237536`.
- Across all 64 original values: minimum fixed-point scale
  **34064**, maximum **860952**.
- A direct real-main-menu first component transforms DC
  `15 × 65536 = 983040`. The first original signed AC
  values become `(position, signed fixed-point)`:
  `(8,47248), (1,47248), (9,34064), (3,55736), (18,-76784)`.
- The full 64-position quantized first-component grid has **15**
  nonzero values, with SHA-256 of packed little-endian 64×signed-int32:
  `d074fa03f380438bfccbdf88dc2375f700434891889399e4750fc7bc2c75c2d7`.

`reconstruction/ea444_quantization.py` reads the original table from
the exact checked executable SHA, original `.rdata` section and
expected source matrix SHA. `reconstruction/ea444_quantized_block.py`
joins it to the source-backed entropy output while refusing duplicate
or out-of-range grid assignments. Their synthetic and opt-in actual-source
regressions are in the corresponding `test_ea444_*.py` files.
A local first-hand verification used the real original executable and
the real 532×532 source image, not generic/JPEG quantization tables.

### Original two-pass inverse transform boundary

Direct disassembly now also bounds the next transformation:

- `0x7B95D0` (the 16-bit output tile path) calls `0x7B9040`
  for three component blocks in sequence before its conditional
  channel handling.
- Each coefficient block undergoes **eight consecutive
  `0x7B9360` column-like 1D passes**, over eight-element source
  arrays with source stride 32 bytes, into a scratch buffer with
  **36-byte destination row stride**.
- It then performs **eight `0x7B94C0` row-like 1D passes**
  across that scratch buffer, writing contiguous eight-value groups
  to another intermediate component buffer.
- The `0x7B9360` routine has an explicitly verified
  all-seven-AC-zero shortcut at `0x7B948E`: it writes the
  identical DC input to eight output positions at 0x24-byte
  offsets. The general path uses original x87 coefficients
  in the initialized `TQIA_DAT` section.
- The original pixel conversion/packing after the 2D transform and
  conditional fourth component are **not yet reconstructed**;
  intermediate fixed-point numbers must not be misrepresented
  as final pixel values.

## Key remaining decoding tasks

1. Transcribe the complete signed amplitude, run-skip, and escape control flow at `0x7B91C7..0x7B9354`, applying recovered per-component quantization coefficients from original source constants at `0x7DABF0`.
2. Determine precise per-tile component-block ordering and conditional fourth channel from `0x7B95D0` and `0x7BB960`. **Do not assume** a generic 16×16/YUV420 EA TQI frame layout; the actual .444 conversion calls are 8×8 tiles and different output paths.
3. Reproduce the original inverse-transform routines `0x7B9360` and `0x7B94C0`, channel packing at `0x6868E0`, clipping, transparency and dither semantics.
4. Validate fully decoded first-slice original backgrounds and animations against bounded screenshots, then import only original verified assets / faithful converted derivatives and connect to `front_end_session.py`. No speculative UI redesign.

**Important fidelity boundary:** Attempts to wrap these `.444` bytes as EA TGQ and decode them with FFmpeg's general EA TQI video decoder produced invalid/corrupted images, so they are *not* valid original-asset conversions. The original per-tile decoder should be reconstructed from the verified executable rather than promoting those speculative images.

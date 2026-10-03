# Gate 14 FastView chrome source trace

_Date: 3 October 2026 KST. Recovery 204. Evidence tier: canonical executable plus first-hand authorized source-disc bytes._

## Scope

This trace source-closes the two directly bound static FastView chrome images
that are constructed as `PictureControl` children of the live FastViewPanel:
`top_bar.444` and `ticker.444`.

It deliberately excludes the loose 800x600 `background.444` path rejected by
Recovery 202/203. Filename or dimensions alone do not establish live ownership.

## Exact source assets

| Resource | Literal VA | Bytes | Dimensions | SHA-256 | Exact screen rect | PictureControl call |
| --- | ---: | ---: | ---: | --- | --- | ---: |
| `FM2001_Art/FastView/top_bar.444` | `0x829734` | 19,268 | 800x95 | `f7410cf85900846ee1b276fa309bca4e560580286d5641092f2f98d20afa379a` | `(0,0)-(800,95)` | `0x51FDA3 -> 0x527730` |
| `FM2001_Art/FastView/ticker.444` | `0x829714` | 6,352 | 800x33 | `b0fe2d8266ae157b7821e8c1de310e89bbc37ae859f666e64f59731c78e68257` | `(0,557)-(800,590)` | `0x51FE31 -> 0x527730` |

Both files were re-extracted from the authorized MODE1/2352 source image and
their EA444 headers independently reproduce the dimensions above.

## Direct live ownership

FastViewPanel construction uses the exact source paths at the same callsites
that build the controls:

- top bar string setup at `0x51FD63`, rectangle fields
  `0,0,0x320,0x5F`, then constructor call `0x51FDA3`;
- ticker string setup at `0x51FDF0`, rectangle fields
  `0,0x22D,0x320,0x24E`, then constructor call `0x51FE31`.

Both calls target generic constructor `0x527730`, which installs vtable
`0x7CAA5C`. Canonical x86 MSVC RTTI resolves that vtable to
`.?AVPictureControl@@`.

This establishes direct FastViewPanel child ownership and exact source geometry.
It is materially stronger than the rejected loose `background.444` path,
whose static string has no live draw consumer.

## Reconstruction boundary

`reconstruction/gate14_fastview_chrome.py` records the exact identities,
addresses, dimensions, rectangles and hashes. Its staged-byte validator will
accept only exact byte-identical originals.

`reconstruction/original_fastview_chrome_art.py` provides an exact decoded
placement seam for these two resources only. It explicitly keeps
`complete_fastview_frame_available=False` and retains the rejected loose
background path as a fail-closed boundary.

The current ChatGPT/GitHub connector exposes base64 Git blob creation but has no
direct container-file-to-blob handoff. The recovered source bytes are therefore
not yet committed in this checkpoint; manually transcribing binary base64 would
create unnecessary corruption risk. This is an import-transport boundary, not
an evidence or decoding gap. The exact local/source identities above make a
later byte-identical import deterministic.

## Remaining FastView presentation work

- deliberately import these two exact files when a binary-safe repository
  transport is available, then enable repository-byte validation;
- continue source-closing the next directly owned FastView controls rather than
  filling unrecovered 800x600 pixels;
- keep audio/commentary and 3D choreography as separate Gate-14 workstreams;
- do not declare Gate 14 complete from this bounded chrome slice.

Gate 13 remains the earliest incomplete validation gate pending its external
schema-8 Windows receipt.

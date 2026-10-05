# Gate 14 FastView ScoreCompositeMain source boundary

_Status: source-backed Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Result

The outer FastViewPanel trace proves one visible `ScoreCompositeMain` instance
between GoalFlash and the two top-corner surfaced pictures. This checkpoint
turns that already-canonical evidence into a dedicated fail-closed source
contract without assigning geometry or text semantics that have not been
recovered.

Exactly one of three owner branches constructs the object:

| Owner call | Constructor |
| ---: | ---: |
| `0x520356` | `0x51B400` |
| `0x520416` | `0x51B330` |
| `0x5204D6` | `0x51B330` |

Both concrete constructors flow through shared
`ScoreComposite::0x51A730`.

The base builder appends exactly five controls directly to the outer
FastViewPanel draw array:

1. PictureControl at `0x51A825`;
2. TextControl at `0x51A8C1`;
3. TextControl at `0x51A93C`;
4. TextControl at `0x51A9D2`;
5. TextControl at `0x51AA83`.

Those controls occupy zero-based outer draw ranks **16..20**. They follow the
last GoalFlash control at rank 15 and precede the first top-corner
SurfacedPictureControl at rank 21.

## Important class boundary

These five outer `ScoreCompositeMain` controls are not interchangeable with
the already reconstructed `ScoreCompositeNormal` rows inside
FastViewLeagueScores.

`ScoreCompositeNormal` is constructed by `0x51B740` and already has its
own source-backed grid-2/local-row geometry and phase-event lifecycle. The
outer main composite instead comes from `0x51B400/0x51B330`. Reusing the
nested LeagueScores geometry for this outer family would therefore be an
unsupported inference.

## Fail-closed boundary

Promoted:

- one visible outer ScoreCompositeMain instance;
- the three exact owner callsites;
- the two exact concrete constructors;
- shared base constructor `0x51A730`;
- exact one-PictureControl/four-TextControl registration order;
- exact outer draw ranks and surrounding family order.

Still false:

- meaning of the branch selector;
- branch-specific control rectangles;
- visible text/content semantics;
- the PictureControl resource identity;
- final screen position/geometry;
- pixel rasterization;
- complete FastView frame;
- Gate 14 completion.

The private canonical executable process path remains unavailable in this
session because trivial shell/Python execution returns
`caas.internal.errors.ClientError`. No missing branch geometry or semantics
are inferred from the nested score tables while that source path is blocked.

## Readiness consequence

`gate14_readiness.py` now distinguishes:

- `scorecomposite_main_source_contract_recovered = true`;
- `scorecomposite_main_geometry_recovered = false`;
- `scorecomposite_main_pixels_rasterized = false`.

A complete FastView frame cannot be promoted until the omitted visible family
has exact source geometry and source-backed pixels.

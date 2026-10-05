# Gate 14 FastView embedded outer-control source boundary

_Status: source-backed Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Result

The exhaustive outer FastViewPanel trace proves four visible embedded controls
that are not represented by any current raster plane. This checkpoint records
their existing source topology without assigning UI meaning or borrowing pixels
from unrelated Button/control families.

Two controls are appended immediately before GoalFlash:

| Identity | Parent offset | Outer rank | Append call | Later setup call | Constructor target |
| --- | ---: | ---: | ---: | ---: | ---: |
| `embedded_button_0` | `+0x388` | 4 | `0x51FFE5` | `0x520061` | `0x652FD0` |
| `embedded_button_1` | `+0x3D4` | 5 | `0x52000B` | `0x52009F` | `0x652FD0` |

Two more controls are appended after the FastViewTeam wrapper by the exact
two-iteration loop at `0x520F8B`:

| Identity | Parent offset | Outer rank | Append loop | Constructor path |
| --- | ---: | ---: | ---: | ---: |
| `post_team_control_0` | `+0x424` | 34 | `0x520F8B` | `0x652C50` |
| `post_team_control_1` | `+0x478` | 35 | `0x520F8B` | `0x652C50` |

The second pair follows the canonical `+0x424` base, `0x54` stride and
count two. Their ranks come from the already exhaustive 36-entry outer draw
array, not from a guessed presentation order.

## Existing raster boundary

The current `direct_chrome` raster owns only the source-bound
`FastView/top_bar.444` and `FastView/ticker.444` PictureControls. These four
embedded controls are separate outer registrations and are not included in
that plane or another current FastView component plane.

The constructor paths alone do not prove that these objects share a resource,
rectangle, state model, or user-visible role with another reconstructed
control family. No such substitution is made.

## Fail-closed boundary

Promoted:

- exactly four omitted visible outer embedded controls;
- exact parent offsets;
- exact pre-GoalFlash append/setup paths;
- exact post-team two-entry loop, stride and constructor path;
- exact outer draw ranks 4, 5, 34 and 35.

Still false:

- user-visible role/semantics;
- control rectangles or absolute geometry;
- resource identities;
- state/interaction behavior;
- pixel rasterization;
- complete FastView frame;
- Gate 14 completion.

The private canonical-executable process path remains unavailable in this
session, so the missing geometry/content cannot be source-qualified here.
Keeping these controls explicit prevents a partial raster set from being
mistaken for a complete original frame.

## Readiness consequence

`gate14_readiness.py` now distinguishes:

- `embedded_outer_controls_source_contract_recovered = true`;
- `embedded_outer_controls_geometry_recovered = false`;
- `embedded_outer_controls_pixels_rasterized = false`.

A complete FastView frame cannot be promoted until these already-proven visible
outer controls have their own source-qualified geometry and pixels.

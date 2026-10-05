# Gate 14 FastView SurfacedPictureControls

_Status: independent source-backed Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Result

The three outer `SurfacedPictureControl@FastViewPanel` registrations are now
source-closed by semantic owner instead of being treated as anonymous surfaces.

| Outer control | Rectangle | Source meaning |
| --- | --- | --- |
| `0x51FD31 -> 0x526940` | `(0,0)-(800,600)` | match-club background surface |
| `0x520642 -> 0x526940` | `(38,1)-(173,94)` | home-club badge |
| `0x520697 -> 0x526940` | `(627,1)-(762,94)` | away-club badge |

The left/right badge semantics are proven from Match/fixture constructor
dataflow, not inferred from screen position.

## Home/away proof

Fixed League builder `0x6173D0` reads a DBRRealFixture record:

- `+0x0C` = shipped home club;
- `+0x10` = shipped away club.

It resolves those DBTClubs records and calls LeagueMatch constructor
`0x5104F0`. Base Match constructor `0x5103D0` stores constructor argument 2
as its first side object at `+0x14` and argument 3 as its second side object
at `+0x28`.

FastView setup `0x51FA70` later calls those exact two side accessors. The
resource passed to the control at `0x520642` comes from Match `+0x14`;
the resource at `0x520697` comes from Match `+0x28`.

Therefore:

- `(38,1)-(173,94)` = home badge;
- `(627,1)-(762,94)` = away badge.

## Badge resource ownership

Both badges use club-art selector `0x40C850` with exact source family:

`FM2001_Art\Generic\Team_badge_stills`

and exact requested variant:

`badge_2`

The fallback is exact:

`fm2001_art\generic\team_badge_stills\generic.444`

The selector resolves the club country through global table `0x874BFC`,
then reads:

- club graphics basename through `0x40DA90`, DBRClub `+0xE0`;
- country graphics directory through `0x411610`, DBRCountry `+0x34`.

Those two clean-room data fields already exist in `fm2001_data.py` as
`Club.graphics_basename` and `CountryDefinition.graphics_directory`.

The authorized source-disc catalog independently corroborates the resulting
grammar with real resources such as:

`FM2001_Art/Generic/Team_badge_stills/England/arsenal_badge_2.444`

The same structure exists across the other shipped countries and clubs. This
is a data-driven original-resource path, not a hardcoded Premier League list.

## Full 800x600 surface

The full-surface control is **not** the previously rejected loose
`FastView/background.444` guess.

FastView setup calls Match helper `0x514220`, resolves the returned club id
through DBTClubs `0x874B9C`, and passes that club to
`ClubBackgroundSurface::0x5D3490`. The resulting surface is retained at
FastViewPanel `+0x84`; `0x5D3510` exposes its nested surface pointer and
`0x51FD31` gives that exact surface to the 800x600 SurfacedPictureControl.

The background factory uses exact family:

`FM2001_Art\Generic\Team_backgrounds`

with original generic fallback:

`fm2001_art\generic\Team_backgrounds\generic.444`

The source disc contains club-specific families such as
`England/arsenal_background0.444` through `background3.444`.

## Dynamic club-background selector

Fresh disassembly of the canonical executable SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
closes the remaining `ClubBackgroundSurface::0x5D3490/0x5D3560` selector.

`0x5D3490` reads the global game-date serial at `0x9847FC` and passes it
through date splitter `0x64CCD0`. That helper emits a 1-based month in its
second dword. The month is then used directly as the index into literal table
`0x83339C`.

The exact month -> background variant mapping is:

| Month | Variant |
| --- | ---: |
| January | 2 |
| February | 2 |
| March | 3 |
| April | 3 |
| May | 0 |
| June | 0 |
| July | 0 |
| August | 0 |
| September | 1 |
| October | 1 |
| November | 1 |
| December | 2 |

The current FastView owner passes background-client index **1**. The two
client-cache records begin at `0x87AC68`, stride `0x0C`, so FastView uses
the second record at `0x87AC74`. Each client record is keyed by exact club
identity plus the month-derived background variant.

Changed keys release the previous shared resource reference and acquire through
the shared cache at `0x87AC30`. That shared cache has exactly **two** slots,
each **0x18** bytes. `0x5D3560` reuses a matching active
`(club, variant)` slot and increments its reference count; otherwise it
allocates the first free slot.

The source resource attempt order is also exact:

1. club-specific `<club>_backgroundN.444`;
2. club-specific unsuffixed `<club>_background.444`;
3. generic `genericTier_backgroundN.444`.

The generic tier comes from signed raw `DBRClub+0x70` without assigning that
field a speculative higher-level label:

- raw value > 20 -> tier 0;
- raw value 9..20 -> tier 1;
- raw value <= 8 -> tier 2.

The authorized Joliet disc tree independently contains all twelve expected
generic seasonal files:
`generic0_background0..3.444`,
`generic1_background0..3.444`, and
`generic2_background0..3.444`, as well as club-specific seasonal families
such as `England/arsenal_background0..3.444`.

The full-surface club selector is also bounded more precisely. Match helper
`0x514220` returns Match `+0x48` when that explicit club override is not
`-1`; otherwise it falls back through Match side `+0x14`, already proven
to be the home side. The background is therefore **override-or-home**, not an
unconditional home-club guess.

## Fidelity boundary

This checkpoint closes:

- all three surfaced-control rectangles and owner callsites;
- full-surface match-club-background ownership;
- override-or-home background-club selection;
- exact month-derived `background0..3` selection;
- two-level client/shared cache identity, capacity and reference reuse;
- exact club-specific and generic fallback order;
- home/away badge orientation;
- badge family, exact `badge_2` variant and generic fallback;
- the DBRClub/DBRCountry fields that drive club-art paths.

It deliberately keeps false:

- repository staging/decoding of the surfaced background/badge source bytes;
- integration of these surfaced pixels into the FastView component raster set;
- complete FastView frame;
- Gate 14 completion.

## Next step

Bind the source-closed selector to reconstructed match state and a verified
original-game source root, decode the selected background plus home/away badge
EA444 resources, then lift those exact pixels into the component/overlap model.
Do not bulk-stage every club resource or choose a background independently of
the source month/club rules.

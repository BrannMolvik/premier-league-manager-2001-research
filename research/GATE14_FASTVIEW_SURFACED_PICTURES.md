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

## Fidelity boundary

This checkpoint closes:

- all three surfaced-control rectangles and owner callsites;
- full-surface match-club-background ownership;
- home/away badge orientation;
- badge family, exact `badge_2` variant and generic fallback;
- the DBRClub/DBRCountry fields that drive club-art paths.

It deliberately keeps false:

- the exact dynamic `Team_backgrounds` background index selected for one
  FastView instance;
- repository staging/decoding of badge/background source bytes;
- complete FastView frame;
- Gate 14 completion.

## Next step

Source-close `ClubBackgroundSurface::0x5D3490/0x5D3560` background-index/cache
selection. In parallel, the badge path is already sufficiently closed to stage
and decode the exact source badges once a concrete match pair is supplied by
the reconstructed match presentation state.

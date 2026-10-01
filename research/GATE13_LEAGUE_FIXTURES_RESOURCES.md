# Gate 13 PLeagueFixtures original resource trace

_Date: 2 October 2026 KST_

This checkpoint continues from the source-proven PMenu ID `0x25C` ->
`PLeagueFixtures` identity in
`research/GATE13_CALENDAR_FIXTURES_NAVIGATION.md`.

Canonical executable SHA-256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

All six selected source files were re-read from the authorized raw disc outside
Git. No original graphic bytes are committed by this checkpoint.

## Exact original resource loader chain

The executable retains six exact League Fixtures paths. Static initialization
passes each path to `0x64D750`, then wraps the raw resource through
`0x64E500`.

| Resource | Literal VA | Load init | Raw handle | Wrapper init | Wrapper | Original geometry | SHA-256 |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `date_fixtures_box.444` | `0x836D30` | `0x5F80E0` | `0x944B50` | `0x5F8130` | `0x944B30` | 24x13 | `b02036ae2d37c893e74a60a53eb1cdb514585654773916978e88f11ef66ab142` |
| `played_fixtures_box.444` | `0x836D6C` | `0x5F8170` | `0x944B10` | `0x5F81C0` | `0x944AF0` | 24x13 | `8c61143070c399477af735683b9e8a7effdfffee25b27d397f321cfe3a7d0db4` |
| `red_fixtures_box.444` | `0x836DA8` | `0x5F8200` | `0x944AD0` | `0x5F8250` | `0x944AB0` | 24x13 | `0acd8300cd9bbb129924270f354e0a7017d3f78729be4ad5311895f9f5064c2e` |
| `toggled_fixtures_box.444` | `0x836DE0` | `0x5F8290` | `0x944A90` | `0x5F82E0` | `0x944A70` | 24x13 | `d99af52f7c4f20c88bc93f24ac2447febf2250da161a639070af840721c2539e` |
| `fixtures_hori_grid.444` | `0x836E1C` | `0x5F8320` | `0x944A50` | `0x5F8370` | `0x944A30` | 132x52 | `37e94e0eb2420aa498ca98d560ab180f80d1b8b7ffc6d4e8c664c398f7ebf8db` |
| `fixtures_vert_grid.444` | `0x836E58` | `0x5F83B0` | `0x944A10` | `0x5F8400` | `0x9449F0` | 24x528 | `726bbb5df0fb632592a5e9f902fff7ca109b55e07ab433776e8f6973476f0ecb` |

Exact paths:

```text
FM2001_Art/Generic/league_fixtures/date_fixtures_box.444
FM2001_Art/Generic/league_fixtures/played_fixtures_box.444
FM2001_Art/Generic/league_fixtures/red_fixtures_box.444
FM2001_Art/Generic/league_fixtures/toggled_fixtures_box.444
FM2001_Art/Generic/league_fixtures/fixtures_hori_grid.444
FM2001_Art/Generic/league_fixtures/fixtures_vert_grid.444
```

All six private source files matched their recorded byte sizes, SHA-256 values,
EA444 dimensions and original `64 ff 00 ff` descriptor.

## PLeagueFixtures ownership

The concrete panel vtable is `0x7C24B8`. Its primary setup method is
`0x46AA70`.

That setup directly supplies:

- wrapper `0x9449F0` (`fixtures_vert_grid.444`) to bitmap setup helper
  `0x5D5280` twelve times;
- wrapper `0x944A30` (`fixtures_hori_grid.444`) to the same helper
  twenty-four times.

The four 24x13 fixture-box wrappers are referenced by screen-specific
`PLeagueFixtures` methods in the contiguous class implementation around
`0x46CA40..0x46D25B`, including wrapper selection among
`0x944B30/0x944AF0/0x944AB0/0x944A70`.

That establishes panel ownership. The original filenames are retained as
resource identities, but the runtime branches selecting those four boxes are
not yet renamed as result/date/selection states without a complete data-flow
trace.

## Exact grid placements

The first two positional arguments passed to `0x5D5280` are consistent
screen-space x/y origins across the setup.

### Vertical grid

Twelve controls use `fixtures_vert_grid.444`:

```text
(x, y) = (378 + 29*n, 98), n = 0..11
```

Exact x origins:

```text
378, 407, 436, 465, 494, 523, 552, 581, 610, 639, 668, 697
```

### Horizontal grid

Twenty-four controls use `fixtures_hori_grid.444`:

```text
(x, y) = (241, 235 + 14*n), n = 0..23
```

This ends at y=557.

The helper/resource dimensions overlap these placement steps; this checkpoint
records the source calls rather than assuming one resource image equals one
logical table cell.

## Reconstruction consequence

`reconstruction/original_league_fixtures_resources.py` now guards the six
exact resources, their static loader/wrapper addresses and the two repeated grid
placement sequences.

Still open:

1. exact mapping from runtime fixture/date/result state to the four 24x13 box
   wrappers;
2. the text/control objects surrounding the 12x24 grid;
3. fixture row ordering and filtering inside the panel;
4. date and result string bindings;
5. navigation/events from the grid to match/result detail;
6. intentional provenance import of these six source graphics;
7. real Windows integrated presentation verification.

No completion claim for the full Fixtures/results screen is made here.

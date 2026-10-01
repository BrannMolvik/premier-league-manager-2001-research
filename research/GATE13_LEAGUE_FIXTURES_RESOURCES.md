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


## Recovery 151 fixture-box state and visible text closure

The four 24x13 fixture boxes are no longer only ownership-proven. The bounded
row/update methods at `0x46CA40..0x46D2F9` establish their selection rules.

### Fixture completion/status bit

A runtime fixture initializes `+0x44` to zero in its constructor near
`0x5104CF`.

Routine `0x511370` begins by OR-ing bit 0 into fixture `+0x44` before the
post-match processing it performs. The League Fixtures row/update paths test
that same bit at `0x46CA9E`, `0x46CFDD` and `0x46D195`.

For a populated fixture:

```text
fixture +0x44 bit 0 clear -> date_fixtures_box.444
fixture +0x44 bit 0 set   -> played_fixtures_box.444
```

The UI branch therefore agrees with the original filename without relying on
the filename alone: bit 0 is the source completion/status boundary that switches
the cell from scheduled-date presentation to completed-score presentation.

### Completed score text

When bit 0 is set, the row helper calls:

- `0x513E70` -> signed word at fixture `+0x3C`;
- `0x513E80` -> signed word at fixture `+0x3E`.

It then formats those values using exact executable string
`0x81C504 = "%i:%i"`.

The broader fixture implementation independently proves those words are the
match score fields: `0x5112A0` copies MatchCalculator side-indexed score
fields `+0xD4C/+0xD50` directly into fixture `+0x3C/+0x3E`.

The visible completed-fixture text is therefore source-exact:

```text
left_score:right_score
```

No extra-time/penalty suffix is inferred by this checkpoint.

### Scheduled date text

When bit 0 is clear, the same row helper:

1. calls fixture accessor `0x510A20`;
2. feeds the returned date value through date decomposition helper
   `0x64CCD0`;
3. formats the resulting day and month through executable string
   `0x81C4F8 = "%02i.%02i"`.

The visible scheduled-fixture text is therefore exact `DD.MM`.

### Selected-cell overlay

`PLeagueFixtures` keeps two selected-index fields at:

- previous/alternate selected index: `+0x109B0`;
- current selected index: `+0x109B4`.

The refresh path at `0x46D09B..0x46D127` applies wrapper
`0x944A70` (`toggled_fixtures_box.444`) across all 24 cell entries belonging
to the selected index at `+0x109B4`.

The transition path at `0x46D140..0x46D2F9` first restores the previous
index's base cells (played/date/red as appropriate), stores the new selected
index into `+0x109B0`, then applies the toggled wrapper across all 24 cells of
that new index.

Accordingly, **toggled_fixtures_box is source-proven as the selected-cell
overlay** and has precedence over the base box state while that index is
selected.

### Empty-slot red predicate remains neutral

When no fixture pointer exists, the row helper at `0x46CA6B..` chooses between
`red_fixtures_box.444` and `date_fixtures_box.444` from a separate boolean
argument.

The larger refresh loops derive the equivalent decision by comparing
panel-owned table identities at offsets under the object referenced by
`PLeagueFixtures+0x2C`.

That predicate's higher-level football meaning is not yet sufficiently bounded.
The clean-room code names it only `empty_slot_red_predicate` and refuses to
call it unavailable, postponed, current-date, home/away, or another semantic
label without further source evidence.

## Updated reconstruction consequence

`reconstruction/original_league_fixtures_resources.py` now additionally
guards:

- the source completion bit at fixture `+0x44 bit 0`;
- base box choice for populated fixtures;
- selected-cell toggled-box precedence;
- exact score words at `+0x3C/+0x3E` and `"%i:%i"` formatting;
- exact scheduled-date `DD.MM` presentation.

Still open:

1. semantic meaning of the null/empty-cell red predicate;
2. fixture ordering/filtering used to populate the 12x24 grid;
3. surrounding header/team/date text controls;
4. event/navigation behavior from selected grid cells;
5. original asset import and integrated Windows verification.


## Recovery 153 matrix identity, filtering and grid navigation closure

The remaining neutral empty-slot predicate is now source-resolved, and the
same bounded trace closes the fixture matrix layout and visible grid navigation.

### The red empty cell is the same-club diagonal

The embedded grid is constructed at `PLeagueFixtures+0x1CF0`.
`PLeagueGrid::0x46CBC0` stores its owning `PLeagueFixtures` pointer at
`PLeagueGrid+0x2C` (write at `0x46CC08`). RTTI identifies:

- grid vtable `0x7C23D0` as `PLeagueGrid`;
- header vtable `0x7C25C0` as `ClubText@fm2001_ctrls`.

`PLeagueFixtures` constructs two `ClubText` arrays:

- 12 elements at `+0x9A0`, stride `0x4C`;
- 24 elements at `+0x15D0`, stride `0x4C`.

The exact `ClubText` setter is `0x5D5490`. It stores the supplied identity
pointer directly at `ClubText+0x48` before resolving its visible club name.

Both axis-population paths pass a club pointer from the selected competition:

- the 24-row family at `0x46DAE2..0x46DBD7`;
- the 12-column family at `0x46DDA6..0x46DE93`.

Each path independently compares that same pointer to current user club
`user+0x5B4` when choosing the header text color, which confirms the identity
is a club rather than a fixture, competition, or arbitrary row token.

The empty-cell branches at `0x46CFF5..0x46D01C` and
`0x46D1AD..0x46D1D9` compare:

```text
column ClubText+0x48 == row ClubText+0x48
```

Equality selects `red_fixtures_box.444`; inequality selects
`date_fixtures_box.444`.

Therefore the red empty cell is source-proven as the **same-club self-fixture
diagonal**. It marks the matrix positions where one club would otherwise be
paired with itself. The former neutral `empty_slot_red_predicate` name is
superseded by `empty_slot_same_club`.

### Competition member order and temporary matrix indices

The selected competition exposes member count at `+0x3C` and member storage
at `+0x34`.

Before reading that list, `PLeagueFixtures::0x46D950` calls
`0x4F4940`. That routine performs the competition object's own preparation
vcall and then assigns one-based member-record order at member object `+0x28`.

The League Fixtures builder then walks the resulting competition member list in
that preserved order, resolves each member to its club, and writes a temporary
zero-based matrix index to club `+0x2A0`.

This checkpoint therefore preserves **the competition's prepared member-list
order**. It does not substitute alphabetical order, table position, club ID,
or another modern sort.

### Matrix allocation and repeated fixtures

`0x616F40(selected_competition)` supplies a source helper count. At
`0x46D98A..0x46D98F`, the panel divides that non-negative result by two with
the original signed truncating sequence. That becomes the repeat-layer count.

For `N = competition club count`, the panel allocates:

```text
layer_count * N * N
```

fixture-pointer slots.

A fixture whose resolved club indices are `left` and `right` first targets:

```text
left * N + right
```

If that slot is already occupied, the source adds exactly `N*N` and retries,
placing another same-pair fixture into the next repeat layer:

```text
layer * N*N + left*N + right
```

No date sort is applied at insertion. Repeated pair order therefore follows the
retained global fixture-chain encounter order described below.

### Exact fixture acceptance filters

The builder scans the global fixture chain-head region beginning at
`0x947AD8` over exactly `0x5D4` bytes, four bytes per head:
**373 chain heads**. Each chain follows fixture `+0x04` to the next node.

A fixture is inserted only when all recovered conditions pass:

1. its virtual kind-code method at slot `+0x28` returns **1**;
2. fixture `+0x4C` is exactly the currently selected competition;
3. fixture `+0x44 bit 0x20` is **clear**;
4. the side reference at fixture `+0x14` resolves to a club;
5. the side reference at fixture `+0x28` resolves to a club.

Status bit `0x20` remains deliberately **semantically unnamed**. It is
source-proven as a matrix-exclusion bit, but its higher-level football meaning
is not sufficiently bounded by this trace. Other status bits, including the
already-proven completion bit `0x01`, do not participate in this matrix
eligibility branch.

Within those filters, fixtures preserve the global chain scan order, and
same-pair duplicates preserve first-free repeat-layer order.

### Visible row/column arrangement

The 12-element `ClubText` family is the visible column header window.
Panel offset `+0xA4` is the first visible competition-member index.

Columns are therefore:

```text
competition_member[a4 + column], column = 0..11
```

The 24-element row-header family is populated layer-major. For each competition
club, the panel repeats the club identity once per repeat layer at row indices:

```text
row = layer * N + club_index
```

The fixture lookup used during cell refresh is correspondingly:

```text
matrix[(row * N) + a4 + column]
```

which is algebraically the same layer-major `layer*N*N + club*N + opponent`
layout constructed above.

Unused row/column controls are hidden rather than populated with invented clubs.

### Horizontal paging

The visible column window is exactly 12 clubs.

The left-page handler at `0x46E489` subtracts 12 from `PLeagueFixtures+0xA4`
and clamps at zero.

The right-page handler at `0x46E4AB` adds 12 and clamps to:

```text
club_count - 12
```

for the source-reachable enabled state. Thus a 20-club competition pages from
offset 0 directly to the final offset 8, rather than forcing offsets to be
multiples of 12.

### Exact selector ranges and pointer reduction

The panel dispatcher routes:

- column selector indices **0..11** to `PLeagueGrid::0x46CF90`;
- row selector indices **0..23** to `PLeagueGrid::0x46D140`.

Pointer method `0x46D300` derives both from a grid-relative point. Its two
signed-multiply division sequences are exact division by the existing native
placement steps for valid non-negative deltas:

```text
column = (x - grid_origin_x) // 29
row    = (y - grid_origin_y) // 14
```

It then applies the exact column and row selectors.

Companion method `0x46D390` uses the same coordinate reduction, reads the
fixture pointer for that cell, and calls `0x488C80` only when the fixture is
non-null. This checkpoint records that downstream action target by address only;
it does not invent a modern label for the action.

Method `0x46D400` uses the same cell lookup and returns the already-proven
completion bit for a populated fixture.

### Reconstruction consequence

`reconstruction/original_league_fixtures_resources.py` now guards:

- same-club diagonal identity and red-box selection;
- the neutral type/competition/status/club fixture filters;
- the 373-head retained fixture-chain scan boundary;
- exact `N*N` pair indexing and repeat-layer stepping;
- the source helper-result / 2 layer-count arithmetic;
- 12-column paging by exact 12-club steps with last-window clamping;
- exact 12-column / 24-row selector ranges;
- exact 29x14 grid coordinate reduction.

Still open after Recovery 153:

1. higher-level semantic meaning of fixture status bit `0x20`;
2. surrounding screen header/filter controls outside the now-proven matrix;
3. the higher-level meaning of the non-null cell action at `0x488C80`;
4. remaining competition/category tab controls and their captions/resources;
5. original asset import and integrated Windows verification.

The earlier open item “semantic meaning of the null/empty-cell red predicate”
is closed and must not be reintroduced.


## Recovery 154 country and League selector closure

The League Fixtures matrix is not fed by generic modern category controls.
Recovery 154 traces the exact original country/League selector shell around
`PLeagueFixtures`.

### Concrete selector control class

The panel constructor creates two arrays with the same concrete control type:

- eight controls at `PLeagueFixtures+0x110`, stride `0x4C`;
- six controls at `PLeagueFixtures+0x3B8`, stride `0x4C`.

RTTI identifies their vtable `0x7D6AB8` as
`fmRadioTextSm@fm2001_ctrls`.

Relevant source methods are:

- constructor `0x5D4B50`;
- owner/event bind `0x5D48C0`;
- control setup `0x5D4C70`;
- text setter `0x5D3F10`;
- selected/toggle vcall at vtable slot `+0x98` = `0x5D49F0`.

A separate `LeagueFixRadioButton` class exists elsewhere in the panel, but it
does **not** own these country/League selector arrays. The clean-room contract
therefore keeps these controls as `fmRadioTextSm`.

### Exact eight-country order

`PLeagueFixtures::0x46AA70` writes the following country IDs at
`+0xF0 + 4*index`, builds the corresponding controls, and assigns events
1 through 8 in the same order:

| Index | Country ID | Original name | Event | Control offset | Per-country selected-League index |
| ---: | ---: | --- | ---: | ---: | ---: |
| 0 | 26 | England | 1 | `+0x110` | `+0x68` |
| 1 | 33 | Germany | 2 | `+0x15C` | `+0x6C` |
| 2 | 40 | Italy | 3 | `+0x1A8` | `+0x70` |
| 3 | 73 | Spain | 4 | `+0x1F4` | `+0x74` |
| 4 | 66 | Scotland | 5 | `+0x240` | `+0x78` |
| 5 | 31 | France | 6 | `+0x28C` | `+0x7C` |
| 6 | 24 | Holland | 7 | `+0x2D8` | `+0x80` |
| 7 | 9 | Belgium | 8 | `+0x324` | `+0x84` |

The names are independently source-backed by the canonical database mapping
already used by TeamSelect. The order is intentionally **not** copied from
TeamSelect: League Fixtures places Germany/Italy/Spain before Scotland.

The panel's active-country index is stored at `+0x64`. During setup, the
source compares current-user club country ID `DBRClub+0x14` against these
eight exact IDs and selects the matching country control.

The clean-room seam fails closed for a club country outside this eight-country
set instead of silently choosing England or another default.

### Current club selects its League within that country

The current user's club provides:

- a compact competition/League identifier at `DBRClub+0x10`;
- country ID at `DBRClub+0x14`.

The compact competition identity is resolved through
`0x4056F0 -> 0x4F3B10` to the runtime competition object.

The country record is resolved from the club country ID, and helper
`0x410FF0` searches the country's competition pointer array for that exact
runtime object identity. The returned zero-based index is stored in the active
country's per-country selected-League slot at `+0x68 + 4*country_index`.

The original helper can return `-1`; the normal current-club path assumes a
valid League. The clean-room selector helper fails closed if the current League
is absent rather than accepting a negative index.

### Dynamic six-League radio list

`PLeagueFixtures::0x46D840` rebuilds the second selector family whenever the
active country changes.

The active country supplies:

- competition pointer array at country `+0x48`;
- competition count at country `+0x4C`.

Those entries are base-class `LeagueBase*` objects. Before exposing one as a
League Fixtures radio option, the source performs `__RTDynamicCast`
at `0x668995` from:

- `LeagueBase` TypeDescriptor `0x818AA0`;
- to `League` TypeDescriptor `0x818978`.

The visible radio caption is taken from the successfully cast
`League+0x14` string. Resolved League pointers are retained at
`PLeagueFixtures+0x88 + 4*index`.

The screen owns exactly six League radio controls. The modeled source boundary
therefore exposes between one and six validated League identities/captions and
fails closed beyond that fixed control capacity. Unused source controls are
cleared/hidden.

This is a strong presentation boundary: the selector is specifically a
**League** selector after the source RTTI cast, not a generic list of arbitrary
competition subclasses.

### Exact event dispatch

`PLeagueFixtures::0x46E040` dispatches the radio controls as follows:

```text
events 1..8  -> country indices 0..7
events 9..14 -> League indices 0..5
```

A country event:

1. updates active country `+0x64`;
2. rebuilds the visible League radios through `0x46D840`;
3. rebuilds the fixture matrix through `0x46D950`;
4. refreshes the grid/view through `0x46DCD0`.

A League event:

1. updates `+0x68[active_country]` to the selected League index;
2. rebuilds the matrix;
3. refreshes the grid/view.

No additional modern filtering or cross-country League merge is inserted.

### Reconstruction consequence

`reconstruction/original_league_fixtures_resources.py` now additionally
guards:

- the exact eight-country order, IDs, events and object offsets;
- current-club country -> active selector resolution;
- current-club League identity -> per-country selected index;
- the six-control `fmRadioTextSm` League selector family;
- exact `LeagueBase -> League` RTTI cast boundary;
- source League `+0x14` captions;
- exact country and League event index ranges.

Still open after Recovery 154:

1. remaining non-selector header/footer controls and captions/resources around
   the League Fixtures panel;
2. exact higher-level meaning of non-null fixture action target `0x488C80`;
3. semantic label for fixture matrix-exclusion status bit `0x20`, if a later
   independent producer/consumer trace proves it;
4. original binary asset import and integrated Windows verification.

No selector caption is synthesized from a modern competition name or from
control order.


## Recovery 155 populated-cell PMatchInfo action closure

The previously address-only non-null cell action at `0x488C80` is now tied to
a concrete original presentation class and its fail-closed context resolution.

### Grid passes the fixture pointer directly

`PLeagueGrid::0x46D390` uses the already-proven 29x14 point reduction to
resolve the matrix cell. At `0x46D3E6` it loads the matrix pointer for that
cell, tests it for null, and only when non-null:

```text
push fixture_pointer
call 0x488C80
```

No modern route ID or synthesized match record is inserted by the grid.

### 0x488C80 resolves a second context before opening

The target receives that fixture pointer and calls its virtual slot `+0x18`.
The returned source object supplies a signed 16-bit link index at `+0x40`.

The function then walks the source-linked structure rooted through global
`0x8755F8`. If:

- the link index is `0xFFFF`;
- the linked-list root is absent;
- or the requested linked node cannot be resolved;

the function reaches its no-op exit without allocating a dialog.

Therefore a populated League Fixtures cell is **necessary but not sufficient**
for the original match-info dialog to open.

### Concrete dialog identity

When the secondary context resolves, `0x488C80`:

1. allocates exactly `0x1828` bytes through `0x668140`;
2. calls constructor `0x487580`;
3. stores the constructor result as the dialog object.

The constructor initially installs the inherited
`PExplodingDialog` vtable `0x7C0D54` and finishes by installing final vtable
`0x7C41D4`.

MSVC RTTI resolves:

- final TypeDescriptor `0x81D058` -> **`PMatchInfo`**;
- base TypeDescriptor `0x81BB38` -> **`PExplodingDialog`**.

This independently identifies the League Fixtures populated-cell action as an
attempt to open the original `PMatchInfo` presentation dialog.

### Constructor contexts

Immediately before constructor `0x487580`, `0x488C80` pushes:

1. the source object returned from the fixture virtual `+0x18`;
2. the resolved linked context.

Inside `PMatchInfo`, those two arguments are retained at:

- `PMatchInfo+0x70`: primary fixture-derived context;
- `PMatchInfo+0x74`: resolved linked context.

The exact higher-level class/football name of the secondary linked context is
not promoted by this checkpoint. The clean-room boundary names it only as the
source-resolved secondary context.

### Dialog geometry

After construction, `0x488C80` calls generic geometry helper `0x653320`.
That helper stores:

```text
left   = x
top    = y
right  = x + width
bottom = y + height
```

The `PMatchInfo` caller supplies exact dimensions:

- width = `0x2F8` = **760**;
- height = `0x1F4` = **500**.

The x/y origin is dynamically clamped from the existing source UI globals at
`0x8779C0/0x8779C4`; this checkpoint therefore preserves only the proven
760x500 size and does not invent a fixed origin.

### Reconstruction consequence

`reconstruction/original_league_fixtures_resources.py` now guards a
`LeagueFixturesMatchInfoAction` with:

- action target `0x488C80`;
- class `PMatchInfo`;
- final vtable `0x7C41D4`;
- constructor `0x487580`;
- allocation size `0x1828`;
- base `PExplodingDialog` vtable `0x7C0D54`;
- fixture-derived primary context and linked secondary context;
- exact 760x500 dialog size;
- no-op behavior unless both the cell fixture and linked context are present.

Still open after Recovery 155:

1. broader `PMatchInfo` internal resources/layout/content, which is a separate
   presentation slice from proving the navigation target;
2. the exact higher-level semantic identity of the linked secondary context;
3. remaining non-selector League Fixtures header/footer controls;
4. fixture matrix status bit `0x20` semantic name, if independently provable;
5. original binary asset import and integrated Windows validation.

The former open item “exact semantics of action target `0x488C80`” is closed
at the presentation/navigation level as **open original PMatchInfo dialog when
its source-linked context resolves**.

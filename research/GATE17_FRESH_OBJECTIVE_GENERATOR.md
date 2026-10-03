# Gate 17 fresh chairman-objective generator recovery

_Status: source-backed clean-room recovery from the authorized canonical executable; integration remains fail-closed until the caller CRT-state boundary is complete._

## Canonical source identity

The private canonical executable used for this recovery was extracted from the
authorized original disc image and verified before analysis:

- file: `FOOTBAL.EXE`
- size: 4,714,541 bytes
- SHA-256:
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

No original executable bytes are stored in Git.

## Exact fresh-state 0x5DFD30 inputs

For objective state byte `+0x9C == 0`, the candidate generator is now
source-resolved around four inputs:

1. `rank_high = fan_base_rank_count >= floor(league_team_count / 2)`;
2. `first_class = (0x4FA520(league) == 0)`;
3. `last_class_equal = 0x4FA590(league)`;
4. the second dword returned by `0x4F88C0`, i.e. the number of table positions
   marked status 2 by promotion-playoff child ClubRefs.

The generator is called three times with slot arguments 0, 1 and 2.

## Exact fresh candidate branches

```text
if first_class:
    if rank_high:
        slot0 = 1
        slot1 = 2 if RNG(100) <= 50 else 15
        slot2 = 3
    else:
        slot0 = 4
        slot1 = 5
        slot2 = 6
else:
    if rank_high:
        slot0 = 13
        slot1 = 1
        slot2 = 5 if playoff_count <= 0 else (5 if RNG(100) <= 50 else 8)
    else:
        slot0 = 1
        slot1 = 5 if playoff_count <= 0 else (5 if RNG(100) <= 50 else 8)
        slot2 = 9 if last_class_equal else 6
```

The comparison is inclusive. Since `0x64D540(100)` returns 0..99, the
lower-numbered random alternative occurs for 51 of 100 possible results.

The already-implemented Premier League branch is a strict subset:
`first_class=False`, `last_class_equal=False`, `playoff_count=0`, giving
`(13,1,5)` for high-half fan rank and `(1,5,6)` for low-half rank with no RNG.

## 0x4FA520 / 0x4FA570 / 0x4FA590

`0x4FA510` is the zero-based index in the exact DBRCountry +0x48
League/DummyLeague root subset already reconstructed by
`country_league_root_storage_order()`.

`0x4FA520` normally returns that index unchanged. Germany (country ID 33) is
the only recovered special case:

- index 3 -> class 2;
- index 4 -> class 3;
- every other index -> unchanged.

Canonical Germany therefore classifies:

- Bundesliga 1 -> 0;
- Bundesliga 2 -> 1;
- Regional North -> 2;
- Regional South -> 2;
- German Spare DummyLeague -> 3.

`0x4FA570` is exactly class == 0.

`0x4FA590` compares the current class with the class of the final entry in the
same country +0x48 subset.

## 0x4F88C0 promotion-playoff count

The second output count is now reproduced without guessing competition names.

`0x4F88C0` finds the source-order upper LeagueAllocation neighbour, seeds
direct top/bottom status positions, then calls virtual +0x34 on relevant child
competitions with marker 2. Both recovered virtual implementations only mark
type-2 ClubRefs whose source competition is the current League, at the ClubRef
selector/table position.

The clean-room helper therefore reuses the existing exact allocation expansion:

- League/DummyLeague child: `expand_league_position_allocation_instructions()`;
- Cup child: the first qsorted Cup runtime round from
  `expand_standard_cup_allocation_instructions()`.

Relevant children are:

- every child of the upper neighbouring competition; plus
- a child of the current League when that child has a LeagueAllocation relation
  to the upper neighbour, reproducing `0x4F83F0`.

The resulting count is the number of unique selectors marked status 2.

Canonical patterns covered by regression include:

- English Division 1: 4 promotion-playoff positions;
- Italian Division 2: 2 positions through the upper League's child playoff;
- Dutch Division 2: 6 unique positions across its two child Leagues;
- a top League with no upper allocation: 0.

## Integration boundary

Fresh DBRUser construction `0x425680` initializes objective state byte
`+0x9C = 0` and source-backed Balance cash, but does not itself establish the
shared CRT state at the later candidate-generation event.

Normal objective setup in `0x5DF670` calls `0x5DFD30` three times. The full
fresh branch table makes the remaining uncertainty narrower than an all-or-none
non-PL guard:

- first hierarchy class + lower-half fan rank is deterministic `(4,5,6)`;
- non-first classes with zero promotion-playoff status-2 positions are
  deterministic in both fan-rank halves;
- first hierarchy class + high-half fan rank requires one `RNG(100)`;
- every non-first branch with promotion-playoff positions requires one
  `RNG(100)`.

The clean-room runtime may therefore materialize a non-PL objective only when
the exact recovered inputs prove that `0x5DFD30` consumes no RNG. The runtime
uses a sentinel RNG object that raises if a supposedly deterministic branch
tries to draw. RNG-bearing branches remain fail-closed until the exact
`0x5DF670` caller CRT state is connected.

Gate-17 scope readiness remains stricter than this per-club improvement: a
League scope must not be reported complete while any selectable club can still
reach an unresolved RNG-bearing fresh branch.

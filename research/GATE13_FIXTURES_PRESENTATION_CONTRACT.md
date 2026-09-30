# Gate 13 Fixtures / Results Presentation Contract

_Date: 1 October 2026 KST_

## Scope

This checkpoint promotes only the already recovered fixed-real-fixture backend
identity and construction ordering into the Gate-13 read-only presentation
seam. It does not claim the original Fixtures/Results screen sort or visuals.

## Original fixed-fixture records

Canonical executable/static-data research establishes:

- `DBTRealFixtures` vtable `0x7C9884`, global `0x876C18`;
- `DBRRealFixture` vtable `0x7C9898`, runtime size `0x14`;
- shipped real Premier League table at `Static.dat 0x10057`;
- 380 fixtures, 38 rounds, 10 fixtures per round;
- each packed source fixture supplies round/home/away club identity.

The corresponding round identity is:

- `DBTRounds` vtable `0x7C99C4`, global `0x876BD0`;
- `DBRRound` vtable `0x7C99D8`.

## Construction order

The fixed League path is directly recovered:

1. `0x4F72D0` walks DBTRounds table order and attaches rounds through
   `League::AddRound 0x4F4500`;
2. `0x4F76A4..0x4F770D` walks DBTRealFixtures in global table order and
   appends fixtures to each DBRRound;
3. fixed builder `0x6173D0` walks those preserved round/fixture lists;
4. it constructs `LeagueMatch` through `0x5104F0` and inserts through
   `0x615950`;
5. no `rand` / `0x64D540` occurs before those fixed insertions.

Thus backend source order is proven before schedule-container insertion.

## Screen-order boundary

Backend source order is **not** evidence that the original Fixtures/Results
screen displayed rows in that same order. Later schedule insertion/shuffle
mechanics and presentation-specific sorting are separate concerns.

Therefore the contract explicitly records:

- `source_order_preserved_before_schedule_insertion = True`;
- `rng_before_fixed_schedule_insertion = False`;
- `original_screen_sort_proven = False`;
- `screen_class_name = None`.

The existing `fixture_rows()` view preserves source fixture order only as a
neutral, source-backed presentation data seam until the original screen
comparator/navigation is recovered.

## Explicit non-claims

No original screen ID/class, visible column/header binding, row geometry,
artwork, control ID, screen sort, click target or navigation edge is claimed.

## Hosted verification

PR #43 head `8551d9774353f1b44af8c8c2e62da07b89cfd088` passed:

- focused Gate-13 run `36773557317`: **236 tests**, **19 expected
  original-source-gated skips**, zero failures;
- full reconstruction run `36773557140`: **1,072 tests**, **21 expected
  original-source-gated skips**, zero failures;
- repository asset-policy run `36773557226`: passed.

It was squash-merged to main as
`a346762f0fcfc54cdb17fbd0d1787a539dfa8fd7`.

## Gate 13 consequence

Fixtures/Results now has an explicit source-backed backend identity/construction
contract. The actual original Fixtures/Results screen presentation remains open.

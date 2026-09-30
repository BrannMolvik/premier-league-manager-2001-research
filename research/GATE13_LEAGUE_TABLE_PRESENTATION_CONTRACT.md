# Gate 13 League Table Presentation Contract

_Date: 1 October 2026 KST_

## Scope

This checkpoint promotes the already recovered original League ranking
comparator into the Gate-13 read-only presentation seam. It does not reconstruct
the proprietary League-table screen.

## Backend identity

Primary executable research identifies:

- competition backend class: `League`;
- backend vtable: `0x7C9AC0`;
- ranking comparator: `0x4F45E0`.

These are backend identities. The persisted research used here does not pin a
specific League-table presentation panel class. Therefore
`screen_class_name = None`.

## Exact recovered ordering

`League::0x4F45E0` orders rows by:

| Priority | Recovered field | Direction |
| ---: | --- | --- |
| 1 | points | descending |
| 2 | games played | ascending |
| 3 | goal difference | descending |
| 4 | goals for | descending |
| 5 | goals against | ascending |
| 6 | original DBRClub short-name CP1252 byte string | ascending lexical |

The sixth comparison is not a Unicode/display-name convenience sort. It uses
the source short-name byte identity, so presentation/ranking code must use the
original CP1252 bytes when the numeric fields tie.

## Full-key tie boundary

The native comparator can return equality when every field above matches.
Persisted evidence does not prove the original CRT qsort's relative permutation
for such fully equal keys.

Therefore the contract records:

- `strict_source_name_required_on_numeric_tie = True`;
- `equal_full_key_relative_order_proven = False`.

The existing reconstruction already fails closed for exact ranking publication
when a complete original key remains indistinguishable, while retaining a
clearly documented deterministic fallback only for synthetic/display callers.

## Read-only projection

`ManagementSourceDataBridge.league_table_rows()` consumes
`GameState.premier_league_table()`, which already routes original runtime club
short names through strict CP1252 encoding into the recovered comparator.

The bridge does not sort those rows again. It only projects the backend's
already ordered result into immutable presentation data.

## Explicit non-claims

The contract contains no:

- original League-table screen class or numeric screen ID;
- visual column/header binding;
- row or column geometry;
- table artwork/resource path;
- font/color/alignment rule;
- click target or navigation edge.

Those remain open Gate-13 presentation work.

## Gate 13 consequence

The League table now has an explicit source-proven presentation ordering
contract instead of relying only on an implicit backend sort. Original table
art, headers, geometry, controls and navigation remain unresolved.

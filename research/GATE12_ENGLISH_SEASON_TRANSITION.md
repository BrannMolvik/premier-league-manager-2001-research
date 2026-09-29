# Gate 12 - English Cross-Division Season Transition

_Last updated: 29 September 2026_

## Scope

This note records the source-backed annual English promotion/relegation
mechanism recovered from canonical `Static.dat` and `FOOTBAL.EXE`.

It follows `research/GATE12_ENGLISH_DIVISIONS.md`, which already proves that
the regular-season English procedural Leagues are IDs 2, 3, 4 and 7.

## Canonical source table

`Static.dat` contains `DBTLeagueAllocations` at offset `0xFD43`.

- record count: **28**
- packed row size: **28 bytes**
- table end: `0xFD43 + 4 + 28 * 28 = 0x10057`
- `0x10057` is the already-proven real-fixture table start

Each packed row contains seven dwords:

```text
allocation_id
competition_a_id
competition_a_start
competition_a_end
competition_b_id
competition_b_start
competition_b_end
```

The two ranges are inclusive and zero-based.

Runtime construction prepends the vtable, making the corresponding runtime
fields:

```text
+0x04 allocation_id
+0x08 competition_a_id
+0x0C competition_a_start
+0x10 competition_a_end
+0x14 competition_b_id
+0x18 competition_b_start
+0x1C competition_b_end
```

### Instruction evidence

- `0x4F88C0` scans the global allocation rows and compares both runtime
  `+0x08` and `+0x14` against the current League competition ID. This
  proves the two endpoint fields are competition IDs.
- `0x4F83D0` computes both inclusive range lengths and returns the smaller:
  `min(end_a - start_a, end_b - start_b) + 1`.
- startup `0x4F7858..0x4F78C6` builds and qsorts the global allocation-pointer
  list with comparator `0x4F7940`.
- `0x4F7940` groups by country and then orders by the higher-ranked endpoint's
  position in that country's competition list through `0x4FA510`.
- annual finalization `0x4F948F` iterates that sorted global allocation list
  and calls `0x4F4BD0` for every row.
- `0x4F4BD0` resolves the paired ranking slots and applies each exchange.
- `0x4F4ED0` performs the core club swap by exchanging the two selected
  clubs' competition-membership values through the existing setter path.

The table is therefore the actual season-transition mechanism, not display or
advisory data.

## English slot exchanges

Canonical English rows are:

| Row | Side A | Side B | Meaning |
|---:|---|---|---|
| 0 | Premier League 18..19 | Division 1 0..1 | PL 19th/20th exchange with D1 1st/2nd |
| 1 | Premier League 17 | Division 1 Playoff 0 | PL 18th exchanges with D1 playoff winner |
| 2 | Division 1 22..23 | Division 2 0..1 | D1 23rd/24th exchange with D2 1st/2nd |
| 3 | Division 1 21 | Division 2 Playoff 0 | D1 22nd exchanges with D2 playoff winner |
| 4 | Division 2 21..23 | Division 3 0..2 | D2 22nd-24th exchange with D3 1st-3rd |
| 5 | Division 2 20 | Division 3 Playoff 0 | D2 21st exchanges with D3 playoff winner |
| 6 | Division 3 23 | Conference 0 | D3 24th exchanges with Conference champion |
| 25 | Conference 19..21 | Conference 2 0..2 | Conference 20th-22nd exchange with Conference 2 top three |

Competition IDs:

- 0: F.A. Premier League
- 2: Division 1 (ENG)
- 3: Division 2 (ENG)
- 4: Division 3 (ENG)
- 7: Conference
- 11: Division 1 Playoff
- 12: Division 2 Playoff
- 13: Division 3 Playoff
- 89: Conference 2 (DummyLeague)

For England, the recovered allocation sort groups execute top-down:
Premier↔Division 1, Division 1↔Division 2, Division 2↔Division 3,
Division 3↔Conference, then Conference↔Conference 2.

Rows tied on the same higher endpoint use disjoint ranking ranges, so their
internal tie order does not change which clubs are selected.

## English playoff source structure

The playoff Cups are ordinary primary Cup runtime competitions and can use the
already-recovered generic Cup bridge.

Canonical rounds:

| Competition | Round | Type | Source date |
|---|---|---|---|
| Division 1 Playoff (11) | Semi Final | type 2 | week 46, weekday 2 |
| Division 1 Playoff (11) | Final | type 1 | week 48, weekday 1 |
| Division 2 Playoff (12) | Semi Final | type 2 | week 46, weekday 2 |
| Division 2 Playoff (12) | Final | type 1 | week 47, weekday 7 |
| Division 3 Playoff (13) | Semi Final | type 2 | week 46, weekday 2 |
| Division 3 Playoff (13) | Final | type 1 | week 47, weekday 6 |

Each Semi Final has four new entrants; the Final takes the two previous winners.

Canonical Cup-allocation instructions prove the entrants:

```text
D1 playoff: type 4 skip 2 from League 2; type 1 take 4
D2 playoff: type 4 skip 2 from League 3; type 1 take 4
D3 playoff: type 4 skip 3 from League 4; type 1 take 4
```

The already-recovered `0x4F4FD0` / Cup-allocation semantics therefore yield:

- Division 1 playoff: league positions **3rd through 6th**
- Division 2 playoff: league positions **3rd through 6th**
- Division 3 playoff: league positions **4th through 7th**

These are emitted as type-2 competition-position ClubRefs, so they resolve
only after the referenced regular-season League publishes its exact final
ranking.

## Conference 2

Competition 89 is a `DummyLeague`, not a scheduled procedural League.

It is already consumed as a type-5 ranked source elsewhere in canonical
Cup allocation, which invokes the recovered RNG-bearing DummyLeague lazy
ranking path (`0x4F4750`). The season-transition row consumes positions
0..2 of that same competition.

Do not model Conference 2 as a played League or invent fixtures.

## Implementation checkpoints

- `71a4b67a`: parse the 28-row LeagueAllocation table losslessly.
- `6eeafa36`: lock table boundary and packed-row parsing.
- `89627691`: verify canonical row count.
- `087ad60a`: name the recovered competition/ranking-range fields.
- `bd33855d`: test named inclusive-range semantics.
- `41f19e3e`: verify the exact eight English allocation rows.
- `1e8cd6f1`: add playoff IDs 11/12/13 to live English Cup state.
- `97184e81`: include those playoff Cups in the shared primary order.
- `fcb23448`: regression-lock playoff primary-order tagging.
- `eb582e7f`: correct the canonical playoff source-date regression to
  23 May 2001.
- `e78d10c9` / `505561ea` / `79e59cbc`: preserve canonical ranked
  Cup-source state through primary reconstruction and publish the already-drawn
  Conference 2 ranking without consuming additional RNG.
- `c3d321d8`: regression-lock preserved DummyLeague source ranking.
- `8272f4f1` / `f38eb6cf`: expose/publish a gameplay-safe exact Premier
  League final ranking only when the recovered points / goal-difference /
  goals-scored keys uniquely determine every position.
- `d76f2e8c` / `d3572bf0`: expose and test the unique completed playoff
  final winner.
- `85b786c8` / `802a15d0`: implement and test the exact paired
  LeagueAllocation membership swaps, including all 14 English slot exchanges
  and the playoff-winner parent-membership behavior.
- `85420011`: add source allocation rows plus a separate mutable live
  club-competition-membership map to GameState and integrate the English annual
  transition.
- `3aafce9f` / `d02639af`: advance internal save schema to **33** and
  preserve changed club competition memberships across save/reload.
- `618a223a`: end-to-end GameState regression for exact rankings, playoff
  winners, Conference 2, and all 14 annual exchanges.
- `3a699c17` / `64baafb8`: keep lightweight synthetic club sources
  compatible while preserving real source memberships.

At `64baafb8772cc7d6a003ed92c6df41eec41c33a9`, GitHub Actions ran
**792 tests** with only the two unchanged known secondary-schedule failures;
repository asset policy passed.

## Verified live transition boundary

The annual English membership transition is now live, source-backed and
save-persistent:

1. regular-season Leagues publish exact final rankings;
2. playoff Cups 11/12/13 run in the shared primary Cup stream and expose their
   resolved final winners;
3. Conference 2 reuses the exact startup DummyLeague ranking already produced
   by canonical RNG, with no second sort;
4. GameState resolves every LeagueAllocation endpoint and refuses to run if any
   exact ranking is unresolved;
5. the eight English source rows execute in recovered top-down order and
   perform **14 paired current-membership swaps**;
6. immutable source Club records remain untouched; the live membership map is
   persisted under internal save schema **33**.

The remaining Gate-12 transition boundary is **next-season regeneration**:
rebuild Premier League, procedural League, playoff/Cup, ranking, and primary
schedule state from the post-transition live memberships in the original
season-rollover order. Do not reuse the old season's schedule objects or
re-materialize Conference 2 with a second RNG pass.

Do not substitute modern football rules for any missing source behavior.

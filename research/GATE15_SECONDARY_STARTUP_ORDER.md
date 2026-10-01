# Gate 15 secondary startup root-order recovery

_Date: 1 October 2026 KST_

## Scope

This checkpoint closes the equal-key root-order half of the Gate-15 secondary
startup fidelity gap. It does **not** yet claim the exact mode-1 per-date bucket
vector; that remains the next task.

## Source path

The secondary schedule container is `0x947AF0`. New-game setup calls
`0x616620` for the primary container first and then for the secondary
container. For each country, `0x616620 -> 0x411020` traverses the same root
competition array used by the primary pass.

The root array is:

1. appended in global competition source order;
2. qsorted with comparator `0x4F79A0`, which compares runtime `+0x18`;
3. traversed backwards by `0x411020`;
4. filtered by virtual `+0x30` so schedule-container codes 2/3 enter the
   secondary pass.

Runtime `+0x18` is the negated signed packed initialization-order word.

## CRT qsort source lock

Canonical `FOOTBAL.EXE` SHA-256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

Direct disassembly of CRT qsort `0x668DA4` independently matches the
reconstruction's `msvc_crt_qsort`:

- arrays of 8 or fewer elements use shortsort `0x668EF8`;
- larger ranges swap the midpoint element into the low/pivot slot;
- the low scan advances while comparator result is `<= 0`;
- the high scan retreats while comparator result is `>= 0`;
- crossed scans place the pivot at the final high-scan position;
- `0x668E8F` compares partition sizes and processes the smaller partition
  immediately while stacking the larger;
- shortsort chooses the strict-greater maximum and swaps it to the tail.

The algorithm is not stable for equal keys. Therefore the exact permutation
must be computed from the complete input array, not from the comparator alone.

## Canonical country-116 root input

The real country-116 root source array contains twenty roots. The equal-key
group includes four primary-container roots before the fourteen mode-1 roots.
Those primary roots cannot be omitted before qsort because their presence
changes the large-array partition permutation even though they are filtered out
afterward.

The exact qsorted storage IDs are:

```text
16, 15, 86, 88, 82, 101, 170, 171, 174, 177,
178, 179, 180, 181, 182, 183, 184, 185, 186, 187
```

Walking that array backwards and applying the mode-1 filter proves the exact
secondary root initialization IDs:

```text
187, 186, 185, 184, 183, 182, 181, 180, 179, 178,
177, 174, 171, 170
```

This preserves the previously proven World Cup 174 before European Championship
171 boundary while now also locking every other equal-key root position.

## Regression

`reconstruction/test_competition_startup.py` now contains a regression using
the complete twenty-root canonical country-116 key/container input. It asserts
both the qsorted storage permutation and the reverse-filtered mode-1 order.

Focused local result:

```text
1 test passed
```

## Remaining secondary schedule gap

The exact mode-1 date-bucket vector remains open.

`0x4FA790` has now been reconfirmed to qsort the 108 Static.dat
InternationalFixture pointers, select national teams from lazily shuffled
competition pools, construct one 0x50-byte match per record through
`0x5105D0`, and insert every match directly into `0x947AF0` through
`0x615950`.

The canonical secondary container has 262 nodes total, so the remaining
competition-initialization path contributes 154 nodes. The next task is to
materialize those 154 source-backed mode-1 competition nodes, append the 108
InternationalFixture nodes in original insertion order, run all 262 through
the exact secondary `0x615950` placement rules, and record the resulting 45
nonempty bucket sizes before the final 217-draw `0x615BE0` shuffle.

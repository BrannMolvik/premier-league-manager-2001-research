# Secondary schedule legacy assertion audit (later Gate 15 fidelity dependency)

_Status: regression evidence corrected for its actually demonstrated scope.
Native equal-key tie order and exact mode-1 date-bucket distribution remain
unresolved, explicitly tracked in `research/FIDELITY_GAPS.md`._

## Why this work was necessary

At full-suite GitHub Actions run `36699473326` (30 September 2026,
commit `1cf7af7`) exactly two of 899 test cases failed, and earlier full
runs recorded the same two legacy expectations. Neither failure arose from
the new Gate-13 UI work.

1. `test_secondary_root_order_uses_same_crt_qsort_then_mode_filter`
   expected the equal-key competitor 181 before 170. Actual recovered
   qsort/reverse implementation returned 170 before 181. The test's
   full hard-coded tuple was more specific than the original research.
2. `test_secondary_container_bucket_counts_reach_canonical_staff_seed`
   used a handwritten 45-bucket array that in fact sums to **280**
   despite asserting **262**. Its claimed per-bucket content never
   had an independent original-byte verification.

## Established original source evidence (not synthetic observations)

`research/EXECUTABLE_ANALYSIS.md` establishes:

- canonical executable `0x4F79A0` compares each country-root's
  runtime `+0x18`, which is negative packed sort key;
- `0x411020` walks the country-root array **backwards**;
- the comparator does **not** define the relative ordering of
  equal-key Other-country roots;
- the source-grounded mode-1 RNG checkpoint requires World Cup
  competition **174** to be initialized before European
  Championship **171**, so their first-access regional/seed
  DummyLeague RNG ordering is preserved.

`research/PROGRESS.md` independently records the firsthand Gate-11
secondary tail at the later effective source-backed checkpoint:
`0x4FA790` ends at CRT state **`0xCAB0B953`**; the secondary
container holds **262** nodes in **45** nonempty buckets; final
per-bucket shuffle takes **217** raw CRT draws, ending at
**`0x61D6DFA2`**. The staff RNG boundary relies on those
aggregate numbers. The exact vector of 45 bucket sizes and the
complete equal-key country-root permutation were NOT part of
that independent evidence.

## Tightened tests

The secondary root test now verifies that the existing helper
traverses the separately materialized, source-backed country
root array **in reverse**, retains each of the fourteen input
competitions exactly once, and preserves 174 before 171. It
does not freeze the unproven 170-versus-181 equal-key permutation.

The secondary RNG regression no longer materializes any synthetic bucket
vector. `advance_msvc_schedule_shuffle_aggregate_state` accepts only the
independently proven total node count and nonempty-bucket count. For any
45 nonempty buckets summing to 262, descending Fisher-Yates consumes exactly
`262-45=217` shared MSVC CRT RNG draws. Because the MSVC hidden-state update
performed by `rand15()` is independent of the later bound scaling, those
aggregates are sufficient to validate the source-backed staff-seed transition
without inventing original per-date secondary placement.

The aggregate helper deliberately cannot produce shuffle outputs, original
bound sequences, bucket contents, or date placement. Impossible aggregate
counts fail closed.

**Do not use this aggregate-only checkpoint to claim exact
secondary match ordering, exact original date-bucket contents,
equal-key native qsort implementation fidelity, or any Gate
13/Gate 15/Windows 11 release audit.** Those are explicit open
fidelity questions until private canonical source or independent
equivalent evidence answers them.

The full reconstruction CI remains intentionally manual for
ordinary commits, with an extra narrowly scoped PR trigger only
when these secondary tests or this full-suite workflow change.

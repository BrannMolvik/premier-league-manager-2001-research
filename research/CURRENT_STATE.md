# Current State

_Last reconciled: 30 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in
`PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and
topic-specific research files.

## Current gate

**Gate 13 - Restore original management presentation**

Gates 1 through 12 are complete. Gate 12 closed on 30 September 2026 after a
canonical real-data season reached the complete annual qualification snapshot
and atomically regenerated the year-two primary world.

Evidence:

- `research/GATE12_COMPLETION_AUDIT.md`
- `research/GATE12_ENGLISH_DOMESTIC_CUPS.md`
- `research/GATE12_EUROPEAN_COMPETITIONS.md`
- `research/GATE12_ENGLISH_DIVISIONS.md`
- `research/GATE12_ENGLISH_SEASON_TRANSITION.md`
- `research/GATE12_NEXT_SEASON_REGENERATION.md`

## Porting mission

This is a **Windows 11 modernization/port**. The supplied FM2001 archive/disc
contents are authorized for project use. Original FM2001 resources and
recoverable original behavior are the default source of truth. Use them
directly, convert them, or wrap them as needed; do not replace or redesign them
for convenience. Authorized original resources belong under
`original_assets/` with provenance tracked according to
`research/ASSET_POLICY.md`.

## Latest verified implementation

```text
19e599f34c3330a5d258902d5311649f62271ecb
Test content-based raw BIN disc detection without excluding UI binary resources
```

Dedicated GitHub Actions Gate 13 run `36698353585` passed **61/61 focused
tests**. Full reconstruction run `36698353568` ran **889 tests with 2 failures**,
exactly the two long-standing secondary-schedule assertions:

- secondary root-order assertion;
- secondary bucket-count assertion (262 expected vs 280 recovered).

All Gate-13 navigation, source-inventory, MODE1-conversion, native
ISO9660/Joliet inventory/extraction, and provenance-import tests passed.
Repository asset policy passed.

## Gate 12 closure checkpoint

The canonical annual run used the recovered fresh-game date **4 July 2000** and
reached a complete annual qualification snapshot on **4 June 2001**, after 335
simulated days.

It captured:

- played League sources `(0, 17, 21, 27, 31, 40, 50, 54)`;
- all 44 required DummyLeague ranking sources;
- all ten annual Cup sources `(1, 5, 9, 10, 19, 23, 33, 91, 98, 101)`.

The source-derived Champions League child phases 14/167 and WCC group phase 192
all ran live. Recovered League comparator `0x4F45E0` now resolves European
group ties with points, played, goal difference, goals for, goals against, then
CP1252 short-name bytes.

Atomic annual regeneration then:

- applied 28 membership changes;
- generated season year 2001;
- consumed 15,539 annual materialization draws;
- changed controller match RNG from `0xCE9A6E40` to `0x6F763739`;
- produced a fresh 380-fixture Premier League;
- produced 150 year-two primary-order dates;
- retained every played annual qualification-source League.

Internal save schema remains **34**.

## Stable startup / scheduler checkpoint

- DBTPlayers startup RNG: **180,384 calls** for 30,064 players;
- synthetic post-youth state: **`0x4B68DE28`**;
- actual-count primary competition RNG: **5,836 calls**;
- state entering primary `0x615BE0`: **`0x4F5CF274`**;
- complete primary schedule nodes: **9,346**;
- primary buckets: **373**;
- primary bucket-shuffle calls: **9,178**;
- state after primary schedule shuffle: **`0xD25DFFE6`**;
- first PL fixture order: **0, 6, 8, 5, 1, 9, 3, 2, 4, 7**.

## Gate 13 presentation checkpoint

The first front-end contract is now bounded in
`research/GATE13_FRONTEND_FOUNDATION.md`:

- initial PStartMenu screen identity: `0x323`;
- PStartMenu New Game control/event: `2`;
- TeamSelect Back control/event: `0x29`;
- TeamSelect Start/Continue control/event: `0x2A`;
- TeamSelect object/activation path is already recovered and remains separate
  from gameplay simulation.

A tested, headless Gate-13 application boundary now exists in
`reconstruction/front_end_session.py`. Confirmed PStartMenu New Game event 2
constructs the gameplay backend before entering TeamSelect, failures leave
PStartMenu active, choosing a club remains presentation-only until confirmed
TeamSelect Start/Continue event `0x2A` delegates to the existing
`HumanGameplayController.select_club`, and Back event `0x29` returns to
PStartMenu without an invented gameplay reset. The current implementation is
limited to the existing Premier League gameplay subset. It is **not** a visual
renderer and does not imply that source assets have been recovered.
See `research/GATE13_FRONTEND_FOUNDATION.md`.

The authorized source archive now has a durable private locator in
`research/ORIGINAL_SOURCE_LOCATOR.md`. This recovery resolved the exact
511,121,336-byte Library file and materialization reported success, but the
current CAAS/container still returns a container-level `ClientError`. A
control test consisting only of `printf 'container-health'` fails the same
way, proving this is a general execution-container outage rather than a
511 MB ZIP or source-file-specific failure. Persistent source recovery is
working; execution-container availability is the remaining infrastructure
blocker. No visual asset has been guessed or substituted;
`original_assets/MANIFEST.md` remains intentionally empty.

Repository-native ISO9660/Joliet inventory is implemented and CI-verified.
After raw MODE1/2352 conversion, Gate-13 filesystem enumeration and extraction
no longer require 7-Zip for the documented source path. Reports contain the
complete disc file catalog (path, byte size, ISO extent) plus the smaller
presentation shortlist. Opaque resources discovered from that catalog can be
selected with repeatable exact `--extract-path` arguments and staged without
dumping unrelated disc contents; missing requested paths fail loud via report
warnings. GitHub Actions run `36685946489` verified the current source-analysis tooling
at `eaa738de9f6cb16acee99462f8bfa740a1c9a0ee`: 860 tests, with only the two
known secondary-schedule failures. A saved full-disc report can be queried
offline with `gate13_catalog_query.py` by substring, suffix, top-level
directory, or regex. Query results can be emitted as a reusable path-list file
and fed back to `gate13_source_inventory.py --extract-path-file --only-explicit`, avoiding
repeated 511 MB conversion while narrowing and staging opaque
PStartMenu/TeamSelect leads.

Exact-path staging now supports `--only-explicit`, which deliberately
excludes unrelated heuristic candidates from extraction while retaining the
complete disc catalog. An empty exact-path selection fails immediately.
GitHub Actions run `36688232893` verified all three new tests; full-suite
results remain 863 tests with only the same two known secondary-schedule failures.
The repository asset-policy workflow also passed.

Gate-13 staging path normalization now rejects parent traversal (`..`) and
drive-prefixed archive paths rather than letting an unexpected source member
escape the temporary extraction root. This is tested through both direct
normalization and a malicious nested ZIP fixture. GitHub Actions run
`36690708130` verified both new tests and ran 865 tests in total, with
only the same two known secondary-schedule failures; the repository
asset-policy workflow also passed.

Latest source-access retry: the exact private 511,121,336-byte Library ZIP
was resolved and materialized again, but container commands (including the
materialized-file stat operation) still fail with a general CAAS `ClientError`.
The Files text reader returns no readable text for this binary ZIP. No claim
is made that its internal disc files were inventoried.

Further Gate-13 source validation uses the original-disc-confirmed
`FM2001_Art/Generic/bground.444` length of **222,616 bytes** in addition to
the already-enforced header dimensions and SHA-256. Inventory now records that
expected length and warns on a mismatched listing even before extraction.
A dedicated `.github/workflows/gate13-tests.yml` isolates the presentation,
source-inventory, import and ISO reader regressions from unrelated simulation
tests. GitHub Actions run `36693094247`: **38 focused Gate-13 tests passed**;
repository asset-policy run `36693094248` passed. Full reconstruction run
`36693078539`: **866 tests, 2 failures**, exactly the same two known
secondary-schedule assertions.

In this recovery the durable 511,121,336-byte private Library ZIP resolved and
materialized successfully again, but a trivial container health operation
still returned CAAS `ClientError`. No source asset contents were read and
`original_assets/MANIFEST.md` remains unmodified. The catalog search plan
now explicitly includes the verified background size and `--only-explicit`
for intentional staging.

Outer-ZIP Gate-13 inventory now supports explicit selection and extraction
of **loose resources** alongside the already-supported nested ISO/Joliet
selection. `--only-explicit` excludes unrelated heuristic candidates at both
archive layers. The deep ZIP pass retains its nested-disc names from its
first enumeration rather than re-reading and hashing loose files a second
time. Synthetic mixed-ZIP regression tests verify that an explicitly selected
loose UI file is staged, the nested ISO catalog remains intact, unrelated
nested artwork is not staged, and the outer ZIP is inventoried exactly once.
GitHub Actions run `36697061364` passed all 50 focused Gate-13 tests and
the full suite `36697061476` reached 878 tests with only the two existing
secondary-schedule failures. Repository asset policy passed.

The original 511,121,336-byte private Library source was confirmed again
and materialized successfully. However, even a trivial local container
health/file-stat command still raises a general CAAS `ClientError`;
therefore the actual 511 MB disc has **not** been byte-inventoried here.
No real source asset has been imported or substituted.

Both outer ZIP and nested-disc **complete catalogs** are now saved in each
deep source-inventory report. Catalog queries search both layers and annotate
their provenance, with optional layer filters for investigation. Matching
duplicate paths fail closed during `--paths-only` export; exact-path staging
also refuses case-insensitive duplicate paths, collisions between archive
layers, and overwriting preexisting staged files. Most importantly, raw
`.bin` disc images are now identified by valid MODE1 sector signatures rather
than file extension: opaque `.bin` files containing ordinary UI data are
still eligible as original interface resources.

Latest focused GitHub Actions run `36698353585` passed all **61** Gate-13
tests; full suite run `36698353568` ran **889** tests with only the same
two existing secondary-schedule failures; asset-policy run `36698353633`
passed. None of those tests involves the actual authorized 511 MB archive.
The global container and both Python execution environments still returned
CAAS `ClientError` on trivial health commands. The actual source-disc
catalog and visual resources remain the first unfulfilled Gate-13 dependency.

Secondary visual evidence is now bounded in
`research/GATE13_VISUAL_REFERENCE.md`. It confirms the original main-menu and
TeamSelect compositions/labels while explicitly remaining non-canonical for
pixel coordinates and non-authoritative for shipped asset bytes.

## Exact next task

1. Retry byte access in a working execution container using the durable source
   locator in `research/ORIGINAL_SOURCE_LOCATOR.md`. Materialization has
   already been proven to succeed; do not ask for a re-upload. Run
   `reconstruction/gate13_source_inventory.py --deep` against the recovered
   ZIP. The tool now performs ZIP -> raw MODE1/2352 -> temporary ISO9660/Joliet
   inventory using the repository-native reader, without requiring 7-Zip for
   this documented source path, and emits the complete disc file catalog plus
   targeted Gate-13 candidates. Use `--extract-path <exact-disc-path>` with
   `--extract-candidates-to` for deliberately selected opaque resources.
2. Once the real full-disc report exists, follow
   `research/GATE13_CATALOG_SEARCH_PLAN.md` and use
   `reconstruction/gate13_catalog_query.py` to narrow directories/extensions
   and opaque path leads without re-reading the source archive. Emit a
   reproducible `--paths-only` shortlist and feed it back through
   `--extract-path-file --only-explicit`. Inventory the exact original graphics, strings,
   rectangles/layout data and other resources required by PStartMenu and
   TeamSelect, using the bounded secondary screenshots only as a visual
   cross-check.
3. Identify source paths/hashes and import only the minimum intentional first
   slice with `reconstruction/gate13_asset_import.py`, which writes under
   `original_assets/source/` with manifest provenance.
4. Connect the verified `front_end_session.py` application boundary to the
   source-derived PStartMenu/TeamSelect visual renderer. Keep simulation
   separate; reuse the established headless New Game, Back, and
   Start/Continue handoff rather than recreating those rules.
5. Regression-test the first recognizably original main-menu -> TeamSelect flow
   before moving to manager home.

The priority is **original look and interaction flow**, not redesign.

## Known live fidelity boundaries

See `research/FIDELITY_GAPS.md`. The two known secondary-schedule assertions,
original FM2001 save compatibility, residual transfer/finance branches, the
special both-controlled-participants Cup revenue policy, and presentation/audio
fidelity remain explicit later work.

## Do not work on yet

Unless required to support the active Gate-13 presentation slice, defer:

- Gate-14 FastView/3D and audio/match presentation;
- Gate-15 broad fidelity sweep;
- Gate-16 destructive multi-season testing;
- Gate-17 release audit.

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
9a6bd853010e6492f3f96f89e68dc0f0dea68e3a
Reproduce MODE1 source conversion for Gate 13
```

GitHub Actions ran **847 tests with 2 failures**, exactly the two long-standing
secondary-schedule assertions:

- secondary root-order assertion;
- secondary bucket-count assertion (262 expected vs 280 recovered).

All new Gate-13 navigation, source-inventory, MODE1-conversion, and
provenance-import tests passed. GitHub repository asset policy passed.

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

The authorized source archive now has a durable private locator in
`research/ORIGINAL_SOURCE_LOCATOR.md`. This recovery resolved the exact
511,121,336-byte Library file and materialization reported success, but the
current CAAS/container still returns a container-level `ClientError` even for
a simple read/list operation on the materialized path. Persistent source
recovery is therefore working; execution-container byte access is the remaining
infrastructure blocker. No visual asset has been guessed or substituted;
`original_assets/MANIFEST.md` remains intentionally empty.

Repository-native ISO9660/Joliet inventory is now implemented in commits
`784a9095f072f25c6980fe0ffc346e9d8db67576` and
`971bea6ce8caffa778cd713d1e0718907154f32d`. After raw MODE1/2352 conversion,
Gate-13 filesystem enumeration and candidate extraction no longer require
7-Zip. Focused tests cover direct Joliet extraction and nested
ZIP -> MODE1/2352 -> ISO9660/Joliet inventory. CI status for these newest
commits was not yet available at the checkpoint, so the latest CI-verified
baseline above remains unchanged.

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
   this documented source path.
2. Inventory the exact original graphics, strings, rectangles/layout data and
   other resources required by PStartMenu and TeamSelect, using the bounded
   secondary screenshots only as a visual cross-check.
3. Identify source paths/hashes and import only the minimum intentional first
   slice with `reconstruction/gate13_asset_import.py`, which writes under
   `original_assets/source/` with manifest provenance.
4. Bind the already-verified presentation/navigation boundary to the recovered
   original resources without moving simulation logic into presentation code.
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

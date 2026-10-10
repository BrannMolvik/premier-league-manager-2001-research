# Recovery 505 — Firsthand source: Southport's Conference identity and original League member preparation

**11 October 2026 KST.** This is a new, independently reproduced original-disc and PE inspection following the restoration of local execution; **not** a simulated Windows 11 playthrough, fixture matrix implementation, or Gate 13 closure. Main at source verification: `138f80651828848193316c976aa4023ac379c0f9` (after tested PR #569 merge).

## Authorized source and reproducibility

Read the already-authorized private archive from the Library source location specified in `research/ORIGINAL_SOURCE_LOCATOR.md`. Do not commit or distribute it. Its original ZIP SHA-256 was revalidated as `677dcbc859109818d22599f34890ca7873393aea5adbf1f1a32d1a76f8a8a4`. Extracted the MODE1/2352 `famg2001.bin`, selected the source ISO Joliet descriptor `%/E`, used 2,048 bytes at physical sector offset 16, and extracted the actual root `/footballmanager.exe`, `/Master.dat`, `/Static.dat`, and `/English.str`. The binary is 4,714,541 bytes with previously pinned SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`; checked both hashes again during this recovery. The three original database artifact SHA-256 values are:

- `Master.dat` (3,391,446 bytes): `183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8`;
- `Static.dat` (86,929 bytes): `e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8`;
- `English.str` (369,644 bytes): `aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601`.

The existing `reconstruction/iso9660_reader.py::RawMode1IsoImage` and `reconstruction/fm2001_data.py` document the source catalog and field layouts. Master club records begin at offset 4 with stride 181 bytes; record `349` stores the name IDs at +4/+6, source competition ID at +8 and country ID at +12. `Static.dat` competitions begin at offset `0x2726+4`, stride 53 bytes, with competition ID at +0, country at +27, kind byte at +14, signed parent at +4, initialization ordinal at +15 and scheduled matchdays at +18. `English.str` resolves the original names through its indexed CP1252 NUL-terminated payload.

## Southport source identity: now closed, do not use League 27

The real imported club 349 is **Southport**, source short name **Southport**, original `DBRClub+0x10` competition **7**, `DBRClub+0x14` country **26 (England)**. Competition 7 is `Conference`, root parent `-1` (no parent), runtime kind **1 (League)**, initialization order **13**, source scheduled matchday count **42**, source calendar container code **1**, and exactly **22** imported member clubs. All 22 have individually distinct CP1252 source short-name keys, and Southport appears in that 22-member set.

**Competition 27** is a completely different original record: `Premiership`, country **66 (Scotland)**, root kind 1, scheduled matchday count 38. A contemporaneous source event token `('league_match',27,0,18)` cannot be used to infer Southport's competition. This positively resolves the source-identity gap flagged in `research/LEAGUE_FIXTURES_NONPL_SOURCE_PRODUCER_BOUNDARY_2026-10-11.md`. For a freshly started career the default PLeagueFixtures and PLeagueTables selected League for Southport must therefore be Conference **7**, not PL **0** or Scottish **27**; any later season transition must read the *current* retained membership rather than hardcode 7.

The source English root League family, after native country `+0x48` kind/order filtering, is:

| Original League ID | Name from English.str | Kind | Initialization | Source members |
| --- | --- | ---: | ---: | ---: |
| 0 | F.A. Premier League | League 1 | 9 | 20 |
| 2 | Division 1 (ENG) | League 1 | 10 | 24 |
| 3 | Division 2 (ENG) | League 1 | 11 | 24 |
| 4 | Division 3 (ENG) | League 1 | 12 | 24 |
| 7 | Conference | League 1 | 13 | 22 |
| 89 | Conference 2 | DummyLeague 3 | 14 | 15 |

`Conference 2` is NOT one of the five actual `League` RTTI cast-success options, though present in the country LeagueBase family. For Southport the fifth dynamic League radio is **event 13** (events 9–14, using original zero-based League option index 4); the source PLeagueTables five-division radio also uses native event 13. Neither statement supplies unverified on-screen hit geometry.

## Firsthand original PE member-sort dispatch closure

Disassembly from the hash-verified PE confirms the concrete virtual function behind the original League preparation. `PLeagueFixtures::0x46D950` calls `League::0x4F4940` at `0x46D9DA` and `0x46DAE8`, then enumerates `League+0x34` ordered member pointers and assigns their team index at `DBRTeam+0x2A0`.

`League::0x4F4940` at `0x4F4943` first tests `League+0x40 bit0` (source preparation/cached ordering). When unset, `0x4F4949` invokes virtual **vtable+0x38**. The verified League vtable `0x7C9AC0` has pointer `0x4F4720` at slot `0x7C9AF8`. That function calls the original CRT `qsort` at `0x668DA4` with data pointer `League+0x34`, item count `League+0x38`, item size **4 bytes**, and comparator **`0x4F45E0`**. The original comparator's points, played, difference, for, against, CP1252 short-name ordering is already source-recovered in `research/GATE13_LEAGUE_TABLE_PRESENTATION_CONTRACT.md`. `0x4F4720` also resets `League+0x58` to zero. After this call, `0x4F4957–0x4F4968` writes one-based rank at member `+0x28` and `0x4F496A` sets the prepared bit `+0x40 bit0`.

**New practical conclusion:** For an eligible live non-PL League with a complete native participant set and qualified numeric/CP1252 comparison keys, the `0x4F4940` *member order* is precisely the `0x4F45E0` sort used for native League Position. It is **not** the first home/away fixture encounter order that currently happens to be stored in `LiveProceduralLeagueState.club_ids`. Current port `exact_ranking(source_short_name_key)` is a suitable source-bounded candidate when full key equality is resolved conservatively. The original also caches preparation and may clear/recompute during calendar updates; do not assume that immutable startup order persists through played matches.

## Original fixture-chain ordering remains a distinct blocker

Independently checked the exact original `0x46D9FF–0x46DAB7` path: it walks the global source fixture array `0x947AD8` from byte-offset 0 to `0x5D4` in strides of four, **373 heads**; per-head fixture chain uses `fixture+0x04`. It checks source fixture virtual+0x28 kind1, selected League pointer at `+0x4C`, rejects `+0x44 bit0x20` and requires two resolvable clubs before filling first-free directed-pair layer. This corroborates but does not yet replace the earlier Recovery153 source trace.

The physical 373 heads have a further newly confirmed allocation detail: native `0x615670` constructs the table at `0x947AD8` with requested length `0x16E = 366` through `0x615700`, whose `0x61573B` rounds capacity to **requested+7 = 373**. `0x615A60` is one insertion function; at `0x615AC6–0x615ACB` it links a node to the *front* of its chosen slot's chain, so per-slot encounter order cannot simply be equated to forward scheduler insertion order. `0x615950` is another insertion path called by source primary League preparation. The exact slot assignment and relationship of these calls to clean-room `primary_schedule_shadow` still require tracing. No verified source equivalence from symbolic schedule token ordering to native 373-head encounter/slot order is established by this memo.

## Recovery505 additional first-hand fixture-bucket insertion/port equivalence inspection

Further disassembly of the same SHA-verified original PE (without executing it) confirms source bucket mechanics, narrowing the previously open 373-head encounter-order question for the **fresh primary season**:

- `ScheduleContainer::0x615950` is called by original primary League producers at `0x4F66E8`, `0x4F6A21`, `0x4F6A83`. Its `0x615A26–0x615A4D` tail inserts the newly constructed node at the selected bucket's linked-list **head**. `0x615890` probes the original +/-1 nearby buckets for conflicts, and `0x615950` performs the original fallback displacement. `0x615670 → 0x615700` establishes the primary 373-slot array.
- This was **already implemented and previously source audited** in `reconstruction/primary_schedule.py`: `place_primary_schedule_nodes` performs the original relative date placement, +/-1 conflict probe, outward conflict search, Christmas exception and head insertion; `shuffle_primary_schedule_buckets` implements `0x615BE0 → 0x615AE0` descending Fisher-Yates rewiring of each linked bucket. `reconstruction/canonical_matchday_audit.py` verifies startup deterministic source seed, original primary bucket digest, original League fixed 38-round scheduler order, and post-shuffle RNG state. `reconstruction/primary_schedule_shadow.py::from_primary_schedule_buckets` retains the **exact shuffled per-day head-to-tail node sequence**. These existing source-backed receipts should be reused, **not duplicated** in a new approximate fixture-sort implementation.
- The source `0x46D950` matrix scans bucket indices ascending (373), then traverses node `+0x04` links head-to-tail. Consequently, the port's **verified fresh primary** shuffled buckets have a credible source-accepted fixture encounter-order producer: flatten original primary bucket sequence with the original node order retained. This removes the earlier assumption that the port only has arbitrary fixture-first-encounter or date/ID sorting. **Qualification remains necessary:** map every relevant original fixture node kind1, selected competition pointer, `+0x44 bit0x20`, resolved club sides, one-based prepared index, and source-linked PMatchInfo context; reject unknown/dynamic reinsertions. `PrimaryScheduleShadowState.days` and the live `LiveProceduralLeagueState` may contain different representations or subsets of those native records, so the complete source-filtered candidate list cannot be called proven solely by this disassembly.

**Recommended next real functionality slice after PR570:** original first-season Conference7 fixture matrix built from the *existing canonical primary shuffled source buckets*, joined to the newly source-qualified League member order; preserve opaque procedural node tokens (do not forge native integer fixture IDs), reject unknown status/link semantics, and block PMatchInfo where source secondary context is absent. Then test Southport actual Conference vs unrelated Scottish27 and normal country/League selectors on Windows11. This is a concrete route toward **actual fixtures**, not another source-only review task.

## Next implementation/acceptance requirements

1. Add source-backed Southport Conference7 and English five-League/DummyLeague exclusion regressions to current-club `original_league_fixtures_selector_context`; use actual current membership on a later transferred/transitioned season.
2. For a genuinely materialized, complete non-PL source League, use the original `0x4F4940 → vtable+0x38 → 0x4F4720 → qsort(0x4F45E0)` member order, never fixture first encounter order. PR569 has already independently implemented this comparator in PLeagueTables under strict source guards, but it has *not* established actual PLeagueFixtures rows.
3. Resolve native `0x615950/0x615A60` slot and linked-node encounter order from actual original primary event producers, preserving source RNG and statuses, before filling the non-PL matrix; preserve native repeat-layer handling, original date/status text and guarded PMatchInfo links.
4. Complete ordinary country/League GUI radio controls, selected League switching, and independent country/division/form controls for PLeagueTables; verify real mouse interactions and source clip geometry on Windows 11. Gate13 and Gates14–17 remain OPEN until their full audits.

**Source policy:** only metadata, source-address proof, and derived research may be published here. No copyrighted private executable, ISO, ZIP, disc files or raw extraction were added to GitHub.

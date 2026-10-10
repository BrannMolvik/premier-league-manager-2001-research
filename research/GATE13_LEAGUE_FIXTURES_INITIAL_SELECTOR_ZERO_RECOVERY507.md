# Recovery507: native PLeagueFixtures initializes all eight country League slots to zero

**11 October 2026 KST, after the merged Recovery506 geometry milestone**. **Original executable firsthand instruction evidence; no original-game execution.** Canonical root `footballmanager.exe` 4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, privately extracted from user-authorized original disc. Nothing from the disc was committed.

## Recovered constructor writes

`PLeagueFixtures` concrete constructor `0x46D470`, near end at **`0x46D5FC..0x46D60C`**:
```asm
46d5fc: lea edi,[esi+0x68]     ; selected League index array
46d5ff: mov ecx,0x8            ; all eight country entries
46d604: xor eax,eax            ; integer zero
46d606: mov [esi],0x7c24b8    ; PLeagueFixtures vtable
46d60c: rep stos DWORD PTR es:[edi],eax
```
The original intentionally initializes all eight per-country selected League indexes to **0**, not uninitialized memory or an arbitrary unknown. This is the first hand proof absent from Recovery154/502. When panel setup runs, `0x46AFE0..0x46B028` resolves the current human club's League pointer and original country competition-array index using `0x4056F0→0x410FF0`, then **overwrites only `panel+0x68+4*active_country`** at `0x46B028`. A currently managed club in the second German League starts with indices `[0,1,0,0,0,0,0,0]`; an English Conference League manager starts with England's actual source-ranked radio, not always zero.

Native country event `PLeagueFixtures::0x46E040` (e.g. `0x46E2E3..0x46E2F6` for event1) changes `+0x64`, calls `0x46D840` for that country's original `LeagueBase→League` candidate list, then `0x46D950` fixture matrix and `0x46DCD0` refresh. This does **not** reinitialize the selected League index: returning to a country retains its prior selection. Explicit League radio events 9..14 update only the active country's own `+0x68` slot; Recovery154 already proved dispatch and per-country storage. Source `0x46D840` highlights selected `radio[index]` through vtable+0x98. The original bound is still 1..6 eligible true League radios per country; DummyLeague, Cup and child competitions are not source-equivalent.

## Clean-room correction

`reconstruction/original_league_fixtures_selector_context.py` formerly represented seven non-current countries as `None`, and so refused an ordinary country switch even though the original constructor explicitly gave that country its first real League. It now source-initializes **all eight indexes zero**, overwrites current club's country from source membership and exposes first real League when changing countries. The context remains an immutable **identity/selector** projection, not permission to display arbitrary League fixtures. Existing per-country event transactional guards remain intact.

Updated the dedicated selector tests to verify initial zero state, cross-country first-radio selection, correct managed-club override, separate persistent per-country choices, and hidden radio refusal. Added both selector module and its test path to the existing **Gate13 focused and full reconstruction PR CI triggers** once, so future selector changes receive normal exact-head integration verification without triggering unnecessary checks on unrelated research commits.

## Explicit incompleteness

The managed-club-only `ManagementSourceDataBridge.league_fixtures_grid_source()` is **not** a backend for the alternate source-selected League. Source-derived country zero now enables correct selection **identity** but must not be connected to normal GUI rendering without source-accepted input/qualified alternate League fixture producer. No GUI pointer owner, original header/caption raster, live alternate-League results, native link-based PMatchInfo dialog, Windows11 acceptance, Codex R1 changes, Gate13 closure, Gate14–17 or release claim.

**Next**: source-qualified selected-competition matrix for original radio events (Premier League and other true root Leagues), preserving 0x4F4940 prepared members and 373-head linked calendar encounter, then guarded native Tk paint/event integration. This is a user-visible playability task, not perpetual passive source cataloguing.

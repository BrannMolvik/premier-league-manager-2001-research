# Recovery 506: Original PLeagueFixtures country and League radio rectangles

**11 October 2026 KST. Gate 13 OPEN.** Started at verified main `3748862d2814fc8a7aba6ceef73034ed0d958a1c`. This is independent, fresh canonical-PE instruction evidence, not observation of an original-game process or Windows11 GUI click acceptance.

## Private original reference

Recovered the authorized original disc-image ZIP through the private Library location in `research/ORIGINAL_SOURCE_LOCATOR.md`; extracted the original root `footballmanager.exe` **without executing it**. Its 4,714,541 bytes match original SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Reproduced with `objdump -d -Mintel` at all addresses below. No original executable, archive, disc or original asset bytes are published.

## Exact constructor and coordinate producer

- `PLeagueFixtures::0x46AA70` binds first header at panel `+0xA8`. `0x46AB02–0x46AB13` calls `0x5D6090` with x=`0x1B`=27, y=`0xEB`=235 and wrapper `0x946AF0`. Wrapper initializer `0x5F38C0–0x5F38E8` sets width 183 and height 20.
- Header dimensions and the bottom ordinate are not an assumed graphic box: `0x5D6090→0x5D5EB0→0x651E30→0x651BA0→0x64F380` passes wrapper `+0x14/+0x18` width/height into base control rectangle. `0x64F394/0x64F3A4` writes y and y+height to control `+0xC/+0x14`; first header bottom is **255**.
- Country radios are eight `fmRadioTextSm@fm2001_ctrls` controls at `PLeagueFixtures+0x110` stride `0x4C`, with original events 1–8 and country order England26, Germany33, Italy40, Spain73, Scotland66, France31, Holland24, Belgium9. The first uses header bottom+1. Subsequent constructors offset by `0x9450C8+2` per radio. The radio wrapper initializer `0x5F74D0–0x5F74F8` gives height **18** at `0x9450C8`.
- `fmRadioTextSm` setup `0x5D4C70–0x5D4C8B` calls `0x64F380` with width `0xB6`=**182**, height `0x12`=**18**, x=27 and the native constructed top y. Thus eight source country rectangles are **(27, 256+20*i, 182, 18)**, `i=0..7`, top y 256,276,296,316,336,356,376,396.
- The League header at panel `+0x370` is placed by `0x46AFB4–0x46AFCA` at last country radio bottom (`PLeagueFixtures+0x338`=414) **+10**, x=27, width183 height20. Its top is **424**, bottom **444**.
- Six original League radio controls at `+0x3B8…+0x534` use the same class: `0x46B04D–0x46B069` starts at header bottom+1, and `0x46B096–0x46B20B` increments with source 18+2. Six candidate rects are **(27, 445+20*i, 182, 18)**, `i=0..5`, event IDs9–14. The final candidate spans y545..562.
- The native `PLeagueFixtures::0x46E040` events1–8 and 9–14 map to country and League selections as separately established in Recovery154. Native RTTI `LeagueBase→League` hides unused radio options. The original five English Leagues include Conference7 (Southport349's own fifth selection/event13), while `Conference 2` DummyLeague3 is excluded, leaving England's sixth radio/event14 absent.

## Safe code seam and verification

`reconstruction/original_league_fixtures_radio_layout.py` exposes source-coordinate **candidate** rectangles and filtered point lookup, never claiming native child hit-test acceptance or dispatch. Explicit 1..6 eligible League radios, integer-coordinate guards and suppression of absent options preserve source safety. Six direct source-derived local `unittest` tests passed (control census, names/events, exact bounds, 2px gutters/header, England hidden sixth, invalid values). Full repository/CI validation still required at exact feature branch head. No protected Codex R1 central NEXT/pre-match/match/results or host mouse code touched.

## Not closed / next major task

The original `fmRadioTextSm` actual hit ownership, visibility flags, font/caption/raster, default selection on a different country, and per-country preserved indices need further original source proof. Crucially the current integrated `league_fixtures_grid_source()` is only source-qualified for the **managed club's current League**. Connecting alternate-League clickable radios to that data would falsely render Conference under another League. Next complete vertical slice: source-prove native radio click/event owner and qualify alternate selected-competition fixture producer before atomic normal GUI event/render integration. Follow with country8/division5/CurrentForm League Tables; respect Codex R1 lock and actual Windows11 acceptance. **Gate13 and Gates14–17 and Windows11 release remain OPEN.**

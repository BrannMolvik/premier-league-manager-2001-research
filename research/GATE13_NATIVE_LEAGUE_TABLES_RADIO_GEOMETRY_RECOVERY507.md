# Recovery 507: independently traced PLeagueTables native radio rectangles

**11 October 2026 KST; Gate 13 OPEN.** This result was derived from the original private executable, **not** from the existing reconstruction and **not** from observing a running original game.

## Source provenance

Authorized original disc ZIP: Library `/FM2001/Original Source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`. Recovered the MODE1/2352 Joliet root `/footballmanager.exe` in a new healthy Linux container, without launching the game. Verified original executable: 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Disassembled with `objdump -Mintel -d`; no original executable or asset bytes are committed.

## Original constructor-to-rectangle chain

- `PLeagueTables::0x446F00` constructs and installs eight country `fmRadioTextSm` objects starting at panel `+0x23C` (`0x446FE5..0x44728F`), five DIVISION objects at `+0x4E4` (`0x447306..0x447440`) and two Sort By objects at `+0x6A8` (`0x4474B5/0x447501`). Original source event IDs are respectively **1..8**, **9..13**, **14..15**. Country/Division distinction must not be conflated with the separate six-League PLeagueFixtures selector.
- Each radio setup calls `fmRadioTextSm::0x5D4C70`, which at `0x5D4C7C..0x5D4C8B` passes **width 0xB6 = 182, height 0x12 = 18** into base rectangle setup `0x64F380`. At `0x64F38F..0x64F3A4` the native base stores left/top and right=left+width/bottom=top+height.
- The shared header text wrapper at `0x5D6090` uses `0x946AF0`, initialized at `0x5F38C0..0x5F38E8` with **183x20**. The Country header call `0x446F92` gives x=27/y=150, so its bottom is y=170.
- First country radio `0x446FE5` explicitly pushes x=27, y=`0xAC`=**172**. Remaining seven constructors encode `0xAE+height*1`, `0xB0+height*2`, … `0xBA+height*7` using original global `0x9450C8` whose line height is **18**, establishing x27/y**172+20*i** for i0..7. Last country candidate ends y330 (half-open).
- Division header `0x4472AA..0x4472C1` uses last radio bottom `panel+0x464 + 10`, so header starts y340 and ends y360. First Division radio `0x447306` uses `panel+0x4B0 + 1`, thus y**361**; subsequent constructors `0x447353/0x4473A1/0x4473F2/0x447440` use `header_bottom + (height+2)*i +1`, giving y**361+20*i** (i0..4).
- Sort By header `0x44745B..0x447472` uses last Division radio bottom `panel+0x628 + 10`: y469..489. First Sort radio `0x4474B5` uses `panel+0x674+1`: y**490**. Second `0x447501` uses `panel+0x674+height+3`: y**510**.
- All 15 fully constructed control *candidate rectangles* are **(27,y,182,18)**. The country headers/gutters, Division and Sort headers and unused Division slots are not candidate radio targets. Native `0x448E60` can hide unused Division controls, so code requires the exact known number 1..5 and rejects coordinates in hidden slots.

## Source-qualified implementation and local check

`reconstruction/original_league_tables_radio_layout.py` adds a pure geometrical candidate enumeration/hit rectangle helper with strict integer and source-capacity gates; no host handler calls it. Five independent local Python regression cases verify all 15 family/event mappings, source ordinates and edges, 2-pixel gaps, absent divisions, invalid positions/counts. The source suite must also pass on exact PR head before merging. No original assets or binaries are added.

## Crucial remaining native interaction boundary

Freshly traced native `fmRadioTextSm` vtable **0x7D6AB8** and method **0x5D4AC0** show a callback path that checks `this+0x18 bit2`, selected/activation state `this+0x40`, and delegates to a parent callback `this+0x24` before invoking virtual selector +0x98. Shared `0x5D4680` traverses children, tests child flags, clips child rectangles, and dispatches their virtual child method. **This does not yet prove the complete incoming screen mouse-event entrypoint, child focus/clip acceptance, panel-parent callback dispatch and visible caption/raster matching**, so merely containing a candidate rectangle must not invoke `source_accepted_league_tables_radio_event` in the Tk host. Original `0x4F4A10` Current Form ordering, alternative original Premier0 fixture selection, full-game GUI and real Windows11 human acceptance also remain open. The next investigation must close those exact input/owner/caption paths or advance other fully source-qualified high-impact functionality without pretending the panel is clickable.

**Gate 13, Gates 14–17, full original-scope verified Windows 11 release all remain OPEN.** Protected Codex R1 NEXT→PPreMatch→Quick3→PResults untouched.

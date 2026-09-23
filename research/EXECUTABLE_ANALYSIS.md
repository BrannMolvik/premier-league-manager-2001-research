# Executable Analysis

## Binary identity

- Executable: `footballmanager.exe`
- SHA-256: `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
- Architecture: 32-bit x86 PE
- Application type: native Windows GUI application
- Era: built in 2000
- Compiler clues: Microsoft C++ RTTI is present extensively

## Important imports / runtime families

Verified legacy runtime/API families include:

- DirectDraw
- DirectInput
- DirectSound
- WinMM
- ADVAPI32 registry APIs
- GDI32
- USER32
- KERNEL32

The title is a Windows game, not a DOS executable.

## Source-path leakage

The binary retains original development paths that make subsystem identification unusually strong.

Examples include:

- `D:\Projects\FM2001\Applications\FootballManager\Season.cpp`
- `...\Training.cpp`
- `...\Scouting.cpp`
- `...\TransPan.cpp`
- `...\Youth.cpp`
- `...\MatchFrontEnd.cpp`
- `...\FastView\MatchController.cpp`
- `...\FastView\PossessionFigures.cpp`
- `D:\Projects\FM2001\Libraries\Database\Club.cpp`
- `...\Player.cpp`
- `...\Competitions.cpp`
- `...\Match.cpp`
- `...\Game.cpp`
- `...\PlayerMovements.cpp`
- `...\ManagerMovements.cpp`
- `D:\Projects\FM2001\Libraries\MatchCalculator\MatchRecord.cpp`
- `D:\Projects\FM2001\Libraries\MatchEngine\MatchEngine.cpp`

## RTTI / recovered subsystem map

MSVC RTTI exposes database record/table concepts including:

- clubs
- players
- managers
- countries
- nationalities
- positions
- statuses
- rounds
- competitions
- league allocation
- cup allocation
- fixtures
- manager ratings/sacking
- formations

Match/event RTTI exposes concepts for:

- goals / own goals
- possession
- score
- substitutions
- half time / full time
- extra time
- penalties
- player form / energy

This supports a layered architecture in which database/season state, match calculation and FastView/3D presentation are separable.

## Tuning system

The executable contains hundreds of human-readable tuning-key names.

Static disassembly indicates a named-key loader that parses key/value data and assigns values to global simulation variables.

High-value future work:

1. identify the tuning source file/resource;
2. map string-key references to loader calls/target globals;
3. recover defaults and units;
4. connect variables to transfer, finance, training, development and match formulas.

## Save system

Located strings include:

- `games\\%d.sav`
- explicit incompatible-save/version text

The actual serializer/deserializer has not yet been mapped.

## Runtime failure on Windows 11

The user's host Windows 11 system blocks the analyzed legacy executable under Code Integrity/Smart App Control.

Code Integrity Operational Event ID 3077 explicitly identified:

`C:\Games\FM2001\footballmanager.exe`

Consequences:

- compatibility mode does not address the current host block;
- launching from CMD does not bypass it;
- administrator elevation does not bypass it;
- binary modification also remains subject to the same trust policy.

Static reverse engineering and clean-room reimplementation can continue without executing the blocked binary.


## Manager-control RTTI / record methods

MSVC RTTI has now been followed from type descriptors through Complete Object Locators to vtables for four manager-control table/record pairs.

Recovered table vtables and record-access/allocation behavior:

- `DBTManagerRatings`: table vtable at approximately `0x7BD454`; record indexing uses 12-byte in-memory records.
- `DBTManagerExpectedRankings`: table vtable at approximately `0x7BD494`; record indexing uses 16-byte in-memory records.
- `DBTManagerSackLeagues`: table vtable at approximately `0x7BD4D4`; record indexing uses 12-byte in-memory records.
- `DBTManagerSackCups`: table vtable at approximately `0x7BD514`; record indexing uses 12-byte in-memory records.

Recovered record vtables / parse functions:

- `DBRManagerRating`: vtable ~`0x7BD468`, parser ~`0x4013B0`
- `DBRManagerExpectedRanking`: vtable ~`0x7BD4A8`, parser ~`0x4014B0`
- `DBRManagerSackLeague`: vtable ~`0x7BD4E8`, parser ~`0x4015D0`
- `DBRManagerSackCup`: vtable ~`0x7BD528`, parser ~`0x4016C0`

The parsers reveal different combinations of 32-bit, 16-bit and 8-bit fields.

Important caution: the 12/16-byte sizes above are **in-memory record strides**, not automatically the packed on-disk `Static.dat` size. Known position/formation/status parsing code demonstrates that file serialization can pack fields differently. Therefore the 108-record block at `Static.dat +0x1181B` remains an unresolved candidate and must not yet be labeled as a manager table solely because 16-byte grouping appears possible.



## Player runtime object / save-state structure

The player table has now been followed through RTTI and its record accessors.

- `DBTPlayers` vtable: approximately `0x7BDA78`
- player-record accessor: approximately `0x416F90`
- runtime record stride returned by the table: `0x250` bytes = **592 bytes**
- `DBRPlayer` vtable: approximately `0x7BDEDC`
- a large player binary/save reader begins around `0x416210`

This is a critical distinction from the compact 103-byte player record in `Master.dat`: the initial database record is expanded into a much larger runtime object that contains mutable career/game state.

The runtime/save reader includes two loops reading 17 one-byte values into adjacent arrays:

- runtime offsets `+0x1E..+0x2E` (17 bytes)
- runtime offsets `+0x2F..+0x3F` (17 bytes)

The exact semantics of those paired arrays are not yet proven. A base/current, current/potential, or similar skill pairing is plausible, but remains a hypothesis until accessor/consumer code is traced.

The compact `Master.dat` player attribute bytes must therefore be analyzed separately from the runtime/save representation rather than assuming identical layout or scaling.

## Player-rating labels visible in resources

`English.str` exposes 13 clearly player/scouting-facing dimensions:

- Speed
- Strength
- Stamina
- Determination
- Passing
- Shooting
- Tackling
- Heading
- Control
- Agility
- Keeping
- Confidence
- Influence

Scouting commentary strings occur in matching groups for these dimensions, providing strong evidence that these are core visible evaluation axes.

Additional strings elsewhere include `INJURY PRONENESS`, `TECHNIQUE`, `HANDLING`, `CREATIVITY`, and `OFFENSIVE`. Their existence is verified, but they are **not yet proven** to correspond directly, or in that order, to the remaining bytes of the compact player record.




## Master.dat startup loader and compact player importer

The actual `master.dat` startup path has now been located.

A reference to the `master.dat` filename at approximately `0x827F48` leads to the loader around `0x50D630`.

Its sequence is:

- clubs: global table around `0x874B88`, specialized loader `0x40B9C0`
- players: global `DBTPlayers` object around `0x875638`, specialized loader `0x4218C0`
- managers: global table around `0x875620`, specialized loader `0x415B70`

For players:

- `0x4218C0` calls `0x421C80` and then post-processing `0x421CE0`
- `0x421C80` reads the player count, allocates 592-byte runtime records, and loops over all records
- each compact player is imported by **`0x418B90`**

### Compact player importer `0x418B90`

`0x418B90` performs 35 direct file reads via `0x667E90`.

Read sizes:

`2,2,2,2,1,1,4,4,1,1,1,3,17,17,1,1,1,1,1,1,4,8,4,2,2,1,1,1,1,4,4,1,2,2,2`

Their sum is **103 bytes exactly**, independently confirming the player-record size.

Key consequences:

- the player record contains a 3-byte compact position-related group at file `+21..+23`;
- it contains two **17-byte arrays** at file `+24..+40` and `+41..+57`;
- those arrays copy directly into runtime object `+0x1E..+0x2E` and `+0x2F..+0x3F`;
- the earlier hypothesis of an 18-byte attribute block at `+22..+39` is wrong.

The position-data temporary is passed through `0x4EA2D0` and expanded into a runtime position structure.

Two early 16-bit file fields are processed through helper `0x64E320`, which indexes a shared table/reference object (argument based around global `0x876CA0`) and stores pointers into runtime offsets `+0x08` and `+0x0C`. The purpose/type of `0x876CA0` remains an active target and is necessary before confidently naming those early fields.

No further disk reads occur after the final 103rd byte; the rest of `0x418B90` derives and initializes runtime state.

### Import-vs-save distinction

This establishes three separate player representations/workflows:

1. CSV/editor-style parser around `0x415CD0`;
2. compact `Master.dat` startup importer `0x418B90`;
3. full runtime/save binary reader around `0x416210`.

These must be analyzed separately.

## Core.str reference-table identification

Global object `0x876CA0` is now identified directly as the loaded `core.str` indexed-string table.

Evidence:

- startup at `0x50D3AD` sets ECX to `0x876CA0`;
- it pushes literal filename `"core.str"` at `0x827F30`;
- it calls generic string-table loader `0x64E140`;
- compact player importer `0x418B90` passes 16-bit file indices through helper `0x64E320`;
- `0x64E320` uses the table object's pointer array at +8 and stores an indexed reference into the runtime player.

Adjacent globals are sibling language-string tables:
- `0x876C88`: localized language table such as `english.str`
- `0x876C70`: corresponding EAM-language table such as `englisheam.str`

This resolves compact player file offsets +2 and +4 as Core.str references for first name and surname.

## Corrected Master.dat player boundary

Loader `0x421C80` reads exactly one 4-byte player count and then immediately loops over 103-byte records. There is **no additional 2-byte player-section header**.

The prior six-byte-header assumption shifted every inferred player field by two bytes. Corrected verified compact fields now include:

- +0: player record ID
- +2: first-name Core.str ID
- +4: surname Core.str ID
- +6: club index
- +8: nationality ID
- +14: date of birth
- +19: height cm
- +20: weight kg
- +21..+23: three zero-based position codes


## Current executable-analysis priorities

1. Correlate RTTI table classes with `Static.dat` load sequence and record sizes.
2. Build function/subsystem map around season initialization.
3. Locate fixture generation and competition initialization.
4. Locate movement/transfer and finance state transitions.
5. Locate tuning-key loader and recover target globals.
6. Trace MatchCalculator/MatchEngine event production.
7. Trace FastView consumption of match events and rendering state.

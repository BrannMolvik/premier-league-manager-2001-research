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


## Current executable-analysis priorities

1. Correlate RTTI table classes with `Static.dat` load sequence and record sizes.
2. Build function/subsystem map around season initialization.
3. Locate fixture generation and competition initialization.
4. Locate movement/transfer and finance state transitions.
5. Locate tuning-key loader and recover target globals.
6. Trace MatchCalculator/MatchEngine event production.
7. Trace FastView consumption of match events and rendering state.

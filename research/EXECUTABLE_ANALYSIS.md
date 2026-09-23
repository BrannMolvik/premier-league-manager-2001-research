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

## Current executable-analysis priorities

1. Correlate RTTI table classes with `Static.dat` load sequence and record sizes.
2. Build function/subsystem map around season initialization.
3. Locate fixture generation and competition initialization.
4. Locate movement/transfer and finance state transitions.
5. Locate tuning-key loader and recover target globals.
6. Trace MatchCalculator/MatchEngine event production.
7. Trace FastView consumption of match events and rendering state.

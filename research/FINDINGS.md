# Confirmed Findings

This document contains technical findings that have been directly verified against the user's FM2001 disc image and derived analysis files.

## Binary identities

SHA-256 values for the analyzed files:

- `footballmanager.exe`: `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
- `Editor.exe`: `0dd121f1e27906b7c839374288cfb497e38c87595b4736ee2c9febbe956408c5`
- `Master.dat`: `183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8`
- `Static.dat`: `e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8`
- `English.str`: `aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601`
- `Core.str`: `b0800475769fa087e69de989388569e5b29f495e5abe5d62687c2acb1d339e06`

These hashes define the exact analyzed dataset and should be checked before assuming offsets apply to another release.

## String tables

`English.str` and `Core.str` are indexed string tables.

Observed structure:

- file offset +0: uint32 string-data/table boundary
- file offset +4: uint32 string count
- index begins at `table_offset + 8`
- index contains `count` uint32 relative offsets
- each string is NUL-terminated and decoded correctly as Windows-1252
- string byte position is `8 + indexed_offset`

Decoded counts in this release:

- `Core.str`: about 29,033 strings
- `English.str`: about 21,856 strings

`Core.str` contains large numbers of person-name components; early entries resolve the Arsenal-era player sequence beginning David Seaman, Lee Dixon, Nigel Winterburn, etc.

## Master.dat

`Master.dat` is structured and directly parseable, not encrypted.

### Top-level layout

- uint32 club count at file +0
- 1,246 club records
- club record size: 181 bytes
- after club records, a player-section count/header is present
- 30,064 player records
- player record size: 103 bytes
- remaining tail contains 1,612 manager records
- manager record size: 43 bytes
- manager tail is followed by two bytes

### Club records

Confirmed fields:

- +4 uint16: club full-name string ID in `English.str`
- +6 uint16: club short-name string ID in `English.str`
- +16 uint16: map-file string ID
- +30 uint16: stadium-name string ID
- +44 uint16: badge-file string ID
- +46 uint16: sponsor string ID
- +48 uint16: manager record ID

Record 0 resolves to Arsenal and includes strings/assets for Arsenal/Highbury.

### Player records

The earlier player-field map was corrected after tracing EA's actual compact importer.

Confirmed:

- player section header is 4 bytes: uint32 count = 30,064
- compact record size: 103 bytes
- +0 uint16: player record ID
- +2 uint16: first-name ID in `Core.str`
- +4 uint16: surname ID in `Core.str`
- +6 uint16: club record index
- +8 uint8: nationality ID
- +14 uint32: date of birth, OLE-style serial date using epoch 1899-12-30
- +19 uint8: height in centimeters
- +20 uint8: weight in kilograms
- +21..+23: three zero-based position codes
- +24..+40: first 17-byte skill-related array
- +41..+57: second 17-byte skill-related array

Strongly verified:

- +9 behaves as a primary/default zero-based position code
- +18 behaves as shirt/squad number

Example first records resolve correctly when aligned to the true boundary:
- record 0: David Seaman, Arsenal, English, goalkeeper
- record 1: Lee Dixon, Arsenal, English, right back
- record 2: Nigel Winterburn, Arsenal, English, left back

The exact labels and relationship of the paired 17-byte skill arrays remain under active investigation.

### Manager records

Confirmed fields:

- +6 uint16: first-name string ID in `Core.str`
- +8 uint16: surname string ID in `Core.str`
- +10 uint32: date of birth, OLE-style serial date
- +22 uint32: date joined club
- +29 uint32: club ID; `0xffffffff` indicates no current club

Examples:

- manager record 10 resolves to Alex Ferguson
- DOB decodes to 1941-12-31
- joined club decodes to 1986-11-06
- club link resolves to Manchester United
- Arsenal club record points to manager record 204, resolving to Arsène Wenger

## Static.dat

`Static.dat` is a concatenation of typed tables that correspond closely to database classes visible through MSVC RTTI in `footballmanager.exe`.

Confirmed tables:

### Position table

- table offset: `0x25E0`
- count: 20
- record size: 7 bytes
- +0 uint8: position ID
- +1 uint16: long position-name string ID in `English.str`
- +3 uint16: abbreviation string ID in `English.str`

Records decode to positions including Goalkeeper/GK and Right Back/RB.

### Competition table

- table offset: `0x2726`
- count: 193
- record size: 53 bytes
- +0 uint32: competition ID
- +12 uint16: competition-name string ID in `English.str`

Decoded competition names include the F.A. Premier League, FA Cup, English Divisions 1/2/3, League Cup, Charity Shield, Conference, Champions League, UEFA Cup, playoffs and competitions from other countries.

## Executable architecture

The executable contains original source-path strings and MSVC RTTI revealing a modular C++ architecture.

Verified source-path/module strings include:

- `Applications\\FootballManager\\Season.cpp`
- `Training.cpp`
- `Scouting.cpp`
- `TransPan.cpp`
- `Youth.cpp`
- `MatchFrontEnd.cpp`
- `FastView\\MatchController.cpp`
- `FastView\\PossessionFigures.cpp`
- `Libraries\\Database\\Club.cpp`
- `Libraries\\Database\\Player.cpp`
- `Libraries\\Database\\Competitions.cpp`
- `Libraries\\Database\\Match.cpp`
- `Libraries\\Database\\Game.cpp`
- `Libraries\\Database\\PlayerMovements.cpp`
- `Libraries\\Database\\ManagerMovements.cpp`
- `Libraries\\MatchCalculator\\MatchRecord.cpp`
- `Libraries\\MatchEngine\\MatchEngine.cpp`

RTTI also exposes record/table classes for clubs, players, managers, countries, nationalities, positions, statuses, rounds, competitions, league allocation, cup allocation, fixtures, manager ratings/sacking, formations and additional systems.

## Match subsystem

Static RTTI/string evidence shows an event-driven separation between calculation and presentation.

Identified event concepts/classes include:

- goal
- own goal
- possession
- score
- substitution
- half time
- full time
- extra time
- penalties
- player form/energy updates

The executable distinguishes backend match calculation from FastView/3D presentation.

The disc contains approximately 252 binary `.SCI` files under `DataInGame`, plus a readable `camera.scr` describing in-play, set-piece, replay, manual-replay, out-of-play and half-time camera modes. The `.SCI` format is not yet decoded.

## Simulation tuning

The executable contains hundreds of named tuning keys covering areas such as:

- transfer budgets and wage budgets
- transfer limits and negotiations
- injuries
- player aging/development
- stadium costs
- attendance
- merchandising and ticketing
- loans/APR
- training
- youth generation
- tactical biases
- pitch/weather
- manager sacking
- role-specific match-performance rating weights

Static disassembly shows a named-key loader that parses values into global simulation variables. The value source and full variable mapping remain active research targets.

## Runtime compatibility

On the user's Windows 11 system, Code Integrity/Smart App Control blocks the legacy unsigned `footballmanager.exe` before meaningful execution.

Verified:

- launching produces only a brief shell spinner
- Command Prompt launch returned `-1` during earlier tests
- admin launch does not solve it
- Code Integrity Operational log Event ID 3077 explicitly names `C:\Games\FM2001\footballmanager.exe`

Compatibility mode, command-line launch and administrator elevation do not bypass that policy.

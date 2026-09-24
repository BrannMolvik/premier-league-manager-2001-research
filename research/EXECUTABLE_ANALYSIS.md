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



## Player overall-rating formula and tuning-key recovery

Function `0x41C7E0` is a position-specific player-overall calculation.

It dispatches on position ID 1..19 through a jump table at approximately `0x41E160`. The 19 cases correspond to playable positions after the leading "None" position.

The routine converts raw current-skill bytes to 0..30 values and multiplies them by position-specific tuning weights loaded from named keys.

Recovered tweak mappings include:

- `0x821858` = `overallgkgoalkeeping`
- `0x821860` = `overallgkagility`
- `0x821868` = `overallgkawareness`
- `0x821870` = `overallgkpassing`
- `0x821878` = `overallgkspeed`
- `0x821880` = `overallgkconfidence`
- `0x821888` = `overallgkstrength`

The same pattern continues for RB, LB, CD, SW, RWB, LWB, ANC, DM, RM, LM, CM, RW, LW, AM, CF and ST.

For outfield positions, the repeated seven weighted inputs prove the current-skill slots:

- slot 1 = Strength
- slot 14 = Confidence
- slot 0 = Speed
- slot 8 = Heading
- slot 6 = Shooting
- slot 5 = Passing
- slot 7 = Tackling

The goalkeeper case additionally proves:

- slot 11 = Awareness
- slot 12 = Agility
- slot 13 = Goalkeeping

Accessor `0x41EDE0` returns current-skill slot 15, and callers compare it to tweak `goodleadership`, proving slot 15 = Leadership.

### Exact skill scaling

The repeated byte conversion in `0x41C7E0` is mathematically equivalent for raw byte `x` to:

```text
floor((30*x + 128) / 255)
```

so the game maps raw 0..255 skill storage to an integer 0..30 rating.

### Current vs potential/ceiling arrays

Two routines now establish the relationship between the adjacent 17-byte arrays:

- `0x41A870` reads current `[player + 0x1E + slot]` and ceiling `[player + 0x2F + slot]`; it raises current by 8 raw units only when the result remains below the ceiling.
- the development/aging routine around `0x41EB03..0x41EDC8` uses the second-array byte as an endpoint while writing adjusted values into the first-array byte.

A complete scan of Master.dat shows 99.605% of all paired bytes satisfy second-array >= first-array.

Therefore runtime `+0x1E..+0x2E` is the current-skill state and `+0x2F..+0x3F` is the matching ceiling/potential-target state. The small number of exceptions need separate investigation.



## Editor.exe confirmation of complete 17-skill ordering

EA's bundled `Editor.exe` contains a Player Skills dialog (dialog resource ID `0x73`) with 17 editable characteristics.

Parsed dialog controls include:

- Speed
- Strength
- Stamina
- Determination
- Passing
- Shooting
- Tackling
- Heading
- Control
- Leadership
- Agility
- Goalkeeping
- Confidence
- Awareness
- Technique
- Set Piece
- Injury Proneness

The dialog population routine around `0x40D620` binds these controls to an internal contiguous skill-byte region beginning around editor-object `+0x210`.

The binding order by internal byte is:

- +0x210 Speed
- +0x211 Strength
- +0x212 Stamina
- +0x213 Determination
- +0x214 Injury Proneness
- +0x215 Passing
- +0x216 Shooting
- +0x217 Tackling
- +0x218 Heading
- +0x219 Control
- +0x21A Technique
- +0x21B Awareness
- +0x21C Agility
- +0x21D Goalkeeping
- +0x21E Confidence
- +0x21F Leadership
- +0x220 Set Piece

This ordering exactly matches the independently proven runtime slots for Speed, Strength, Passing, Shooting, Tackling, Heading, Awareness, Agility, Goalkeeping, Confidence and Leadership.

Therefore the full runtime current-skill array `+0x1E..+0x2E` is now mapped slot-for-slot as:

`Speed, Strength, Stamina, Determination, Injury Proneness, Passing, Shooting, Tackling, Heading, Control, Technique, Awareness, Agility, Goalkeeping, Confidence, Leadership, Set Piece`.

The second 17-byte array uses the same slot ordering for the corresponding ceiling/potential targets.


## Player aging/development implementation

The player development path is now mapped around `0x41E970` and `0x41EAD0`.

### Initialization at 0x41E970

The routine:

1. reads current player age via `0x4173B0`;
2. selects individualized peak ages from tuning-controlled ranges;
3. stores the current age as development baseline at player `+0x122`;
4. copies the 17 current skill bytes from `+0x1E..+0x2E` into baseline snapshot `+0x111..+0x121`;
5. stores physical, skill and third/goalkeeper peaks at `+0x123/+0x124/+0x125`.

Recovered tuning globals/defaults:

- `0x821130 AGEPhyical_lowest_peak = 25`
- `0x821134 AGEPhyical_highest_peak = 26`
- `0x821138 AGESkill_lowest_peak = 27`
- `0x82113C AGESkill_highest_peak = 29`
- `0x821140 AGEGoalie_lowest_peak = 30`
- `0x821144 AGEGoalie_highest_peak = 32`
- `0x821148 AGEPeakPeriod = 5`

### Monthly recalculation at 0x41EAD0

For each of the 17 skill slots, the routine selects a peak:

- slots 0..4 -> physical peak
- slots 5..8 -> skill peak
- slots 9..16 -> third/goalkeeper peak

For normal forward time, with baseline age `A0`, age `A`, baseline byte `B`, target byte `T`, and peak `P`:

Before peak:
```
C = B + ((A-A0)/(P-A0))*(T-B)
```

When a player crosses the peak, the target is held through the configured peak period. Beyond that period, decline trends toward zero by age 60:
```
C = T * (60-A)/(60-P)
```

If the player's stored baseline is already beyond the peak:
```
C = B * (60-A)/(60-A0)
```

Backward-time/date-edge branches also exist and should be reproduced only after separate verification.

The target byte is not a hard upper ceiling. Original data contains a small number of target < current pairs, consistent with players whose development path is intended to regress.

### Calendar call frequency

The main calendar routine around `0x4A8070` conditionally calls club-table method `0x40BB10` when a decoded date component equals 1. `0x40BB10` iterates club objects and calls `0x4042E0`; that routine iterates each club's players, calls `0x41EAD0`, then monthly post-development/retirement logic `0x41ABC0`.

This is strong evidence that skill-development recalculation runs on the first day of each month.

### Training/modifier layer

After calculating the pure age curve, `0x41EAD0` obtains a club-related 40-entry array:

- 40 records
- 200 bytes (`0xC8`) each
- total allocation `0x1F40` bytes
- allocated around `0x424E46`
- record constructor around `0x424F90`
- pointer stored at owning object `+0x6B8`

The selected record is indexed by a player-assignment byte returned via `0x41E3D0` (player runtime `+0x70` for the current club; `+0x76` otherwise).

Per-skill modifier bytes are read from two regions of that 200-byte record around `+0x30+i` and `+0x54+i`.

Exact record/class identity and the meanings of the two modifier regions remain active targets.

Related training defaults:

- `TRNMax_boost = 8192`
- `TRNBuild_Boost = 65`
- `TRNInjuryReturnDefault = 75`
- `TRN_condition_divider = 512.0`
- `TRN_Condition_Warning_Threshold = 75`


## Club player-training records and training profiles

Training is now confirmed as per-player club state rather than a generic modifier table.

- A club-side object owns 40 records of 200 bytes each (0xC8), total allocation 0x1F40, pointer at owner +0x6B8.
- Initialization around 0x61C9C0 clears all 40 records then walks the club player list and initializes one record per eligible player via 0x61C460.
- Whole-record +8 is a uint16 player ID; unused slots contain 0xffff. 0x61C4B0 resolves it back to the runtime player.
- Player runtime bytes +0x70/+0x76 are 1-based selectors; 0x417380 computes base + (selector-1)*200.
- Embedded training state begins at whole-record +0x24. It contains a method ID, countdown/state, 17 per-skill counters, 17 dword states, seven per-method counters, date fields, and a second 17-byte timed-effect region.
- The monthly development routine reads the primary per-skill byte at whole-record +0x30+skill. Earlier notes suggesting two monthly modifier arrays were incorrect.

Global 0x876B40 is seven contiguous 17-byte skill profiles built by 0x4EAA00. With the verified 17-skill order, vectors identify as: vector0 attacking; vector1 defensive; vector2 midfield; vector3 goalkeeper; vector4 rest; vector5 fitness; vector6 technique.

Profile selector 0x4EA9A0 maps method IDs: 0->rest/recovery vector4, 1->attacking vector0, 2->midfield vector2, 3->defensive vector1, 4->goalkeeper vector3, 5->fitness vector5, 6->technique vector6. Earlier analysis incorrectly labeled ID 1 as NULL: its jump-table target is 0x4EA9DE, which returns with EAX still equal to the base address 0x876B40. Only out-of-range IDs reach 0x4EA9DC (`xor eax,eax`) and return NULL.

Coach dispatcher 0x42C240 maps the same IDs to specialist employee lookups. The lookup routines search employee types 7..12. Their one-to-one agreement with profile semantics and EA's UI labels identifies types 7 goalkeeper, 8 fitness, 9 technique, 10 defensive, 11 midfield, 12 attacking. Method 1 routes to type12 (attacking coach), while method0 and method5 route to type8.

Training update 0x4EACE0 loops all 17 skills. For a nonzero profile weight it combines profile/staff/club multipliers with a random 0..99 roll; if current skill is below development target, it increments the per-skill training counter/state, calls 0x41A870 for a +8 raw-skill step when still below target, and increments the per-method result counter. Zero-profile paths can reverse a prior step via 0x41A9A0 under the internal countdown/state condition.

## Exact active-training success probability

The numerical training-success formula in `0x4EACE0` is now verified instruction-by-instruction.

For each skill with a nonzero profile weight:

```
threshold = profile_weight * quality_multiplier * 0.5
success if random_integer(0..99) < threshold
```

Evidence:

- random source `0x64D540(100)` returns the 0..99 roll;
- constant `0x7BD6A8` is double `0.5`;
- the x87 compare at `0x4EAE09` takes the success path only when the computed threshold is strictly greater than the random roll.

### Quality multiplier

Default multiplier begins at `1.00`.

The routine first searches staff employee type **3** via `0x4D0C10`. EA's own `YouthTeamCoach@ModFmt` formatter at `0x613290` calls that exact lookup, proving employee type 3 is **Youth Team Coach**.

If present, its virtual rating method at vtable +0x40 returns 1..5 and maps to:

- rating 1 -> 1.25
- rating 2 -> 1.30
- rating 3 -> 1.35
- rating 4 -> 1.40
- rating 5 -> 1.45

If no Youth Team Coach is present, the routine searches employee type **1** via `0x4D0B10`. EA's `AssistantManager@ModFmt` formatter at `0x6134F0` calls this lookup, proving employee type 1 is **Assistant Manager**. Presence of an Assistant Manager supplies fallback multiplier **1.25**.

If neither exists, multiplier remains **1.00**.

### Training Centre bonus

The club building/feature collection at club `+0x65C` is queried for feature ID **5** with `0x5EE9A0`.

The external-building factory around `0x5EECB4` constructs `CTrainingBuilding` and passes literal ID **5** to the common building constructor `0x5EF290`. Therefore feature ID 5 is definitively the **Training Centre**.

If present, constant `0x7BD550` (double **0.25**) is added to the quality multiplier.

Thus:

```
Q = 1.00
if YouthTeamCoach exists:
    Q = {1:1.25, 2:1.30, 3:1.35, 4:1.40, 5:1.45}[rating]
else if AssistantManager exists:
    Q = 1.25

if TrainingCentre exists:
    Q += 0.25

threshold = profile_weight * Q * 0.5
success = random(0..99) < threshold
```

For a maximum profile emphasis byte of 25, representative per-update chances are:

- no staff / no Training Centre: 12.5%
- 1-star Youth Team Coach: 15.625%
- 5-star Youth Team Coach: 18.125%
- 5-star Youth Team Coach + Training Centre: 21.25%

The specialist coach selected by training method is handled separately through dispatcher `0x42C240`; additional specialist effects should not be conflated with this Youth-Team-Coach/Training-Centre multiplier until their call path is fully reconstructed.


## Contract / transfer-state analysis

Transfer/contract analysis has begun from `DBRPlayer`, `CDealInProgress`, and the contract-terms object.

### Confirmed player contract fields

- runtime player `+0xC4`: **weekly wage**. Proven by `WeeklyWageCompare` / function `0x40B7F0` and direct contract application.
- runtime player `+0x154`: **contract expiry date**. Function `0x4190F0` computes contract months remaining from this value and global current date `0x9847FC`.
- player `+0xC0`: a contract-duration/state byte used on a special path in the remaining-contract calculation. Exact semantic label is still unresolved.

### Contract application routine 0x418FB0

A contract terms object is applied to a player by `0x418FB0`.

Confirmed mappings:

- terms `+0x18` -> player `+0xC4`: weekly wage
- terms `+0x24`: contract length/duration, used by date arithmetic to advance player expiry `+0x154`; its low byte also increments player `+0xC0`
- terms `+0x2C` toggles player `+0x174` bit 5
- terms `+0x2D` toggles player `+0x14` bit 27
- terms `+0x2E` toggles player `+0x14` bit 28
- terms `+0x28` is converted to double and stored at player `+0x98`
- terms `+0x1C` is added to player double at `+0x88`
- terms `+0x20` is converted to double and stored at player `+0xA0`

The exact semantic names of the three money/benefit fields and three clause booleans are being tied to EA's contract UI before promotion.

### Contract terms object

Constructor `0x4EC270` initializes a 0x50-byte terms object. Relevant fields include dwords at `+0x18,+0x1C,+0x20,+0x24,+0x28` and booleans `+0x2C..+0x30`.

Setup routine `0x4EC360` initializes terms from the current player:

- +0x18 = player current wage
- +0x1C = result from player `0x4202A0` under a club/status condition
- +0x20 = converted result of player `0x417D30`
- +0x28 = converted result of player `0x417CF0`
- +0x2C = player `0x422010`
- +0x2D = player `0x422030`
- +0x2E = player `0x422020`
- +0x2F = player `0x41BC90`
- +0x30 = player `0x41BCA0`

The complete negotiated-contract field map is now recovered:

- `+0x18`: weekly wage
- `+0x1C`: signing-on fee
- `+0x20`: promotion bonus
- `+0x24`: contract length
- `+0x28`: appearance fee
- `+0x2C`: relegation transfer-request clause
- `+0x2D`: big-club offer clause
- `+0x2E`: big-money offer clause
- `+0x2F`: house
- `+0x30`: car

Evidence combines the transfer formatter keys (`WAGE`, `CONTRACT`, `SIGNONFEEAMOUNT`, `APPEARANCEFEEAMOUNT`, `PROMOTIONBONUSAMOUNT`, `RELEGATIONTRANSFERREQUEST`, `BIGCLUBOFFER`, `BIGMONEYOFFER`, `HOUSE`) with EA's localized contract UI strings, which expose the adjacent clause/benefit sequence:

`RELEGATION CLAUSE`, `BIG CLUB OFFER`, `BIG MONEY OFFER`, `House`, `Car`

and the paired values `No house / Plus a house` and `No car / Plus a car`.

The terms initializer `0x4EC360` fills +0x2F and +0x30 from adjacent player accessors `0x41BC90` and `0x41BCA0`, matching House and Car respectively.

### CDealInProgress

RTTI identifies `CDealInProgress` (vtable around `0x7C9D30`).

- constructor `0x50E410`
- parameterized constructor `0x50E460`
- nested contract-terms object begins at deal `+0x14`
- main identifier/state dwords at deal `+4,+8,+0xC`
- byte state at `+0x10`
- timestamp/date at `+0x64`
- serialization around `0x50E4B0/0x50E520`

Several helpers test deal state values 1..5; the enum names remain to be recovered.

### Player status bitfields

Player `+0x174` is a bitfield. Functions:

- `0x4181E0`: set bit0, clear bit1
- `0x418280`: set bit1, clear bit0
- `0x418180`: clear bit0
- `0x418170`: clear bit1
- `0x41BC90`: return bit2
- `0x41BCA0`: return bit3
- `0x422010`: return bit5

Player `+0x14` also contains clause/status bits:
- `0x422030`: bit27
- `0x422020`: bit28

Do **not** yet label +0x174 bits0/1 as transfer-list/loan-list. Their setter paths also interact with a position/team-status object at player `+0x248`, and code `0x4218E0/0x421950` maps them together with other status bits into category codes 0..4. Named UI actions must establish semantics first.

### Transfer-related classes located

RTTI/source-path analysis has identified:

- `CDealInProgress`
- `CPlayerBidLog`
- `CPlayerMovement`
- `CPlayerTransferHistory`
- `CClubTransferLog`
- `CLeagueTransferLog`
- `EAMPlayerMovements`

Relevant EAM event classes include transfer-list/loan-list actions, club offers/replies, counter offers, accepted offers, player approaches, medical pass/fail, and final deal conclusion.

`PlayerMovements.cpp` source-path literal is present in the executable.


## CPlayerMovement transfer-history record

RTTI identifies `CPlayerMovement` (vtable approximately `0x7CA024`).

Relevant routines:

- default constructor `0x514F20`
- parameterized constructor `0x514F60`
- serializer/reader `0x514FB0`
- serializer/writer `0x515010`
- formatter `0x515070`
- list insertion helper `0x515290`

The record is 0x18 bytes and is now semantically mapped:

- `+0x04`: player record ID
- `+0x08`: source/from club ID
- `+0x0C`: destination/to club ID
- `+0x10`: transfer consideration (normally numeric fee; special sentinels below)
- `+0x14`: movement date/current game date

Evidence:

- formatter `0x515070` resolves +0x04 through the player table;
- +0x08 and +0x0C are resolved through the club table;
- +0x14 is stamped from the global current date by the constructor;
- +0x10 is normally passed through the game's currency formatter.

### Special consideration values

`0x515070` treats two numeric values specially:

- value 1 loads global localized string pointer `0x981F9C`
- value 2 loads global localized string pointer `0x981F98`

Those globals are populated by the language-index loader `0x635F30` from `English.idx`. The relevant `English.idx` entries resolve through `English.str` as:

- index-list entry 2583 -> English.str ID 21747 -> **"on a free transfer"**
- index-list entry 2584 -> English.str ID 21748 -> **"Bosman"**

Therefore:

- `consideration == 1` means **free transfer**
- `consideration == 2` means **Bosman**
- other values are ordinary transfer fees

This record is suitable for reconstructing the game's transfer-history UI independently of the live negotiation state machine.


## Transfer proposal structure and bid log

The core live transfer proposal is the same 0x50-byte structure previously analyzed through its player-contract terms. It is broader than a contract-only object.

Constructor `0x4EC270` initializes the full structure; `0x4EC250` additionally sets the main player and club context. Copy routine `0x4EC1B0` copies all 0x50 bytes.

Verified/strongly established layout:

- `+0x00`: main/target player ID
- `+0x04`, `+0x08`, `+0x0C`: up to three exchange/swap player IDs; initialized to -1
- `+0x10`: cash transfer-fee component
- `+0x14`, `+0x15`: small negotiation/AI state bytes; exact labels unresolved
- `+0x18`: weekly wage
- `+0x1C`: signing-on fee
- `+0x20`: promotion bonus
- `+0x24`: contract length
- `+0x28`: appearance fee
- `+0x2C`: relegation transfer-request clause
- `+0x2D`: big-club offer clause
- `+0x2E`: big-money offer clause
- `+0x2F`: house
- `+0x30`: car
- `+0x34`: buying/bidding club ID
- `+0x38`, `+0x3C`, `+0x40`, `+0x44`, `+0x48`, `+0x4C`: negotiation/history/derived values; exact meanings still being mapped

`0x4EDA20` resolves the main player from +0x00. `0x4ED9A0` resolves the club at +0x34.

`0x4EFA70` computes a total offer-value expression by adding the cash component at +0x10 to `0x4F0E00`, which values non-cash/exchange components. Therefore +0x10 is confirmed as the cash transfer-fee component.

### Swap-aware deal creation

Routine `0x4EFA80` creates per-player `CDealInProgress` entries for a proposal.

- A simple cash-only proposal creates state 0 for the main target.
- If any exchange player exists in +0x04/+0x08/+0x0C, each exchange player receives state 3, and the main target also receives state 3.
- Thus states 3/4/5 are definitively the swap/player-exchange variants of states 0/1/2.

The generic transition helper `0x50E5B0` maps:
- 0 -> 1
- 1 -> 1
- 2 -> 1
- 3 -> 4
- 4 -> 4
- 5 -> 4

This proves states 1/4 are the same later negotiation phase, states 2/5 another phase, and the +3 offset encodes player-exchange involvement. Exact user-visible names for base states 0/1/2 are still being tied to named transfer actions.

### CPlayerBidLog

RTTI identifies `CPlayerBidLog` (vtable approximately `0x7CA01C`).

Relevant functions:

- default constructor `0x514AD0`
- parameterized constructor `0x514B20`
- update `0x514B70`
- binary read/write `0x514B90` / `0x514BF0`
- list add/update wrapper `0x514C50`

Record layout:

- `+0x08`: player ID
- `+0x0C`: bidding club ID
- `+0x10..+0x17`: 8-byte monetary bid value
- `+0x18`: current game date / bid date
- `+0x1C`: additional counter/status field, semantic meaning unresolved

The list is keyed by player ID + bidding club ID. A repeated bid from the same club for the same player updates the monetary value and date rather than creating a duplicate.

A live caller around `0x4EE23A` passes the proposal's main player, club at +0x34, and monetary offer into this list, confirming the key semantics.


## Transfer negotiation history fields and deal-state event evidence

Additional transfer-proposal fields are now identified from the negotiation-adjustment routines:

- proposal `+0x38`: **previous/anchor wage offer**.
  - `0x4EDB10` uses it as the old wage when constructing a counter-offer.
  - if zero, the routine obtains a fresh wage expectation from player routine `0x420180`;
  - otherwise it moves halfway from the old offer toward the current offer and enforces at least the player's present weekly wage;
  - the current wage offer at +0x18 is then copied into +0x38 before any revised offer is written.
- proposal `+0x3C`: **previous/anchor signing-on-fee offer**.
  - the same routine performs the analogous midpoint/counter-offer operation against the current signing-on fee at +0x1C and player routine `0x4202A0`.
- proposal `+0x48`: **stored anchor/previous total proposal valuation** (strongly verified, exact UI name unknown).
  - helper `0x4F04E0` computes proposal total value with `0x4EFA20`, rounds it, and stores the result at +0x48;
  - later AI negotiation routines compare current total value against this stored amount when revising the proposal.

Fields +0x40/+0x44/+0x4C remain unresolved.

### End-negotiations event

Vtable `0x7C8F50`, created by routine `0x4EEE50`, is identified through MSVC RTTI as:

`EAMTPUserEndNegotiationssub`

Thus `0x4EEE50` is directly tied to the user-facing **End Negotiations** transfer event, not a generic proposal message.

### MPMTryExecuteTransfer and deal states

Vtable `0x7D7D94` is `MPMTryExecuteTransfer`.

Its execution routine at `0x61BAF0` inspects every player participating in the pending transfer (target plus up to three exchange players):

- global deal predicate `0x50E830` tests states **2/5**;
- global deal predicate `0x50E870` tests states **1/4**;
- entries in neither pair are treated as another/pending condition and may cause the transfer execution check to be rescheduled.

This establishes that 0/1/2 are not arbitrary labels: they encode distinct lifecycle conditions relevant to executing an already-constructed transfer, with +3 preserving the same condition for swap/player-exchange deals.

State 2/5 is a special execution-blocking/outcome path inside `MPMTryExecuteTransfer`: when encountered, the routine retrieves the player's active proposal and generates a transfer event before taking the non-normal completion path. The exact user-facing enum name remains deliberately unresolved until tied to a named medical/rejection/contract action.

State 1/4 is treated differently from both pending 0/3 and state 2/5. Earlier provisional wording that 1/4 simply meant "later negotiation phase" or "closed" should not be treated as final.

### Relevant event classes now located

RTTI/vtables tied to the transfer-completion and medical paths include:

- `EAMTPUserEndNegotiationssub` -> vtable `0x7C8F50`
- `EAMConfirmConcludeTransferDealsub` -> `0x7C9008`
- `EAMTransferDealConcludedsub` -> `0x7C8FAC`
- `EAMTPPlayerPassesMedical` -> `0x7D0DC4`
- `EAMTPPlayerPassesMedicalsub` -> `0x7CCD68`
- `EAMTPPlayerFailsMedical` -> `0x7CD1DC`
- `EAMTPPlayerFailsMedicalsub` -> `0x7CCDBC`
- `EAMEndNegotiationsTransferDeadLinePassed` -> `0x7CE3CC`
- `EAMTPUserEndNegotiationsOfferNotEnoughM` -> `0x7D5C38`

The proposal routine around `0x4EF170` creates either a Confirm-Conclude-Transfer-Deal or Transfer-Deal-Concluded event depending on club/control conditions, confirming that the transfer subsystem has a distinct conclusion stage after proposal/contract negotiation.


## CDealInProgress rejection state resolved

The semantic meaning of CDealInProgress state **2** (and swap variant **5**) is now directly established from the event path used by `MPMTryExecuteTransfer`.

When `MPMTryExecuteTransfer` detects state 2/5 through `0x50E830`, it calls the transfer-event factory `0x4EC780` with event/reason code **3**.

That factory branches by player context. For reason code 3, the concrete EA event classes are:

- free player: `EAMFreePlayerDeclinesContractMsub` (vtable `0x7C8C5C`)
- player renewing with the same club: `EAMPlayerDeclinesContractRenewalMsub` (vtable `0x7C8B60`)
- normal transfer negotiation: `EAMTPUserPlayerRejectsMsub` (vtable `0x7C8AB8`)

Therefore:

- state **2** = player **rejected/declined contract terms**
- state **5** = the same rejected/declined outcome for a swap/player-exchange deal

This is no longer a provisional "blocking/failure" label.

### Revised interpretation of the three state families

Current evidence supports:

- 0 / 3: pending/unresolved
- 1 / 4: resolved/cleared for transfer execution
- 2 / 5: player rejected/declined contract terms

The +3 offset continues to encode involvement in a swap/player-exchange deal.

Do not yet rename state 1/4 simply "contract accepted": it is broader. Proposal helper `0x4F0460` is now proven to return true when any exchange-player slot (+0x04/+0x08/+0x0C) contains a valid player ID. In `0x4EEB80`, either an already-swap-marked target or a proposal containing exchange players can route through `0x422920`, which removes the active proposal and normalizes the player's deal state to 1/4. Thus 1/4 means the player's deal condition is **cleared/non-pending for execution**, but not necessarily by the same acceptance action in every context.

### 0x4F0460 correction

`0x4F0460` checks only whether at least one of proposal fields +0x04, +0x08 or +0x0C is a valid player ID in the global player range.

It is therefore:

`proposal_has_exchange_player()`

It is not an eligibility, chairman, finance or medical check.


## Transfer execution / club movement path

The actual transfer-completion path is now traced through the Movement Process Manager (MPM) layer and player club-switch routines.

### MPM transfer classes

RTTI/vtables identify:

- `MPMLoanPlayer` vtable ~`0x7D7D54`
- `MPMTryExecuteTransfer` vtable ~`0x7D7D94`
- `MPMRemovePlayerDealInProgress` vtable ~`0x7D7DB4`
- `MPMTransferPlayer` vtable ~`0x7D7DF4`

Relevant execute methods:

- `MPMTryExecuteTransfer::Execute` ~`0x61BAF0`
- `MPMRemovePlayerDealInProgress::Execute` ~`0x61B950`
- `MPMTransferPlayer::Execute` ~`0x61B4A0`

The try-execute object stores the four proposal player IDs (target plus up to three exchange players) at object `+8..+0x14`.

Its constructor resolves:

- object `+0x18`: buying/bidding club, from proposal getter `0x4EFEA0`, which returns proposal `+0x34`;
- object `+0x1C`: selling/current club, from `0x4EFEB0`, which resolves the target player and returns current club at player `+0x72`.

### Deal-state gating before execution

`MPMTryExecuteTransfer::Execute` checks every involved player.

- helper `0x50E830` tests CDealInProgress state 2/5;
- helper `0x50E870` tests state 1/4.

When state 2/5 is present, the routine:

1. resolves the player;
2. copies the player's stored negotiation terms back into a local proposal via `0x422970` / `0x421F50`;
3. calls proposal/event routine `0x4EC780`;
4. blocks execution.

This is strong evidence that states 2/5 are a **counter-offer / renewed-terms-required phase**, but the exact enum label remains intentionally unconfirmed.

If a player is in neither 1/4 nor 2/5, execution is also blocked. Therefore states 1/4 are the family that satisfies the readiness predicate for progressing toward conclusion.

Function `0x422920` copies proposal terms into the player negotiation object via `0x421EE0`, then invokes `0x50E760`, which promotes base states 0/2 -> 1 and swap states 3/5 -> 4.

### MPMTransferPlayer scheduling

The MPMTransferPlayer constructor around `0x61B300`:

- copies the transfer proposal;
- schedules execution at current date + 7;
- sets a mode/state byte/dword at object `+0x5C`.

An alternate constructor path sets the corresponding mode to 0, while this path sets it to 1.

Its execute method `0x61B4A0` ultimately calls player transfer-completion routine `0x4229B0(proposal)` when validation/financial conditions permit.

### Player transfer completion at 0x4229B0

`0x4229B0` is the core target-player transfer-completion routine.

It:

1. gets the buyer club from proposal `+0x34` via `0x4EFEA0`;
2. computes total offer/consideration via `0x4EFA70`, then converts/rounds it with `0x668350`;
3. appends a `CPlayerMovement` transfer-history record through `0x515290`, supplying:
   - player ID,
   - old/current club from player `+0x72`,
   - buyer club,
   - transfer consideration;
4. copies proposal contract terms into the player's negotiation/contract staging area via `0x421EE0`;
5. invokes `0x422AA0` with the buyer club;
6. cleans transient team/position/transfer state associated with the player object.

This connects the live negotiation proposal directly to the previously decoded completed-transfer history object.

### Club switch at 0x422AA0 / 0x422BA0 / 0x422F70

`0x422AA0(newClub)` performs high-level club-switch preparation.

If the player has an old club, it:

- preserves/copies historical state around player `+0x1F8/+0x1FC`;
- removes the player from the old club through club routines including `0x404BB0`;
- adds/attaches the player to the new club through routines including `0x404B30`;
- applies the negotiated wage from the player's staging terms into player `+0xC4`;
- delegates to lower-level cleanup/setup routines `0x422B80/0x422BA0` and `0x422F40/0x422F70`.

`0x422F70` is the lower-level assign/reset routine. It:

- writes the new club record ID into player club fields including `+0x10` and `+0x72`;
- invokes club squad/status setup;
- stamps player `+0x158` from the global current date, strongly identifying it as current-club join date;
- clears/reset numerous temporary status bits in player `+0x14` and `+0x174`;
- clears player `+0x178` negotiation/deal count and other transient fields;
- performs additional post-move initialization.

`0x422BA0` handles removal from the old club and related historical/club-record state. It also cleans club training state when applicable and maintains club-level record/value fields associated with player movements. Exact financial/statistical semantics of those club fields remain under investigation.

### Swap execution

After readiness/financial validation, `MPMTryExecuteTransfer::Execute` loops target plus up to three exchange-player IDs.

For each valid involved player it removes the corresponding live deal with `0x417870` and routes exchange players through the reverse club path using the same club-switch machinery. Later setup invokes `0x422F70` to finalize assignment.

This confirms swap transfers are not a separate simplified record type: they use the same player movement/club assignment machinery, applied symmetrically to the exchanged players.

### Current open transfer questions

- exact user-facing enum names for CDealInProgress states 0/1/2;
- exact buyer debit / seller credit routines and transfer-budget effects;
- semantics of proposal trailing fields `+0x40..+0x4C`;
- exact meanings of club historical/value fields touched by `0x422BA0`.


## Transfer financial posting / Balance subsystem

The cash movement for completed transfers is now directly traced and directionally proven.

### Buyer debit and seller credit

During `MPMTryExecuteTransfer::Execute`, after deal-readiness checks, the transfer amount is posted through two club methods:

- seller club -> `0x404BB0`
- buyer club -> `0x404B30`

The methods are exact financial opposites.

`0x404B30` resolves the user-controlled club finance object and calls `0x5DC650`. That backend routine subtracts the supplied money amount from the finance money field at `finance +0x10`.

`0x404BB0` resolves the same type of finance object and calls `0x5DC510`. That backend routine adds the supplied amount to `finance +0x10`.

Therefore, for the transfer amount used by this path:

- buyer is debited;
- seller is credited;
- both postings use the same monetary amount.

### Affordability check

Club method `0x404AE0` compares a requested monetary amount against the same finance-object money value at `+0x10` for a user-controlled club. AI/non-user clubs take a bypass path.

This is used by transfer execution before completion, so a user-controlled buyer must have sufficient available current money for the transaction.

### Balance subsystem evidence

The relevant backend code has source-path metadata for:

`D:\Projects\FM2001\Applications\FootballManager\Balance.cpp`

Related strings include `BALANCE`, `CASH`, and `/cash777`.

Constructor-like routine `0x5DC400` initializes the balance/finance object and embeds the current money object beginning at `+0x10`.

The evidence therefore supports describing `finance +0x10` as the club/user's **current cash/balance amount**. It should not be conflated with the separate transfer-budget system.

### Accounting transaction category

Both buyer and seller posting paths construct a transaction using accounting/category code:

`1000 (0x3E8)`

The finance backend treats code 1000 specially in routines around `0x5DCF5D` and `0x5DDD1D`.

This is clearly part of the transfer cash-flow/accounting hierarchy, but the exact user-facing category name for code 1000 remains unconfirmed.

### Transfer budget is separate

The executable contains distinct budget concepts and tuning/UI strings including:

- `TRANSFERBUDGET`
- `TRANSFERBUDGETINCREASE`
- `PLAYERWAGEBUDGET`
- `STAFFBUDGET`
- `MAINTENANCEBUDGET`
- `MERCHANDISINGBUDGET`
- `MISCBUDGET`
- `BUILDINGSBUDGET`
- `TOTALBUDGET`

Tuning/global references such as the `TransferBudget` value around `0x821DC0` belong to this separate budget layer.

Do not label `finance +0x10` as transfer budget. Current evidence identifies it with current cash/balance, while transfer-budget allocation and adjustment remain active research targets.


## Chairman budget-settings message layout

RTTI identifies vtable `0x7CDAC0` as `EAMchairbudgetsettings`.

Formatter `0x55C860` exposes the exact user-facing order of its budget fields:

- event +0x3C: TOTALBUDGET
- event +0x40: STAFFBUDGET
- event +0x44: PLAYERWAGEBUDGET
- event +0x48: MAINTENANCEBUDGET
- event +0x4C: MERCHANDISINGBUDGET
- event +0x50: MISCBUDGET
- event +0x54: BUILDINGSLIMIT
- event +0x58: TRANSFERBUDGET

Serializer/deserializer methods `0x55CFD0` and `0x55D0A0` independently confirm these as persistent 32-bit fields in the event object.

This establishes that FM2001 treats transfer budget as a distinct chairman-assigned budget bucket rather than simply reusing current cash/balance.

The runtime authoritative storage from which this message is populated has not yet been located, so these event offsets must not be mistaken for the live budget object.

Configuration/tuning keys loaded around `0x506E..0x5070` include:

- TransferBudget
- MiscBudget
- StadiumBudget
- FacilitiesBudget
- PlayerWageBudget
- StaffWageBudget
- matching *2K variants

These are configuration inputs/defaults and are likewise separate from the current cash balance.


## Start-of-season budget message lead

RTTI identifies a named EA message class `EAMbcstartseasonmail` associated with the board/chairman start-of-season budget announcement.

Its formatter exposes the same family of budget concepts already confirmed in `EAMchairbudgetsettings`, including the transfer-budget bucket and the other operating-budget categories.

This is an important bridge candidate between the board's season-start budget assignment logic and the user-facing finance/mail system.

Current status: **active lead, not yet a complete live-storage mapping**.

Next trace:

1. identify every constructor/call site that allocates `EAMbcstartseasonmail`;
2. locate where its budget fields are populated;
3. follow those source values back to the authoritative live club-budget object;
4. determine whether completed transfers decrement that budget directly, or whether the budget is recomputed/adjusted through a board policy routine.

Do not treat the message object itself as the authoritative budget store.


## EAMbcstartseasonmail exact budget-field layout

RTTI identifies `EAMbcstartseasonmail` with vtable approximately `0x7D0150`.

Relevant methods:

- constructor/default initializer: `0x541AD0`
- message/class ID accessor: `0x541B00`, returns `0xA0`
- class-name accessor: `0x541B10`, returns `"bcstartseasonmail"`
- formatter: `0x572AE0`
- serialization-related method: `0x5730C0`

The formatter directly proves the seven season-start budget fields:

- event `+0x3C`: STAFFBUDGET
- event `+0x40`: PLAYERWAGEBUDGET
- event `+0x44`: MAINTENANCEBUDGET
- event `+0x48`: MERCHANDISINGBUDGET
- event `+0x4C`: MISCBUDGET
- event `+0x50`: BUILDINGSLIMIT
- event `+0x54`: TRANSFERBUDGET

Unlike `EAMchairbudgetsettings`, this message does **not** carry a separate TOTALBUDGET field in the preceding slot.

This class is a message/container, not yet proven to be authoritative live storage. The current target is to trace where these seven values are populated.

A potentially related structural clue is that runtime `DBRClub` records are `0x2A8` bytes and contain seven consecutive dwords at club `+0x3C..+0x54`. A club copy path copies this block verbatim. The count/spacing matches the start-season budget message, but this is **not yet sufficient evidence** to call those club fields budgets; their semantics must be established independently.


## Rejected live-budget hypothesis: club +0x3C..+0x54

The apparent seven-dword similarity between runtime `DBRClub +0x3C..+0x54` and the seven fields of `EAMbcstartseasonmail` is **coincidental**. This club region is not the authoritative budget block.

EA's compact club reader at `0x4022D0` was traced byte-for-byte. It consumes exactly 181 bytes per `Master.dat` club record and expands string indices into runtime pointers before `0x403660` copies the temporary record into the 0x2A8-byte runtime club object.

Relevant mappings:

- runtime/temp `+0x38` <- disk `+0x2C`, 2-byte localized string reference
- runtime/temp `+0x3C` <- disk `+0x2E`, 2-byte localized string reference
- runtime/temp `+0x40` <- disk `+0x30`, 4-byte integer
- runtime/temp `+0x44..+0x49` <- disk `+0x34..+0x39`, six raw bytes
- runtime/temp `+0x4A..+0x61` <- disk `+0x3A..+0x51`, 24 raw bytes
- runtime/temp `+0x64` <- disk `+0x52`, 4-byte integer

Validation against club record 0 (Arsenal):

- disk `+0x2C` string ID 920 -> `arsenal.tga`
- disk `+0x2E` string ID 921 -> `Sponsor`
- disk `+0x30` uint32 -> 204, matching the already-identified Arsène Wenger manager record ID
- disk `+0x52` uint32 -> 82

Therefore runtime club `+0x3C` is a localized sponsor-string pointer/reference, and `+0x40` is the manager ID/reference field. The following bytes belong to compact club visual/kit/other record data, not a seven-budget array.

This falsifies the proposed shortcut from club `+0x3C..+0x54` to start-season budget fields. Continue tracing the budget event population through its actual creation/fill path.


## EAMbcmonthlybudget field layout

The event adjacent to `bcstartseasonmail` is class ID `0xA1`, name `bcmonthlybudget`, vtable approximately `0x7D01A4`.

Relevant methods:

- constructor: `0x541B20`
- ID accessor: `0x541B50` -> `0xA1`
- name accessor: `0x541B60` -> `"bcmonthlybudget"`
- formatter: `0x573190`

The formatter proves this seven-dword layout:

- event `+0x3C`: TOTALBUDGET
- event `+0x40`: STAFFBUDGET
- event `+0x44`: PLAYERWAGEBUDGET
- event `+0x48`: MAINTENANCEBUDGET
- event `+0x4C`: MISCBUDGET
- event `+0x50`: BUILDINGSBUDGET
- event `+0x54`: TRANSFERBUDGET

This differs from `EAMbcstartseasonmail`, which carries staff, player wages, maintenance, merchandising, miscellaneous, buildings limit and transfers without a separate total-budget field.

The monthly-budget message is a promising recurring bridge to authoritative live budget state; its population source remains the next trace target.


## Board-budget configuration globals

The tuning/config loader around `0x506C00..0x5072E0` has now been mapped directly from key string -> destination global.

Budget-related mappings:

- `StaffWageBudget2K` -> `0x821D94`
- `PlayerWageBudget2K` -> `0x821D98`
- `FacilitiesBudget2K` -> `0x821D9C`
- `MiscBudget2K` -> `0x821DA0`
- `StadiumBudget2K` -> `0x821DA4`
- `TransferBudget2K` -> `0x821DA8`
- `StaffWageBudget` -> `0x821DAC`
- `PlayerWageBudget` -> `0x821DB0`
- `FacilitiesBudget` -> `0x821DB4`
- `StadiumBudget` -> `0x821DB8`
- `MiscBudget` -> `0x821DBC`
- `TransferBudget` -> `0x821DC0`

Related business-consultant/finance tuning:

- `ChairBudgetProfit` -> `0x821D80`
- `profitpoolmax` -> `0x821D88` (double)
- `profitpoolreturn` -> `0x821D90`
- `BCExtraPerLevel` -> `0x821DC4`
- `MerchPercentageP` -> `0x821DC8`
- `MerchPercentageN` -> `0x821DCC`
- `AdvertPercentageN` -> `0x821DD0`
- `ConcessionPercentageP` -> `0x821DD4`
- `ConcessionPercentageN` -> `0x821DD8`
- `BCIncrease` -> `0x821DDC`

These are global configuration/default values, not yet identified as the authoritative live per-club budget store.

### EAM factory-tag caution

A large generic allocation/factory switch around `0x53B4xx` passes values such as `0xA3` and `0xA4` to allocator `0x537C80` before constructing `bcstartseasonmail` and `bcmonthlybudget`.

Those values are **not the EAM event IDs**.

The classes' own virtual ID accessors prove:

- `EAMbcstartseasonmail::ID` at `0x541B00` returns `0xA0`;
- `EAMbcmonthlybudget::ID` at `0x541B50` returns `0xA1`.

The allocator/factory tags must therefore be kept distinct from EAM message IDs.


## Finance cheat-code trace checkpoint

A finance/debug-cheat trace is being used as a shortcut to the live cash/budget guards.

Current verified/strong evidence:

- The transfer execution path performs a user-club affordability check against the current cash/balance object.
- On the insufficient-cash branch, the code calls cheat getter `0x516090` before deciding whether to reject the transfer.
- Therefore `0x516090` is strongly associated with the **cash-affordability bypass** and is the leading candidate for the developer switch exposed as `/cash777`.
- A distinct cheat getter `0x516020` is used elsewhere inside the finance/business subsystem and is now the leading candidate for the **budget-related bypass**, potentially `/budget777`.

These identities are not yet promoted to final labels until the command-line flag initialization table and all getter consumers are correlated.

Immediate next trace:

1. map each cheat getter back to its global byte/flag;
2. map those global flags to the literal command-line strings `/cash777` and `/budget777`;
3. follow the budget getter's consumers to the exact live transfer-budget check/storage.


## Resolved finance cheat mappings

The two finance-related cheat getters can now be assigned semantically from their consumers.

### 0x516090 = cash affordability bypass (/cash777)

Getter `0x516090` returns global byte `0x877559`.

All four known consumers occur immediately after comparisons between a requested monetary amount and the club/user's **current cash/balance** value:

- `0x439072`
- `0x43CBBA`
- `0x61B5A0`
- `0x61BD08`

In each case, if available cash is insufficient, the operation is rejected unless `0x516090` returns true.

The executable also contains literal command-line switch `/cash777`.

This identifies `0x516090` as the cash-affordability cheat getter.

### 0x516020 = unresolved finance-adjacent cheat getter

Getter `0x516020` returns global byte `0x877552`.

Its known consumer is a finance/business routine ending around `0x5DE6C3`. RTTI now identifies the objects constructed there as `EAMChairSeasonTicketSetsub` and `EAMSeasonTicketSetsub`, so the routine is tied to season-ticket setting, not directly proven budget allocation. It is invoked from:

- year/season transition path around `0x4A870D`;
- recurring season/month finance path around `0x4C4826`.

The routine constructs/dispatches season-ticket-related finance events and ends by returning `0x516020`.

The executable contains a literal `/budget777` switch, but the getter-to-string association has not yet been proven.

Therefore `0x516020` remains a finance-adjacent cheat getter/candidate, but must not yet be labeled `/budget777`.

### Correction: season-ticket RTTI at 0x5DE530

RTTI inspection of the vtables constructed by the routine ending at `0x5DE6C3` gives:

- vtable `0x7BD95C` -> `EAMChairSeasonTicketSetsub`
- vtable `0x7CC3A4` -> `EAMSeasonTicketSetsub`

This invalidates the earlier claim that the routine itself was directly the periodic budget-allocation routine. The `0x516020` getter must be mapped through the actual cheat-command parser or independent consumers before assigning it the `/budget777` label.

### Consequence for further tracing

The two concepts are therefore explicitly separate in the original executable:

- `0x516090`: proven cash-affordability bypass, strongly matching `/cash777`;
- `0x516020`: unresolved finance-adjacent getter; `/budget777` remains a candidate until the command-line mapping is recovered.

This reinforces the already-established distinction between the club's live cash balance and its board-assigned budget buckets.


## Current executable-analysis priorities

1. Correlate RTTI table classes with `Static.dat` load sequence and record sizes.
2. Build function/subsystem map around season initialization.
3. Locate fixture generation and competition initialization.
4. Locate movement/transfer and finance state transitions.
5. Locate tuning-key loader and recover target globals.
6. Trace MatchCalculator/MatchEngine event production.
7. Trace FastView consumption of match events and rendering state.

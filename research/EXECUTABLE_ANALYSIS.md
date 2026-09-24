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


## Finance cheat-code trace checkpoint — SUPERSEDED

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


## Resolved finance cheat mappings — SUPERSEDED

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


## Major correction: 0x515Fxx/0x5160xx block is C++ stream machinery, not cheat flags — SUPERSEDED AGAIN

RTTI has now resolved the global object at `0x877540` conclusively.

`0x515F10` constructs the object by calling `0x5162A0` with ECX=`0x877540`. The vtables manipulated by this constructor/destructor chain identify the object as Microsoft C++ standard-library stream machinery:

- vtable `0x7CA080` -> `std::basic_istream<char, std::char_traits<char>>`
- vtable `0x7CA088` -> `std::basic_istringstream<char, ...>`
- vtable `0x7BD734` -> `std::basic_streambuf<char, ...>`
- vtable `0x7BD76C` -> `std::basic_stringbuf<char, ...>`

Therefore the absolute bytes at `0x877550..0x877562` lie **inside the global istringstream object**. The tiny functions `0x515FF0`, `0x516000`, `0x516020`, ..., `0x5160E0` are accessors for stream/internal state, not a table of developer cheat booleans.

This invalidates the previous attempted mappings:

- `0x516090` must **not** be called `/cash777` merely because some callers occur near cash comparisons;
- `0x516020` must **not** be called `/budget777`;
- caller context around these functions must be reinterpreted as stream/parser-state use.

The literal cheat switches `/cash777` and `/budget777` still exist in the executable, but their actual parser/storage must be located independently from the command-string table.

### Why this is definitive

The RTTI Complete Object Locators immediately preceding the vtables point to type descriptors:

- `.?AV?$basic_istream@DU?$char_traits@D@std@@@std@@`
- `.?AV?$basic_istringstream@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@`
- `.?AV?$basic_streambuf@DU?$char_traits@D@std@@@std@@`
- `.?AV?$basic_stringbuf@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@`

This is stronger evidence than behavioral inference from individual call sites.

### New cheat-trace direction

The real cheat parser must now be recovered from the literal command table itself. Known literals include `/cash777`, `/budget777`, `/fastbuild777`, `/alwayswin777`, `/alwayslose777`, `/skipmatchcalc777`, etc. A pointer table in `.data` references them, but direct code xrefs are absent, implying a data-driven parser or another level of indirection.

## Current executable-analysis priorities

1. Correlate RTTI table classes with `Static.dat` load sequence and record sizes.
2. Build function/subsystem map around season initialization.
3. Locate fixture generation and competition initialization.
4. Locate movement/transfer and finance state transitions.
5. Locate tuning-key loader and recover target globals.
6. Trace MatchCalculator/MatchEngine event production.
7. Trace FastView consumption of match events and rendering state.


## Literal cheat-command pointer table recovered

Fresh analysis was performed against the exact hashed `footballmanager.exe` recorded in `FINDINGS.md`.

### Confirmed literal table

The known developer switches are referenced by one contiguous pointer table in `.data`:

- `0x828510` -> `/nofmvplease777`
- `0x828514` -> `/fastbuild777`
- `0x828518` -> `/budget777`
- `0x82851C` -> `/sacked777`
- `0x828520` -> `/cash777`
- `0x828524` -> `/autorun777`
- `0x828528` -> `/alwayswin777`
- `0x82852C` -> `/alwayslose777`
- `0x828530` -> `/countrywin777`
- `0x828534` -> `/countrylose777`
- `0x828538` -> `/skipmatchcalc777`
- `0x82853C` -> `/nolimit777`
- `0x828540` -> `/nosackwarnings777`
- `0x828544` -> `/alttab777`
- `0x828548` -> `/showskill777`
- `0x82854C` -> `/showstat777`
- `0x828550` -> `/stadiumflags`
- `0x828554` -> `/pitchlitter`
- `0x828558` -> `/pitchwear`
- `0x82855C` -> `/noslidefx`
- `0x828560` -> `/cameraflashes`
- `0x828564` -> `/setslide`
- `0x828568` -> `/alwayssell`

A raw little-endian absolute-pointer scan finds no direct code references to the individual pointer-table entries, reinforcing the earlier conclusion that the switches are consumed through iteration or another level of indirection rather than one hard-coded xref per literal.

### Important refinement to the stream-accessor correction

The earlier RTTI-based interpretation of global `0x877540` is superseded by constructor-level analysis below. The object at `0x877540` is a 16-byte ordered-tree container ending at `0x87754F`, so the bytes at `0x877550..` are independent globals, not members of that container.

However, not every tiny routine in the surrounding `0x515Fxx/0x5160xx` address range reads that stream object. Three separate accessors read globals immediately following the literal command table:

- `0x515FE0`: returns byte `[0x82856C]`
- `0x516010`: returns byte `[0x82856E]`
- `0x5160B0`: returns byte `[0x82856F]`

The four bytes at `0x82856C..0x82856F` are initialized to `01 01 01 01` in the image.

Additionally:

- `0x5160F0` loads a qword floating value from `0x828570`.

These `0x82856x` globals are separate from the `0x877540` `basic_istringstream` object. Their exact option meanings are not yet proven and must not be assigned to `/cash777` or `/budget777` without tracing their writers/consumers.

### Exact next trace

Recover the parser/initializer that consumes the pointer table at `0x828510`. Because direct xrefs to individual table slots are absent, search for:

1. command-line API call sites and startup parsing code;
2. indirect/base-address references spanning the table;
3. writers to the state corresponding to each command;
4. callers of the separate `0x82856C/0x82856E/0x82856F` accessors.

Only after a literal-to-state mapping is proven should `/cash777` or `/budget777` be connected to a runtime budget/cash bypass.


## Correction to the 0x877540 interpretation: tree container, not istringstream

**Confirmed. This supersedes the earlier claim that the global beginning at `0x877540` is itself a `std::basic_istringstream`.**

Fresh constructor-level analysis separates two adjacent C++ template implementations that had previously been conflated.

### 0x877540 object

Static initializer `0x515F00` calls `0x515F10`, which invokes `0x5162A0` with ECX=`0x877540`.

Routine `0x5162A0` is an ordered-tree container constructor:

- stores two one-byte policy/allocator/comparator values at object `+0/+1`;
- clears object `+0x08`;
- allocates a 0x24-byte sentinel/header node;
- stores that node at object `+0x04`;
- initializes self-referential tree links in the sentinel;
- clears object `+0x0C`;
- uses shared tree bookkeeping globals at `0x877568/0x87756C`.

Destructor `0x515F50` operates on the same 16-byte container and destroys its tree nodes.

Therefore the object beginning at `0x877540` occupies the 16-byte range `0x877540..0x87754F`. The bytes beginning at `0x877550` are **not inside that container**.

### Where the stream RTTI actually appears

The `std::basic_streambuf` / `std::basic_stringbuf` RTTI and vtables are used by a different routine family beginning around `0x5166A0`. For example, `0x5166A0` installs streambuf/stringbuf vtables `0x7BD734` and `0x7BD76C` in the object passed through ECX.

This nearby stream implementation caused the earlier false association with the global at `0x877540`.

### Consequence for the tiny getters

The following getters once again represent independent global bytes rather than bytes proven to be internal stream state:

- `0x515FF0` -> `[0x877550]`
- `0x516000` -> `[0x877551]`
- `0x516020` -> `[0x877552]`
- `0x516030` -> `[0x877553]`
- `0x516040` -> `[0x877554]`
- `0x516050` -> `[0x877555]`
- `0x516060` -> `[0x877556]`
- `0x516070` -> `[0x877557]`
- `0x516080` -> `[0x877558]`
- `0x516090` -> `[0x877559]`
- `0x5160A0` -> `[0x87755A]`
- `0x5160C0` -> `[0x87755C]`
- `0x5160D0` -> `[0x877560]`
- `0x5160E0` -> `[0x877562]`

Their command-line meanings still require literal-to-state mapping. In particular, the strong consumer evidence that `0x516090` bypasses insufficient-current-cash checks becomes relevant again, but it is not yet enough by itself to prove that the corresponding literal is `/cash777`.

The separate initialized globals at `0x82856C/0x82856E/0x82856F` remain distinct from both the tree header and the `0x87755x` bytes.

### Updated parser target

The current parser investigation must now determine how:

1. the literal pointer table at `0x828510..0x828568`;
2. the ordered-tree container at `0x877540`; and
3. the independent state bytes beginning at `0x877550`

are connected during startup/command-line parsing.


## TransferBudget config globals are write-only in this executable

Fresh whole-image reference scanning has clarified the role of the previously mapped board-budget tuning globals.

### Confirmed direct-reference result

The budget-related globals beginning at `0x821D80`, including:

- `TransferBudget2K` -> `0x821DA8`
- `TransferBudget` -> `0x821DC0`

are written by the configuration parser around `0x506CFA..0x5072E0`.

A byte-by-byte scan of the entire executable for absolute 32-bit values in the range `0x821D80..0x821DFF` found **only the parser's own destination operands**. There are no other absolute pointers or direct reads of any address in this range.

The disassembly likewise shows no direct read of `0x821D80+`.

### Interpretation

**Confirmed:** these configuration globals are not themselves the authoritative live per-club/user transfer-budget storage.

**Probable:** in this build they are either consumed only through an indirect/indexed mechanism that leaves no embedded absolute address, or are dormant/legacy tuning outputs. The absence of any pointer to the range makes a normal indirect consumer less likely, but not impossible.

The live-budget investigation should therefore prioritize the board/business-consultant state that populates `EAMchairbudgetsettings`, `EAMbcstartseasonmail`, and `EAMbcmonthlybudget`, rather than assuming the `TransferBudget` tuning global is read directly during transfer execution.


## First command-state semantic mapping: /nofmvplease777

**Confirmed semantic mapping:** getter `0x515FF0`, which returns byte `[0x877550]`, is the game's no-FMV switch and corresponds to literal `/nofmvplease777`.

Evidence:

- startup at `0x530F99` calls `0x515FF0`;
- when the byte is clear, startup calls the media routine at `0x461E20` with literal filename `easp.tgq`;
- when the getter is nonzero, that playback block is skipped;
- the same getter also gates two related media/video paths at `0x461E26` and `0x461F9B`;
- the recovered literal command table contains the unique matching switch `/nofmvplease777`.

This mapping does not yet reveal how the parser writes `0x877550`, but it establishes that the independent `0x87755x` bytes are genuine developer-command state rather than stream internals.


## Match-result developer flags mapped

The adjacent command-state getters used by match setup at `0x512D80` and match processing at `0x513010` can now be mapped semantically to the matching literal developer switches.

### Confirmed mappings

- `0x516040` -> byte `0x877554` -> **`/alwayswin777`**
  - in `0x512D80`, when enabled, the routine tests which participating club satisfies the user/control predicate `0x4037B0` and forces that side's result flag to win while clearing the opponent.
- `0x516050` -> byte `0x877555` -> **`/alwayslose777`**
  - performs the exact inverse assignment for the user/control predicate.
- `0x516060` -> byte `0x877556` -> **`/countrywin777`**
  - resolves the configured/selected country-side club through the global competition/country path and forces a matching side to win.
- `0x516070` -> byte `0x877557` -> **`/countrylose777`**
  - performs the inverse country-side result assignment.
- `0x516080` -> byte `0x877558` -> **`/skipmatchcalc777`**
  - at `0x5130DC`, when enabled, match processing calls the compact result-selection routine `0x512D80` directly instead of continuing through the normal calculation path;
  - the same getter has a second consumer at `0x60BE75`, consistent with a global match-calculation bypass.

These mappings align one-for-one with the unique literal switches in the recovered command table and with the behavior of the corresponding consumers.

### Consequence

Together with `0x877550 = /nofmvplease777`, six independent bytes in the `0x877550+` block are now semantically tied to literal developer commands. This further disproves the superseded interpretation of these bytes as stream internals.


## Cash-bypass developer flag recovered

**Confirmed behavior / effectively unique literal match:** getter `0x516090` -> byte `[0x877559]` is the game's cash-affordability bypass and corresponds to `/cash777`.

Evidence from all four known consumers:

- `0x439072`
- `0x43CBBA`
- `0x61B5A0`
- `0x61BD08`

Each path first computes a prospective monetary amount using the finance/money wrapper routines `0x5E43B0` / `0x5E48D0`, obtains the club finance object through the already mapped `+0x670` path, and compares the required value against the current-money object at finance `+0x10`.

When the current-money comparison indicates insufficient funds, the code calls `0x516090`:

- flag clear -> enters the insufficient-funds/rejection handling path;
- flag set -> branches past that handling and proceeds as if affordability succeeded.

The recovered command table has the unique literal `/cash777`, matching this behavior exactly.

This restores the earlier cash-cheat conclusion, but on correct evidence: `0x877559` is an independent developer-state byte, not a stream member.


## 0x877552 / 0x516020 budget-cheat candidate: return value currently unused

The sole direct consumer of getter `0x516020` (byte `0x877552`) has now been traced through its complete direct call chain.

### Function 0x5DE530

Finance/business routine `0x5DE530`:

- operates on the club finance/business state associated with club runtime offsets including `+0x670`;
- constructs and dispatches season/business-related EAM messages;
- conditionally reads the current-money object at finance `+0x10`;
- ends unconditionally with `call 0x516020`;
- returns the getter's AL value directly (`ret 8`).

Thus `0x516020` is not used to branch inside `0x5DE530`; it is merely the routine's returned boolean.

### All direct callers ignore that return

Only two direct calls to `0x5DE530` are present:

- around `0x4A870D`, during season/year processing, called with the current club and mode 0;
- around `0x4C4826`, during another recurring/seasonal club-finance path, called with the current club and mode 1.

In both cases execution immediately overwrites/ignores EAX/AL after the call. There is no `test al`, conditional branch, or propagation of the value.

### Conclusion

**Confirmed:** in all direct executable call paths currently found, the value returned by `0x516020` / `0x877552` has no behavioral effect.

**Unresolved:** `0x877552` may still be the state associated with literal `/budget777`, but finance proximity alone is insufficient to prove that mapping, and no transfer-budget bypass behavior has yet been found for this byte.

This weakens the earlier assumption that `0x516020` would lead directly to the live transfer-budget guard. Continue looking for the actual budget-limit comparison/state rather than forcing this getter into that role.


## Accounting category 1000 and transfer-ledger checkpoint

Fresh tracing of the completed-transfer posting path and finance aggregators has clarified how category `1000 (0x3E8)` is used.

### Confirmed: completed transfers post category 1000

The already-mapped transfer-completion path calls:

- seller wrapper `0x404BB0 -> 0x5DC510`
- buyer wrapper `0x404B30 -> 0x5DC650`

Both wrappers construct a finance transaction with accounting category `1000`.

The transfer-completion routine around `0x422AA0` uses these wrappers on the old and new clubs around the player club-switch operation. No second obvious transfer-budget scalar write is visible in this immediate completion path.

### Confirmed: category 1000 is a normal two-sided finance-ledger category

The finance subsystem stores transactions in a ledger and independently aggregates positive and negative entries by category and date range.

- `0x5DC890(category, range)` ultimately uses `0x5DD1F0` to sum matching nonnegative/credit entries.
- `0x5DD650(category, range)` uses the parallel negative-entry path around `0x5DD560` and returns the magnitude of matching debits/outflows.
- helper `0x43F1E0` calls both sides and returns the net value: positive credits minus negative/outflow magnitude.

Category `1000` is explicitly queried through all of these paths in the finance-overview code around `0x43E03E..0x43E10x`. The overview therefore maintains/report credits, debits and a net value for category 1000 rather than treating the transfer posting code as an isolated side effect.

### Seller-side secondary posting

When `0x5DC510` credits incoming money it also constructs an additional debit using category `1600 (0x640)`.

The secondary amount is:

`incoming_amount * 0.01 * 0.2 = incoming_amount * 0.002`

from constants `0x7BD600 = 0.01` and `0x821850 = 0.2`.

The semantic name of category 1600 is not yet proven, so this must not be described as a tax/levy/commission without further evidence.

### Current transfer-budget model

**Confirmed:** completed transfer purchases/sales change current cash and create category-1000 finance-ledger entries.

**Confirmed:** no separate transfer-budget scalar mutation has been found in the immediate player-movement/posting path.

**Hypothesis:** the user's remaining/available transfer budget may be derived dynamically from a board/chairman transfer allocation combined with the category-1000 transfer ledger (for example allocation adjusted by net transfer spending), rather than maintained as a separately decremented scalar.

The hypothesis is not yet promoted because the actual board-allocation-versus-category-1000 comparison has not been located.

### Exact next trace

Locate the authoritative board/chairman transfer-allocation state and find the code that:

1. reads that allocation;
2. queries category 1000 transfer credits/debits or net flow;
3. derives/checks remaining transfer budget or an overspent condition.

The most promising bridges are the producer paths for `EAMchairbudgetsettings`, `EAMbcstartseasonmail`, `EAMbcmonthlybudget`, and the `OVERSPENTBUDGET` warning/message family.


## Corrected WinMain hInstance handoff (supersedes the previous command-line interpretation)

A first pass mistakenly identified the value passed at `0x531398` as WinMain's third parameter (`lpCmdLine`). Rechecking the live stack layout shows that two arguments pushed for the immediately preceding `0x5ECF30` call are still present at that point. Those two pushes shift the apparent stack offset.

Corrected interpretation:

- `0x531398` loads WinMain's **first** argument, `hInstance`;
- `0x5313A0` calls `0x531AF0(hInstance)`;
- `0x531AF0` forwards it to `0x531C10`;
- under startup option `0x5160B0`, `0x531D35` calls `0x530380(hInstance)`;
- `0x530380` stores it at `0x87784C`;
- `0x530390` later passes `0x87784C` as the `hMod` argument to `SetWindowsHookExA`, confirming that the value is an HINSTANCE/module handle rather than command-line text.

Therefore this path is **not** the cheat parser and must not be used as a command-line lead.

The real cheat parser remains unresolved and should continue to be traced from the literal table and actual command-line/argv consumers.


## Correction: 0x877540 is a tree/container, not an istringstream

Fresh re-analysis of the exact hashed executable disproves the earlier repository-level conclusion that global `0x877540` itself is a `std::basic_istringstream`.

### Confirmed object construction

Static constructor `0x515F10` calls `0x5162A0` with `ECX=0x877540`.

`0x5162A0` initializes a **16-byte non-polymorphic tree/container header**, not an iostream object:

- writes two one-byte comparator/allocator-like state values at object +0/+1;
- clears object +8;
- allocates a **0x24-byte sentinel/node**;
- stores the node pointer at object +4;
- stores zero at object +0x0C;
- makes the node self-linked through its tree-link fields;
- uses globals `0x877568` and `0x87756C` as a shared sentinel/allocation reference pair.

Destructor `0x515F50` walks/frees that node structure and releases the sentinel. There is no stream vtable written into `0x877540`.

This shape is consistent with an old MSVC ordered tree/set/map-style container implementation.

### Why the earlier RTTI conclusion happened

The stream RTTI/vtables recorded earlier are real:

- `0x7CA080`: `std::basic_istream<...>`
- `0x7CA088`: `std::basic_istringstream<...>`
- `0x7BD734`: `std::basic_streambuf<...>`
- `0x7BD76C`: `std::basic_stringbuf<...>`

However, those vtables are manipulated by the **separate routine family beginning at `0x516370`**, which operates on a much larger stream object via offsets such as `-0x54`, `-0x4C`, etc. They do not establish the type of the 16-byte global at `0x877540`.

### Consequence for the adjacent byte getters

The bytes beginning at `0x877550` occur immediately **after** the 16-byte tree/container object and are not fields inside an istringstream.

Therefore these accessors must be reopened as independent global option/cheat-state bytes:

- `0x515FF0` -> `0x877550`
- `0x516000` -> `0x877551`
- `0x516020` -> `0x877552`
- `0x516030` -> `0x877553`
- `0x516040` -> `0x877554`
- `0x516050` -> `0x877555`
- `0x516060` -> `0x877556`
- `0x516070` -> `0x877557`
- `0x516080` -> `0x877558`
- `0x516090` -> `0x877559`
- `0x5160A0` -> `0x87755A`
- `0x5160C0` -> `0x87755C`
- `0x5160D0` -> `0x877560`
- `0x5160E0` -> `0x877562`

This does **not** by itself prove which literal switch controls which byte. In particular, `0x516090` again becomes a strong `/cash777` candidate because its four known consumers gate insufficient-current-cash branches, while `0x516020` remains only a finance-adjacent candidate until the literal-to-byte parser mapping is recovered.

The parser investigation should now treat the tree at `0x877540`, the adjacent option bytes, and the literal pointer table at `0x828510..0x828568` as potentially related components rather than stream internals.


## Cheat-state consumer semantics checkpoint

The reopened adjacent global-byte getters now have enough consumer evidence to recover several behaviors independently of the still-unresolved literal decoder.

### Confirmed behavior

- `0x516000` reads byte `0x877551`. Its consumers at `0x438EB7` and `0x43CF70` force a computed timing/count value down to the literal value 3 when the byte is set. This is a fast-path override and is strongly compatible with the nearby developer switch `/fastbuild777`.
- `0x516040` / `0x516050` / `0x516060` / `0x516070` read `0x877554..0x877557` and are consumed consecutively inside match setup routine `0x512D80`. They force opposite match-result directions for the user-controlled side and for the country/national side. This is the match-result override family.
- `0x516080` reads `0x877558`. In match-processing code at `0x60BE50`, the true branch bypasses later match-calculation work. This is the match-calculation skip/bypass behavior.
- `0x516090` reads `0x877559`. Four known consumers (`0x439072`, `0x43CBBA`, `0x61B5A0`, `0x61BD08`) occur after comparisons against the already-recovered current cash/balance value. When cash is insufficient, this byte allows the operation/transfer to proceed. Thus its **behavior is definitively a current-cash affordability bypass**.

### Probable literal associations

The executable literals and the consumer behavior make these associations strong, but the literal-to-byte decoder itself is still not recovered:

- `0x877551` / `0x516000` -> probably `/fastbuild777`
- `0x877554` / `0x516040` -> probably `/alwayswin777`
- `0x877555` / `0x516050` -> probably `/alwayslose777`
- `0x877556` / `0x516060` -> probably `/countrywin777`
- `0x877557` / `0x516070` -> probably `/countrylose777`
- `0x877558` / `0x516080` -> probably `/skipmatchcalc777`
- `0x877559` / `0x516090` -> very probably `/cash777`

This ordering demonstrates that the runtime option bytes are **not** a simple same-index copy of the literal pointer table. In the literal table, `/cash777` appears before the always-win/lose family; in the runtime-byte behavior, the cash bypass follows that family.

### Budget candidate at 0x877552

`0x516020` reads byte `0x877552`. Its only currently identified caller is the end of finance/business routine `0x5DE530`, which creates/dispatches the named season-ticket event classes `EAMChairSeasonTicketSetsub` and `EAMSeasonTicketSetsub`.

At `0x5DE6C3`, the routine calls `0x516020` immediately before restoring registers and returning. Its two known callers at `0x4A870D` and `0x4C4826` do not visibly branch on the returned AL value afterward.

Therefore:

- the byte's behavior is **not yet sufficient** to call it a budget bypass;
- `0x877552` remains a strong structural candidate for `/budget777`, especially given the surrounding option-byte ordering;
- the association must remain probable until the literal decoder or an independent budget consumer proves it.

The next finance trace should therefore proceed from the actual `TransferBudget` configuration globals and transfer-completion code rather than assuming that `0x516020` directly exposes the live transfer budget.


## TransferBudget global xref result: configuration-only storage

A full absolute-reference scan of the exact hashed executable was performed for the mapped board-budget tuning globals:

- `StaffWageBudget2K` `0x821D94`
- `PlayerWageBudget2K` `0x821D98`
- `FacilitiesBudget2K` `0x821D9C`
- `MiscBudget2K` `0x821DA0`
- `StadiumBudget2K` `0x821DA4`
- `TransferBudget2K` `0x821DA8`
- `StaffWageBudget` `0x821DAC`
- `PlayerWageBudget` `0x821DB0`
- `FacilitiesBudget` `0x821DB4`
- `StadiumBudget` `0x821DB8`
- `MiscBudget` `0x821DBC`
- `TransferBudget` `0x821DC0`

For the entire budget block, each exact global address occurs in the executable image only at its tuning-loader assignment. For example:

- `TransferBudget2K` is written at `0x506ECE`;
- `TransferBudget` is written at `0x507030`.

A raw binary scan also found no data-table pointer references to `0x821DA8`, `0x821DC0`, or the neighboring mapped budget globals. Their only occurrences are the immediate destination operands of those loader writes.

### Consequence

These globals are **not the authoritative live per-club/user budget store**, and there is no static evidence that normal gameplay reads them directly after loading.

They should be treated as configuration/tuning outputs or legacy/default values until a dynamic/indirect relationship is independently demonstrated.

The live-budget investigation must therefore proceed through the board/business runtime state and its budget events/checks rather than attempting to follow direct xrefs from `TransferBudget`.


## Chairman extra-transfer / budget event classes

RTTI and vtable analysis has now resolved several chairman events that are likely relevant to runtime budget adjustments.

### Exact event classes

- `EAMchairextratransferfail`
  - type descriptor: `0x82C5A0`
  - complete-object locator: `0x7EFE20`
  - vtable: `0x7CDA6C`
  - ID accessor `0x540C40` returns `0x4F`
  - name accessor `0x540C50` returns `"chairextratransferfail"`

- `EAMchairextratransfersuccess`
  - type descriptor: `0x82C3E0`
  - complete-object locator: `0x7EF998`
  - vtable: `0x7CDA18`
  - ID accessor `0x540C60` returns `0x50`
  - name accessor `0x540C70` returns `"chairextratransfersuccess"`

- `EAMchairextraforallbudgets`
  - type descriptor: `0x82C280`
  - complete-object locator: `0x7EF638`
  - vtable: `0x7CD9C4`
  - ID accessor `0x540C80` returns `0x51`

- `EAMchairbudgetwarning`
  - type descriptor: `0x82C410`
  - complete-object locator: `0x7EF9E8`
  - vtable: `0x7CDC10`

The already-mapped `EAMchairbudgetsettings` uses vtable `0x7CDAC0`.

### Generic EAM factory

Generic factory `0x538DE0` validates an EAM/event ID and dispatches through the jump table at `0x540200`.

Relevant branches include:

- `0x53A10B`: allocate 0x50 bytes, construct vtable `0x7CDA6C` = extra-transfer failure
- `0x53A147`: allocate 0x50 bytes, construct vtable `0x7CDA18` = extra-transfer success
- `0x53A183`: allocate 0x4C bytes, construct vtable `0x7CD9C4` = extra-for-all-budgets
- `0x53A0CF`: allocate 0x68 bytes, construct vtable `0x7CDAC0` = chairman budget settings
- `0x539FDC`: allocate 0x44C bytes, construct vtable `0x7CDC10` = chairman budget warning

The jump-table entries for the first three correspond to IDs `0x4F`, `0x50`, and `0x51`, agreeing with the classes' own virtual ID accessors.

### Extra-transfer success message fields

Formatter-like method `0x55D5A0` for `EAMchairextratransfersuccess` consumes:

- object `+0x3C`
- object `+0x40`
- object `+0x44`

The +0x44 field is passed through club/team lookup helper `0x41C5B0`. If +0x40 is -1, the formatter chooses a randomized value 1..6 and stores it back. +0x3C is used as another formatted value.

The localized template key is `CHAIREXTRACASHSUCCESS`, despite the class being named `chairextratransfersuccess`. Exact semantic names for these three fields are not yet proven.

### Budget-warning message

`EAMchairbudgetwarning` is a much larger 0x44C-byte event object. Formatter `0x55B650` uses:

- a 0x400-byte payload beginning at +0x3C;
- +0x43C as a formatted integer/money-like value associated with `OVERSPENTBUDGET`;
- +0x440 as a club/team identifier passed through `0x41C5B0`.

These event objects are message containers, not yet identified as authoritative live budget storage. Their producer paths are now priority leads because an extra-transfer-budget success/failure decision necessarily consumes live budget/board state.


## Rejected live-budget candidate: game/session +0x694

The global game/session object returned by `0x4139D0` owns a pointer at `+0x694` that initially looked promising because it is heavily used in the `0x5DAxxx..0x5DExxx` finance/business region.

Its allocation and consumers now identify it with the **season-ticket/business-selection state**, not the authoritative transfer-budget store.

### Construction

During game/session initialization around `0x425BCA`:

- 0x7C bytes are allocated;
- dwords +0x00, +0x04, +0x08, +0x0C and +0x10 are initialized to zero;
- the pointer is stored at game/session `+0x694`.

### Season-ticket evidence

Routine `0x5DE530`, already tied by RTTI to `EAMChairSeasonTicketSetsub` / `EAMSeasonTicketSetsub`, immediately reads:

- game/session `+0x694`;
- state `+0x04` from that object.

The preceding season/business calculations around `0x5DE2xx` populate the same object's `+0x08` and `+0x0C` fields when zero.

Separately, routines `0x618Cxx..0x618EFF` iterate dword entries from object offsets `+0x14` through `+0x78` and use them as selection/category state while evaluating club/player/business data.

### Conclusion

`game/session +0x694` is a compact season-ticket/business-state object. It is not the seven-bucket chairman budget store.

Do not pursue `+0x694` as transfer-budget storage. Continue with expenditure/budget-check paths and chairman budget event producers instead.


## Expenditure-refusal event and category-1000 finance-row checkpoint

### EAMChairmanRefusesExpenditureM

RTTI resolves the chairman expenditure-refusal message:

- type descriptor begins at approximately `0x82D348` (`EAMChairmanRefusesExpenditureM` name at `0x82D350`)
- Complete Object Locator: `0x7F0E68`
- vtable: `0x7CFCB0`
- constructor: `0x56E480`
- serializer: `0x56E6A0`
- formatter: `0x56E540`

The constructor stores its two explicit arguments at:

- event `+0x3C`
- event `+0x40`

The serializer also persists those fields plus the inherited/event field at `+0x38`.

Direct constructor callers include:

- `0x42B5F8`
- `0x43913F`
- `0x43CC81`
- `0x4ED795`
- `0x61BE71`
- `0x61BE92`

A closely related/subclass constructor at `0x56E6E0` is called from:

- `0x42B64E`
- `0x4390D5`
- `0x43CC1D`
- `0x4ED6D3`
- `0x4ED6F2`
- `0x61BDB3`
- `0x61BDD3`

Crucially, the transfer-path callers are the same insufficient-cash branches already used to establish the behavior of `0x516090`. Inspection of the constructor arguments shows the refusal message is populated with club/index/manager-like identifiers, not with the failed expenditure amount or a transfer-budget scalar.

Therefore `EAMChairmanRefusesExpenditureM` is a **notification/event layer**, not the authoritative live budget store.

### Category 1000 in Finance Overview

The transfer posting path uses accounting category `1000 (0x3E8)` on both buyer and seller sides.

The finance backend contains explicit category-1000 branches:

- aggregate routine `0x5DC890`: special `0x3E8` comparison at `0x5DCF5D`, exact branch around `0x5DD0CA`
- aggregate routine `0x5DD650`: special `0x3E8` comparison at `0x5DDD1D`, exact branch around `0x5DDE8A`
- helper `0x43F1E0` calls both aggregate routines and computes their net difference for the requested category/date range

Finance Overview explicitly passes `0x3E8` into these routines around `0x43E067..0x43E115`. The resulting category-1000 net value is stored in the panel state at approximately `+0xAC0` and rendered through the corresponding Finance Overview row widgets.

This proves category 1000 is not merely an internal transfer posting tag; it has a dedicated aggregate/net presentation path in the finance UI. Its exact localized user-facing label is still unresolved.

### Event-ID xref caution

Direct immediate references to:

- `0x4A` budget warning
- `0x4F` extra-transfer failure
- `0x50` extra-transfer success
- `0x51` extra-for-all-budgets

around `0x46C4D2..0x46C730` were inspected and are UI/event-handler registration, not message producers.

Likewise immediate `0xA1` references at `0x4B480F`, `0x4B4849`, and `0x4D2F4E` are UI/control registration for `bcmonthlybudget`, not the runtime population path.

Do not use these immediate event-ID xrefs as evidence for live budget storage.


## bcmonthlyincome transfer-fee field checkpoint

RTTI resolves vtable `0x7D00FC` as `EAMbcmonthlyincome`.

Relevant methods:

- constructor `0x541A80`
- ID accessor `0x541AB0` -> `0x9F`
- name accessor `0x541AC0` -> `"bcmonthlyincome"`
- formatter `0x5724D0`
- serialization-related method `0x5730C0`

The formatter uses EA's own literal formatter keys to label the seven business-income dwords:

- `+0x3C` -> `GATE`
- `+0x40` -> `MERCH`
- `+0x44` -> `CONC`
- `+0x48` -> `ADVERTS`
- `+0x4C` -> `SPONSOR`
- `+0x50` -> `TELLY`
- `+0x54` -> `TRANSFERFEES`

The literal `TRANSFERFEES` is at `0x832904` and has only three references, all formatter variants inside `0x5724D0`.

This gives an exact EA-authored semantic label for the monthly-business event's `+0x54` field.

**Not yet proven:** although transfer postings use accounting category 1000 and Finance Overview has a dedicated category-1000 row, the population path connecting category 1000 directly to `EAMbcmonthlyincome +0x54` has not yet been recovered. Keep that relationship as a hypothesis until a producer/aggregation path is found.


## Chairman extra-budget adjustment formatter checkpoint

The literal formatter key `TRANSFERBUDGETINCREASE` at `0x83A200` has 13 static references, all concentrated in the formatter routine family around `0x60E3A0..0x60E77F`.

RTTI resolves the relevant formatter classes:

- `0x60FD00` / RTTI around `0x7F72A0` -> `chairextracashfail@ModFmt`
- `0x60E3A0` / RTTI around `0x7F72F0` -> `chairextracashsuccess@ModFmt`
- `0x60E5C0` / RTTI around `0x7F7340` -> `chairextraallbudgets@ModFmt`

### chairextracashsuccess input model

Formatter `0x60E3A0` reads:

- object `+0x10`: transfer-budget success message/reason variant selector
- object `+0x14`: monetary/integer increase amount

It dispatches on selector values 1 through 7 via a seven-entry jump table and formats the amount through the common key `TRANSFERBUDGETINCREASE`, while choosing one of seven localized **transfer-budget-success wording/reason variants**.

A second formatter branch beginning around `0x60E5C0` performs the analogous operation for the `chairextraallbudgets` family.

### Significance

This proves that this chairman extra-transfer-success formatter carries:

1. **which transfer-budget success wording/reason variant is being used**; and
2. **the transfer-budget increase amount**.

It is not merely a generic success/failure mail.

The surrounding formatter source also contains chairman budget keys, but the English resource resolves the seven-way dispatch here as message/reason variants for a **transfer-budget increase**, not seven budget buckets.

### Next trace

Locate constructors/callers that populate the ModFmt object's `+0x10/+0x14`, or the event/handler that supplies those values. That path should expose the board allocation/adjustment state used for transfer budget increases.


## EAMchairextratransfersuccess fields feed the budget-adjustment formatter

The relationship between `EAMchairextratransfersuccess` and the generic seven-way chairman budget-adjustment formatter is now directly proven.

Formatter `0x55D5A0` handles the event and, in each of its presentation variants, constructs a temporary `chairextracashsuccess@ModFmt` object.

### Correct ModFmt vtable identification

The generated RTTI/function table around `0x7D6180` alternates vtable function pointers and Complete Object Locator pointers. In particular:

- `0x7D618C` contains COL `0x7F72F0`
- `0x7D6190` is the vtable start whose first function is `0x60E5C0`
- COL `0x7F72F0` points to type descriptor `0x8322C0`:
  `.?AVchairextracashsuccess@ModFmt@@`

Thus the temporary object assigned vptr `0x7D6190` at `0x55D645` is definitively a `chairextracashsuccess@ModFmt`.

### Exact field transfer

After accounting for the two arguments pushed to constructor `0x547160`, the temporary ModFmt object begins at the stack address later written with vptr `0x7D6190`.

The writes are:

- event `+0x40` -> temporary ModFmt `+0x10`
- event `+0x3C` -> temporary ModFmt `+0x14`

Those are the exact fields consumed by the seven-way chairman adjustment formatter:

- ModFmt `+0x10` = transfer-budget success message/reason variant selector
- ModFmt `+0x14` = increase amount

Therefore the event fields are now confirmed as:

- `EAMchairextratransfersuccess +0x3C` = **budget increase amount**
- `EAMchairextratransfersuccess +0x40` = **transfer-budget success message/reason variant selector**
- `EAMchairextratransfersuccess +0x44` = **club/team ID**, passed through club lookup `0x41C5B0`

### Selector default behavior

If event `+0x40 == -1`, the formatter generates a random selector in the range **1..6** and stores it back into event `+0x40`.

The generic `chairextracashsuccess@ModFmt` formatter supports **seven** selector values (1..7).

The English localization resolves the meaning of this dispatch: all variants are transfer-budget-increase messages. Selector value 7 is therefore another transfer-budget success wording/reason branch, **not a transfer-budget category ID**.

### Immediate next step

Trace writers/producers of `EAMchairextratransfersuccess +0x3C/+0x40/+0x44`. A producer that sets `+0x40` explicitly should reveal the selector semantics and lead to the authoritative board-budget update state.


## Chairman extra-transfer success message/reason dispatch map

The seven-way `chairextracashsuccess@ModFmt` dispatch at `0x60E3A0` is now mapped exactly.

The routine reads selector `object +0x10`, subtracts 1, bounds-checks against 6, and dispatches through jump table `0x60E5A4`.

Exact selector branches:

- selector 1 -> `0x60E3BA` -> template/global `0x87A870`
- selector 2 -> `0x60E3EB` -> template/global `0x87A86C`
- selector 3 -> `0x60E41C` -> template/global `0x87A868`
- selector 4 -> `0x60E45B` -> template/global `0x87A864`
- selector 5 -> `0x60E48C` -> template/global `0x87A860`
- selector 6 -> `0x60E4CD` -> template/global `0x87A85C`
- selector 7 -> `0x60E50A` -> template/global `0x87A858`

Every branch formats the same amount from `object +0x14` through `TRANSFERBUDGETINCREASE`; only the selected localized chairman-success template changes.

The immediately following `chairextraallbudgets@ModFmt` formatter uses the next template-global block beginning at `0x87A854`.

The selector numbering and branch identity are exact. `ENGLIS2.STR` shows the corresponding texts are all variants describing an **increase to the transfer budget**, so these values select message/reason variants rather than budget buckets.

## game/session +0x5B4 is current-club context, not budget storage

A repeatedly encountered pointer at game/session `+0x5B4` appeared in the chairman extra-transfer formatter and many finance routines.

Initialization at `0x4258D0` proves it is not an internally allocated budget object:

- the function receives a pointer argument at `[esp+0x10]`;
- at `0x4258F2` that argument is stored directly into game/session `+0x5B4`.

The pointer is used pervasively throughout general club/team code, not only finance. Known uses include reading its small club/manager identity fields such as `+0x04` and `+0x40`, which are passed into event/message constructors and formatters.

Therefore `game/session +0x5B4` is current-club/team context and must not be treated as an owned chairman-budget controller or hidden seven-bucket storage object.


## DBRClub runtime size and budget-cheat caller-chain correction

RTTI now ties the current-club table and record types together:

- `DBRClub` RTTI type descriptor: `0x8185B8`
- `DBRClub` vtable: `0x7BD614`
- constructor: `0x405A40`
- destructor: `0x405AD0`
- runtime record size: **0x2A8 bytes**, proven by `DBTClubs` allocation stride in `0x40BBB0..0x40BC43`
- `DBTClubs` vtable: `0x7BD718`
- global table object is stored at `0x874B9C`

This independently confirms that game/session `+0x5B4` points into the current `DBRClub` context.

### 0x516020 / 0x877552 caller-chain correction

Routine `0x5DE530` ends with:

- `0x5DE6C3: call 0x516020`

so the getter's AL/EAX technically becomes the function return value.

Both known callers were checked:

- `0x4A870D`
- `0x4C4826`

In both cases execution proceeds immediately into unrelated calls/state updates and does **not** branch on or otherwise consume the return value from `0x5DE530`.

Therefore the byte at `0x877552` remains an unresolved option state. Its adjacency to the literal `/budget777` command family is insufficient to call it a working live-budget bypass, and no current caller evidence connects it to transfer-budget enforcement.


## game/session +0x670 finance object structure

The finance object referenced throughout transfer affordability, transfer posting, Finance Overview, and season-business code is now structurally mapped at construction time.

### Allocation and constructor

During game/session rebuild at `0x425A6A..0x425AEF`:

- any previous object at game/session `+0x670` is destroyed/freed;
- exactly **0xE0 bytes** are allocated;
- constructor `0x5DC400` initializes the object;
- the resulting pointer is stored at game/session `+0x670`.

Constructor `0x5DC400` initializes:

- `+0x00 = 1`
- `+0x04 = 0`
- `+0x08 = 0`
- `+0x10..+0x1C` from its four explicit constructor inputs
- an object/subrecord beginning at `+0x20`
- six 16-byte accounting/range-like subrecords beginning at `+0x30, +0x40, +0x50, +0x60, +0x70, +0x80` via `0x5E42E0`
- later bookkeeping fields around `+0x94..+0xA8`
- a byte at `+0xCC`

The constructor does **not** initialize an obvious contiguous seven-dword chairman-budget array.

### Cash/balance field

The cash/balance is definitively the qword at finance-object `+0x10`.

Evidence:

- `0x5DC650` (debit path) loads current value via `0x5E48D0` with ECX = object `+0x10`, compares it against the requested debit, and subtracts the requested amount from the qword at `+0x10`.
- `0x5DC510` (credit path) adds the posted amount directly to qword `[object+0x10]`.
- UI/business routines including `0x42962C`, `0x4298B4`, and `0x42C083` read this same qword for displayed/current finances.
- transfer buyer/seller paths call these same credit/debit routines through game/session `+0x670`.

### Consequence for live transfer budget

The `+0x670` object is the authoritative cash/accounting object, but its constructor and directly observed field layout do not expose a separate obvious seven-bucket chairman allocation array.

This strengthens the distinction already seen at transfer completion:

- cash is a persistent qword field at finance object `+0x10`;
- transfer fees are posted into accounting ledger/category state;
- chairman budget allocations are likely stored or derived elsewhere rather than as a simple adjacent cash scalar in this object.

Do not infer that the whole 0xE0 finance object is itself the chairman budget store merely because it owns cash and ledger state.


## Six Balance objects and chairman financial-objective tolerance

A save/load trace corrects the shape of game/session `+0x670..`.

### Six Balance-object pointer slots

Game/session initialization at `0x425EA0` clears exactly six dword pointer slots beginning at `+0x670`.

When active state is built, the first object is created at `+0x670` and the adjacent slots `+0x674..+0x684` are handled as additional objects of the same family. Save code at `0x427E19..0x427E69` loops exactly six times across these pointers:

- for each pointer it calls Balance serializer `0x5DDFB0`;
- it then serializes the internal state beginning at object `+0x30` through `0x5E1FF0`.

Thus `+0x670..+0x684` are **six separate Balance-object pointers**, not one Balance pointer followed by unrelated fields.

The exact gameplay ownership of all six slots (for example manager/user slots) is not yet assigned here; only the six-object structure is confirmed.

### Balance internal serialized state

Serializer `0x5E1FF0`, called with ECX = Balance `+0x30`, serializes six consecutive 16-byte value/range records at relative offsets:

- +0x00
- +0x10
- +0x20
- +0x30
- +0x40
- +0x50

followed by bookkeeping fields through roughly relative `+0x9C`.

This matches constructor `0x5DC400`, which initializes the same six 16-byte subrecords at absolute Balance offsets `+0x30..+0x80`.

### ChairmanPercentBudgetMiss is financial-objective tolerance, not transfer-budget logic

Tuning key `ChairmanPercentBudgetMiss` loads integer global `0x822488`. Unlike the old TransferBudget defaults, this global has a real gameplay consumer at `0x5E1ECE`.

Routine `0x5E1D90` is called with ECX = Balance `+0x30`. It compares:

- current cash = Balance qword `+0x10`
- a stored target value at Balance `+0x50` (relative +0x20 from the passed subobject)

It first compares the full stored target against current cash. If that branch is not satisfied, it computes:

`target * ChairmanPercentBudgetMiss * 0.01`

The constant at `0x7BD600` is exactly IEEE-754 double **0.01**.

The two event constructors identify the semantics of this check:

- constructor `0x5A5C20`, vtable `0x7D4E04`, RTTI = **EAMManagerObjectiveContinuedSuccess**
- constructor `0x5952C0`, vtable `0x7D3044`, RTTI = **EAMManagerFailedObjective**

Therefore this path evaluates a manager/chairman **financial objective target and tolerance**, not the seven chairman spending-budget buckets and not transfer affordability.

This is a useful distinction: the Balance object contains persistent financial objectives in addition to current cash and ledger data, but those objective values must not be mislabeled as transfer-budget allocation.


## Localization correction: extra-transfer success selector is a reason/message variant

Direct inspection of `ENGLIS2.STR` resolves an earlier ambiguity in the generated `chairextracashsuccess@ModFmt` formatter.

The localized chairman-success variants all describe **increasing the transfer budget** by the formatted `TRANSFERBUDGETINCREASE` amount. They differ in the chairman's wording/circumstance for granting the extra funds.

Therefore:

- `EAMchairextratransfersuccess +0x3C` = transfer-budget increase amount
- `EAMchairextratransfersuccess +0x40` = success message/reason variant selector
- `EAMchairextratransfersuccess +0x44` = club/team ID
- ModFmt `+0x10` = success message/reason variant selector
- ModFmt `+0x14` = transfer-budget increase amount

If the selector is -1, the formatter randomizes among 1..6; the formatter also has a seventh branch. This is a presentation/reason dispatch, not a seven-budget-category dispatch.

This **supersedes** the earlier hypothesis that selector 1..7 mapped the seven chairman budget buckets or that selector 7 specifically denoted transfer budget. The entire event is already transfer-budget-specific; `EAMchairextraforallbudgets` is the separate across-the-board budget-increase event.

The same English resource also states in the chairman budget-settings mail that the transfer budget “currently stands at” a value while the manager is free to buy and sell players as desired. This is consistent with the binary evidence that completed transfer affordability is enforced against current cash, while transfer budget is a distinct board allocation/reference concept. The exact storage/derivation of that displayed transfer-budget value remains unresolved.


## Manager-initiated extra-funds request event

The manager-facing “ask the chairman for extra funds” feature is now tied to a specific EAM event family rather than inferred from the automatic `chairextratransfersuccess` mail.

### EAMFundRequest

RTTI/string data identifies:

- type: `EAMFundRequest`
- vtable: `0x7D4C04`
- constructor/reset routine: `0x545C10`
- event ID accessor: `0x545C40` -> **0x185**
- name accessor: `0x545C50` -> `"FundRequest"`
- serialization routines include `0x56E6A0` and `0x59E300`

The event serializes three dwords:

- `+0x38`
- `+0x3C`
- `+0x40`

Their exact semantic names are not yet assigned.

### EAMFundRequestReject

The immediately following event is:

- type: `EAMFundRequestReject`
- vtable: `0x7D4C60`
- constructor/reset routine: `0x545C60`
- event ID accessor: `0x545C90` -> **0x186**
- name accessor: `0x545CA0` -> `"FundRequestReject"`

### UI/event registration evidence

Event ID 0x185 is registered/handled in several UI/message paths, including code around:

- `0x4365C4`
- `0x44CCEC`
- `0x44D012`
- `0x46C158`

These references are registration/presentation plumbing and should not by themselves be treated as the gameplay decision producer.

### English resource evidence

Decoded `ENGLIS2.STR` index **1465** is the manager's outgoing request to the chairman. It explicitly asks that “further monies be made available” for squad strengthening.

Nearby response strings include:

- index **1468**: chairman refusal because the club's financial circumstances cannot allow extra funding;
- index **1470**: chairman response granting a **loan** amount that must be repaid after a specified number of months.

This proves the user-initiated funding-request system is broader than the automatic transfer-budget-increase mail: at least one accepted response can be structured as repayable funding.

### Next trace

Follow the `EAMFundRequest` handling/decision path into the accept/reject event family and identify:

1. where the requested/approved amount is calculated;
2. whether the approved funds modify current cash, transfer budget, or both;
3. where the repayment term is stored;
4. how this interacts with the separate automatic `EAMchairextratransfersuccess` transfer-budget increase.


## FundRequestAccept credits current cash and stores repayment state

The manager-initiated funding request path is now traced through its accepted-result event and into the finance mutation.

### EAMFundRequestAccept

RTTI resolves:

- type: `EAMFundRequestAccept`
- vtable: `0x7D4CB4`
- ID accessor `0x472550` -> **0x187**
- name accessor `0x472560` -> `"FundRequestAccept"`
- serializer pair includes `0x5B4BA0` / `0x586A90`

The event serializes five dwords:

- `+0x38`
- `+0x3C`
- `+0x40`
- `+0x44`
- `+0x48`

Formatter `0x5A5110` gives exact semantic labels for two of these fields:

- event `+0x3C` -> formatter key **AMOUNT**
- event `+0x40` -> formatter key **MONTHS**

Thus:

- `+0x3C` = approved funding amount
- `+0x40` = repayment period in months

### Tuning connection

The accept construction path around `0x472480..0x4724E1` reads global `0x8222B8`.

The tuning loader at `0x50A215..0x50A24B` proves:

- key `FUNDMaxTimeToRepay` at `0x823BA0`
- parsed value stored at global `0x8222B8`

The neighboring loader proves:

- key `FUNDMaxReqPerYear` at `0x823BB4`
- parsed value stored at global `0x8222B4`

Routine `0x5E2330` checks a funding-state object's request count at `+0x08` against `FUNDMaxReqPerYear`, confirming that the request subsystem tracks yearly request usage.

### Approved amount calculation

Routine `0x5E2350` computes the amount granted by an accepted request.

Observed behavior:

- accesses the active Balance object through game/session `+0x670`;
- if Balance `+0x94` is active, it derives a temporary value/range from Balance `+0x40`;
- otherwise it constructs the basis from current-club data around runtime `+0xD0/+0xD4`;
- helper `0x5E48D0` extracts/converts that financial value;
- the result is reduced by a divisor: a fallback path effectively divides by 10, while another path divides by `10 + <context-dependent value>`.

The exact semantic label of the basis at Balance +0x40 / club +0xD0/+0xD4 is still unresolved, but `0x5E2350` is definitively the approved-funding amount calculator.

### Actual finance mutation

Handler `0x472570` is the critical path.

After validating the event/club context, it obtains a per-club/request-state object at runtime `+0x688` and then:

- calls `0x5E2350` and stores the approved amount at request-state `+0x04`;
- increments request-state `+0x08`;
- stores `FUNDMaxTimeToRepay` at request-state `+0x0C`;
- calls `0x5E2350` again to obtain the cash amount;
- converts it to the finance value object used by Balance;
- passes that value to **`0x5DC510`**, the already-proven Balance credit routine.

Therefore an accepted manager `FundRequest` **credits current cash/balance**.

This is distinct from the automatic `EAMchairextratransfersuccess` mail, which explicitly describes an increase to the transfer budget.

### Consequence

The game has at least two distinct “extra money” mechanisms:

1. **Manager FundRequest / FundRequestAccept**
   - produces a repayable amount;
   - stores repayment/request counters;
   - adds the approved amount to current cash via Balance.

2. **Automatic chairman extra-transfer success**
   - presentation explicitly says the transfer budget is increased;
   - its authoritative transfer-budget mutation is still being traced.

Do not conflate the FundRequest cash loan with the chairman transfer-budget allocation.


## Automatic transfer-budget event is presentation-only; transfer budget acts as reserve

A vtable-slot comparison with the now-resolved `EAMFundRequestAccept` side-effect handler clarifies where the automatic transfer-budget increase must occur.

### Side-effect slot comparison

`EAMFundRequestAccept` has its class-specific gameplay handler `0x472570` in the vtable slot at vtable +0x3C. That routine performs the confirmed Balance cash credit.

For the automatic chairman events:

- `EAMchairextratransfersuccess` vtable `0x7CDA18`:
  - vtable +0x3C = **0x4093E0**
- `EAMchairextratransferfail` vtable `0x7CDA6C`:
  - vtable +0x3C = **0x4093E0**
- `EAMchairextraforallbudgets` vtable `0x7CD9C4`:
  - vtable +0x3C = **0x4093E0**

`0x4093E0` is the shared/default no-op-style handler used broadly by event classes.

The class-specific method `0x55D920` shared by the extra-transfer success/fail events is instead a presentation/navigation handler: for UI action 0x43 it resolves event +0x44 as a club ID and calls `0x604900`.

Therefore the automatic chairman transfer-budget mutation occurs **before** the success event is emitted. The event is notification/presentation, unlike `FundRequestAccept`, which owns its own gameplay mutation.

### Original localization defines transfer budget as a reserve/reference allocation

`ENGLIS2.STR` index 757 (chairman season-budget mail) says:

- quarterly Staff/Wages/Maintenance/Merchandising/Other budgets are **fixed and should not be exceeded**;
- buildings have a yearly limit;
- the transfer budget “currently stands at” a value, but the manager is **free to buy and sell players as desired**.

This matches the executable evidence that transfer completion enforces current cash affordability rather than a separate transfer-budget hard cap.

Even more importantly, early chairman budget phrase variants show how the transfer allocation participates in overspending recovery:

- index 22: next-quarter budgets are modified to account for overspending;
- index 24: the chairman says he has had to **take money from the building and transfer budgets** to account for overspending.

Thus the transfer budget is definitely a mutable board reserve/allocation that can be reduced to compensate for operating-budget overspending, while not serving as the immediate purchase-affordability gate.

### ChairBudgetProfit tuning key

The tuning key `ChairBudgetProfit` loads into global `0x821D80` at `0x506CFA`.

A complete direct-reference check currently finds no later static read of `0x821D80`, so—like the previously mapped TransferBudget defaults—it is configuration-only/indirect unless a dynamic relationship is independently recovered. Do not use it as live transfer-budget storage.

### Refined model

Confirmed behavior now supports this model:

1. current cash/balance controls whether a transfer payment can actually be made;
2. transfer fees are posted through the finance ledger;
3. transfer budget is a separate mutable chairman allocation/reference;
4. quarterly operating overspending can consume the transfer/building reserves;
5. automatic chairman events can increase transfer budget;
6. the mutation happens in the producer/board-finance logic before the notification event is created.

Exact storage for the mutable transfer allocation remains unresolved.


## Chairman budget-settings event field/producer checkpoint

Further direct analysis of `EAMchairbudgetsettings` sharpens its runtime layout and rules out several misleading producer leads.

### Event identity and serialization

- vtable: `0x7CDAC0`
- event ID accessor `0x439400` returns **0x4E**
- serializer `0x55CFD0` persists dwords at:
  - +0x3C
  - +0x40
  - +0x44
  - +0x48
  - +0x4C
  - +0x50
  - +0x54
  - +0x58
  - +0x5C
  - +0x60
  - +0x64
  followed by inherited/event state at +0x38

Formatter `0x55C860` proves the known budget-value fields:

- +0x3C = TOTALBUDGET
- +0x40 = STAFFBUDGET
- +0x44 = PLAYERWAGEBUDGET
- +0x48 = MAINTENANCEBUDGET
- +0x4C = MERCHANDISINGBUDGET
- +0x50 = MISCBUDGET
- +0x54 = BUILDINGSLIMIT
- +0x58 = TRANSFERBUDGET

UI/action handler `0x55D170` handles action 0x43 by resolving event +0x5C as a club/team identifier and navigating to that club. Therefore:

- +0x5C = **club/team ID**

The semantics of +0x60/+0x64 remain unresolved.

### Immediate event-ID xrefs are not gameplay producers

All currently found hard-coded immediate uses of event ID **0x4E** were inspected. The sites at approximately:

- 0x46C62A
- 0x483B06
- 0x4C864B
- 0x4C88A8..0x4C8A6F
- 0x4D7D83
- 0x4D80F1
- 0x5FA24E

are UI/widget/event registration or setup paths. They do not populate the budget fields and therefore do not reveal the authoritative live budget store.

The same check was performed for hard-coded **0x4A** (`EAMchairbudgetwarning`) references. Sites including 0x475605, 0x4B9E43, and 0x4DF907 are likewise UI/control construction rather than the budget-warning producer.

Consequently the gameplay producer for budget-settings/warning events is likely reached through dynamic event creation/dispatch rather than a direct immediate event-ID constant.

### Rejected DBRClub candidate

A consecutive copy block around `DBRClub +0x21C..+0x234` initially resembled a possible persistent budget block. Broader xref inspection shows these offsets participate in unrelated club/runtime operations and mixed pointer/index/byte behavior. There is no evidence that they represent the chairman budget array.

Do not label `DBRClub +0x21C..+0x234` as budget storage without new independent evidence.


## Stadium/Groundsman no-budget events are current-cash expenditure checks

The named event classes adjacent to the monthly-business events are now tied to real gameplay producers:

- event ID 0x9C = `EAMsmnobudget` ("Stadium Manager no budget")
- event ID 0x9D = `EAMgdnobudget` ("Groundsman no budget")

Their formatters use EA's own `STADIUMMANAGER` and `GROUNDSMAN` keys.

Direct gameplay construction occurs in the expenditure routines around `0x5D2130..0x5D2A8F`, including:

- `0x5D230E -> 0x571E80` for the Groundsman no-budget message
- `0x5D23DB -> 0x571BF0` for the Stadium Manager counterpart
- analogous repeated paths at `0x5D2834` / `0x5D28FE`

The surrounding code proves these are **current-cash affordability** checks, not the chairman transfer-budget reserve:

1. requested cost is converted to the common finance value representation;
2. active Balance is fetched from game/session +0x670;
3. current cash is read from Balance +0x10 via `0x5E48D0`;
4. requested cost is compared against cash;
5. if affordable, `0x5DC650` is called to debit Balance;
6. if not affordable, the appropriate Stadium Manager/Groundsman no-budget event is emitted.

This gives another independent example where a user-facing "no budget" message actually corresponds to **cash availability**, reinforcing the need not to infer chairman reserve storage from message wording alone.

These routines are building/facility expenditure logic, not the quarterly transfer/building-reserve rebudget path.


## Balance +0x30..+0x80 block is financial-objective/target state

The six serialized 16-byte records inside each Balance object at absolute offsets +0x30, +0x40, +0x50, +0x60, +0x70 and +0x80 have now been tied directly to the manager financial-objective system.

### Periodic objective routine

Routine `0x5E12C0` is invoked with:

`ECX = active Balance + 0x30`

from the periodic/calendar path at `0x42AE21`.

It reads and updates the six value/range records, compares them with current cash from Balance +0x10, and emits named manager-objective events.

Named constructors called from this routine include:

- `0x5954F0` -> RTTI **EAMManagerWarnedObjective**
- `0x5A6360` -> RTTI **EAMMonthlyFinancialTargets**

The nearby routine `0x5E1C00`, also called with `ECX = Balance + 0x30`, emits:

- `0x5A5F50` -> RTTI **EAMManagerObjectiveGoodWork**

The already-mapped `0x5E1D90` emits the continued-success / failed-objective family.

### EAMMonthlyFinancialTargets field labels

`EAMMonthlyFinancialTargets` uses vtable `0x7D4EAC`.

Formatter `0x5A6450` labels its monetary fields with EA-authored keys:

- event +0x3C -> **BALANCEA**
- event +0x40 -> **BALANCEB**
- event +0x44 -> **PROFITA**
- event +0x48 -> **PROFITB**
- event +0x4C -> **TARGET**
- event +0x50 -> club/team ID

The label strings are:

- `0x8330FC` = `BALANCEA`
- `0x833108` = `BALANCEB`
- `0x833114` = `PROFITA`
- `0x83311C` = `PROFITB`
- `0x833124` = `TARGET`

At `0x5E15E8..0x5E1616`, `0x5E12C0` extracts values from the Balance +0x30 objective block and passes them directly into the `EAMMonthlyFinancialTargets` constructor.

### Consequence

The six serialized Balance records at +0x30..+0x80 are persistent **financial-target/objective/forecast state**. They are not the chairman's staff/wage/maintenance/merchandising/misc/buildings/transfer budget array.

This rules out the remaining unmapped members of this six-record block as the authoritative live transfer-budget reserve.

The Balance object still owns current cash and accounting/ledger data, but the transfer-budget allocation must be found elsewhere or derived before presentation.


## game/session +0x698 is the bank-loan subsystem

The persistent 0x108-byte object at game/session +0x698 has now been identified from its constructor inputs and save path.

### Lifetime / persistence

- allocation size: 0x108 bytes
- constructor: `0x5DED10`
- stored at game/session `+0x698`
- load path invokes `0x5DF430`
- save path invokes `0x5DF360`

The object is therefore persistent save-state, which initially made it a plausible chairman-budget candidate.

### Constructor tuning proves bank-loan identity

Constructor `0x5DED10` initializes finance-value records and allocates several 0xB0 child records from tuning globals.

The tuning-loader xrefs feeding those records resolve to explicit bank-loan keys, including:

- `Bank1LoanMax`
- `Bank1Term1`
- `Bank1Term2`
- `Bank1APR`
- `Bank2LoanMin`
- `Bank2LoanMax`
- `Bank2Term1`
- `Bank2Term2`
- `Bank2APR`
- `Bank3LoanMin`
- `Bank3LoanMax`
- `Bank3Term1`
- and the continuation of the same bank parameter family.

For example:
- global 0x821178 is loaded from `Bank1LoanMax`;
- 0x821180 / 0x821184 from `Bank1Term1` / `Bank1Term2`;
- 0x821188 from `Bank1APR`;
- 0x8211A0 / 0x8211A4 from `Bank2Term1` / `Bank2Term2`;
- 0x8211A8 from `Bank2APR`.

### Conclusion

game/session +0x698 owns the **bank-loan configuration/state subsystem**, not the chairman transfer-budget reserve.

Its finance-like structure and save persistence are therefore explained without invoking chairman budget storage.


## Finance category 1100 / false 0x44C allocation lead

A transient analysis lead around Balance.cpp has been corrected before it could contaminate the event-size model.

Several sites including `0x5DD1C2`, `0x5DDF82`, `0x5E188A` and `0x5E18B4` contain:

`push 0x44C`

The value **0x44C is not an allocation size at these sites**. In each case it is passed as the accounting-category argument into finance aggregation/posting routines such as `0x5DC890`, `0x5DD650`, `0x5DD1F0`, or `0x5DD560`.

This is independently confirmed by real expenditure paths around `0x5D21E5`, `0x5D2440`, `0x5D2712`, and `0x5D2963`: they build a finance value with category **1100 (0x44C)** and then call Balance debit routine `0x5DC650`. These are the same Stadium Manager/Groundsman/facility expenditure paths whose no-budget events were previously mapped.

Finance Overview also queries category 1100 through `0x43F1E0` at `0x43D5BB..0x43D5CE`.

Therefore category 1100 is confirmed as a genuine ledger category used by stadium/grounds/facility expenditure. Its exact EA-facing account-row label is not yet resolved.

Important distinction:

- `0x44C` decimal 1100 as a pushed argument in these Balance.cpp paths = **ledger category**
- `EAMchairbudgetwarning` object size = also **0x44C bytes**

The numerical equality is coincidental and must not be used to identify an event allocation.


## game/session +0x690 is the concession-offer subsystem

The large persistent object at game/session `+0x690` initially looked like a plausible per-manager/per-club chairman state owner because it is serialized and contains eight repeated records.

### Lifetime and layout

During game/session rebuild around `0x425B52..0x425BB9`:

- exactly **0xB50 bytes** are allocated;
- constructor `0x425F90` initializes the object;
- it contains **8 repeated 0x168-byte records** beginning at object +0x08;
- each record is initialized by `0x5E4E90`;
- trailing object fields exist at +0xB48 and +0xB4C;
- the object is stored at game/session **+0x690**.

Each repeated record serializes:

- dword +0x00
- 0x40-byte text buffer at +0x04
- 0x100-byte text buffer at +0x44
- dwords +0x144, +0x148, +0x14C, +0x150
- qword +0x158
- dwords +0x160 and +0x164

### Tuning identity

Periodic routine `0x5E5330` uses globals:

- `0x821280`
- `0x821284`

The tuning-loader writes at `0x4FF02D` and `0x4FF068` resolve those exact globals to:

- **FCConcessionOfferMinWait** -> `0x821280`
- **FCConcessionOfferMaxWait** -> `0x821284`

Nearby tuning names continue the same concession family, e.g. `FCBadConcessionHighCrowd`.

### Cash-credit behavior

Routine `0x5E5640`, called from the periodic game path at `0x42A9FD`, iterates the active +0x690 records, obtains a financial value from each record through `0x5E56F0`, converts it to the common Balance value representation, and calls **`0x5DC510`** on the active Balance.

Thus matured/active concession records can directly credit current cash.

### Conclusion

game/session **+0x690 is the food/concession commercial-offer subsystem**, not chairman transfer-budget storage.

The eight-record persistent layout, text buffers, offer timing and cash-credit behavior are fully consistent with concession/commercial offers and inconsistent with a compact chairman budget array.


## game/session +0x69C is the sponsor-offer subsystem

The persistent object at game/session `+0x69C` is now identified from its live tuning inputs and periodic logic.

### Persistence

- the object is allocated during game/session construction;
- it is serialized through routine `0x617BA0`;
- its runtime update path includes `0x617C80`.

### Exact tuning identity

Routine `0x617C80` consumes globals:

- `0x8212B0`
- `0x8212B4`
- `0x8212B8`
- `0x8212BC`

The tuning loader maps these exact globals to:

- `FSNoSponsorMinWait` -> `0x8212B0`
- `FSNoSponsorMaxWait` -> `0x8212B4`
- `FSHaveSponsorMinWait` -> `0x8212B8`
- `FSHaveSponsorMaxWait` -> `0x8212BC`

The immediately following tuning family continues with `FSOfferMinLifeTime`.

### Conclusion

game/session `+0x69C` owns sponsor-offer / sponsor-state scheduling, not chairman transfer-budget storage.

This removes another persistent finance/business-looking object from the live transfer-budget search.


## EAMManagerSackedFailedBudget is financial-objective failure, not quarterly reserve overspending

RTTI resolves `EAMManagerSackedFailedBudget`:

- type descriptor: `0x830D90`
- Complete Object Locator: `0x7F5758`
- vtable: `0x7D4F54`
- ID accessor `0x545EE0` returns **0x190**
- name accessor `0x545EF0` returns `"ManagerSackedFailedBudget"`
- serializer paths `0x59A7B0` / `0x5A8CD0` persist event fields +0x38/+0x3C/+0x40/+0x44
- constructor-like routine `0x5A6E90` stores explicit values at +0x3C/+0x40/+0x44.

The gameplay producer at `0x42936C..0x4293F0` emits this event when game/session sacking-reason state `+0x10D8` equals **5**.

Crucially, the setter for reason 5 is directly visible at:

- `0x5E1F8E: push 5`
- `0x5E1F92: call 0x42C6C0`

inside routine `0x5E1D90`.

That routine was already independently identified as the manager/chairman **financial-objective tolerance** path: it compares current cash against the stored Balance objective target and uses `ChairmanPercentBudgetMiss`.

Therefore `EAMManagerSackedFailedBudget` refers to failure of the chairman financial objective/balance target, not the quarterly operating-budget overspending path that can consume building and transfer reserves.

Do not use this sacking event as the route to live transfer-budget storage.


## EAMChairmanNotEnoughFunds is emitted from the current-cash affordability gate

RTTI and constructor analysis identifies a distinct chairman notification class:

- type: `EAMChairmanNotEnoughFunds`
- type descriptor: approximately `0x82C350`
- Complete Object Locator: `0x7EF838`
- vtable: `0x7CF428`
- constructor-like routine: `0x546D30`
- name method returns `"ChairmanNotEnoughFunds"`

A real gameplay caller exists at `0x4EECA0` inside routine `0x4EEB80`.

The decisive condition immediately preceding that event construction is:

```text
0x4EEBC1  load requested monetary value from object +0x10
0x4EEBCC  call 0x4ED9A0
0x4EEBD3  call 0x404AE0
0x4EEBD8  test AL
0x4EEBDA  if affordable -> branch away
...
0x4EECA0  call 0x546D30  ; EAMChairmanNotEnoughFunds
```

`0x404AE0` is the already-proven current-cash affordability helper used in transfer/financial expenditure paths. Thus this chairman event is emitted when the requested amount fails the **current Balance cash** test.

The event constructor receives club/manager/context identifiers at +0x40/+0x44/+0x48; it does not expose the separate chairman transfer-budget reserve.

### Consequence

`EAMChairmanNotEnoughFunds` is another cash-insufficiency notification despite its chairman wording. It is not evidence for a separate transfer-budget hard cap and should not be used as the route to the authoritative live transfer reserve.


## CMonthHistory monthly finance snapshots at game/session +0x6DC

RTTI identifies the 0x68-byte objects built by the monthly business/calendar routine around `0x429CB0` as **`CMonthHistory`**.

- `CMonthHistory` vtable: `0x7BE088`
- RTTI type descriptor: approximately `0x819738`
- companion/history-container RTTI: `CHistories`, vtable around `0x7BE170`
- each `CMonthHistory` allocation is exactly **0x68 bytes**
- completed snapshots are appended to the persistent list/container at game/session **+0x6DC** via `0x617D70`

The monthly producer populates the snapshot through virtual setters with values drawn from:

- current club/business state;
- the persistent commercial/attendance model at game +0x68C;
- current Balance cash at +0x10;
- Balance monthly/ledger aggregate helpers such as `0x5DD2E0`, `0x5DD3C0`, `0x5DD4A0`, and `0x5DD500`;
- season-ticket/business state at game +0x694;
- additional current-club values including runtime club fields around +0x144/+0x160.

The class contains a mix of integer and qword/double-valued monthly history fields through offsets +0x10..+0x64. Its virtual setter/getter family is concentrated at `0x428B70..0x428D40`.

This is the first confirmed persistent **monthly financial-history** structure and is a plausible input to quarterly chairman budget recalculation. It is not itself yet proven to store the live transfer-budget allocation.


## game/session +0x6B0 is the stadium model/state

The large persistent object at game/session `+0x6B0` is now identified from its initialization and error path.

### Lifetime / structure

- allocation size: **0x1BC4 bytes**
- constructor: `0x65CB20`
- stored at game/session `+0x6B0`
- contains an internal polymorphic `CEntriesList` at object `+0x1B98`
  - vtable `0x7BDF78`
  - RTTI type descriptor `0x819558` = `CEntriesList`
- serializes substantial stadium/entry state through the `0x65Dxxx` routine family.

### Definitive stadium identity

During club/game setup at `0x425722..0x42574F`:

1. the current club's stadium/map-related object is obtained;
2. game/session `+0x6B0` is passed that asset identifier via `0x65D5B0`;
3. if the load fails, the game formats the literal string:

> `Unable to load stadium : %s ,you may continue, but the building screens, and ticketing will not work!`

The same object is then queried via routines such as `0x65D920` and is used together with season-ticket state during club setup and monthly-history calculations.

### Consequence

Game/session `+0x6B0` is the **stadium model/state subsystem**. Its large arrays and `CEntriesList` describe stadium/entry/building/ticketing data rather than chairman budget storage.

Its contribution to `CMonthHistory` is therefore stadium/attendance/ticketing input, not evidence that monthly history owns the transfer-budget reserve.


## Runtime "game/session" object is DBRUser

RTTI resolves the large runtime object whose fields we have been referring to as game/session state as **`DBRUser`**.

### RTTI / vtable proof

- TypeDescriptor: `0x8194E0` = `DBRUser`
- Complete Object Locator: `0x7DFC70`
- vtable: **`0x7BDF4C`**
- constructor begins around **`0x424CA0`**
- destructor/reset path around **`0x424FC0`** restores the same vtable

The constructor writes vtable `0x7BDF4C` at `0x424DBA`, then initializes the fields we have already mapped, including:

- six Balance pointers at `DBRUser +0x670..+0x684`;
- funding-request state at +0x688;
- commercial/attendance state +0x68C;
- concession +0x690;
- season-ticket state +0x694;
- bank-loan state +0x698;
- sponsor state +0x69C;
- additional small business/building state +0x6A0..+0x6AC;
- stadium state +0x6B0;
- event/list state +0x6B4;
- 40×200-byte training state +0x6B8;
- 256×0x18-byte movement-history style table +0x6BC;
- persistent history containers including CMonthHistory around +0x6DC.

### Significance for chairman budgets

The finance/business systems are therefore **per runtime user/manager**, not fields of a generic global game object. The unresolved chairman transfer-budget allocation should be searched as DBRUser-owned or DBRUser-derived state.

This also explains why several apparently unrelated per-club systems are adjacent: DBRUser aggregates the active manager's club, finance, training, stadium, histories and message/event state.

Terminology in older notes that says "game/session +offset" should be read as the same DBRUser-relative offset unless independently referring to a different object.


## DBRUser +0x588..+0x5A8 is media-rights state, not five operating budgets

A block of five consecutive qword values at `DBRUser +0x588, +0x590, +0x598, +0x5A0, +0x5A8` initially looked unusually promising because the chairman system has five quarterly operating-budget categories.

Routine `0x4268C0` initializes all five values together and chooses their contents from tuning globals in the `0x821220..0x821268` range.

The tuning loader resolves those globals to explicit media-rights keys:

- `0x821220` = `LRADIO_MAX`
- `0x821228` = `LRADIO_RES`
- `0x821230` = `NRADIO_MAX`
- `0x821238` = `NRADIO_RES`
- `0x821240` = `LTV_MAX`
- `0x821248` = `LTV_RES`
- `0x821250` = `NTV_MAX`
- `0x821258` = `NTV_RES`
- `0x821260` = `EUROPEAN_MAX`
- `0x821268` = `EUROPEAN_RES`

Thus this five-qword block belongs to radio/TV/European media-rights/reserve state. The numeric coincidence with the five quarterly chairman operating budgets is not semantic evidence.

Do not use DBRUser +0x588..+0x5A8 as the chairman budget array.


## DBRUser +0x5B8/+0x5C4/+0x5D0 are CSupportStaff lists

The repeated triplet structures beginning at `DBRUser +0x5B8` initially resembled compact grouped finance state, but save/load and RTTI analysis identifies them as list/container headers for support-staff objects.

### Structure

Constructor initialization creates repeated list headers:

- +0x5B8/+0x5BC/+0x5C0
- +0x5C4/+0x5C8/+0x5CC
- +0x5D0/+0x5D4/+0x5D8
- +0x5E0/+0x5E4/+0x5E8

The first three are reconstructed during DBRUser loading by reading list counts and appending objects/references through list helper `0x617D70`.

For the first two lists, the loader allocates **0x218-byte** polymorphic objects and constructs them via `0x4CA610` before deserialization.

### RTTI identity

Constructor `0x4CA610` writes vtable `0x7C6834`.

- preceding Complete Object Locator: `0x7E6748`
- TypeDescriptor: `0x81E298`
- RTTI name: **CSupportStaff**
- nearby source-path string: `Applications\\FootballManager\\Manager\\Support.cpp`

The third list at +0x5D0 loads support-staff references through the global support structure at `0x875604` and appends them into the same list family.

The +0x5E0 triplet is also a list header; periodic/user-management code appends small entries to it. Its exact element semantics remain unresolved, but its list behavior rules it out as a scalar chairman-budget field.

### Conclusion

DBRUser `+0x5B8/+0x5C4/+0x5D0` are support-staff-related list containers. The adjacent +0x5E0 structure is also list state. None should be interpreted as the chairman transfer/operating budget array.


## Monthly DBRUser maintenance dispatcher 0x42AEB0

The monthly DBRUser routine `0x42AEB0` is now resolved as a three-part **stadium/facility maintenance debit** dispatcher rather than chairman quarterly rebudgeting.

It calls:

1. `0x42B000`
2. `0x42AED0`
3. `0x42B3B0`

and all three eventually construct finance values and debit the active Balance with `0x5DC650`.

### 0x42AED0 — stadium-size maintenance, accounting category 601

The routine queries the stadium object at `DBRUser +0x6B0` through `0x65DA60` and `0x65D9B0`, combines the result, and feeds it through `0x4290A0`.

The resulting stadium/capacity-like value is bracketed at 10,000-unit steps from 10,000 through 90,000, selecting one of the tuning values:

- `SM_10000`
- `SM_20000`
- ...
- `SM_100000`

The chosen maintenance amount is converted through `0x5E43B0` with accounting category **0x259 = 601** and then debited from the active Balance through `0x5DC650`.

### 0x42B000 — pitch-system maintenance, accounting category 603

This routine reads byte levels/state from the 0x14-byte object at `DBRUser +0x6A8` and computes maintenance from exact tuning-key pairs:

- `SpinklersMaintenance` + `SpinklersMaintenanceLevel`
- `DrainageMaintenance` + `DrainageMaintenanceLevel`
- `PitchCoverMaintenance` + `PitchCoverMaintenanceLevel`
- `HeatingMaintenance` + `HeatingMaintenanceLevel`

The total is posted/debited as accounting category **0x25B = 603** through Balance debit `0x5DC650`.

Thus `DBRUser +0x6A8` is pitch/stadium-installation maintenance state, not chairman-budget storage.

### 0x42B3B0 — major facility maintenance, accounting category 602

This routine queries the collection at `DBRUser +0x65C` for facility IDs 0..6. For present facilities, it combines a base maintenance amount with the facility's current level through these tuning pairs:

- `SchoolMaintenance` / `SchoolMaintenanceLevel`
- `HotelMaintenance` / `HotelMaintenanceLevel`
- `HospitalMaintenance` / `HospitalMaintenanceLevel`
- `ClubMaintenance` / `ClubMaintenanceLevel`
- `TrainingMaintenance` / `TrainingMaintenanceLevel`
- `ParkingMaintenance` / `ParkingMaintenanceLevel`
- `MerchandisingMaintenance` / `MerchandisingMaintenanceLevel`

The accumulated cost is posted/debited as accounting category **0x25A = 602** through `0x5DC650`.

The object at `DBRUser +0x65C` is therefore a facility/building collection used to query facility presence/level, not a chairman-budget scalar.

### Consequence

The monthly `0x42AEB0` branch belongs to operating maintenance and cash accounting. It does not calculate the chairman's quarterly operating limits or the transfer-budget reserve.

It does, however, recover three precise finance categories:

- 601 = stadium-size maintenance
- 602 = major facility/building maintenance
- 603 = pitch-system maintenance

These are separate from category 1000 (transfers) and category 1100 (stadium/grounds expenditure previously mapped).


## Daily FA transfer-window calendar events

The genuine daily DBRUser/calendar dispatcher around `0x42AA60..0x42AD14` directly constructs three FA transfer-window events. RTTI and event-ID accessors identify them exactly:

- **0x88 = EAMFAtransferdeadlinesoon**
  - vtable `0x7CFBB4`
  - constructor/populator `0x56D9A0`
  - ID accessor `0x5414F0` -> 0x88
- **0x89 = EAMFAtransferdeadlinenow**
  - vtable `0x7CFC08`
  - constructor/populator `0x56DC10`
  - ID accessor `0x541540` -> 0x89
- **0x8A = EAMFAtransfernegstart**
  - vtable `0x7CFC5C`
  - constructor/populator `0x56DE00`
  - ID accessor `0x426850` -> 0x8A

The daily path tests calendar/date helpers before allocating and enqueueing these events into the global EAM/message system. This confirms that transfer-window warnings/opening are generated from the DBRUser daily calendar update rather than from transfer negotiation UI code.

These emissions occur before DBRUser event-list cleanup and the weekly/monthly maintenance/training/financial-objective branches.


## EAMbcmonthlybudget exact runtime layout

RTTI and vtable reconstruction now fixes the monthly Business Consultant budget statement precisely.

### Class identity

- RTTI type: `EAMbcmonthlybudget`
- TypeDescriptor: `0x82D5E8` (class name at `0x82D5F0`)
- Complete Object Locator: `0x7F12D0`
- vtable: **`0x7D01A4`**
- constructor/reset: **`0x541B20`**
- event ID accessor: **`0x541B50 -> 0xA1`**
- name accessor: **`0x541B60 -> "bcmonthlybudget"`**
- serializer: **`0x5730C0`**
- formatter: **`0x573190`**

### Serialized fields

Serializer `0x5730C0` persists dwords at:

- +0x3C
- +0x40
- +0x44
- +0x48
- +0x4C
- +0x50
- +0x54
- +0x58

plus the inherited/event field at +0x38.

### Exact EA-authored formatter labels

Formatter `0x573190` maps the budget values to literal keys:

- `+0x3C` -> **TOTALBUDGET**
- `+0x40` -> **STAFFBUDGET**
- `+0x44` -> **PLAYERWAGEBUDGET**
- `+0x48` -> **MAINTENANCEBUDGET**
- `+0x4C` -> **MISCBUDGET**
- `+0x50` -> **BUILDINGSBUDGET**
- `+0x54` -> **TRANSFERBUDGET**

The monthly statement therefore contains seven budget values. Unlike the season chairman budget-settings mail, it has **no separate merchandising-budget field**.

The remaining `+0x58` serialized dword is context/identity state rather than a formatted budget value; its exact semantic label remains to be confirmed.

### Importance

The English `bcsmonthlybudget` text states that these values show how the budgets stand **after last month's expenditure**. Therefore `EAMbcmonthlybudget +0x54` is currently the strongest observable representation of the live/remaining transfer budget and its producer is the highest-priority route to the authoritative derivation/state.


## MatchEngine feasibility / modular calculation checkpoint

A dedicated match investigation now establishes a clearer executable boundary.

### High-level calculator route

At `0x513010`:

- a temporary match-record/state object is built through `0x62ABD0`;
- developer getter `0x516080` (`/skipmatchcalc777`) can redirect processing to compact result routine `0x512D80`;
- the normal path calls `0x632B20` or wrapper `0x632B50`;
- `0x632B50` clears byte `match_record +0x1145` and delegates to `0x632B20`;
- `0x632B20` stores the record pointer at global `0x981C78`, then calls `0x62AC90`, `0x62FBC0`, and `0x667E20`;
- fresh disassembly proves `0x667E20` is just **`ret`** in this build, so it is not a third calculation stage;
- `0x62AC90` initializes/reset match/player state;
- `0x62FBC0` drives the simulator by repeatedly invoking `0x62AE90`.

The primary backend calculation trace is therefore `0x62AC90 -> 0x62FBC0 -> repeated 0x62AE90`, with `0x667E20` a no-op placeholder.

### Presentation/data split

The executable separately exposes:

- MatchCalculator command classes such as tactics, strategy, style, formation and substitution commands;
- FastView sender/receiver classes for semantic match events;
- MatchEngine data loaders for `SCTABLE.STI`, `AISEQS.TBI`, `MOAI.VIV`, `GEN4TBLS.T` and FC/FCDB assets.

This makes the backend calculator, semantic event stream and 3D scenario/animation presentation independently traceable.

Full asset-format findings are maintained in `research/MATCH_ENGINE.md`.


## Match calculator five-minute loop and weighted team aggregates

Further static tracing of `0x62AE90` / `0x62B1A0` establishes the calculator's basic temporal and numerical model.

- normal play is simulated in five-minute chunks at 5..40 and 50..85;
- a type-6 boundary record is inserted at minute 45;
- extra time, when required, is processed at 95/100 and 110/115 with type-8 boundary handling around 90/105;
- penalty routine `0x631730` creates type-9 state at minute 90 or 120 depending extra-time use;
- final state uses the type-7 record family.

Within each five-minute segment, `0x62B1A0` computes complementary floating team-strength aggregates through `0x62F140` and `0x62F3E0`.

Both aggregate routines iterate participating players and then loop exactly **17 skill slots** per player, reading current raw skills from player runtime +0x1E+slot and applying player/status/tactical/context multipliers plus large role/context weight tables.

The resulting ratios feed RNG `0x64D5B0` and event-generation routines including `0x62C740`, `0x62E130`, `0x62E2F0`, and `0x62E6F0`.

This proves the backend is a discrete weighted probabilistic event simulator. Exact semantic names for the two strength dimensions and downstream event branches remain active work.


## MatchCalculator record type -> FastView sender mapping

RTTI on the match-controller sender members plus the record switch at `0x519862` now gives direct semantic mapping for MatchCalculator records.

Controller sender layout from constructor `0x518C80`:

- +0x10 Sender<EventGoal>
- +0x20 Sender<EventPossession>
- +0x30 Sender<EventPenaltyShootoutShot>
- +0x40 Sender<EventHalfTime>
- +0x50 Sender<EventFullTime>
- +0x60 Sender<EventExtraTime>
- +0x70 Sender<EventPenalties>
- +0x80 Sender<EventSub>

The controller's MatchCalculator record type at +0x28 maps:

- 0..4 -> EventGoal family
- 5 -> unresolved player incident/state family
- 6 -> HalfTime
- 7 -> FullTime
- 8 -> ExtraTime
- 9 -> Penalties
- 10 -> Substitution

During penalty-shootout state, type-1 goal-family records are instead sent through EventPenaltyShootoutShot.

Lower calculator branches confirm that the side-indexed score dwords at +0xD4C/+0xD50 are incremented in multiple paths immediately before appending types from the 0..4 family.

This establishes a direct calculator-record -> semantic FastView bridge.

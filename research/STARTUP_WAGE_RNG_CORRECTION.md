# Startup Wage RNG Correction

_Last verified: 27 September 2026_

This note supersedes the earlier Gate-2 through Gate-8 deterministic RNG and
audit values wherever they conflict with the values below.

The underlying reconstructed mechanics remain valid. The correction is one
previously omitted **mandatory DBRPlayer startup RNG call** that changes the
shared CRT stream before development, contract-span initialization, competition
construction, schedule shuffle and all later deterministic gameplay.

## Executable evidence

Canonical `FOOTBAL.EXE` SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

Inside compact-player importer `0x418B90`:

1. the player's overall rating is obtained;
2. the corresponding `DBTAccessSkillFinancialValues` /
   `DBRAccessSkillFinancialValue` record is selected;
3. `0x418E6E` calls **`0x423A50`**;
4. the returned value is stored at **DBRPlayer +0xC4**, the already-proven
   weekly-wage field;
5. only after that does the importer call development initializer
   `0x41E970` and the later `RNG(5)` contract-span initialization.

`0x423A50` reads the selected financial-value record's random range and
**unconditionally calls `0x64D540` once** before producing the starting
weekly wage.

Therefore every compact player contributes one previously omitted CRT draw.

The port currently consumes a neutral `RNG(1)` at that exact point until the
financial-value table itself is materialized. This is sufficient for the
hidden CRT state because every positive bounded call advances the same MSVC LCG
once. It does **not** claim that starting weekly wage values are implemented
yet; decoding/materializing those wages is the next Gate-9 contract task.

## Corrected DBTPlayers startup ledger

Shipped player count: **30,064**.

Original ordering is now:

```text
30,064 x constructor RNG(15)

then for each player in table order:
    wage RNG(financial-value range)
    development RNG(1)
    development RNG(2)
    development RNG(2)
    contract-span RNG(5)
```

Total DBTPlayers calls:

```text
30,064 constructor calls
+ 5 * 30,064 load calls
= 180,384 CRT calls
```

The old **150,320** total omitted the wage call and is superseded.

With fixed test seed `0x12345678` after Loader444's 260 calls:

- old post-player state: `0x8FF8E56C`;
- corrected post-player state: **`0xA9C5115C`**.

For the synthetic composed startup regression used by the Gate-3 tests:

- after players: **`0xC6A1E94A`**;
- after generated team names: **`0x9936CABA`**;
- after youth generation: **`0x4B68DE28`**.

The old synthetic post-youth state `0x2797444C` is superseded.

## Corrected Gate-3 canonical competition replay

Starting from corrected synthetic post-youth state `0x4B68DE28`:

- procedural League round-robin calls: **3,982**;
- actual-count Cup participant shuffles: **1,728**;
- DummyLeague lazy-ranking calls: **124**;
- Europe-selector calls: **2**;
- total primary competition calls: **5,836**;
- RNG-bearing events: **167** plus one zero-draw fixed-League traversal marker;
- state entering primary `0x615BE0`: **`0x4F5CF274`**.

The procedural League count changes from the old 4,302 because the solver's
random choices/backtracking path depends on the corrected incoming CRT stream.

Corrected ordered-bound SHA-256:

`3fb0ad9c8b9d21f55916e36c82d22762a0c45e37045f264ccb01a7dfc5415196`

Europe selector traversal indices remain 138 and 159, but the corrected selected
clubs are:

- Champions League selector: **1118**;
- UEFA Cup selector: **1139**.

Corrected materialization digests:

- Cup participants:
  `dd1f880d75aa63ff6bad1276cbac971c9a5ef568fe7fe0474401e690c12128ca`
- Cup pairings/groups:
  `f8654c52f03bdefde67ed0421d54eeed1e2cc77209dc92d167dae3329817895b`
- Cup schedule nodes:
  `b8705d885dd4d3be6a40df33744746884c074678032add21da1b1001c22bfe33`
- complete primary schedule nodes:
  `d2645b5973e0c6e41d8775724c3632239664331dbdb86eb7b435051f6b5cc058`

Structural counts remain:

- 1,226 Cup schedule nodes;
- 9,346 complete primary schedule nodes;
- 3 capacity-dropped allocation refs;
- 24 type-2 injected refs.

## Corrected Gate-4 schedule shuffle

Primary placement remains structurally stable:

- buckets: **373**;
- non-empty buckets: **168**;
- largest bucket: **147**;
- conflict-displaced nodes: **38**;
- bucket-shuffle calls: **9,178**.

Corrected bucket-count-vector SHA-256:

`5e4f566c7d8dc196d7a4a7064ead2f328debd9216ae06000e1b2c0b06f35b869`

Corrected shuffle state:

- before primary bucket shuffle: **`0x4F5CF274`**;
- after all 373 buckets: **`0xD25DFFE6`**.

Bucket 54 still contains 142 nodes and the fixed PL fixtures still occupy
pre-shuffle slots 96..105 as IDs 9..0. The corrected first Premier League
execution order is:

`0, 6, 8, 5, 1, 9, 3, 2, 4, 7`

Corrected first ten PL orders:

| Round | State before bucket | Fixture order |
| ---: | --- | --- |
| 1 | `0xD545A52D` | 0, 6, 8, 5, 1, 9, 3, 2, 4, 7 |
| 2 | `0x8A86E535` | 16, 14, 19, 11, 17, 13, 18, 15, 10, 12 |
| 3 | `0x6097BC6C` | 20, 23, 21, 29, 22, 27, 26, 24, 25, 28 |
| 4 | `0x5F974FE3` | 31, 35, 36, 37, 33, 38, 30, 32, 34, 39 |
| 5 | `0xA0CA8166` | 49, 43, 44, 47, 42, 41, 46, 48, 45, 40 |
| 6 | `0x9AE8168B` | 50, 58, 54, 59, 53, 51, 56, 55, 52, 57 |
| 7 | `0xE567E387` | 64, 62, 61, 66, 67, 65, 63, 69, 68, 60 |
| 8 | `0x7EE89D5E` | 75, 76, 78, 70, 72, 77, 79, 74, 73, 71 |
| 9 | `0x117F71A5` | 88, 80, 82, 81, 89, 85, 83, 84, 87, 86 |
| 10 | `0x82282EF3` | 99, 91, 97, 95, 92, 90, 94, 98, 93, 96 |

All 38 PL round orders compact digest:

`99496e4c16c423d3d5dd97232643b3e643232857ae0b4930bc2c99500baae89c`

## Corrected Gate-5 canonical integration

Three real PL rounds still complete all structural/persistence checks.

Corrected audit SHA-256:

`3c48d74ef2428dbc421f1ff39fa6952a095499f19dfdc312642884844c0c0a61`

After 30 fixtures:

- table played total: **60**;
- global goals: **108**;
- table wins / draws / losses: **27 / 6 / 27**;
- table points: **87**;
- Condition range: **60..99**;
- injury state entries/exits: **5 / 0**;
- suspension state entries/exits: **3 / 1**;
- yellow total: **47**;
- final match RNG: **`0x49C51E88`**.

## Corrected Gate-6 full-season audits

All three deterministic 38-round / 380-fixture seasons still pass every
full-season invariant and end on 20 May 2001.

### Seed 1

Audit SHA-256:
`c20ac0494001e1efae30d038475cd55fff64156191a9464401fbd82090ecb169`

- goals: **995**;
- wins / draws / losses: **295 / 170 / 295**;
- points: **1,055**;
- Condition: **83..99**;
- injury entries/exits: **114 / 102**;
- final injured: **12**;
- suspension entries/exits: **56 / 52**;
- final suspended: **4**;
- yellow total: **621**;
- final match RNG: **`0xE0B41D65`**.

### Seed 2

Audit SHA-256:
`237933d6771539807e0afce2b0caaffd85d71a87b1135490073c0b84b09f91f3`

- goals: **1,067**;
- wins / draws / losses: **313 / 134 / 313**;
- points: **1,073**;
- Condition: **30..99**;
- injury entries/exits: **92 / 78**;
- final injured: **14**;
- suspension entries/exits: **60 / 57**;
- final suspended: **3**;
- yellow total: **641**;
- final match RNG: **`0x0EF4D519`**.

### Seed 3

Audit SHA-256:
`9ce250077d5b05a73e227cea72e9ec26eae2702bf507841cc6ded3b1c000da16`

- goals: **1,022**;
- wins / draws / losses: **295 / 170 / 295**;
- points: **1,055**;
- Condition: **56..99**;
- injury entries/exits: **105 / 92**;
- final injured: **13**;
- suspension entries/exits: **58 / 52**;
- final suspended: **6**;
- yellow total: **593**;
- final match RNG: **`0x395B758A`**.

## Corrected Gate-7 human audit

Arsenal remains the canonical human club (ID 0). Six fixtures / six complete
matchdays still execute through the shared backend and produce 60 stored
results.

Corrected audit SHA-256:

`4e324f5b231e62893849c904bde5a4c5cb5cb9ee3be4f54d119e5d850c8be33e`

Arsenal's six results are:

- 19 Aug: Aston Villa 1-1 Arsenal;
- 23 Aug: Arsenal 1-2 Liverpool;
- 26 Aug: Arsenal 3-5 Charlton Athletic;
- 2 Sep: Chelsea 1-1 Arsenal;
- 16 Sep: Bradford City 0-3 Arsenal;
- 23 Sep: Arsenal 2-1 Coventry City.

Final segment record: **2-2-2, 8 points, +1 goal difference**.

- human Condition range: **28..80**;
- injured: **1**;
- suspended: **0**;
- final match RNG: **`0xC0009A67`**.

## Corrected Gate-8 save/reload audit

The schema-2 save/reload implementation remains equivalent.

Corrected audit SHA-256:

`25d5a461cf0c7eb4e05ad718d81a81815407deb15c25784eff514842e28d0b03`

The save is still taken on **26 August 2000** before Arsenal fixture ID 20, but
the corrected Gate-4 scheduler now places Arsenal **first** on that date.

Therefore at the save boundary:

- prior same-day results: **0**;
- pending human fixture: **20**;
- later same-day fixtures:
  **23, 21, 29, 22, 27, 26, 24, 25, 28**.

Schema-2 size at this corrected checkpoint:

- raw deterministic JSON: **6,505,031 bytes**;
- gzip: **995,553 bytes**;
- raw save SHA-256:
  `052532ed0958d42ab628887d29d603788c7d5b9789c558de713e824784dfce53`;
- source signature remains:
  `6ba4b9c3bce385f084053d7b0ef13595652e3335ac7ea04991637281785668cc`.

Reloaded and uninterrupted branches remain exactly equal through the remaining
four audited human fixtures and 60 stored PL results.

Final match RNG: **`0xC0009A67`**.

## Validation

At main checkpoint `76ab612b5e9e678a2703f24d0efdc72212146928`:

- GitHub reconstruction suite: **413 tests passed**;
- repository asset-policy workflow: **passed**;
- canonical shipped-data verifier: **passed** locally after re-baseline;
- Gate-5 three-round audit: passed;
- Gate-6 38-round audits for seeds 1, 2 and 3: passed;
- Gate-7 six-human-fixture audit: passed;
- Gate-8 save/reload continuation audit: passed.

## Gate-9 consequence

Gates 1–8 remain complete. The correction does not reopen those functional
gates.

Gate 9 resumes by materializing the already-located
`DBTAccessSkillFinancialValues` wage lookup so `RuntimePlayer` can store the
authentic starting weekly wage and contract expiry/terms rather than merely
consuming the wage RNG call for shared-stream fidelity.
